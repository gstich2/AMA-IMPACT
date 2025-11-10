'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import AppLayout from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { caseGroupsAPI, authAPI, visaAPI, lawFirmsAPI, usersAPI } from '@/lib/api'
import { 
  FolderOpen, 
  ArrowLeft,
  Clock,
  CheckCircle,
  XCircle,
  FileText,
  User,
  Calendar,
  AlertTriangle,
  ExternalLink,
  Send,
  ThumbsUp,
  ThumbsDown,
  Edit,
  Trash,
  Plus,
  ListTodo,
  History
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
    job_title?: string
    country_of_citizenship?: string
    current_visa_type?: string
    current_visa_expiration?: string
    employment_start_date?: string
    i94_expiration?: string
    user?: {
      email: string
      full_name?: string
      role?: string
      department?: {
        id: string
        code: string
        name: string
      }
      reports_to?: {
        id: string
        full_name: string
        email: string
      }
    }
  }
  responsible_party?: {
    id: string
    full_name: string
    email: string
    role?: string
    department?: {
      id: string
      code: string
      name: string
    }
  }
  created_by_manager?: {
    id: string
    full_name: string
    email: string
    role?: string
    department?: {
      id: string
      code: string
      name: string
    }
  }
  approved_by_pm?: {
    id: string
    full_name: string
    email: string
    role?: string
    department?: {
      id: string
      code: string
      name: string
    }
  }
  law_firm?: {
    id: string
    name: string
    contact_person?: string
    email?: string
    phone?: string
  }
  case_started_date?: string
  target_completion_date?: string
  case_completed_date?: string
  pm_approval_date?: string
  pm_approval_notes?: string
  notes?: string
  attorney_portal_link?: string
  visa_applications?: any[]
  todos?: any[]
  created_at?: string
  updated_at?: string
  days_since_initiated?: number
}

