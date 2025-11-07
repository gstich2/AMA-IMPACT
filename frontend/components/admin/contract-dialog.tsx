'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { SearchableSelect } from '@/components/ui/searchable-select'
import { contractsAPI, usersAPI } from '@/lib/api'

const contractSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255, 'Name too long'),
  code: z.string().min(1, 'Code is required').max(50, 'Code too long'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().optional(),
  status: z.enum(['active', 'archived']),
  manager_user_id: z.string().optional(),
  client_name: z.string().optional(),
  client_contact_name: z.string().optional(),
  client_contact_email: z.string().email('Invalid email').optional().or(z.literal('')),
  client_contact_phone: z.string().optional(),
  description: z.string().optional(),
  notes: z.string().optional(),
})

type ContractFormData = z.infer<typeof contractSchema>

interface Contract {
  id: string
  name: string
  code: string
  start_date: string
  end_date?: string
  status: 'active' | 'archived'
  manager_user_id?: string
  client_name?: string
  client_contact_name?: string
  client_contact_email?: string
  client_contact_phone?: string
  description?: string
  notes?: string
  created_at: string
  updated_at: string
}

interface ContractDialogProps {
  open: boolean
  onClose: () => void
  contract?: Contract | null
  onSuccess: () => void
}

export default function ContractDialog({ open, onClose, contract, onSuccess }: ContractDialogProps) {
  const [loading, setLoading] = useState(false)
  const [managers, setManagers] = useState<any[]>([])
  const isEditing = !!contract

  const form = useForm<ContractFormData>({
    resolver: zodResolver(contractSchema),
    defaultValues: {
      name: '',
      code: '',
      start_date: '',
      end_date: '',
      status: 'active',
      manager_user_id: '',
      client_name: '',
      client_contact_name: '',
      client_contact_email: '',
      client_contact_phone: '',
      description: '',
      notes: '',
    },
  })

  // Update form when contract changes
  useEffect(() => {
    if (contract) {
      form.reset({
        name: contract.name,
        code: contract.code,
        start_date: contract.start_date,
        end_date: contract.end_date || '',
        status: contract.status,
        manager_user_id: contract.manager_user_id || '',
        client_name: contract.client_name || '',
        client_contact_name: contract.client_contact_name || '',
        client_contact_email: contract.client_contact_email || '',
        client_contact_phone: contract.client_contact_phone || '',
        description: contract.description || '',
        notes: contract.notes || '',
      })
    } else {
      form.reset({
        name: '',
        code: '',
        start_date: '',
        end_date: '',
        status: 'active',
        manager_user_id: '',
        client_name: '',
        client_contact_name: '',
        client_contact_email: '',
        client_contact_phone: '',
        description: '',
        notes: '',
      })
    }
  }, [contract, form])

  // Fetch managers when dialog opens
  useEffect(() => {
    if (open) {
      const fetchManagers = async () => {
        try {
          const managersData = await usersAPI.getAll()
          // Filter for users who can be managers (pm, manager, admin roles)
          const managerUsers = managersData.filter((user: any) => 
            ['pm', 'manager', 'admin'].includes(user.role)
          )
          setManagers(managerUsers)
          console.log('Loaded managers:', managerUsers)
        } catch (error) {
          console.error('Error fetching managers:', error)
        }
      }
      fetchManagers()
    }
  }, [open])

  const onSubmit = async (data: ContractFormData) => {
    try {
      setLoading(true)

      // Clean up data - remove empty strings
      const cleanData = Object.fromEntries(
        Object.entries(data).map(([key, value]) => [
          key,
          value === '' ? null : value,
        ])
      )

      if (isEditing && contract) {
        await contractsAPI.update(contract.id, cleanData)
        console.log('Contract updated successfully')
      } else {
        await contractsAPI.create(cleanData)
        console.log('Contract created successfully')
      }

      onSuccess()
    } catch (error) {
      console.error('Error saving contract:', error)
      // For now, just log the error. In a real app, you'd show a toast notification
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? 'Edit Contract' : 'Create New Contract'}
          </DialogTitle>
          <DialogDescription>
            {isEditing 
              ? 'Update the contract information below.'
              : 'Fill in the details to create a new contract.'
            }
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-muted-foreground">Basic Information</h4>
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contract Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., ASSESS Contract" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="code"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contract Code</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., ASSESS-2024" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <FormField
                  control={form.control}
                  name="start_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Start Date</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="end_date"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>End Date (Optional)</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="status"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Status</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select status" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="active">Active</SelectItem>
                          <SelectItem value="archived">Archived</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Manager Selection */}
                <FormField
                  control={form.control}
                  name="manager_user_id"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contract Manager</FormLabel>
                      <FormControl>
                        <SearchableSelect
                          options={managers.map(manager => ({
                            value: manager.id,
                            label: manager.full_name,
                            subtitle: `${manager.role} • ${manager.email || 'No email'}`
                          }))}
                          value={field.value}
                          onValueChange={field.onChange}
                          placeholder="Search and select a manager..."
                          className="w-full"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Client Information */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-muted-foreground">Client Information</h4>
              <FormField
                control={form.control}
                name="client_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Client Name</FormLabel>
                    <FormControl>
                      <Input placeholder="e.g., NASA Ames Research Center" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="grid grid-cols-3 gap-4">
                <FormField
                  control={form.control}
                  name="client_contact_name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contact Name</FormLabel>
                      <FormControl>
                        <Input placeholder="John Doe" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="client_contact_email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contact Email</FormLabel>
                      <FormControl>
                        <Input placeholder="john.doe@nasa.gov" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="client_contact_phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contact Phone</FormLabel>
                      <FormControl>
                        <Input placeholder="(650) 555-0123" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            {/* Additional Details */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-muted-foreground">Additional Details</h4>
              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Brief description of the contract..." 
                        className="resize-none"
                        rows={3}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="notes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Notes</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Internal notes..." 
                        className="resize-none"
                        rows={2}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Saving...' : isEditing ? 'Update Contract' : 'Create Contract'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}