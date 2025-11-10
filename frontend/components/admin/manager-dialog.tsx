'use client'

import { useEffect, useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { usersAPI, departmentsAPI } from '@/lib/api'
import { toast } from 'sonner'
import { SearchableSelect } from '@/components/ui/searchable-select'

interface Department {
  id: string
  name: string
  code: string
  manager_id?: string
}

interface User {
  id: string
  full_name: string
  email?: string
  role: string
}

interface ManagerDialogProps {
  open: boolean
  onClose: () => void
  department: Department | null
  onSuccess: () => void
}

export default function ManagerDialog({ open, onClose, department, onSuccess }: ManagerDialogProps) {
  const [users, setUsers] = useState<User[]>([])
  const [selectedManagerId, setSelectedManagerId] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [usersLoading, setUsersLoading] = useState(false)

  useEffect(() => {
    if (open) {
      fetchUsers()
      setSelectedManagerId(department?.manager_id || '')
    }
  }, [open, department])

  const fetchUsers = async () => {
    try {
      setUsersLoading(true)
      const response = await usersAPI.getAll()
      // Filter to show only managers, PMs, and admins
      const eligibleUsers = (response || []).filter((u: User) => 
        ['admin', 'pm', 'manager'].includes(u.role.toLowerCase())
      )
      setUsers(eligibleUsers)
    } catch (error) {
      console.error('Error fetching users:', error)
      toast.error('Failed to load users')
    } finally {
      setUsersLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!department) {
      toast.error('No department selected')
      return
    }

    try {
      setLoading(true)
      
      // Update only the manager_id field
      await departmentsAPI.update(department.id, {
        manager_id: selectedManagerId || null
      })

      toast.success('Manager updated successfully')
      onSuccess()
      onClose()
    } catch (error: any) {
      console.error('Error updating manager:', error)
      toast.error(error.response?.data?.detail || 'Failed to update manager')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    if (!loading) {
      onClose()
    }
  }

  const userOptions = users.map(u => ({
    value: u.id,
    label: u.full_name,
    subtitle: u.email
  }))

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Assign Manager</DialogTitle>
          <DialogDescription>
            {department && (
              <>Assign or change the manager for <strong>{department.name}</strong> ({department.code})</>
            )}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="manager">Manager</Label>
              <SearchableSelect
                options={userOptions}
                value={selectedManagerId}
                onValueChange={setSelectedManagerId}
                placeholder="Select a manager (optional)"
                disabled={usersLoading}
              />
              <p className="text-xs text-muted-foreground">
                Select a manager to assign to this department, or leave empty for no manager.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save Manager'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
