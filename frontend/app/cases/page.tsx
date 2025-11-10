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
  FileText,
  X,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Edit,
  AlertTriangle
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
      department?: {
        code: string
        name: string
      }
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

type SortableColumn = 'case_number' | 'beneficiary' | 'case_type' | 'status' | 'approval_status' | 'priority' | 'case_started_date' | 'target_completion_date' | 'department'

export default function CasesPage() {
  const router = useRouter()
  const [caseGroups, setCaseGroups] = useState<CaseGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)
  
  // Filters - now using arrays for multi-select
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([])
  const [selectedCaseTypes, setSelectedCaseTypes] = useState<string[]>([])
  const [selectedApprovalStatuses, setSelectedApprovalStatuses] = useState<string[]>([])
  const [selectedPriorities, setSelectedPriorities] = useState<string[]>([])
  
  // Sorting
  const [sortColumn, setSortColumn] = useState<SortableColumn | null>(null)
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc')

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
      console.log('Cases loaded:', casesResponse) // Debug log
      setCaseGroups(casesResponse)
    } catch (error) {
      console.error('Error loading cases:', error)
    } finally {
      setLoading(false)
    }
  }

  // Add/remove filter
  const toggleFilter = (filterArray: string[], value: string, setter: (arr: string[]) => void) => {
    if (filterArray.includes(value)) {
      setter(filterArray.filter(v => v !== value))
    } else {
      setter([...filterArray, value])
    }
  }

  const clearAllFilters = () => {
    setSearchTerm('')
    setSelectedStatuses([])
    setSelectedCaseTypes([])
    setSelectedApprovalStatuses([])
    setSelectedPriorities([])
  }

  const hasActiveFilters = () => {
    return searchTerm !== '' || 
           selectedStatuses.length > 0 || 
           selectedCaseTypes.length > 0 || 
           selectedApprovalStatuses.length > 0 || 
           selectedPriorities.length > 0
  }

  // Filter case groups
  const filteredCaseGroups = caseGroups.filter((caseGroup) => {
    const matchesSearch = 
      searchTerm === '' ||
      caseGroup.case_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      caseGroup.beneficiary?.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      caseGroup.beneficiary?.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      caseGroup.beneficiary?.user?.email?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = selectedStatuses.length === 0 || selectedStatuses.includes(caseGroup.status)
    const matchesCaseType = selectedCaseTypes.length === 0 || selectedCaseTypes.includes(caseGroup.case_type)
    const matchesApprovalStatus = selectedApprovalStatuses.length === 0 || selectedApprovalStatuses.includes(caseGroup.approval_status)
    const matchesPriority = selectedPriorities.length === 0 || selectedPriorities.includes(caseGroup.priority)
    
    return matchesSearch && matchesStatus && matchesCaseType && matchesApprovalStatus && matchesPriority
  })

  // Sort case groups
  const sortedCaseGroups = [...filteredCaseGroups].sort((a, b) => {
    if (!sortColumn) return 0
    
    let aValue: any
    let bValue: any
    
    switch (sortColumn) {
      case 'case_number':
        aValue = a.case_number || ''
        bValue = b.case_number || ''
        break
      case 'beneficiary':
        aValue = a.beneficiary ? `${a.beneficiary.first_name} ${a.beneficiary.last_name}` : ''
        bValue = b.beneficiary ? `${b.beneficiary.first_name} ${b.beneficiary.last_name}` : ''
        break
      case 'case_type':
        aValue = a.case_type || ''
        bValue = b.case_type || ''
        break
      case 'status':
        aValue = a.status || ''
        bValue = b.status || ''
        break
      case 'approval_status':
        aValue = a.approval_status || ''
        bValue = b.approval_status || ''
        break
      case 'priority':
        aValue = a.priority || ''
        bValue = b.priority || ''
        break
      case 'department':
        aValue = a.beneficiary?.user?.department?.code || ''
        bValue = b.beneficiary?.user?.department?.code || ''
        break
      case 'case_started_date':
        aValue = a.case_started_date ? new Date(a.case_started_date).getTime() : 0
        bValue = b.case_started_date ? new Date(b.case_started_date).getTime() : 0
        break
      case 'target_completion_date':
        aValue = a.target_completion_date ? new Date(a.target_completion_date).getTime() : 0
        bValue = b.target_completion_date ? new Date(b.target_completion_date).getTime() : 0
        break
      default:
        return 0
    }
    
    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1
    return 0
  })

  const handleSort = (column: SortableColumn) => {
    if (sortColumn === column) {
      if (sortDirection === 'asc') {
        setSortDirection('desc')
      } else {
        setSortColumn(null)
        setSortDirection('asc')
      }
    } else {
      setSortColumn(column)
      setSortDirection('asc')
    }
  }

  const getSortIcon = (column: SortableColumn) => {
    if (sortColumn !== column) {
      return <ArrowUpDown className="h-4 w-4 ml-1 opacity-50" />
    }
    if (sortDirection === 'asc') {
      return <ArrowUp className="h-4 w-4 ml-1" />
    }
    return <ArrowDown className="h-4 w-4 ml-1" />
  }

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { icon?: any; variant: any; label: string }> = {
      PLANNING: { icon: FileText, variant: 'secondary', label: 'Planning' },
      IN_PROGRESS: { icon: Clock, variant: 'default', label: 'In Progress' },
      COMPLETED: { icon: CheckCircle, variant: 'success', label: 'Completed' },
      ON_HOLD: { icon: AlertTriangle, variant: 'warning', label: 'On Hold' },
      CANCELLED: { icon: XCircle, variant: 'destructive', label: 'Cancelled' },
    }
    const config = statusConfig[status] || { variant: 'secondary', label: status }
    const Icon = config.icon
    return (
      <Badge variant={config.variant as any} className="flex items-center gap-1">
        {Icon && <Icon className="h-3 w-3" />}
        {config.label}
      </Badge>
    )
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
    return <Badge variant="outline" className={getPriorityColorClass(priority)}>{config.label}</Badge>
  }

  const getPriorityColorClass = (priority: string) => {
    const colorMap: Record<string, string> = {
      CRITICAL: 'border-red-500 text-red-700 bg-red-50',
      URGENT: 'border-orange-500 text-orange-700 bg-orange-50',
      HIGH: 'border-yellow-500 text-yellow-700 bg-yellow-50',
      MEDIUM: 'border-blue-500 text-blue-700 bg-blue-50',
      LOW: 'border-gray-400 text-gray-600 bg-gray-50',
    }
    return colorMap[priority] || ''
  }

  const getRowColorClass = (priority: string) => {
    const colorMap: Record<string, string> = {
      CRITICAL: 'bg-red-50 hover:bg-red-100 border-l-4 border-l-red-500',
      URGENT: 'bg-orange-50 hover:bg-orange-100 border-l-4 border-l-orange-500',
      HIGH: 'bg-yellow-50 hover:bg-yellow-100 border-l-4 border-l-yellow-400',
      MEDIUM: 'hover:bg-muted/50',
      LOW: 'hover:bg-muted/50',
    }
    return colorMap[priority] || 'hover:bg-muted/50'
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

  const canEditCase = () => {
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
          {canCreateCase() && (
            <Button onClick={() => router.push('/cases/new')}>
              <Plus className="h-4 w-4 mr-2" />
              New Case
            </Button>
          )}
        </div>

        {/* Filters and Actions */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Filter className="h-5 w-5 text-muted-foreground" />
                <CardTitle>Filters</CardTitle>
              </div>
              {hasActiveFilters() && (
                <Button variant="ghost" size="sm" onClick={clearAllFilters}>
                  <X className="h-4 w-4 mr-2" />
                  Clear All Filters
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by case number, employee name, or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Filter Dropdowns */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Status Filter */}
              <Select value="" onValueChange={(value) => toggleFilter(selectedStatuses, value, setSelectedStatuses)}>
                <SelectTrigger className="bg-white">
                  <SelectValue placeholder="Add Status Filter" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="PLANNING">Planning</SelectItem>
                  <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
                  <SelectItem value="COMPLETED">Completed</SelectItem>
                  <SelectItem value="ON_HOLD">On Hold</SelectItem>
                  <SelectItem value="CANCELLED">Cancelled</SelectItem>
                </SelectContent>
              </Select>

              {/* Case Type Filter */}
              <Select value="" onValueChange={(value) => toggleFilter(selectedCaseTypes, value, setSelectedCaseTypes)}>
                <SelectTrigger className="bg-white">
                  <SelectValue placeholder="Add Case Type Filter" />
                </SelectTrigger>
                <SelectContent className="bg-white">
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
              <Select value="" onValueChange={(value) => toggleFilter(selectedApprovalStatuses, value, setSelectedApprovalStatuses)}>
                <SelectTrigger className="bg-white">
                  <SelectValue placeholder="Add Approval Filter" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="DRAFT">Draft</SelectItem>
                  <SelectItem value="PENDING_PM_APPROVAL">Pending Approval</SelectItem>
                  <SelectItem value="PM_APPROVED">Approved</SelectItem>
                  <SelectItem value="PM_REJECTED">Rejected</SelectItem>
                </SelectContent>
              </Select>

              {/* Priority Filter */}
              <Select value="" onValueChange={(value) => toggleFilter(selectedPriorities, value, setSelectedPriorities)}>
                <SelectTrigger className="bg-white">
                  <SelectValue placeholder="Add Priority Filter" />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="CRITICAL">Critical</SelectItem>
                  <SelectItem value="URGENT">Urgent</SelectItem>
                  <SelectItem value="HIGH">High</SelectItem>
                  <SelectItem value="MEDIUM">Medium</SelectItem>
                  <SelectItem value="LOW">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Active Filters as Buttons */}
            {hasActiveFilters() && (
              <div className="flex flex-wrap gap-2">
                {selectedStatuses.map(status => (
                  <Button
                    key={status}
                    variant="secondary"
                    size="sm"
                    onClick={() => toggleFilter(selectedStatuses, status, setSelectedStatuses)}
                  >
                    Status: {getStatusBadge(status).props.children[1]}
                    <X className="h-3 w-3 ml-2" />
                  </Button>
                ))}
                {selectedCaseTypes.map(type => (
                  <Button
                    key={type}
                    variant="secondary"
                    size="sm"
                    onClick={() => toggleFilter(selectedCaseTypes, type, setSelectedCaseTypes)}
                  >
                    Type: {getCaseTypeLabel(type)}
                    <X className="h-3 w-3 ml-2" />
                  </Button>
                ))}
                {selectedApprovalStatuses.map(status => (
                  <Button
                    key={status}
                    variant="secondary"
                    size="sm"
                    onClick={() => toggleFilter(selectedApprovalStatuses, status, setSelectedApprovalStatuses)}
                  >
                    Approval: {getApprovalStatusBadge(status).props.children[1]}
                    <X className="h-3 w-3 ml-2" />
                  </Button>
                ))}
                {selectedPriorities.map(priority => (
                  <Button
                    key={priority}
                    variant="secondary"
                    size="sm"
                    onClick={() => toggleFilter(selectedPriorities, priority, setSelectedPriorities)}
                  >
                    Priority: {getPriorityBadge(priority).props.children}
                    <X className="h-3 w-3 ml-2" />
                  </Button>
                ))}
              </div>
            )}

            {/* Results Count */}
            <div className="text-sm text-muted-foreground">
              Showing {sortedCaseGroups.length} of {caseGroups.length} cases
            </div>
          </CardContent>
        </Card>

        {/* Cases Table */}
        <Card>
          <CardHeader>
            <CardTitle>Immigration Cases</CardTitle>
            <CardDescription>
              View and manage all immigration cases. Click column headers to sort.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="text-muted-foreground">Loading cases...</div>
              </div>
            ) : sortedCaseGroups.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <FolderOpen className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No cases found</h3>
                <p className="text-muted-foreground mb-4">
                  {hasActiveFilters()
                    ? 'Try adjusting your filters'
                    : 'Get started by creating your first case'}
                </p>
                {canCreateCase() && !hasActiveFilters() && (
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
                      <TableHead className="cursor-pointer" onClick={() => handleSort('beneficiary')}>
                        <div className="flex items-center">
                          Employee
                          {getSortIcon('beneficiary')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('department')}>
                        <div className="flex items-center">
                          Department
                          {getSortIcon('department')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('case_type')}>
                        <div className="flex items-center">
                          Case Type
                          {getSortIcon('case_type')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('status')}>
                        <div className="flex items-center">
                          Status
                          {getSortIcon('status')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('priority')}>
                        <div className="flex items-center">
                          Priority
                          {getSortIcon('priority')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('target_completion_date')}>
                        <div className="flex items-center">
                          Next Deadline
                          {getSortIcon('target_completion_date')}
                        </div>
                      </TableHead>
                      <TableHead>Assigned To</TableHead>
                      <TableHead>Law Firm</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedCaseGroups.map((caseGroup) => (
                      <TableRow 
                        key={caseGroup.id}
                        className={`cursor-pointer ${getRowColorClass(caseGroup.priority)}`}
                        onClick={() => router.push(`/cases/${caseGroup.id}`)}
                      >
                        <TableCell>
                          {caseGroup.beneficiary ? (
                            <div>
                              <div className="font-medium">
                                {caseGroup.beneficiary.first_name} {caseGroup.beneficiary.last_name}
                              </div>
                              <div className="text-xs text-muted-foreground">
                                {caseGroup.case_number}
                              </div>
                            </div>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="font-mono">
                            {caseGroup.beneficiary?.user?.department?.code || 'N/A'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {getCaseTypeLabel(caseGroup.case_type)}
                          </Badge>
                        </TableCell>
                        <TableCell>{getStatusBadge(caseGroup.status)}</TableCell>
                        <TableCell>{getPriorityBadge(caseGroup.priority)}</TableCell>
                        <TableCell className="text-sm">
                          {formatDate(caseGroup.target_completion_date)}
                        </TableCell>
                        <TableCell className="text-sm">
                          {caseGroup.created_by_manager?.full_name || 
                           caseGroup.responsible_party?.full_name || 
                           <span className="text-muted-foreground">N/A</span>}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          N/A
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation()
                                router.push(`/cases/${caseGroup.id}`)
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {canEditCase() && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  router.push(`/cases/${caseGroup.id}`)
                                }}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
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
