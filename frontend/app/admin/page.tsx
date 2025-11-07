'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Building2, Users, Settings, BarChart3, FileText, Shield } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { authAPI } from '@/lib/api'
import Sidebar from '@/components/layout/sidebar'

const adminSections = [
  {
    title: 'Contracts Management',
    description: 'Manage company contracts and client relationships',
    icon: Building2,
    href: '/admin/contracts',
    color: 'text-blue-500',
  },
  {
    title: 'User Management',
    description: 'Manage user accounts, roles, and permissions',
    icon: Users,
    href: '/admin/users',
    color: 'text-green-500',
    coming_soon: true,
  },
  {
    title: 'Department Structure',
    description: 'Configure organizational hierarchy and departments',
    icon: Settings,
    href: '/admin/departments',
    color: 'text-purple-500',
    coming_soon: true,
  },
  {
    title: 'System Analytics',
    description: 'View system-wide analytics and performance metrics',
    icon: BarChart3,
    href: '/admin/analytics',
    color: 'text-orange-500',
    coming_soon: true,
  },
  {
    title: 'Audit & Reports',
    description: 'Access audit logs and generate compliance reports',
    icon: FileText,
    href: '/admin/audit',
    color: 'text-red-500',
    coming_soon: true,
  },
  {
    title: 'Security Settings',
    description: 'Configure security policies and access controls',
    icon: Shield,
    href: '/admin/security',
    color: 'text-indigo-500',
    coming_soon: true,
  },
]

export default function AdminPanelPage() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadUserData = async () => {
      try {
        const userResponse = await authAPI.getCurrentUser()
        setUser(userResponse.data || userResponse)
      } catch (error) {
        console.error('Error loading user:', error)
      } finally {
        setLoading(false)
      }
    }

    loadUserData()
  }, [])

  // Check if user is admin
  if (loading) {
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

  if (user?.role !== 'admin') {
    return (
      <div className="container mx-auto py-8">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Access Denied</h3>
              <p className="text-muted-foreground">
                Administrator privileges required to access this area.
              </p>
            </div>
          </CardContent>
        </Card>
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
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Administration Panel</h1>
        <p className="text-muted-foreground">
          Manage system configuration, users, and organizational structure
        </p>
      </div>

      {/* Welcome Card */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Shield className="h-5 w-5 text-blue-500" />
            <span>Welcome, {user?.full_name || user?.name}</span>
          </CardTitle>
          <CardDescription>
            You have administrator access to all system functions. Use the sections below to manage the immigration system.
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Admin Sections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {adminSections.map((section) => {
          const IconComponent = section.icon
          const isComingSoon = section.coming_soon

          return (
            <Card 
              key={section.href} 
              className={`hover:shadow-md transition-shadow ${isComingSoon ? 'opacity-60' : ''}`}
            >
              <CardHeader>
                <CardTitle className="flex items-center space-x-3">
                  <IconComponent className={`h-6 w-6 ${section.color}`} />
                  <span className="text-lg">{section.title}</span>
                  {isComingSoon && (
                    <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded">
                      Soon
                    </span>
                  )}
                </CardTitle>
                <CardDescription className="text-sm">
                  {section.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isComingSoon ? (
                  <Button variant="outline" disabled className="w-full">
                    Coming Soon
                  </Button>
                ) : (
                  <Link href={section.href}>
                    <Button className="w-full">
                      Access {section.title}
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Dynamic Stats - will be loaded from backend when dashboard API is called */}
      <div className="mt-12">
        <h2 className="text-xl font-semibold mb-4">System Overview</h2>
        <p className="text-sm text-muted-foreground mb-4">
          Real-time system statistics from backend database
        </p>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Building2 className="h-8 w-8 text-blue-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">-</div>
                <p className="text-sm text-muted-foreground">Active Contracts</p>
                <p className="text-xs text-muted-foreground">Loading...</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Users className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">-</div>
                <p className="text-sm text-muted-foreground">Total Users</p>
                <p className="text-xs text-muted-foreground">Loading...</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <Settings className="h-8 w-8 text-purple-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">-</div>
                <p className="text-sm text-muted-foreground">Departments</p>
                <p className="text-xs text-muted-foreground">Loading...</p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <BarChart3 className="h-8 w-8 text-orange-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">-</div>
                <p className="text-sm text-muted-foreground">System Status</p>
                <p className="text-xs text-muted-foreground">Loading...</p>
              </div>
            </CardContent>
          </Card>
        </div>
        <p className="text-xs text-muted-foreground mt-4">
          Note: Admin dashboard stats will be implemented using backend APIs, not hardcoded values
        </p>
      </div>
        </div>
      </main>
    </div>
  )
}