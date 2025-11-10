'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { caseGroupsAPI, authAPI } from '@/lib/api'
import { 
  FolderOpen, 
  Plus, 
  Search, 
  Filter,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  FileText
} from 'lucide-react'

interface CaseGroup {
  id: string
  case_number: string
  case_type: string
  status: string
  priority: string
  approval_status: string
  beneficiary?: {
    id: string
    first_name: string
    last_name: string
    user?: {
      email: string
    }
  }
  responsible_party?: {
    full_name: string
  }
  created_by_manager?: {
    full_name: string
  }
  case_started_date?: string
  target_completion_date?: string
  notes?: string
  attorney_portal_link?: string
}

export default function CasesPage() {
  const router = useRouter()
  const [caseGroups, setCaseGroups] = useState<CaseGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [caseTypeFilter, setCaseTypeFilter] = useState<string>('all')
  const [approvalStatusFilter, setApprovalStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Get current user
      const userResponse = await authAPI.getCurrentUser()
      setCurrentUser(userResponse.data)
      
      // Get case groups
      const casesResponse = await caseGroupsAPI.getAll()
      setCaseGroups(casesResponse)
    } catch (error) {
      console.error('Error loading cases:', error)
    } finally {
      setLoading(false)
    }
  }

  // Filter case groups
  const filteredCaseGroups = caseGroups.filter((caseGroup) => {
    const matchesSearch = 
      searchTerm === '' ||
      caseGroup.case_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      caseGroup.beneficiary?.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      caseGroup.beneficiary?.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      caseGroup.beneficiary?.user?.email?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || caseGroup.status === statusFilter
    const matchesCaseType = caseTypeFilter === 'all' || caseGroup.case_type === caseTypeFilter
    const matchesApprovalStatus = approvalStatusFilter === 'all' || caseGroup.approval_status === approvalStatusFilter
    const matchesPriority = priorityFilter === 'all' || caseGroup.priority === priorityFilter
    
    return matchesSearch && matchesStatus && matchesCaseType && matchesApprovalStatus && matchesPriority
  })

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { variant: any; label: string }> = {
      PLANNING: { variant: 'secondary', label: 'Planning' },
      IN_PROGRESS: { variant: 'default', label: 'In Progress' },
      COMPLETED: { variant: 'success', label: 'Completed' },
      ON_HOLD: { variant: 'warning', label: 'On Hold' },
      CANCELLED: { variant: 'destructive', label: 'Cancelled' },
    }
    const config = statusConfig[status] || { variant: 'secondary', label: status }
    return <Badge variant={config.variant as any}>{config.label}</Badge>
  }

  const getApprovalStatusBadge = (approvalStatus: string) => {
    const statusConfig: Record<string, { icon: any; variant: any; label: string }> = {
      DRAFT: { icon: FileText, variant: 'secondary', label: 'Draft' },
      PENDING_PM_APPROVAL: { icon: Clock, variant: 'warning', label: 'Pending Approval' },
      PM_APPROVED: { icon: CheckCircle, variant: 'success', label: 'Approved' },
      PM_REJECTED: { icon: XCircle, variant: 'destructive', label: 'Rejected' },
    }
    const config = statusConfig[approvalStatus] || { icon: FileText, variant: 'secondary', label: approvalStatus }
    const Icon = config.icon
    return (
      <Badge variant={config.variant as any} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    )
  }

  const getPriorityBadge = (priority: string) => {
    const priorityConfig: Record<string, { variant: any; label: string }> = {
      CRITICAL: { variant: 'destructive', label: 'Critical' },
      URGENT: { variant: 'destructive', label: 'Urgent' },
      HIGH: { variant: 'warning', label: 'High' },
      MEDIUM: { variant: 'default', label: 'Medium' },
      LOW: { variant: 'secondary', label: 'Low' },
    }
    const config = priorityConfig[priority] || { variant: 'secondary', label: priority }
    return <Badge variant={config.variant as any}>{config.label}</Badge>
  }

  const getCaseTypeLabel = (caseType: string) => {
    const typeLabels: Record<string, string> = {
      H1B: 'H1B',
      H1B_TRANSFER: 'H1B Transfer',
      H1B_EXTENSION: 'H1B Extension',
      L1: 'L1',
      L1_EXTENSION: 'L1 Extension',
      TN: 'TN',
      TN_RENEWAL: 'TN Renewal',
      O1: 'O-1',
      EB1: 'EB-1',
      EB1A: 'EB-1A',
      EB1B: 'EB-1B',
      EB2: 'EB-2',
      EB2_NIW: 'EB-2 NIW',
      EB3: 'EB-3',
      PERM: 'PERM',
      I485: 'I-485 (AOS)',
      I140: 'I-140',
      EAD: 'EAD',
      AP: 'Advance Parole',
      H4: 'H4',
      H4_EAD: 'H4 EAD',
      L2: 'L2',
      CITIZENSHIP: 'Citizenship',
      OTHER: 'Other',
    }
    return typeLabels[caseType] || caseType
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const canCreateCase = () => {
    return currentUser?.role === 'MANAGER' || currentUser?.role === 'PM' || currentUser?.role === 'HR'
  }

  return (
    <AppLayout>
      <div className="container mx-auto py-6 space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <FolderOpen className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Case Tracking</h1>
              <p className="text-gray-600">Immigration case management and workflow tracking</p>
            </div>
          </div>
        </div>

        {/* Filters and Actions */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Filter className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Filters</CardTitle>
              </div>
              {canCreateCase() && (
                <Button onClick={() => router.push('/cases/new')}>
                  <Plus className="h-4 w-4 mr-2" />
                  New Case
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {/* Search */}
              <div className="lg:col-span-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search by case number, employee name, or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Status Filter */}
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="PLANNING">Planning</SelectItem>
                  <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                  <SelectItem value="COMPLETED">Completed</SelectItem>
                  <SelectItem value="ON_HOLD">On Hold</SelectItem>
                  <SelectItem value="CANCELLED">Cancelled</SelectItem>
                </SelectContent>
              </Select>

              {/* Case Type Filter */}
              <Select value={caseTypeFilter} onValueChange={setCaseTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Case Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Case Types</SelectItem>
                  <SelectItem value="H1B">H1B</SelectItem>
                  <SelectItem value="H1B_TRANSFER">H1B Transfer</SelectItem>
                  <SelectItem value="EB1">EB-1</SelectItem>
                  <SelectItem value="EB1A">EB-1A</SelectItem>
                  <SelectItem value="EB2">EB-2</SelectItem>
                  <SelectItem value="EB2_NIW">EB-2 NIW</SelectItem>
                  <SelectItem value="TN">TN</SelectItem>
                  <SelectItem value="PERM">PERM</SelectItem>
                  <SelectItem value="I485">I-485</SelectItem>
                </SelectContent>
              </Select>

              {/* Approval Status Filter */}
              <Select value={approvalStatusFilter} onValueChange={setApprovalStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Approval Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Approval Statuses</SelectItem>
                  <SelectItem value="DRAFT">Draft</SelectItem>
                  <SelectItem value="PENDING_PM_APPROVAL">Pending Approval</SelectItem>
                  <SelectItem value="PM_APPROVED">Approved</SelectItem>
                  <SelectItem value="PM_REJECTED">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Priority Filter */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Priority:</span>
              <div className="flex gap-2">
                <Button
                  variant={priorityFilter === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPriorityFilter('all')}
                >
                  All
                </Button>
                <Button
                  variant={priorityFilter === 'CRITICAL' ? 'destructive' : 'outline'}
                  size="sm"
                  onClick={() => setPriorityFilter('CRITICAL')}
                >
                  Critical
                </Button>
                <Button
                  variant={priorityFilter === 'URGENT' ? 'destructive' : 'outline'}
                  size="sm"
                  onClick={() => setPriorityFilter('URGENT')}
                >
                  Urgent
                </Button>
                <Button
                  variant={priorityFilter === 'HIGH' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPriorityFilter('HIGH')}
                >
                  High
                </Button>
                <Button
                  variant={priorityFilter === 'MEDIUM' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPriorityFilter('MEDIUM')}
                >
                  Medium
                </Button>
                <Button
                  variant={priorityFilter === 'LOW' ? 'outline' : 'outline'}
                  size="sm"
                  onClick={() => setPriorityFilter('LOW')}
                >
                  Low
                </Button>
              </div>
            </div>

            {/* Results Count */}
            <div className="text-sm text-muted-foreground">
              Showing {filteredCaseGroups.length} of {caseGroups.length} cases
            </div>
          </CardContent>
        </Card>

        {/* Cases Table */}
        <Card>
          <CardHeader>
            <CardTitle>Immigration Cases</CardTitle>
            <CardDescription>
              View and manage all immigration cases
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-muted-foreground">Loading cases...</div>
              </div>
            ) : filteredCaseGroups.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <FolderOpen className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No cases found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm || statusFilter !== 'all' || caseTypeFilter !== 'all' || approvalStatusFilter !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Get started by creating your first case'}
                </p>
                {canCreateCase() && (
                  <Button onClick={() => router.push('/cases/new')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Case
                  </Button>
                )}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Case Number</TableHead>
                      <TableHead>Employee</TableHead>
                      <TableHead>Case Type</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Approval</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Started</TableHead>
                      <TableHead>Target Date</TableHead>
                      <TableHead>Manager</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredCaseGroups.map((caseGroup) => (
                      <TableRow 
                        key={caseGroup.id}
                        className="cursor-pointer hover:bg-muted/50"
                        onClick={() => router.push(`/cases/${caseGroup.id}`)}
                      >
                        <TableCell className="font-medium">
                          {caseGroup.case_number}
                        </TableCell>
                        <TableCell>
                          {caseGroup.beneficiary ? (
                            <div>
                              <div className="font-medium">
                                {caseGroup.beneficiary.first_name} {caseGroup.beneficiary.last_name}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {caseGroup.beneficiary.user?.email}
                              </div>
                            </div>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {getCaseTypeLabel(caseGroup.case_type)}
                          </Badge>
                        </TableCell>
                        <TableCell>{getStatusBadge(caseGroup.status)}</TableCell>
                        <TableCell>{getApprovalStatusBadge(caseGroup.approval_status)}</TableCell>
                        <TableCell>{getPriorityBadge(caseGroup.priority)}</TableCell>
                        <TableCell className="text-sm">
                          {formatDate(caseGroup.case_started_date)}
                        </TableCell>
                        <TableCell className="text-sm">
                          {formatDate(caseGroup.target_completion_date)}
                        </TableCell>
                        <TableCell className="text-sm">
                          {caseGroup.created_by_manager?.full_name || 
                           caseGroup.responsible_party?.full_name || 
                           <span className="text-muted-foreground">N/A</span>}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              router.push(`/cases/${caseGroup.id}`)
                            }}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
