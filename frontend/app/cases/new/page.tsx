'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import AppLayout from '@/components/layout/app-layout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { caseGroupsAPI, beneficiariesAPI, authAPI } from '@/lib/api'
import { ArrowLeft, Save, Send, FolderPlus, AlertCircle } from 'lucide-react'

interface Beneficiary {
  id: string
  first_name: string
  last_name: string
  user?: {
    email: string
  }
  job_title?: string
}

export default function NewCasePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)
  const [beneficiaries, setBeneficiaries] = useState<Beneficiary[]>([])
  const [error, setError] = useState<string>('')

  // Form state
  const [formData, setFormData] = useState({
    beneficiary_id: '',
    case_type: '',
    priority: 'MEDIUM',
    case_started_date: '',
    target_completion_date: '',
    notes: '',
    attorney_portal_link: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Get current user
      const userResponse = await authAPI.getCurrentUser()
      setCurrentUser(userResponse.data)
      
      // Check permissions
      if (!['MANAGER', 'PM', 'HR'].includes(userResponse.data.role)) {
        setError('You do not have permission to create cases.')
        return
      }
      
      // Get beneficiaries
      const beneficiariesResponse = await beneficiariesAPI.getAll()
      setBeneficiaries(beneficiariesResponse)
    } catch (error) {
      console.error('Error loading data:', error)
      setError('Failed to load data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (submitForApproval: boolean = false) => {
    setError('')
    
    // Validation
    if (!formData.beneficiary_id) {
      setError('Please select a beneficiary')
      return
    }
    if (!formData.case_type) {
      setError('Please select a case type')
      return
    }

    try {
      setSubmitting(true)
      
      // Prepare data
      const caseData = {
        beneficiary_id: formData.beneficiary_id,
        case_type: formData.case_type,
        priority: formData.priority,
        status: 'PLANNING',
        approval_status: 'DRAFT',
        case_started_date: formData.case_started_date || null,
        target_completion_date: formData.target_completion_date || null,
        notes: formData.notes || null,
        attorney_portal_link: formData.attorney_portal_link || null,
      }
      
      // Create case
      const newCase = await caseGroupsAPI.create(caseData)
      
      // If submitting for approval, do that next
      if (submitForApproval) {
        await caseGroupsAPI.submitForApproval(newCase.id)
      }
      
      // Redirect to case detail
      router.push(`/cases/${newCase.id}`)
    } catch (error: any) {
      console.error('Error creating case:', error)
      setError(error.response?.data?.detail || 'Failed to create case. Please try again.')
    } finally {
      setSubmitting(false)
    }
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
      I485: 'I-485 (Adjustment of Status)',
      I140: 'I-140',
      EAD: 'EAD (Employment Authorization)',
      AP: 'Advance Parole',
      H4: 'H4 (Dependent)',
      H4_EAD: 'H4 EAD',
      L2: 'L2 (Dependent)',
      CITIZENSHIP: 'Citizenship',
      OTHER: 'Other',
    }
    return typeLabels[caseType] || caseType
  }

  const caseTypes = [
    { value: 'H1B', label: 'H1B' },
    { value: 'H1B_TRANSFER', label: 'H1B Transfer' },
    { value: 'H1B_EXTENSION', label: 'H1B Extension' },
    { value: 'L1', label: 'L1' },
    { value: 'L1_EXTENSION', label: 'L1 Extension' },
    { value: 'TN', label: 'TN' },
    { value: 'TN_RENEWAL', label: 'TN Renewal' },
    { value: 'O1', label: 'O-1' },
    { value: 'EB1', label: 'EB-1' },
    { value: 'EB1A', label: 'EB-1A (Extraordinary Ability)' },
    { value: 'EB1B', label: 'EB-1B (Outstanding Researcher)' },
    { value: 'EB2', label: 'EB-2' },
    { value: 'EB2_NIW', label: 'EB-2 NIW (National Interest Waiver)' },
    { value: 'EB3', label: 'EB-3' },
    { value: 'PERM', label: 'PERM (Labor Certification)' },
    { value: 'I485', label: 'I-485 (Adjustment of Status)' },
    { value: 'I140', label: 'I-140 (Immigrant Petition)' },
    { value: 'EAD', label: 'EAD (Employment Authorization)' },
    { value: 'AP', label: 'Advance Parole' },
    { value: 'H4', label: 'H4 (Dependent)' },
    { value: 'H4_EAD', label: 'H4 EAD' },
    { value: 'L2', label: 'L2 (Dependent)' },
    { value: 'CITIZENSHIP', label: 'Citizenship' },
    { value: 'OTHER', label: 'Other' },
  ]

  if (loading) {
    return (
      <AppLayout>
        <div className="container mx-auto py-6">
          <div className="flex items-center justify-center py-12">
            <div className="text-muted-foreground">Loading...</div>
          </div>
        </div>
      </AppLayout>
    )
  }

  if (error && !currentUser) {
    return (
      <AppLayout>
        <div className="container mx-auto py-6">
          <div className="flex flex-col items-center justify-center py-12">
            <AlertCircle className="h-12 w-12 text-destructive mb-4" />
            <h2 className="text-xl font-semibold mb-2">Access Denied</h2>
            <p className="text-muted-foreground mb-4">{error}</p>
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
            <div className="w-12 h-12 bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg flex items-center justify-center">
              <FolderPlus className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">New Immigration Case</h1>
              <p className="text-gray-600">Create a new case for immigration processing</p>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-destructive/10 border border-destructive/20 text-destructive rounded-lg p-4 flex items-start gap-2">
            <AlertCircle className="h-5 w-5 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Form */}
        <Card>
          <CardHeader>
            <CardTitle>Case Information</CardTitle>
            <CardDescription>
              Fill in the details for the new immigration case. The case will be created in DRAFT status.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Beneficiary Selection */}
            <div className="space-y-2">
              <Label htmlFor="beneficiary">
                Beneficiary <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.beneficiary_id}
                onValueChange={(value) => setFormData({ ...formData, beneficiary_id: value })}
              >
                <SelectTrigger id="beneficiary">
                  <SelectValue placeholder="Select beneficiary" />
                </SelectTrigger>
                <SelectContent>
                  {beneficiaries.map((beneficiary) => (
                    <SelectItem key={beneficiary.id} value={beneficiary.id}>
                      {beneficiary.first_name} {beneficiary.last_name}
                      {beneficiary.user?.email && ` (${beneficiary.user.email})`}
                      {beneficiary.job_title && ` - ${beneficiary.job_title}`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                Select the employee for this immigration case
              </p>
            </div>

            {/* Case Type */}
            <div className="space-y-2">
              <Label htmlFor="case_type">
                Case Type <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.case_type}
                onValueChange={(value) => setFormData({ ...formData, case_type: value })}
              >
                <SelectTrigger id="case_type">
                  <SelectValue placeholder="Select case type" />
                </SelectTrigger>
                <SelectContent>
                  {caseTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                Select the type of immigration case
              </p>
            </div>

            {/* Priority */}
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <Select
                value={formData.priority}
                onValueChange={(value) => setFormData({ ...formData, priority: value })}
              >
                <SelectTrigger id="priority">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="CRITICAL">Critical - Immediate attention required</SelectItem>
                  <SelectItem value="URGENT">Urgent - High priority</SelectItem>
                  <SelectItem value="HIGH">High - Important</SelectItem>
                  <SelectItem value="MEDIUM">Medium - Normal priority</SelectItem>
                  <SelectItem value="LOW">Low - Can wait</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-muted-foreground">
                Set the priority level for this case
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Start Date */}
              <div className="space-y-2">
                <Label htmlFor="case_started_date">Start Date</Label>
                <Input
                  id="case_started_date"
                  type="date"
                  value={formData.case_started_date}
                  onChange={(e) => setFormData({ ...formData, case_started_date: e.target.value })}
                />
                <p className="text-sm text-muted-foreground">
                  When did or will this case start?
                </p>
              </div>

              {/* Target Completion Date */}
              <div className="space-y-2">
                <Label htmlFor="target_completion_date">Target Completion Date</Label>
                <Input
                  id="target_completion_date"
                  type="date"
                  value={formData.target_completion_date}
                  onChange={(e) => setFormData({ ...formData, target_completion_date: e.target.value })}
                />
                <p className="text-sm text-muted-foreground">
                  Expected completion date for this case
                </p>
              </div>
            </div>

            {/* Attorney Portal Link */}
            <div className="space-y-2">
              <Label htmlFor="attorney_portal_link">Attorney Portal Link</Label>
              <Input
                id="attorney_portal_link"
                type="url"
                placeholder="https://example-law-firm.com/cases/..."
                value={formData.attorney_portal_link}
                onChange={(e) => setFormData({ ...formData, attorney_portal_link: e.target.value })}
              />
              <p className="text-sm text-muted-foreground">
                Link to the law firm's case tracking portal (optional)
              </p>
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Case Notes</Label>
              <Textarea
                id="notes"
                placeholder="Enter any relevant notes about this case..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={4}
              />
              <p className="text-sm text-muted-foreground">
                Additional information, requirements, or context for this case
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                onClick={() => router.push('/cases')}
                disabled={submitting}
              >
                Cancel
              </Button>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => handleSubmit(false)}
                  disabled={submitting}
                >
                  <Save className="h-4 w-4 mr-2" />
                  {submitting ? 'Saving...' : 'Save as Draft'}
                </Button>
                <Button
                  onClick={() => handleSubmit(true)}
                  disabled={submitting}
                >
                  <Send className="h-4 w-4 mr-2" />
                  {submitting ? 'Submitting...' : 'Save & Submit for Approval'}
                </Button>
              </div>
            </div>
            <p className="text-sm text-muted-foreground mt-4">
              <strong>Save as Draft:</strong> Case will be saved in draft status and can be edited later.
              <br />
              <strong>Save & Submit for Approval:</strong> Case will be created and immediately submitted to PM for approval.
            </p>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  )
}
