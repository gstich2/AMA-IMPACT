'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { 
  LayoutDashboard,
  FileText,
  Users,
  BarChart3,
  Bell,
  Settings,
  LogOut,
  Plane,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  CheckSquare,
  UserCheck,
  Clock,
  Crown,
  PieChart,
  Building2,
  Briefcase,
  UserCog
} from 'lucide-react'
import { authAPI } from '@/lib/api'

interface SidebarProps {
  user: any
}

export default function Sidebar({ user }: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()

  console.log('Sidebar - user data:', user)
  console.log('Sidebar - user role:', user?.role)

  const navigationItems = [
    // Core Navigation
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      roles: ['admin', 'hr', 'pm', 'manager', 'beneficiary']
    },
    {
      name: 'My Tasks',
      href: '/tasks',
      icon: CheckSquare,
      roles: ['admin', 'hr', 'pm', 'manager', 'beneficiary']
    },
    {
      name: 'Beneficiaries',
      href: '/beneficiaries',
      icon: UserCheck,
      roles: ['admin', 'hr', 'pm']
    },
    {
      name: 'Cases',
      href: '/cases',
      icon: FileText,
      roles: ['admin', 'hr', 'pm', 'manager', 'beneficiary']
    },
    {
      name: 'Timeline',
      href: '/cases/timeline',
      icon: Clock,
      roles: ['admin', 'hr', 'pm', 'manager', 'beneficiary'],
      isSubItem: true
    },
    // Divider will be rendered in the component
    {
      name: 'divider',
      href: '',
      icon: null,
      roles: ['admin', 'hr', 'pm', 'manager', 'beneficiary'] // Show to everyone
    },
    // Admin Panel
    {
      name: 'Admin Panel',
      href: '/admin',
      icon: Crown,
      roles: ['admin'],
      isSection: true
    },
    {
      name: 'Contracts',
      href: '/admin/contracts',
      icon: Briefcase,
      roles: ['admin'],
      isSubItem: true
    },
    {
      name: 'Departments',
      href: '/admin/departments',
      icon: Building2,
      roles: ['admin'],
      isSubItem: true
    },
    {
      name: 'Visa Types',
      href: '/admin/visa-types',
      icon: FileText,
      roles: ['admin'],
      isSubItem: true
    },
    {
      name: 'User Management',
      href: '/admin/users',
      icon: UserCog,
      roles: ['admin'],
      isSubItem: true
    },
    // PM Analytics
    {
      name: 'PM Analytics',
      href: '/analytics',
      icon: PieChart,
      roles: ['admin', 'pm'],
      isSection: true
    },
    {
      name: 'Performance Stats',
      href: '/analytics/performance',
      icon: BarChart3,
      roles: ['admin', 'pm'],
      isSubItem: true
    },
    {
      name: 'Reports',
      href: '/analytics/reports',
      icon: FileText,
      roles: ['admin', 'pm'],
      isSubItem: true
    },
    // Settings
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      roles: ['admin', 'hr', 'pm', 'manager', 'beneficiary']
    }
  ]

  const userRole = user?.role || user?.user_role || 'BENEFICIARY'
  const filteredNavigationItems = navigationItems.filter(item => {
    console.log(`Checking item "${item.name}" with roles:`, item.roles, 'against userRole:', userRole)
    return item.roles.includes(userRole)
  })

  console.log('Sidebar - user:', user)
  console.log('Sidebar - userRole:', userRole, typeof userRole)
  console.log('Sidebar - filteredNavigationItems:', filteredNavigationItems.map(item => item.name))
  console.log('Sidebar - navigationItems length:', navigationItems.length)

  // Temporary fallback while debugging - restore if no items filtered
  const displayItems = filteredNavigationItems.length > 0 ? filteredNavigationItems : navigationItems.slice(0, 5)

  const handleLogout = async () => {
    try {
      await authAPI.logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      // Force logout anyway
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      router.push('/login')
    }
  }

  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="sm"
        className="fixed top-4 left-4 z-50 md:hidden bg-slate-900 text-white hover:bg-slate-800"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        {isMobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </Button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside 
        className={`
          fixed left-0 top-0 z-40 h-full bg-slate-900 border-r border-slate-800 transition-all duration-300
          ${isCollapsed ? 'w-16' : 'w-64'}
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800">
          {!isCollapsed && (
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Plane className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">AMA-IMPACT</h1>
                <p className="text-xs text-slate-400">Immigration Management</p>
              </div>
            </div>
          )}
          
          <Button
            variant="ghost"
            size="sm"
            className="hidden md:flex text-slate-400 hover:text-white hover:bg-slate-800"
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* User info */}
        {!isCollapsed && user && (
          <div className="p-4 border-b border-slate-800 bg-slate-800/50">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-semibold">
                {user.full_name?.charAt(0) || user.username?.charAt(0) || user.email?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  {user.full_name || user.username || user.email}
                </p>
                <p className="text-xs text-slate-400 truncate">
                  {userRole}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {displayItems.map((item, index) => {
            // Handle divider
            if (item.name === 'divider') {
              return (
                <div key={`divider-${index}`} className="my-3">
                  {!isCollapsed && (
                    <div className="border-t border-slate-800"></div>
                  )}
                </div>
              )
            }

            const Icon = item.icon
            const isActive = pathname === item.href
            const isSection = item.isSection
            const isSubItem = item.isSubItem
            
            return (
              <div key={item.href || `section-${index}`}>
                {isSection && !isCollapsed ? (
                  // Section header (non-clickable)
                  <div className={`
                    flex items-center space-x-2 px-3 py-2 mt-3 mb-1
                    ${item.name === 'Admin Panel' ? 'text-amber-400' : 
                      item.name === 'PM Analytics' ? 'text-blue-400' : 
                      'text-slate-400'}
                  `}>
                    {Icon && <Icon className="h-4 w-4" />}
                    <span className="text-xs font-semibold uppercase tracking-wide">
                      {item.name}
                    </span>
                  </div>
                ) : item.href ? (
                  // Regular navigation item
                  <Link
                    href={item.href}
                    className={`
                      flex items-center space-x-3 rounded-lg transition-all duration-200
                      ${isSubItem ? 'ml-4 px-2 py-2' : 'px-3 py-2.5'}
                      ${isActive 
                        ? 'bg-blue-600 text-white shadow-lg' 
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                      }
                      ${isCollapsed ? 'justify-center' : ''}
                    `}
                    onClick={() => setIsMobileOpen(false)}
                  >
                    {Icon && (
                      <Icon className={`
                        ${isSubItem ? 'h-4 w-4' : 'h-5 w-5'} 
                        ${isActive ? 'text-white' : 'text-slate-400'}
                      `} />
                    )}
                    {!isCollapsed && (
                      <span className={`font-medium ${isSubItem ? 'text-xs' : 'text-sm'}`}>
                        {item.name}
                      </span>
                    )}
                  </Link>
                ) : null}
              </div>
            )
          })}
        </nav>

        {/* Logout button */}
        <div className="p-4 border-t border-slate-800">
          <Button
            variant="ghost"
            className={`w-full text-slate-300 hover:bg-red-600 hover:text-white transition-colors ${
              isCollapsed ? 'px-0' : ''
            }`}
            onClick={handleLogout}
          >
            <LogOut className="h-5 w-5" />
            {!isCollapsed && <span className="ml-3">Logout</span>}
          </Button>
        </div>
      </aside>
    </>
  )
}