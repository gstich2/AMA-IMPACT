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
import { caseGroupsAPI, authAPI, petitionsAPI, lawFirmsAPI, usersAPI } from '@/lib/api'
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
  pathway_type: string
  status: string
  priority: string
  approval_status: string
  beneficiary?: {
    id: string
    first_name: string
    last_name: string
    job_title?: string
    country_of_citizenship?: string
    country_of_birth?: string
    passport_country?: string
    passport_expiration?: string
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
  petitions?: any[]
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
  const [progressData, setProgressData] = useState<any>(null)
  const [progressLoading, setProgressLoading] = useState(false)
  
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
  
  // Fetch progress data from API
  useEffect(() => {
    if (caseId) {
      setProgressLoading(true)
      caseGroupsAPI.getProgress(caseId)
        .then(data => {
          console.log('Progress data from API:', data)
          setProgressData(data)
          setProgressLoading(false)
        })
        .catch(err => {
          console.error('Failed to fetch progress:', err)
          setProgressLoading(false)
        })
    }
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

  // Legacy progress calculation for backward compatibility
  // TODO: Remove this once all components use progressData from API
  const calculateProgress = () => {
    // If we have API data, use it
    if (progressData) {
      return {
        percentage: progressData.overall_percentage || 0,
        currentStage: progressData.overall_stage || 'Not Started',
        currentIndex: -1,
        milestones: [],
        allMilestones: []
      }
    }
    
    // Fallback to empty progress
    return { 
      percentage: 0, 
      currentStage: 'Loading...', 
      currentIndex: -1, 
      milestones: [], 
      allMilestones: [] 
    }
  }

  const progress = calculateProgress()

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
                <span className="font-medium">{getCaseTypeLabel(caseGroup.pathway_type)}</span>
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
        </div>

        {/* Case Group Overview - Redesigned */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 flex-wrap">
                  {/* Status - PRIMARY (Large & Prominent) */}
                  <div className="text-xl px-4 py-2 rounded-md font-semibold" style={{
                    backgroundColor: caseGroup.status === 'APPROVED' ? '#dcfce7' : 
                                   caseGroup.status === 'IN_PROGRESS' ? '#dbeafe' :
                                   caseGroup.status === 'PENDING' ? '#fef3c7' :
                                   caseGroup.status === 'DENIED' ? '#fee2e2' : '#f3f4f6',
                    color: caseGroup.status === 'APPROVED' ? '#166534' :
                           caseGroup.status === 'IN_PROGRESS' ? '#1e40af' :
                           caseGroup.status === 'PENDING' ? '#92400e' :
                           caseGroup.status === 'DENIED' ? '#991b1b' : '#374151'
                  }}>
                    {caseGroup.status.replace('_', ' ')}
                  </div>
                  
                  {/* Priority - SECONDARY (Smaller) */}
                  {getPriorityBadge(caseGroup.priority)}
                  
                  {/* PM Approval - COMPACT Indicator */}
                  {caseGroup.approval_status === 'PM_APPROVED' && (
                    <div className="flex items-center gap-1.5 text-green-700 bg-green-50 px-3 py-1 rounded-md">
                      <CheckCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">PM Approved</span>
                    </div>
                  )}
                  {caseGroup.approval_status === 'PM_REJECTED' && (
                    <div className="flex items-center gap-1.5 text-red-700 bg-red-50 px-3 py-1 rounded-md">
                      <XCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">PM Rejected</span>
                    </div>
                  )}
                  {caseGroup.approval_status === 'PENDING_PM_APPROVAL' && (
                    <div className="flex items-center gap-1.5 text-yellow-700 bg-yellow-50 px-3 py-1 rounded-md">
                      <Clock className="h-4 w-4" />
                      <span className="text-sm font-medium">Pending PM Approval</span>
                    </div>
                  )}
                </div>
                
                {/* Case Type */}
                <div className="text-sm text-muted-foreground mt-2">
                  {getCaseTypeLabel(caseGroup.pathway_type)} Case Group
                </div>
              </div>
              
              {/* Action Buttons */}
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
            {/* Petitions in this Case Group */}
            {(caseGroup as any).petitions && (caseGroup as any).petitions.length > 0 && (
              <div>
                <div className="font-medium text-sm mb-3">Petitions in this Case:</div>
                <div className="space-y-2">
                  {(caseGroup as any).petitions.map((app: any) => (
                    <div key={app.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <FileText className="h-5 w-5 text-gray-600 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm">{app.petition_type || app.visa_type || 'Visa Application'}</div>
                        <div className="text-xs text-muted-foreground">
                          {app.visa_type && <>{app.visa_type}</>}
                          {app.status && <> • Status: {app.status.replace(/_/g, ' ')}</>}
                        </div>
                      </div>
                      {app.case_status && (
                        <Badge variant={
                          app.case_status === 'FINALIZED' ? 'success' :
                          app.case_status === 'ACTIVE' ? 'default' : 'secondary'
                        }>
                          {app.case_status}
                        </Badge>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Key Dates */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
              <div>
                <div className="text-xs font-medium text-muted-foreground">Started</div>
                <div className="text-sm font-semibold">{formatDate(caseGroup.case_started_date)}</div>
              </div>
              <div>
                <div className="text-xs font-medium text-muted-foreground">Target Completion</div>
                <div className="text-sm font-semibold">{formatDate(caseGroup.target_completion_date)}</div>
              </div>
              {caseGroup.case_completed_date && (
                <div>
                  <div className="text-xs font-medium text-muted-foreground">Completed</div>
                  <div className="text-sm font-semibold">{formatDate(caseGroup.case_completed_date)}</div>
                </div>
              )}
              <div>
                <div className="text-xs font-medium text-muted-foreground">Last Updated</div>
                <div className="text-sm font-semibold">{formatDateTime(caseGroup.updated_at)}</div>
              </div>
            </div>
            
            {/* PM Approval Notes (if rejected or has notes) */}
            {caseGroup.pm_approval_notes && (
              <div className={`p-3 rounded-lg ${
                caseGroup.approval_status === 'PM_REJECTED' 
                  ? 'bg-red-50 border border-red-200' 
                  : 'bg-blue-50 border border-blue-200'
              }`}>
                <div className={`text-sm font-medium mb-1 ${
                  caseGroup.approval_status === 'PM_REJECTED' ? 'text-red-900' : 'text-blue-900'
                }`}>
                  PM Notes:
                </div>
                <div className={`text-sm ${
                  caseGroup.approval_status === 'PM_REJECTED' ? 'text-red-700' : 'text-blue-700'
                }`}>
                  {caseGroup.pm_approval_notes}
                </div>
                {caseGroup.pm_approval_date && (
                  <div className={`text-xs mt-1 ${
                    caseGroup.approval_status === 'PM_REJECTED' ? 'text-red-600' : 'text-blue-600'
                  }`}>
                    {formatDateTime(caseGroup.pm_approval_date)}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Beneficiary + Progress Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Beneficiary Information */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Beneficiary Information
                </CardTitle>
                {canEdit() && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => {
                      // TODO: Open beneficiary edit dialog or navigate to edit page
                      console.log('Edit beneficiary clicked')
                    }}
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                )}
              </div>
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
                  <div>
                    <div className="text-sm font-medium text-muted-foreground">Job Title</div>
                    <div className="text-sm">{caseGroup.beneficiary.job_title || 'N/A'}</div>
                  </div>
                  
                  {/* Citizenship & Passport Info */}
                  <div className="pt-2 border-t">
                    <div className="text-xs font-semibold text-gray-700 mb-2">Citizenship & Passport</div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Country of Citizenship</div>
                        <div className="text-sm">{caseGroup.beneficiary.country_of_citizenship || 'N/A'}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Country of Birth</div>
                        <div className="text-sm">{caseGroup.beneficiary.country_of_birth || 'N/A'}</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 mt-3">
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Passport Country</div>
                        <div className="text-sm">{caseGroup.beneficiary.passport_country || 'N/A'}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Passport Expiration</div>
                        <div className="text-sm">{formatDate(caseGroup.beneficiary.passport_expiration)}</div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Visa Information */}
                  <div className="pt-2 border-t">
                    <div className="text-xs font-semibold text-gray-700 mb-2">Current Visa Status</div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Current Visa Type</div>
                        <div className="text-sm">{caseGroup.beneficiary.current_visa_type || 'N/A'}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Visa Expiration</div>
                        <div className="text-sm">{formatDate(caseGroup.beneficiary.current_visa_expiration)}</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 mt-3">
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">I-94 Expiration</div>
                        <div className="text-sm">{formatDate(caseGroup.beneficiary.i94_expiration)}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Employment Start</div>
                        <div className="text-sm">{formatDate(caseGroup.beneficiary.employment_start_date)}</div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Contact & Organization Info */}
                  {caseGroup.beneficiary.user && (
                    <div className="pt-2 border-t">
                      <div className="text-xs font-semibold text-gray-700 mb-2">Contact & Organization</div>
                      <div className="space-y-2">
                        <div>
                          <div className="text-sm font-medium text-muted-foreground">Email</div>
                          <div className="text-sm text-blue-600">{caseGroup.beneficiary.user.email}</div>
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
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-muted-foreground">No beneficiary assigned</div>
              )}
            </CardContent>
          </Card>

          {/* Case Progress - Per-Visa Pipelines */}
          {progressLoading ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                Loading progress...
              </CardContent>
            </Card>
          ) : progressData && progressData.petitions && progressData.petitions.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ListTodo className="h-5 w-5" />
                  Case Progress
                </CardTitle>
                <CardDescription>
                  {progressData.overall_percentage}% Complete - {progressData.overall_stage}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Show progress for EACH visa application */}
                {progressData.petitions.map((visa: any) => (
                  <div key={visa.petition_id} className="border-b last:border-b-0 pb-6 last:pb-0">
                    {/* Visa Header */}
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <div className="font-semibold text-sm">{visa.pipeline_name}</div>
                        <div className="text-xs text-muted-foreground">
                          {visa.petition_type} - {visa.percentage}% Complete
                        </div>
                      </div>
                      <Badge variant={visa.percentage === 100 ? 'success' : 'default'}>
                        {visa.current_stage}
                      </Badge>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="h-2 bg-gray-200 rounded-full mb-4">
                      <div 
                        className="h-full bg-blue-600 rounded-full transition-all duration-300"
                        style={{ width: `${visa.percentage}%` }}
                      />
                    </div>
                    
                    {/* Pipeline Stages */}
                    <div className="space-y-2">
                      {visa.pipeline.map((stage: any) => {
                        const isNext = !stage.completed && visa.pipeline.find((s: any) => !s.completed)?.order === stage.order
                        
                        return (
                          <div key={stage.order} className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded-full flex-shrink-0 flex items-center justify-center ${
                              stage.completed 
                                ? 'bg-green-500' 
                                : isNext
                                  ? 'bg-blue-500 ring-2 ring-blue-200'
                                  : 'bg-gray-300'
                            }`}>
                              {stage.completed && (
                                <CheckCircle className="h-3 w-3 text-white" />
                              )}
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className={`text-sm font-medium ${
                                stage.completed ? 'text-green-700' :
                                isNext ? 'text-blue-700' : 'text-gray-500'
                              }`}>
                                {stage.label}
                                {isNext && (
                                  <Badge variant="outline" className="ml-2 text-xs border-blue-500 text-blue-700">
                                    Next
                                  </Badge>
                                )}
                                {!stage.required && (
                                  <Badge variant="outline" className="ml-2 text-xs">
                                    Optional
                                  </Badge>
                                )}
                              </div>
                              {stage.completed && stage.completion_date && (
                                <div className="text-xs text-muted-foreground">
                                  {new Date(stage.completion_date).toLocaleDateString()}
                                </div>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    
                    {/* Next Step Indicator */}
                    {visa.next_stage && (
                      <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                        <div className="text-sm font-medium text-blue-900">Next Step</div>
                        <div className="text-sm text-blue-700">{visa.next_stage}</div>
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No petitions found for progress tracking
                {progressData && (
                  <div className="text-xs mt-2">
                    Debug: {JSON.stringify(Object.keys(progressData))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Activity History - Renamed from Case Timeline */}
        {timeline && timeline.events && timeline.events.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Activity History
              </CardTitle>
              <CardDescription>{timeline.total_events} events (chronological order)</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[...timeline.events].reverse().map((event: any, index: number) => {
                  const isLast = index === timeline.events.length - 1
                  const isMilestone = event.event_type === 'MILESTONE'
                  const isAudit = event.event_type === 'AUDIT_LOG' || 
                                  ['CASE_CREATED', 'CASE_UPDATED', 'SUBMITTED_FOR_APPROVAL', 
                                   'APPROVED', 'REJECTED', 'STATUS_CHANGED'].includes(event.event_type)
                  const isTodo = event.event_type === 'TODO_COMPLETED'
                  
                  return (
                    <div key={event.id} className="relative">
                      {/* Timeline Line */}
                      {!isLast && (
                        <div className="absolute left-2 top-8 bottom-0 w-0.5 bg-gray-200" />
                      )}
                      
                      {/* Event Content */}
                      <div className="flex gap-3">
                        {/* Icon with distinct colors */}
                        <div className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center ${
                          isMilestone ? 'bg-blue-500' :
                          isAudit ? 'bg-purple-500' :
                          'bg-green-500'
                        }`}>
                          {isMilestone ? (
                            <CheckCircle className="h-3 w-3 text-white" />
                          ) : isAudit ? (
                            <FileText className="h-3 w-3 text-white" />
                          ) : (
                            <ListTodo className="h-3 w-3 text-white" />
                          )}
                        </div>
                        
                        {/* Event Details */}
                        <div className="flex-1 pb-6">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-medium text-sm">{event.title}</span>
                                {event.milestone_type && (
                                  <Badge variant="outline" className="text-xs bg-blue-50 border-blue-300 text-blue-700">
                                    {event.milestone_type.replace(/_/g, ' ')}
                                  </Badge>
                                )}
                              </div>
                              {event.description && (
                                <p className="text-sm text-muted-foreground">{event.description}</p>
                              )}
                              {event.user_name && (
                                <div className="text-xs text-muted-foreground mt-1">
                                  by {event.user_name}
                                </div>
                              )}
                            </div>
                            <div className="text-xs text-muted-foreground whitespace-nowrap">
                              {formatDateTime(event.timestamp)}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Case Team */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Case Team
              </CardTitle>
              {canEdit() && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    // TODO: Open case group edit dialog or navigate to edit page
                    console.log('Edit case team clicked')
                  }}
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Button>
              )}
            </div>
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

        {/* Removed redundant Petitions list - already shown in Case Group Overview */}

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