export default function CaseDetailPage() {
  const router = useRouter()
  const params = useParams()
  const caseId = params.id as string

  const [caseGroup, setCaseGroup] = useState<CaseGroup | null>(null)
  const [loading, setLoading] = useState(true)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [timeline, setTimeline] = useState<any>(null)
  const [timelineLoading, setTimelineLoading] = useState(false)
  
  // Dialog states
  const [showApprovalDialog, setShowApprovalDialog] = useState(false)
  const [approvalAction, setApprovalAction] = useState<'approve' | 'reject' | null>(null)
  const [approvalNotes, setApprovalNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  
  // Approval-specific fields
  const [hrUsers, setHrUsers] = useState<any[]>([])
  const [lawFirms, setLawFirms] = useState<any[]>([])
  const [selectedHrUser, setSelectedHrUser] = useState('')
  const [selectedLawFirm, setSelectedLawFirm] = useState('')

  useEffect(() => {
    loadData()
  }, [caseId])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Get current user
      const userResponse = await authAPI.getCurrentUser()
      setCurrentUser(userResponse.data)
      
      // Get case group details
      const caseResponse = await caseGroupsAPI.getById(caseId)
      setCaseGroup(caseResponse)
      
      // Load timeline
      loadTimeline()
    } catch (error) {
      console.error('Error loading case details:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTimeline = async () => {
    try {
      setTimelineLoading(true)
      const timelineResponse = await caseGroupsAPI.getTimeline(caseId)
      setTimeline(timelineResponse)
    } catch (error) {
      console.error('Error loading timeline:', error)
    } finally {
      setTimelineLoading(false)
    }
  }

  const handleSubmitForApproval = async () => {
    if (!caseGroup) return
    
    try {
      setSubmitting(true)
      await caseGroupsAPI.submitForApproval(caseGroup.id)
      await loadData()
    } catch (error) {
      console.error('Error submitting for approval:', error)
      alert('Failed to submit for approval')
    } finally {
      setSubmitting(false)
    }
  }

  const handleApprovalAction = async () => {
    if (!caseGroup || !approvalAction) return
    
    try {
      setSubmitting(true)
      
      if (approvalAction === 'approve') {
        // Validation for approval
        if (!selectedHrUser) {
          alert('Please select an HR user to assign this case')
          return
        }
        if (!selectedLawFirm) {
          alert('Please select a law firm for this case')
          return
        }
        
        await caseGroupsAPI.approve(caseGroup.id, {
          approval_notes: approvalNotes,
          assigned_hr_user_id: selectedHrUser,
          law_firm_id: selectedLawFirm
        })
      } else {
        if (!approvalNotes.trim()) {
          alert('Please provide rejection notes')
          return
        }
        await caseGroupsAPI.reject(caseGroup.id, {
          rejection_reason: approvalNotes
        })
      }
      
      setShowApprovalDialog(false)
      setApprovalNotes('')
      setApprovalAction(null)
      setSelectedHrUser('')
      setSelectedLawFirm('')
      await loadData()
    } catch (error) {
      console.error('Error processing approval:', error)
      alert(`Failed to ${approvalAction} case`)
    } finally {
      setSubmitting(false)
    }
  }

  const openApprovalDialog = async (action: 'approve' | 'reject') => {
    setApprovalAction(action)
    setApprovalNotes('')
    setSelectedHrUser('')
    setSelectedLawFirm('')
    
    // Load HR users and law firms when opening approval dialog
    if (action === 'approve') {
      try {
        const [usersResponse, lawFirmsResponse] = await Promise.all([
          usersAPI.getAll({ role: 'HR' }),
          lawFirmsAPI.getAll()
        ])
        setHrUsers(usersResponse)
        setLawFirms(lawFirmsResponse)
      } catch (error) {
        console.error('Error loading HR users or law firms:', error)
      }
    }
    
    setShowApprovalDialog(true)
  }

  const canSubmitForApproval = () => {
    if (!caseGroup || !currentUser) return false
    const role = currentUser.role?.toUpperCase()
    return (
      caseGroup.approval_status === 'DRAFT' &&
      (role === 'MANAGER' || role === 'HR' || role === 'ADMIN')
    )
  }

  const canApprove = () => {
    if (!caseGroup || !currentUser) return false
    const role = currentUser.role?.toUpperCase()
    return (
      caseGroup.approval_status === 'PENDING_PM_APPROVAL' &&
      (role === 'PM' || role === 'ADMIN')
    )
  }

  const canEdit = () => {
    if (!caseGroup || !currentUser) return false
    const role = currentUser.role?.toUpperCase()
    return (
      role === 'ADMIN' ||
      role === 'PM' ||
      role === 'MANAGER' ||
      role === 'HR'
    )
  }

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
      TN: 'TN',
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
      CITIZENSHIP: 'Citizenship',
      OTHER: 'Other',
    }
    return typeLabels[caseType] || caseType
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const formatDateTime = (dateString?: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <AppLayout>
        <div className="container mx-auto py-6">
          <div className="flex items-center justify-center py-12">
            <div className="text-muted-foreground">Loading case details...</div>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (!caseGroup) {
    return (
      <AppLayout>
        <div className="container mx-auto py-6">
          <div className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-muted-foreground mb-4" />
            <h2 className="text-xl font-semibold mb-2">Case Not Found</h2>
            <p className="text-muted-foreground mb-4">The case you're looking for doesn't exist.</p>
            <Button onClick={() => router.push('/cases')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Cases
            </Button>
          </div>
        </div>
      </AppLayout>
    )
  }

  return (
    <AppLayout>
      <div className="container mx-auto py-6 space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.push('/cases')}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
              <FolderOpen className="h-6 w-6 text-white" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h1 className="text-3xl font-bold text-gray-900">{caseGroup.case_number}</h1>
                {getApprovalStatusBadge(caseGroup.approval_status)}
                {getStatusBadge(caseGroup.status)}
                {getPriorityBadge(caseGroup.priority)}
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600">
                <span className="font-medium">{getCaseTypeLabel(caseGroup.case_type)}</span>
                {caseGroup.beneficiary && (
                  <>
                    <span className="text-gray-400">•</span>
                    <span>{caseGroup.beneficiary.first_name} {caseGroup.beneficiary.last_name}</span>
                  </>
                )}
                {(caseGroup as any).days_since_initiated && (
                  <>
                    <span className="text-gray-400">•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {(caseGroup as any).days_since_initiated} days since initiated
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {canEdit() && (
              <Button variant="outline" onClick={() => router.push(`/cases/${caseId}/edit`)}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Button>
            )}
          </div>
        </div>

        {/* Status and Approval Section */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Case Overview</CardTitle>
              <div className="flex items-center gap-2">
                {canSubmitForApproval() && (
                  <Button onClick={handleSubmitForApproval} disabled={submitting}>
                    <Send className="h-4 w-4 mr-2" />
                    Submit for Approval
                  </Button>
                )}
                {canApprove() && (
                  <>
                    <Button 
                      variant="destructive" 
                      onClick={() => openApprovalDialog('reject')}
                      disabled={submitting}
                    >
                      <ThumbsDown className="h-4 w-4 mr-2" />
                      Reject
                    </Button>
                    <Button 
                      onClick={() => openApprovalDialog('approve')}
                      disabled={submitting}
                    >
                      <ThumbsUp className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                  </>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Key Dates */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pb-4 border-b">
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-1">Started</div>
                <div className="text-sm">{formatDate(caseGroup.case_started_date)}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-1">Target Completion</div>
                <div className="text-sm">{formatDate(caseGroup.target_completion_date)}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-1">Created</div>
                <div className="text-sm">{formatDate(caseGroup.created_at)}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-1">Last Updated</div>
                <div className="text-sm">{formatDate(caseGroup.updated_at)}</div>
              </div>
            </div>

            {caseGroup.approval_status === 'PM_APPROVED' && caseGroup.pm_approval_notes && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <div className="font-medium text-green-900">Approved by {caseGroup.approved_by_pm?.full_name}</div>
                    <div className="text-sm text-green-700 mt-1">{caseGroup.pm_approval_notes}</div>
                    <div className="text-xs text-green-600 mt-1">{formatDateTime(caseGroup.pm_approval_date)}</div>
                  </div>
                </div>
              </div>
            )}

            {caseGroup.approval_status === 'PM_REJECTED' && caseGroup.pm_approval_notes && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                  <div className="flex-1">
                    <div className="font-medium text-red-900">Rejected by {caseGroup.approved_by_pm?.full_name}</div>
                    <div className="text-sm text-red-700 mt-1">{caseGroup.pm_approval_notes}</div>
                    <div className="text-xs text-red-600 mt-1">{formatDateTime(caseGroup.pm_approval_date)}</div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Beneficiary Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Beneficiary Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {caseGroup.beneficiary ? (
                <>
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">Name</div>
                    <div className="text-lg font-semibold">
                      {caseGroup.beneficiary.first_name} {caseGroup.beneficiary.last_name}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Job Title</div>
                      <div className="text-sm">{caseGroup.beneficiary.job_title || 'N/A'}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Citizenship</div>
                      <div className="text-sm">{caseGroup.beneficiary.country_of_citizenship || 'N/A'}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Current Visa</div>
                      <div className="text-sm">{caseGroup.beneficiary.current_visa_type || 'N/A'}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Visa Expiration</div>
                      <div className="text-sm">{formatDate(caseGroup.beneficiary.current_visa_expiration)}</div>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">Employment Start</div>
                      <div className="text-sm">{formatDate(caseGroup.beneficiary.employment_start_date)}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-muted-foreground">I-94 Expiration</div>
                      <div className="text-sm">{formatDate(caseGroup.beneficiary.i94_expiration)}</div>
                    </div>
                  </div>
                  {caseGroup.beneficiary.user && (
                    <>
                      <div className="pt-2 border-t">
                        <div className="text-sm font-medium text-muted-foreground mb-1">Contact</div>
                        <div className="text-sm">{caseGroup.beneficiary.user.email}</div>
                      </div>
                      {caseGroup.beneficiary.user.department && (
                        <div>
                          <div className="text-sm font-medium text-muted-foreground">Department</div>
                          <div className="text-sm">{caseGroup.beneficiary.user.department.name} ({caseGroup.beneficiary.user.department.code})</div>
                        </div>
                      )}
                      {caseGroup.beneficiary.user.reports_to && (
                        <div>
                          <div className="text-sm font-medium text-muted-foreground">Reports To</div>
                          <div className="text-sm font-medium text-blue-600 cursor-pointer hover:underline">
                            {caseGroup.beneficiary.user.reports_to.full_name}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </>
              ) : (
                <div className="text-muted-foreground">No beneficiary assigned</div>
              )}
            </CardContent>
          </Card>

          {/* Key Dates */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Key Dates
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-sm font-medium text-muted-foreground">Started Date</div>
                <div>{formatDate(caseGroup.case_started_date)}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Target Completion</div>
                <div>{formatDate(caseGroup.target_completion_date)}</div>
              </div>
              {caseGroup.case_completed_date && (
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Completed Date</div>
                  <div>{formatDate(caseGroup.case_completed_date)}</div>
                </div>
              )}
              <div>
                <div className="text-sm font-medium text-muted-foreground">Created</div>
                <div className="text-sm">{formatDateTime(caseGroup.created_at)}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Last Updated</div>
                <div className="text-sm">{formatDateTime(caseGroup.updated_at)}</div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Case Team */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Case Team
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* HR Responsible Party */}
              <div className="border rounded-lg p-4">
                <div className="text-sm font-medium text-muted-foreground mb-2">HR Responsible Party</div>
                {caseGroup.responsible_party ? (
                  <div className="space-y-1">
                    <div className="font-semibold">{caseGroup.responsible_party.full_name}</div>
                    {caseGroup.responsible_party.role && (
                      <Badge variant="secondary" className="text-xs">{caseGroup.responsible_party.role}</Badge>
                    )}
                    {caseGroup.responsible_party.department && (
                      <div className="text-xs text-muted-foreground">{caseGroup.responsible_party.department.name}</div>
                    )}
                    <div className="text-xs text-blue-600">{caseGroup.responsible_party.email}</div>
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">Not assigned</div>
                )}
              </div>

              {/* Law Firm */}
              <div className="border rounded-lg p-4">
                <div className="text-sm font-medium text-muted-foreground mb-2">Law Firm</div>
                {caseGroup.law_firm ? (
                  <div className="space-y-1">
                    <div className="font-semibold">{caseGroup.law_firm.name}</div>
                    {caseGroup.law_firm.contact_person && (
                      <div className="text-xs text-muted-foreground">Contact: {caseGroup.law_firm.contact_person}</div>
                    )}
                    {caseGroup.law_firm.email && (
                      <div className="text-xs text-blue-600">{caseGroup.law_firm.email}</div>
                    )}
                    {caseGroup.law_firm.phone && (
                      <div className="text-xs text-muted-foreground">{caseGroup.law_firm.phone}</div>
                    )}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">Not assigned</div>
                )}
              </div>

              {/* PM Approver */}
              <div className="border rounded-lg p-4">
                <div className="text-sm font-medium text-muted-foreground mb-2">PM Approver</div>
                {caseGroup.approved_by_pm ? (
                  <div className="space-y-1">
                    <div className="font-semibold">{caseGroup.approved_by_pm.full_name}</div>
                    {caseGroup.approved_by_pm.department && (
                      <div className="text-xs text-muted-foreground">{caseGroup.approved_by_pm.department.name}</div>
                    )}
                    {caseGroup.pm_approval_date && (
                      <div className="text-xs text-muted-foreground">{formatDate(caseGroup.pm_approval_date)}</div>
                    )}
                    <div className="text-xs text-blue-600">{caseGroup.approved_by_pm.email}</div>
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">Not yet approved</div>
                )}
              </div>

              {/* Created By Manager */}
              <div className="border rounded-lg p-4">
                <div className="text-sm font-medium text-muted-foreground mb-2">Created By</div>
                {caseGroup.created_by_manager ? (
                  <div className="space-y-1">
                    <div className="font-semibold">{caseGroup.created_by_manager.full_name}</div>
                    {caseGroup.created_by_manager.role && (
                      <Badge variant="outline" className="text-xs">{caseGroup.created_by_manager.role}</Badge>
                    )}
                    {caseGroup.created_by_manager.department && (
                      <div className="text-xs text-muted-foreground">{caseGroup.created_by_manager.department.name}</div>
                    )}
                    <div className="text-xs text-blue-600">{caseGroup.created_by_manager.email}</div>
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground">N/A</div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Timeline Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Activity Timeline
            </CardTitle>
            <CardDescription>
              Complete history of case events, milestones, and actions
            </CardDescription>
          </CardHeader>
          <CardContent>
            {timelineLoading ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                Loading timeline...
              </div>
            ) : timeline && timeline.events && timeline.events.length > 0 ? (
              <div className="space-y-4">
                {timeline.events.map((event: any, index: number) => {
                  const getEventIcon = () => {
                    switch (event.event_type) {
                      case 'case_created':
                        return <Plus className="h-4 w-4 text-blue-600" />
                      case 'submitted_for_approval':
                      case 'case_submitted':
                        return <Send className="h-4 w-4 text-yellow-600" />
                      case 'approved':
                      case 'case_approved':
                        return <CheckCircle className="h-4 w-4 text-green-600" />
                      case 'rejected':
                      case 'case_rejected':
                        return <XCircle className="h-4 w-4 text-red-600" />
                      case 'milestone':
                        return <Calendar className="h-4 w-4 text-purple-600" />
                      case 'todo_completed':
                        return <CheckCircle className="h-4 w-4 text-emerald-600" />
                      case 'status_changed':
                        return <Clock className="h-4 w-4 text-orange-600" />
                      default:
                        return <FileText className="h-4 w-4 text-gray-600" />
                    }
                  }

                  const getEventColor = () => {
                    switch (event.event_type) {
                      case 'approved':
                      case 'case_approved':
                        return 'border-l-green-500 bg-green-50'
                      case 'rejected':
                      case 'case_rejected':
                        return 'border-l-red-500 bg-red-50'
                      case 'submitted_for_approval':
                      case 'case_submitted':
                        return 'border-l-yellow-500 bg-yellow-50'
                      case 'milestone':
                        return 'border-l-purple-500 bg-purple-50'
                      case 'todo_completed':
                        return 'border-l-emerald-500 bg-emerald-50'
                      default:
                        return 'border-l-gray-300 bg-gray-50'
                    }
                  }

                  return (
                    <div 
                      key={event.id || index} 
                      className={`border-l-4 ${getEventColor()} p-4 rounded-r-lg relative`}
                    >
                      <div className="flex items-start gap-3">
                        <div className="mt-0.5">
                          {getEventIcon()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <div className="font-semibold text-sm">{event.title}</div>
                            <div className="text-xs text-muted-foreground whitespace-nowrap">
                              {formatDateTime(event.timestamp)}
                            </div>
                          </div>
                          {event.user_name && (
                            <div className="text-xs text-muted-foreground mb-1">
                              by {event.user_name}
                            </div>
                          )}
                          {event.description && (
                            <div className="text-sm text-gray-700 mt-1">
                              {event.description}
                            </div>
                          )}
                          {event.milestone_type && (
                            <Badge variant="secondary" className="text-xs mt-2">
                              {event.milestone_type.replace(/_/g, ' ')}
                            </Badge>
                          )}
                          {event.new_values && Object.keys(event.new_values).length > 0 && (
                            <details className="mt-2 text-xs">
                              <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                                View changes
                              </summary>
                              <div className="mt-1 p-2 bg-white rounded border space-y-1">
                                {Object.entries(event.new_values).map(([key, value]) => (
                                  <div key={key} className="flex gap-2">
                                    <span className="font-medium">{key}:</span>
                                    <span className="text-green-700">{String(value)}</span>
                                  </div>
                                ))}
                              </div>
                            </details>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No timeline events yet
              </div>
            )}
          </CardContent>
        </Card>

        {/* Case Notes */}
        {caseGroup.notes && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Case Notes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <p className="whitespace-pre-wrap">{caseGroup.notes}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Attorney Portal Link */}
        {caseGroup.attorney_portal_link && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ExternalLink className="h-5 w-5" />
                Attorney Portal
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                variant="outline"
                onClick={() => window.open(caseGroup.attorney_portal_link, '_blank')}
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Open Attorney Portal
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Visa Applications (if populated) */}
        {caseGroup.visa_applications && caseGroup.visa_applications.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Visa Applications ({caseGroup.visa_applications.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {caseGroup.visa_applications.map((visa: any) => (
                  <div key={visa.id} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <div className="font-medium">{visa.visa_type} - {visa.petition_type}</div>
                      <div className="text-sm text-muted-foreground">{visa.status}</div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => router.push(`/visas/${visa.id}`)}
                    >
                      View Details
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Todos (if populated) */}
        {caseGroup.todos && caseGroup.todos.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ListTodo className="h-5 w-5" />
                Related Todos ({caseGroup.todos.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {caseGroup.todos.map((todo: any) => (
                  <div key={todo.id} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <div className="font-medium">{todo.title}</div>
                      <div className="text-sm text-muted-foreground">
                        Status: {todo.status} | Priority: {todo.priority}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Approval Dialog */}
      <Dialog open={showApprovalDialog} onOpenChange={setShowApprovalDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {approvalAction === 'approve' ? 'Approve Case' : 'Reject Case'}
            </DialogTitle>
            <DialogDescription>
              {approvalAction === 'approve' 
                ? 'Assign an HR user and law firm, and optionally add approval notes.'
                : 'Please provide rejection notes explaining why this case is being rejected.'}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            {approvalAction === 'approve' && (
              <>
                {/* HR User Selection */}
                <div className="space-y-2">
                  <Label htmlFor="hr-user">Assign HR User *</Label>
                  <Select value={selectedHrUser} onValueChange={setSelectedHrUser}>
                    <SelectTrigger id="hr-user" className="w-full">
                      <SelectValue placeholder="Select HR user to assign this case" />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      {hrUsers.map((user) => (
                        <SelectItem key={user.id} value={user.id}>
                          {user.full_name} ({user.email})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Law Firm Selection */}
                <div className="space-y-2">
                  <Label htmlFor="law-firm">Assign Law Firm *</Label>
                  <Select value={selectedLawFirm} onValueChange={setSelectedLawFirm}>
                    <SelectTrigger id="law-firm" className="w-full">
                      <SelectValue placeholder="Select law firm for this case" />
                    </SelectTrigger>
                    <SelectContent className="bg-white">
                      {lawFirms.map((firm) => (
                        <SelectItem key={firm.id} value={firm.id}>
                          {firm.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}

            {/* Notes/Comments */}
            <div className="space-y-2">
              <Label htmlFor="notes">
                {approvalAction === 'approve' ? 'Approval Notes (Optional)' : 'Rejection Reason *'}
              </Label>
              <Textarea
                id="notes"
                placeholder={approvalAction === 'approve' ? 'Add any approval notes or comments...' : 'Explain why this case is being rejected...'}
                value={approvalNotes}
                onChange={(e) => setApprovalNotes(e.target.value)}
                rows={4}
                className="w-full"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowApprovalDialog(false)}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button
              variant={approvalAction === 'approve' ? 'default' : 'destructive'}
              onClick={handleApprovalAction}
              disabled={submitting}
            >
              {submitting ? 'Processing...' : (approvalAction === 'approve' ? 'Approve & Assign' : 'Reject')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AppLayout>
  )
}
