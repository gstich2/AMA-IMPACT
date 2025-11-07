'use client'

import { useState, useEffect } from 'react'
import { Plus, Edit, Trash2, Building2, Calendar, DollarSign, User, Phone, Mail } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { contractsAPI, authAPI, usersAPI } from '@/lib/api'
import { toast } from 'sonner'
import ContractDialog from '@/components/admin/contract-dialog'
import Sidebar from '@/components/layout/sidebar'

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

export default function ContractsManagementPage() {
  const [contracts, setContracts] = useState<Contract[]>([])
  const [filteredContracts, setFilteredContracts] = useState<Contract[]>([])
  const [activeFilter, setActiveFilter] = useState<'all' | 'active' | 'archived'>('all')
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingContract, setEditingContract] = useState<Contract | null>(null)
  const [user, setUser] = useState<any>(null)
  const [userLoading, setUserLoading] = useState(true)
  const [users, setUsers] = useState<any[]>([])

  const loadUserData = async () => {
    try {
      const userResponse = await authAPI.getCurrentUser()
      setUser(userResponse.data || userResponse)
      console.log('Loaded user:', userResponse.data || userResponse)
    } catch (error) {
      console.error('Error loading user:', error)
    } finally {
      setUserLoading(false)
    }
  }

  const fetchContracts = async () => {
    try {
      setLoading(true)
      const response = await contractsAPI.getAll()
      setContracts(response.data || response)
      console.log('Loaded contracts:', response.data || response)
    } catch (error) {
      console.error('Error fetching contracts:', error)
      toast.error('Failed to load contracts')
    } finally {
      setLoading(false)
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await usersAPI.getAll()
      setUsers(response.data || response)
      console.log('Loaded users for manager names:', response.data || response)
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  // Filter contracts based on active filter
  useEffect(() => {
    const now = new Date()
    let filtered = contracts

    switch (activeFilter) {
      case 'active':
        filtered = contracts.filter(contract => contract.status === 'active')
        break
      case 'archived':
        filtered = contracts.filter(contract => contract.status === 'archived')
        break
      case 'all':
      default:
        filtered = contracts
    }

    setFilteredContracts(filtered)
  }, [contracts, activeFilter])



  useEffect(() => {
    loadUserData()
    fetchContracts()
    fetchUsers()
  }, [])

  const handleCreateContract = () => {
    setEditingContract(null)
    setDialogOpen(true)
  }

  const handleEditContract = (contract: Contract) => {
    setEditingContract(contract)
    setDialogOpen(true)
  }

  const handleDeleteContract = async (contractId: string) => {
    if (!confirm('Are you sure you want to delete this contract? This action cannot be undone.')) {
      return
    }

    try {
      await contractsAPI.delete(contractId)
      toast.success('Contract deleted successfully')
      fetchContracts()
    } catch (error) {
      console.error('Error deleting contract:', error)
      toast.error('Failed to delete contract')
    }
  }

  const handleDialogSuccess = () => {
    setDialogOpen(false)
    setEditingContract(null)
    fetchContracts()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  const getStatusBadge = (status: string) => {
    return (
      <Badge variant={status === 'active' ? 'default' : 'secondary'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    )
  }

  const isContractExpired = (contract: Contract) => {
    return contract.end_date && new Date(contract.end_date) < new Date()
  }

  const getManagerName = (managerId: string) => {
    const manager = users.find(u => u.id === managerId)
    return manager ? manager.full_name : 'Unknown Manager'
  }

  // Show loading while checking user authentication
  if (userLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-muted-foreground">Loading...</p>
          </div>
        </div>
      </div>
    )
  }

  // Check if user is admin after loading
  if (user?.role !== 'admin') {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <p className="text-center text-muted-foreground">Access denied. Admin role required.</p>
              <p className="text-sm text-muted-foreground mt-2">Current role: {user?.role || 'Not loaded'}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-muted-foreground">Loading contracts...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex">
      {/* Sidebar */}
      {user && <Sidebar user={user} />}
      
      {/* Main content */}
      <main className={`flex-1 transition-all duration-300 ${user ? 'md:ml-64' : ''}`}>
        <div className="container mx-auto py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Contracts Management</h1>
          <p className="text-muted-foreground">
            Manage company contracts and project relationships
          </p>
        </div>
        <Button onClick={handleCreateContract} size="sm">
          <Plus className="h-4 w-4 mr-2" />
          New Contract
        </Button>
      </div>

      {/* Filter Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card 
          className={`cursor-pointer transition-colors hover:bg-muted/50 ${activeFilter === 'all' ? 'ring-2 ring-primary' : ''}`}
          onClick={() => setActiveFilter('all')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Building2 className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Total Contracts</p>
                <p className="text-2xl font-bold">{contracts.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card 
          className={`cursor-pointer transition-colors hover:bg-muted/50 ${activeFilter === 'active' ? 'ring-2 ring-primary' : ''}`}
          onClick={() => setActiveFilter('active')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <DollarSign className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Active Contracts</p>
                <p className="text-2xl font-bold">
                  {contracts.filter(c => c.status === 'active').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card 
          className={`cursor-pointer transition-colors hover:bg-muted/50 ${activeFilter === 'archived' ? 'ring-2 ring-primary' : ''}`}
          onClick={() => setActiveFilter('archived')}
        >
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-yellow-500" />
              <div>
                <p className="text-sm text-muted-foreground">Archived Contracts</p>
                <p className="text-2xl font-bold">
                  {contracts.filter(c => c.status === 'archived').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Contracts List */}
      {filteredContracts.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                {contracts.length === 0 
                  ? 'No contracts found' 
                  : `No ${activeFilter === 'all' ? '' : activeFilter} contracts found`
                }
              </h3>
              <p className="text-muted-foreground mb-4">
                {contracts.length === 0 
                  ? 'Get started by creating your first contract'
                  : activeFilter === 'all' 
                    ? 'No contracts match your criteria'
                    : `No ${activeFilter} contracts at this time`
                }
              </p>
              {contracts.length === 0 && (
                <Button onClick={handleCreateContract}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Contract
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredContracts.map((contract) => (
            <Card key={contract.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{contract.name}</CardTitle>
                    <CardDescription>
                      <code className="text-xs bg-muted px-1.5 py-0.5 rounded">
                        {contract.code}
                      </code>
                    </CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusBadge(contract.status)}
                    {isContractExpired(contract) && (
                      <Badge variant="destructive" className="text-xs">
                        Past End Date
                      </Badge>
                    )}
                    <div className="flex items-center space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditContract(contract)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteContract(contract.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {/* Dates */}
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span>Start: {formatDate(contract.start_date)}</span>
                    </div>
                    {contract.end_date && (
                      <div className="flex items-center space-x-1">
                        <span className={isContractExpired(contract) ? 'text-red-600 font-medium' : ''}>
                          End: {formatDate(contract.end_date)}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Client Info */}
                  {contract.client_name && (
                    <div className="flex items-center space-x-1 text-sm">
                      <Building2 className="h-4 w-4 text-muted-foreground" />
                      <span>Client: {contract.client_name}</span>
                    </div>
                  )}

                  {/* Contract Manager */}
                  {contract.manager_user_id && (
                    <div className="flex items-center space-x-1 text-sm">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <span>Manager: {getManagerName(contract.manager_user_id)}</span>
                    </div>
                  )}

                  {/* Client POC */}
                  {contract.client_contact_name && (
                    <div className="flex items-center space-x-1 text-sm">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <span>Client POC: {contract.client_contact_name}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Contract Dialog */}
      <ContractDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        contract={editingContract}
        onSuccess={handleDialogSuccess}
      />
        </div>
      </main>
    </div>
  )
}