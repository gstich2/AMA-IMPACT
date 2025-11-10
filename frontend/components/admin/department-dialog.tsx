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
import { departmentsAPI, contractsAPI, usersAPI } from '@/lib/api'
import { toast } from 'sonner'

// Zod schema for department validation
const departmentSchema = z.object({
  name: z.string().min(1, 'Department name is required'),
  code: z.string().min(1, 'Department code is required'),
  description: z.string().optional(),
  contract_id: z.string().min(1, 'Contract is required'),
  parent_id: z.string().optional(),
  manager_id: z.string().optional(),
  level: z.number().min(1),
  is_active: z.boolean(),
})

type DepartmentFormData = z.infer<typeof departmentSchema>

interface Department {
  id: string
  name: string
  code: string
  description?: string
  contract_id: string
  parent_id?: string
  manager_id?: string
  level: number
  is_active: boolean
}

interface DepartmentDialogProps {
  open: boolean
  onClose: () => void
  department?: Department | null
  onSuccess: () => void
  preselectedContractId?: string
}

export default function DepartmentDialog({ open, onClose, department, onSuccess, preselectedContractId }: DepartmentDialogProps) {
  const [loading, setLoading] = useState(false)
  const [contracts, setContracts] = useState<any[]>([])
  const [departments, setDepartments] = useState<any[]>([])
  const [managers, setManagers] = useState<any[]>([])
  const isEditing = !!department

  const form = useForm<DepartmentFormData>({
    resolver: zodResolver(departmentSchema),
    defaultValues: {
      name: '',
      code: '',
      description: '',
      contract_id: '',
      parent_id: '',
      manager_id: '',
      level: 1,
      is_active: true,
    },
  })

  // Watch contract_id to filter departments
  const selectedContractId = form.watch('contract_id')
  const selectedParentId = form.watch('parent_id')

  // Load contracts, departments, and users on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        const [contractsRes, departmentsRes, usersRes] = await Promise.all([
          contractsAPI.getAll(),
          departmentsAPI.getAll(),
          usersAPI.getAll(),
        ])
        
        setContracts(contractsRes || [])
        setDepartments(departmentsRes || [])
        
        // Filter for manager-level users
        const managerUsers = (usersRes || []).filter((u: any) => 
          ['admin', 'pm', 'manager'].includes(u.role?.toLowerCase())
        )
        setManagers(managerUsers)
      } catch (error) {
        console.error('Error loading data:', error)
        toast.error('Failed to load form data')
      }
    }

    if (open) {
      loadData()
    }
  }, [open])

  // Update form when department changes
  useEffect(() => {
    if (department) {
      form.reset({
        name: department.name,
        code: department.code,
        description: department.description || '',
        contract_id: department.contract_id,
        parent_id: department.parent_id || '',
        manager_id: department.manager_id || '',
        level: department.level,
        is_active: department.is_active,
      })
    } else {
      form.reset({
        name: '',
        code: '',
        description: '',
        contract_id: preselectedContractId || '',
        parent_id: '',
        manager_id: '',
        level: 1,
        is_active: true,
      })
    }
  }, [department, preselectedContractId, form])

  // Auto-calculate level based on parent selection
  useEffect(() => {
    if (selectedParentId) {
      const parent = departments.find(d => d.id === selectedParentId)
      if (parent) {
        form.setValue('level', parent.level + 1)
      }
    } else {
      form.setValue('level', 1)
    }
  }, [selectedParentId, departments, form])

  const onSubmit = async (data: DepartmentFormData) => {
    try {
      setLoading(true)
      
      // Clean up empty strings
      const cleanData = {
        ...data,
        description: data.description || undefined,
        parent_id: data.parent_id || undefined,
        manager_id: data.manager_id || undefined,
      }

      if (isEditing) {
        await departmentsAPI.update(department.id, cleanData)
        toast.success('Department updated successfully')
      } else {
        await departmentsAPI.create(cleanData)
        toast.success('Department created successfully')
      }

      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('Error saving department:', error)
      toast.error(error.response?.data?.detail || 'Failed to save department')
    } finally {
      setLoading(false)
    }
  }

  // Get available parent departments (filter by contract and exclude self)
  const availableParents = departments.filter(d => 
    d.contract_id === selectedContractId && 
    (!isEditing || d.id !== department?.id) &&
    d.is_active
  )

  // Get available managers (filter by contract if selected)
  const availableManagers = selectedContractId
    ? managers.filter(m => m.contract_id === selectedContractId)
    : managers

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? 'Edit Department' : 'Create Department'}</DialogTitle>
          <DialogDescription>
            {isEditing 
              ? 'Update department information and organizational structure' 
              : 'Add a new department to your organizational hierarchy'}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Information */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-muted-foreground">Basic Information</h4>
              
              <FormField
                control={form.control}
                name="contract_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Contract *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value} disabled={isEditing}>
                      <FormControl>
                        <SelectTrigger className="bg-background">
                          <SelectValue placeholder="Select contract" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-background">
                        {contracts.map((contract) => (
                          <SelectItem key={contract.id} value={contract.id}>
                            {contract.name} ({contract.code})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Department Name *</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., Technology Systems" {...field} />
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
                      <FormLabel>Department Code *</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g., TS" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Brief description of the department"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Organizational Structure */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-muted-foreground">Organizational Structure</h4>
              
              <FormField
                control={form.control}
                name="parent_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Parent Department</FormLabel>
                    <Select 
                      onValueChange={(value) => field.onChange(value === '__none__' ? '' : value)} 
                      value={field.value || '__none__'}
                      disabled={!selectedContractId}
                    >
                      <FormControl>
                        <SelectTrigger className="bg-background">
                          <SelectValue placeholder={selectedContractId ? "Top level (no parent)" : "Select contract first"} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-background">
                        <SelectItem value="__none__">Top level (no parent)</SelectItem>
                        {availableParents.map((dept) => (
                          <SelectItem key={dept.id} value={dept.id}>
                            {dept.name} ({dept.code}) - Level {dept.level}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="manager_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Department Manager</FormLabel>
                    <FormControl>
                      <SearchableSelect
                        options={availableManagers.map(manager => ({
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

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="level"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Hierarchy Level</FormLabel>
                      <FormControl>
                        <Input 
                          type="number" 
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                          disabled
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="is_active"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Status</FormLabel>
                      <Select 
                        onValueChange={(value) => field.onChange(value === 'true')} 
                        value={field.value === undefined ? 'true' : field.value.toString()}
                      >
                        <FormControl>
                          <SelectTrigger className="bg-background">
                            <SelectValue />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent className="bg-background">
                          <SelectItem value="true">Active</SelectItem>
                          <SelectItem value="false">Inactive</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Saving...' : isEditing ? 'Update Department' : 'Create Department'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
