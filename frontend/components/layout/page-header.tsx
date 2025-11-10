'use client'

import { LogOut, Plane } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { authAPI } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface PageHeaderProps {
  user?: {
    full_name?: string
    username?: string
    email?: string
    role?: string
  } | null
}

export default function PageHeader({ user }: PageHeaderProps) {
  const router = useRouter()

  const handleLogout = async () => {
    try {
      await authAPI.logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout failed:', error)
      // Force logout anyway
      localStorage.removeItem('token')
      router.push('/login')
    }
  }

  // Format role display
  const formatRole = (role?: string) => {
    if (!role) return ''
    const roleMap: { [key: string]: string } = {
      admin: 'Administrator',
      pm: 'Project Manager',
      hr: 'HR Manager',
      manager: 'Department Manager',
      beneficiary: 'Beneficiary'
    }
    return roleMap[role.toLowerCase()] || role
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 border-b border-slate-800 bg-slate-900 shadow-lg">
      <div className="flex items-center justify-between px-6 py-3">
        {/* Left: AMA-IMPACT Branding */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <Plane className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">AMA-IMPACT</h1>
            <p className="text-xs text-slate-400">Beyond Borders, Bringing the World's Best Minds to America's Missions.</p>
          </div>
        </div>

        {/* Right: User Info & Logout */}
        <div className="flex items-center space-x-4">
          {/* User Info */}
          {user && (
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-white">
                  {user.full_name || user.username || user.email}
                </p>
                <p className="text-xs text-slate-400">
                  {formatRole(user.role)}
                </p>
              </div>
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center text-white font-semibold">
                {user.full_name?.charAt(0) || user.username?.charAt(0) || user.email?.charAt(0) || 'U'}
              </div>
            </div>
          )}

          {/* Logout Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-slate-300 hover:text-white hover:bg-red-600 transition-colors"
          >
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </div>
      </div>
    </div>
  )
}
