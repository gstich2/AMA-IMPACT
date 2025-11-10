'use client'

import { useState, useEffect, useRef } from 'react'
import { Plus, Edit,  const fetchTreeData = async () => {
    try {
      // Fetch tree for all selected contracts
      if (selectedContracts.length === 0) {
        // No filter - get all
        const response = await departmentsAPI.getTree()
        setTreeData(response || [])
      } else if (selectedContracts.length === 1) {
        // Single contract
        const response = await departmentsAPI.getTree(selectedContracts[0])
        setTreeData(response || [])
      } else {
        // Multiple contracts - fetch and merge
        const responses = await Promise.all(
          selectedContracts.map(id => departmentsAPI.getTree(id))
        )
        setTreeData(responses.flat())
      }
    } catch (error) {
      console.error('Error fetching tree data:', error)
    }
  }

  const fetchContracts = async () => {ilding2, Users, User, ChevronRight, ChevronDown, UserCog, X, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { departmentsAPI, contractsAPI, authAPI, usersAPI } from '@/lib/api'
import { toast } from 'sonner'
import DepartmentDialog from '@/components/admin/department-dialog'
import ManagerDialog from '@/components/admin/manager-dialog'
import Sidebar from '@/components/layout/sidebar'
import { Input } from '@/components/ui/input'

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
  children?: Department[]
  user_count?: number
  created_at: string
  updated_at: string
}

interface Contract {
  id: string
  name: string
  code: string
}

interface User {
  id: string
  full_name: string
  email?: string
  role: string
}

export default function DepartmentsManagementPage() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [treeData, setTreeData] = useState<Department[]>([])
  const [contracts, setContracts] = useState<Contract[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [userMap, setUserMap] = useState<Record<string, User>>({})
  const [selectedContracts, setSelectedContracts] = useState<string[]>([]) // Changed to array
  const [contractSearch, setContractSearch] = useState('')
  const [showContractDropdown, setShowContractDropdown] = useState(false)
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [managerDialogOpen, setManagerDialogOpen] = useState(false)
  const [editingDepartment, setEditingDepartment] = useState<Department | null>(null)
  const [selectedDeptForManager, setSelectedDeptForManager] = useState<Department | null>(null)
  const [user, setUser] = useState<any>(null)
  const [userLoading, setUserLoading] = useState(true)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const dropdownRef = useRef<HTMLDivElement>(null)

  const loadUserData = async () => {
    try {
      const userResponse = await authAPI.getCurrentUser()
      setUser(userResponse.data || userResponse)
    } catch (error) {
      console.error('Error loading user:', error)
    } finally {
      setUserLoading(false)
    }
  }

  const fetchDepartments = async () => {
    try {
      setLoading(true)
      const response = await departmentsAPI.getAll()
      setDepartments(response || [])
    } catch (error) {
      console.error('Error fetching departments:', error)
      toast.error('Failed to load departments')
    } finally {
      setLoading(false)
    }
  }

  const fetchTreeData = async () => {
    try {
      const contractId = selectedContract !== 'all' ? selectedContract : undefined
      const response = await departmentsAPI.getTree(contractId)
      setTreeData(response || [])
    } catch (error) {
      console.error('Error fetching tree data:', error)
    }
  }

  const fetchContracts = async () => {
    try {
      const response = await contractsAPI.getAll()
      setContracts(response || [])
    } catch (error) {
      console.error('Error fetching contracts:', error)
    }
  }

  const fetchUsers = async () => {
    try {
      const response = await usersAPI.getAll()
      const userList = response || []
      setUsers(userList)
      
      // Create lookup map for O(1) access
      const map: Record<string, User> = {}
      userList.forEach((u: User) => {
        map[u.id] = u
      })
      setUserMap(map)
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  useEffect(() => {
    loadUserData()
    fetchContracts()
    fetchDepartments()
    fetchUsers()
  }, [])

  useEffect(() => {
    fetchTreeData()
  }, [selectedContract])

  const handleCreateDepartment = (contractId?: string) => {
    setEditingDepartment(contractId ? { contract_id: contractId } as Department : null)
    setDialogOpen(true)
  }

  const handleEditDepartment = (department: Department) => {
    setEditingDepartment(department)
    setDialogOpen(true)
  }

  const handleAssignManager = (department: Department) => {
    setSelectedDeptForManager(department)
    setManagerDialogOpen(true)
  }

  const handleDeleteDepartment = async (departmentId: string) => {
    if (!confirm('Are you sure you want to delete this department? This will deactivate the department.')) {
      return
    }

    try {
      await departmentsAPI.delete(departmentId, false)
      toast.success('Department deleted successfully')
      fetchDepartments()
      fetchTreeData()
    } catch (error: any) {
      console.error('Error deleting department:', error)
      toast.error(error.response?.data?.detail || 'Failed to delete department')
    }
  }

  const handleDialogSuccess = () => {
    fetchDepartments()
    fetchTreeData()
  }

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  // Get manager name by ID
  const getManagerName = (managerId?: string) => {
    if (!managerId) return null
    return userMap[managerId]?.full_name || 'Unknown Manager'
  }

  // Filter contracts by search
  const filteredContracts = contracts.filter(c => 
    c.code.toLowerCase().includes(contractSearch.toLowerCase()) ||
    c.name.toLowerCase().includes(contractSearch.toLowerCase())
  )

  // Get statistics
  const totalDepartments = departments.length
  const topLevelDepartments = departments.filter(d => !d.parent_id).length
  const activeDepartments = departments.filter(d => d.is_active).length

  // Get departments by contract for displaying multiple contract sections
  const departmentsByContract: Record<string, Department[]> = {}
  treeData.forEach(dept => {
    if (!departmentsByContract[dept.contract_id]) {
      departmentsByContract[dept.contract_id] = []
    }
    departmentsByContract[dept.contract_id].push(dept)
  })

  // Recursive tree renderer
  const renderTreeNode = (dept: Department, depth: number = 0) => {
    const hasChildren = dept.children && dept.children.length > 0
    const isExpanded = expandedNodes.has(dept.id)
    const manager = dept.manager_id ? userMap[dept.manager_id] : null

    return (
      <div>
        <div 
          className="flex items-center space-x-2 py-2.5 px-3 hover:bg-muted/50 rounded-md transition-colors group"
          style={{ paddingLeft: `${depth * 24 + 12}px` }}
        >
          {hasChildren ? (
            <button
              onClick={() => toggleNode(dept.id)}
              className="p-0.5 hover:bg-muted rounded transition-colors"
            >
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              ) : (
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              )}
            </button>
          ) : (
            <div className="w-5" />
          )}
          
          <Building2 className="h-4 w-4 text-blue-500 flex-shrink-0" />
          
          <div className="flex-1 min-w-0 flex items-center space-x-2">
            <span className="font-medium text-sm">{dept.name}</span>
            <Badge variant="outline" className="text-xs">
              {dept.code}
            </Badge>
            <Badge variant="secondary" className="text-xs">
              L{dept.level}
            </Badge>
            {!dept.is_active && (
              <Badge variant="destructive" className="text-xs">
                Inactive
              </Badge>
            )}
          </div>

          {/* Manager Badge */}
          {manager ? (
            <button
              onClick={() => handleAssignManager(dept)}
              className="flex items-center space-x-1.5 px-2 py-1 rounded-md bg-green-50 hover:bg-green-100 text-green-700 transition-colors text-xs"
            >
              <UserCog className="h-3 w-3" />
              <span className="font-medium">{manager.full_name}</span>
            </button>
          ) : (
            <button
              onClick={() => handleAssignManager(dept)}
              className="flex items-center space-x-1 px-2 py-1 rounded-md bg-gray-100 hover:bg-gray-200 text-gray-600 transition-colors text-xs opacity-0 group-hover:opacity-100"
            >
              <User className="h-3 w-3" />
              <span>Assign Manager</span>
            </button>
          )}

          {dept.user_count !== undefined && dept.user_count > 0 && (
            <div className="flex items-center space-x-1 text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
              <Users className="h-3 w-3" />
              <span>{dept.user_count}</span>
            </div>
          )}

          <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleEditDepartment(dept)}
              className="h-7 w-7 p-0"
            >
              <Edit className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleDeleteDepartment(dept.id)}
              className="h-7 w-7 p-0"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div>
            {dept.children!.map(child => (
              <div key={child.id}>
                {renderTreeNode(child, depth + 1)}
              </div>
            ))}
          </div>
        )}
      </div>
    )
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

  // Check permissions
  if (!user || !['admin', 'pm'].includes(user.role?.toLowerCase())) {
    return (
      <div className="flex h-screen">
        <Sidebar user={user} />
        <main className="flex-1 overflow-y-auto bg-background">
          <div className="container mx-auto py-8">
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Access Denied</h3>
                  <p className="text-muted-foreground">
                    You don't have permission to manage departments.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex h-screen">
      <Sidebar user={user} />
      <main className="flex-1 overflow-y-auto bg-background">
        <div className="container mx-auto py-8 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Departments</h1>
              <p className="text-muted-foreground">
                Manage organizational structure and hierarchy
              </p>
            </div>
          </div>

          {/* Contract Filter with Search */}
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-3">
                <label className="text-sm font-medium">Filter by Contract</label>
                <Input
                  placeholder="Search by contract code or name..."
                  value={contractSearch}
                  onChange={(e) => setContractSearch(e.target.value)}
                  className="max-w-sm"
                />
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={selectedContract === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedContract('all')}
                  >
                    All Contracts ({contracts.length})
                  </Button>
                  {filteredContracts.map(contract => (
                    <Button
                      key={contract.id}
                      variant={selectedContract === contract.id ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedContract(contract.id)}
                    >
                      {contract.code}
                    </Button>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Statistics Header */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <Building2 className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Total Departments</p>
                    <p className="text-2xl font-bold">{totalDepartments}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <Building2 className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Top-Level Departments</p>
                    <p className="text-2xl font-bold">{topLevelDepartments}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center space-x-2">
                  <Users className="h-5 w-5 text-purple-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Active Departments</p>
                    <p className="text-2xl font-bold">{activeDepartments}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Department Trees by Contract */}
          {loading ? (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <p className="mt-2 text-muted-foreground">Loading departments...</p>
                </div>
              </CardContent>
            </Card>
          ) : selectedContract === 'all' ? (
            /* Show all contracts as separate sections */
            <div className="space-y-6">
              {contracts.map(contract => {
                const contractDepts = departmentsByContract[contract.id] || []
                if (contractDepts.length === 0) return null

                return (
                  <Card key={contract.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <CardTitle className="flex items-center space-x-2">
                            <Building2 className="h-5 w-5 text-blue-500" />
                            <span>{contract.name}</span>
                            <Badge variant="outline">{contract.code}</Badge>
                          </CardTitle>
                        </div>
                        <Button size="sm" onClick={() => handleCreateDepartment(contract.id)}>
                          <Plus className="h-4 w-4 mr-2" />
                          Add Department
                        </Button>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-1">
                        {contractDepts.map(dept => (
                          <div key={dept.id}>
                            {renderTreeNode(dept, 0)}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          ) : (
            /* Show single selected contract */
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-2">
                      <Building2 className="h-5 w-5 text-blue-500" />
                      <span>{contracts.find(c => c.id === selectedContract)?.name}</span>
                      <Badge variant="outline">
                        {contracts.find(c => c.id === selectedContract)?.code}
                      </Badge>
                    </CardTitle>
                  </div>
                  <Button size="sm" onClick={() => handleCreateDepartment(selectedContract)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Department
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {treeData.length === 0 ? (
                  <div className="text-center py-12">
                    <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No departments found</h3>
                    <p className="text-muted-foreground mb-4">
                      Get started by creating your first department
                    </p>
                    <Button onClick={() => handleCreateDepartment(selectedContract)}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Department
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {treeData.map(dept => (
                      <div key={dept.id}>
                        {renderTreeNode(dept, 0)}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Department Dialog */}
        <DepartmentDialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          department={editingDepartment}
          onSuccess={handleDialogSuccess}
        />

        {/* Manager Assignment Dialog */}
        <ManagerDialog
          open={managerDialogOpen}
          onClose={() => setManagerDialogOpen(false)}
          department={selectedDeptForManager}
          onSuccess={handleDialogSuccess}
        />
      </main>
    </div>
  )
}
