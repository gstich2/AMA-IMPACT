'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { 
  LayoutDashboard,
  FileText,
  Users,
  BarChart3,
  Bell,
  Settings,
  Menu,
  X,
  CheckSquare,
  UserCheck,
  Clock,
  Crown,
  PieChart,
  Building2,
  Briefcase,
  UserCog
} from 'lucide-react'

interface SidebarProps {
  user: any
}

export default function Sidebar({ user }: SidebarProps) {
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const pathname = usePathname()

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
      name: 'Departments',
      href: '/analytics/departments',
      icon: Building2,
      roles: ['admin', 'pm'],
      isSubItem: true
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

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="fixed top-4 left-4 z-50 md:hidden bg-slate-900 text-white hover:bg-slate-800 p-2 rounded"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        {isMobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </button>

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
          fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 bg-slate-900 border-r border-slate-800 transition-transform duration-300
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto h-[calc(100%-4rem)]">
          {displayItems.map((item, index) => {
            // Handle divider
            if (item.name === 'divider') {
              return (
                <div key={`divider-${index}`} className="my-3">
                  <div className="border-t border-slate-800"></div>
                </div>
              )
            }

            const Icon = item.icon
            const isActive = pathname === item.href
            const isSection = item.isSection
            const isSubItem = item.isSubItem
            
            return (
              <div key={item.href || `section-${index}`}>
                {isSection ? (
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
                    `}
                    onClick={() => setIsMobileOpen(false)}
                  >
                    {Icon && (
                      <Icon className={`
                        ${isSubItem ? 'h-4 w-4' : 'h-5 w-5'} 
                        ${isActive ? 'text-white' : 'text-slate-400'}
                      `} />
                    )}
                    <span className={`font-medium ${isSubItem ? 'text-xs' : 'text-sm'}`}>
                      {item.name}
                    </span>
                  </Link>
                ) : null}
              </div>
            )
          })}
        </nav>
      </aside>
    </>
  )
}