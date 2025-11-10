'use client'

import { useState, useEffect, useRef } from 'react'
import { Building2, Users, ChevronRight, ChevronDown, UserCog, User, FileText, AlertTriangle, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { departmentsAPI, contractsAPI, authAPI, usersAPI } from '@/lib/api'
import { toast } from 'sonner'
import ManagerDialog from '@/components/admin/manager-dialog'
import Sidebar from '@/components/layout/sidebar'
import PageHeader from '@/components/layout/page-header'

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

interface DepartmentStats {
  department_id: string | null
  department_name: string | null
  department_code: string | null
  contract_id: string
  contract_code: string
  beneficiaries_direct: number
  beneficiaries_total: number
  beneficiaries_active: number
  beneficiaries_inactive: number
  visa_applications_total: number
  visa_applications_active: number
  visa_applications_by_status: Record<string, number>
  visa_applications_by_type: Record<string, number>
  expiring_next_30_days: number
  expiring_next_90_days: number
  expired: number
  generated_at: string
  include_subdepartments: boolean
}

export default function PMDepartmentsAnalyticsPage() {
  const [departments, setDepartments] = useState<Department[]>([])
  const [treeData, setTreeData] = useState<Department[]>([])
  const [departmentStats, setDepartmentStats] = useState<Record<string, DepartmentStats>>({})
  const [loadingStats, setLoadingStats] = useState<Set<string>>(new Set())
  const [contracts, setContracts] = useState<Contract[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [userMap, setUserMap] = useState<Record<string, User>>({})
  const [loading, setLoading] = useState(true)
  const [managerDialogOpen, setManagerDialogOpen] = useState(false)
  const [selectedDeptForManager, setSelectedDeptForManager] = useState<Department | null>(null)
  const [user, setUser] = useState<any>(null)
  const [userLoading, setUserLoading] = useState(true)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

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
      // For PMs, the backend will automatically filter to their contract
      const response = await departmentsAPI.getTree()
      console.log('📊 Tree API Response:', JSON.stringify(response, null, 2))
      setTreeData(response || [])
    } catch (error) {
      console.error('Error fetching tree data:', error)
      toast.error('Failed to load department tree')
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
    fetchTreeData()
  }, [])

  const handleAssignManager = (department: Department) => {
    setSelectedDeptForManager(department)
    setManagerDialogOpen(true)
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
      // Fetch stats when expanding node (if not already loaded)
      if (!departmentStats[nodeId]) {
        fetchDepartmentStats(nodeId, false)
      }
      
      // Also fetch stats for immediate children
      const dept = findDepartmentById(nodeId, treeData)
      if (dept?.children) {
        dept.children.forEach(child => {
          if (!departmentStats[child.id]) {
            fetchDepartmentStats(child.id, false)
          }
        })
      }
    }
    setExpandedNodes(newExpanded)
  }

  // Helper function to find department by ID in tree
  const findDepartmentById = (id: string, departments: Department[]): Department | null => {
    for (const dept of departments) {
      if (dept.id === id) return dept
      if (dept.children) {
        const found = findDepartmentById(id, dept.children)
        if (found) return found
      }
    }
    return null
  }

  const fetchDepartmentStats = async (departmentId: string, includeSubdepartments: boolean = false) => {
    // Check if already loading or loaded
    if (loadingStats.has(departmentId) || departmentStats[departmentId]) {
      return
    }

    // Mark as loading
    setLoadingStats(prev => new Set(prev).add(departmentId))

    try {
      // Determine if this department has children
      const dept = findDepartmentById(departmentId, treeData)
      const hasChildren = dept?.children && dept.children.length > 0
      
      // If has children, include subdepartments for aggregate view
      // If no children (leaf), show only direct stats
      const shouldIncludeSubdepts = hasChildren || includeSubdepartments
      
      const stats = await departmentsAPI.getStats(departmentId, undefined, shouldIncludeSubdepts)
      setDepartmentStats(prev => ({
        ...prev,
        [departmentId]: stats
      }))
    } catch (error) {
      console.error(`Error fetching stats for department ${departmentId}:`, error)
    } finally {
      setLoadingStats(prev => {
        const newSet = new Set(prev)
        newSet.delete(departmentId)
        return newSet
      })
    }
  }

  // Fetch stats for all visible top-level departments on mount
  useEffect(() => {
    const loadInitialStats = async () => {
      if (treeData.length > 0) {
        // Fetch stats for all top-level departments (without subdepartments for granular view)
        const promises = treeData.map(dept => fetchDepartmentStats(dept.id, false))
        await Promise.all(promises)
      }
    }
    loadInitialStats()
  }, [treeData])

  // Get filtered departments
  const filteredDepartments = departments
  const totalDepartments = filteredDepartments.length
  const topLevelDepartments = filteredDepartments.filter(d => !d.parent_id).length
  const activeDepartments = filteredDepartments.filter(d => d.is_active).length

  // Get departments by contract for displaying
  const departmentsByContract: Record<string, Department[]> = {}
  treeData.forEach(dept => {
    if (!dept.parent_id) {
      if (!departmentsByContract[dept.contract_id]) {
        departmentsByContract[dept.contract_id] = []
      }
      departmentsByContract[dept.contract_id].push(dept)
    }
  })

  // Recursive tree renderer
  const renderTreeNode = (dept: Department, depth: number = 0) => {
    const hasChildren = dept.children && dept.children.length > 0
    const isExpanded = expandedNodes.has(dept.id)
    const manager = dept.manager_id ? userMap[dept.manager_id] : null
    const stats = departmentStats[dept.id]
    const isLoadingStats = loadingStats.has(dept.id)
    
    // Determine if stats include subdepartments
    const includesSubdepts = stats?.include_subdepartments || hasChildren

    return (
      <div key={dept.id}>
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

          {/* Statistics Badges */}
          {isLoadingStats ? (
            <div className="flex items-center space-x-1 text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
              <div className="animate-spin h-3 w-3 border-2 border-current border-t-transparent rounded-full"></div>
              <span>Loading...</span>
            </div>
          ) : stats ? (
            <div className="flex items-center space-x-1.5">
              {/* Beneficiaries Count - Always show */}
              <div 
                className={`flex items-center space-x-1 text-xs px-2 py-1 rounded cursor-help transition-colors ${
                  stats.beneficiaries_total > 0 
                    ? 'bg-blue-50 text-blue-700 hover:bg-blue-100' 
                    : 'bg-gray-50 text-gray-400'
                }`}
                title={`Beneficiaries: ${stats.beneficiaries_total} total\n• ${stats.beneficiaries_active} active\n• ${stats.beneficiaries_inactive} inactive${includesSubdepts ? '\n(includes all subdepartments)' : ''}`}
              >
                <Users className="h-3 w-3" />
                <span className="font-medium">{stats.beneficiaries_total}</span>
              </div>
              
              {/* Visa Applications Count - Always show */}
              <div 
                className={`flex items-center space-x-1 text-xs px-2 py-1 rounded cursor-help transition-colors ${
                  stats.visa_applications_total > 0
                    ? 'bg-purple-50 text-purple-700 hover:bg-purple-100'
                    : 'bg-gray-50 text-gray-400'
                }`}
                title={stats.visa_applications_total > 0 
                  ? `Visa Applications: ${stats.visa_applications_total} total\n• ${stats.visa_applications_active} active${includesSubdepts ? '\n(includes all subdepartments)' : ''}\n\nBy Status:\n${Object.entries(stats.visa_applications_by_status).map(([status, count]) => `• ${status}: ${count}`).join('\n')}\n\nBy Type:\n${Object.entries(stats.visa_applications_by_type).map(([type, count]) => `• ${type}: ${count}`).join('\n')}`
                  : `No visa applications${includesSubdepts ? ' (checked subdepartments)' : ''}`
                }
              >
                <FileText className="h-3 w-3" />
                <span className="font-medium">{stats.visa_applications_total}</span>
              </div>
              
              {/* Expiring Soon Warning - Always show */}
              <div 
                className={`flex items-center space-x-1 text-xs px-2 py-1 rounded cursor-help transition-colors ${
                  stats.expiring_next_30_days > 0
                    ? 'bg-orange-50 text-orange-700 hover:bg-orange-100 animate-pulse'
                    : 'bg-gray-50 text-gray-400'
                }`}
                title={stats.expiring_next_30_days > 0 
                  ? `Expiring Soon: ${stats.expiring_next_30_days} visas expiring within 30 days\n• ${stats.expiring_next_90_days} expiring within 90 days${includesSubdepts ? '\n(includes all subdepartments)' : ''}`
                  : `No visas expiring soon${includesSubdepts ? ' (checked subdepartments)' : ''}`
                }
              >
                <AlertTriangle className="h-3 w-3" />
                <span className="font-medium">{stats.expiring_next_30_days}</span>
              </div>
              
              {/* Expired Warning - Always show */}
              <div 
                className={`flex items-center space-x-1 text-xs px-2 py-1 rounded cursor-help transition-colors ${
                  stats.expired > 0
                    ? 'bg-red-50 text-red-700 hover:bg-red-100'
                    : 'bg-gray-50 text-gray-400'
                }`}
                title={stats.expired > 0 
                  ? `Expired Visas: ${stats.expired} visas have expired${includesSubdepts ? '\n(includes all subdepartments)' : ''}\nRequire immediate attention!`
                  : `No expired visas${includesSubdepts ? ' (checked subdepartments)' : ''}`
                }
              >
                <XCircle className="h-3 w-3" />
                <span className="font-medium">{stats.expired}</span>
              </div>
            </div>
          ) : null}

          {/* Legacy user count (if stats not loaded) */}
          {!stats && !isLoadingStats && dept.user_count !== undefined && dept.user_count > 0 && (
            <div className="flex items-center space-x-1 text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
              <Users className="h-3 w-3" />
              <span>{dept.user_count}</span>
            </div>
          )}
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

  // Check permissions - only PM and Admin can access
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
                    You don't have permission to view department analytics.
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    )
  }

  // Get contracts to display - PMs see only their contract
  const contractsToDisplay = user.role?.toLowerCase() === 'admin' 
    ? contracts 
    : contracts.filter(c => c.id === user.contract_id)

  return (
    <>
      <PageHeader user={user} />
      <Sidebar user={user} />
      <main className="pt-16 md:ml-64 transition-all duration-300 overflow-y-auto bg-background min-h-screen">
        <div className="container mx-auto py-8 space-y-6">
          {/* Page Title */}
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Department Analytics</h1>
            <p className="text-muted-foreground">
              View organizational structure and visa tracking statistics
            </p>
          </div>

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
          ) : (
            <div className="space-y-6">
              {contractsToDisplay.map(contract => {
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

              {contractsToDisplay.length === 0 && (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-12">
                      <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No departments found</h3>
                      <p className="text-muted-foreground">
                        No departments are available for your contract
                      </p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>

        {/* Manager Assignment Dialog */}
        <ManagerDialog
          open={managerDialogOpen}
          onClose={() => setManagerDialogOpen(false)}
          department={selectedDeptForManager}
          onSuccess={handleDialogSuccess}
        />
      </main>
    </>
  )
}
