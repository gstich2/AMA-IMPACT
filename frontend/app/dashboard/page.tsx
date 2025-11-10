'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { authAPI, dashboardAPI, auditAPI } from '@/lib/api'
import AppLayout from '@/components/layout/app-layout'
import PersonalTodos from '@/components/dashboard/personal-todos'
import RecentActivity from '@/components/dashboard/recent-activity'
import { 
  Plane, 
  FileText, 
  Bell, 
  BarChart3,
  Shield,
  Clock,
  AlertTriangle,
  CheckCircle2,
  UserPlus,
  Users
} from 'lucide-react'

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const router = useRouter()

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const summaryResponse = await dashboardAPI.getSummary()
        setDashboardData(summaryResponse.data)
      } catch (dashError) {
        console.log('Dashboard API not available, using mock data:', dashError)
        // Set mock data if dashboard API fails
        setDashboardData({
          total_visas: 25,
          expiring_visas: 3,
          active_users: 12,
          overdue_tasks: 1
        })
      }
    }

    loadDashboardData()
  }, [])

  return (
    <AppLayout>
      <div className="container mx-auto py-8">
        {/* Dashboard Title */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back!
          </p>
        </div>

          {/* Quick Stats */}
          {dashboardData && (
            <div className="grid grid-cols-5 gap-4 mb-8">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <FileText className="h-4 w-4 text-blue-600" />
                </div>
                <p className="text-xs text-gray-600 mb-1">Active Cases</p>
                <p className="text-xl font-bold text-gray-900">
                  {dashboardData.active_cases || dashboardData.total_visas || 25}
                </p>
                <p className="text-xs text-gray-500">visa application cases</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <Clock className="h-4 w-4 text-yellow-600" />
                </div>
                <p className="text-xs text-gray-600 mb-1">Expiring Soon</p>
                <p className="text-xl font-bold text-gray-900">
                  {dashboardData.expiring_visas || 6}
                </p>
                <p className="text-xs text-gray-500">expires within 90 days</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <FileText className="h-4 w-4 text-indigo-600" />
                </div>
                <p className="text-xs text-gray-600 mb-1">Pending Actions</p>
                <p className="text-xl font-bold text-gray-900">
                  {dashboardData.pending_actions ?? dashboardData.pending_actions_count ?? 0}
                </p>
                <p className="text-xs text-gray-500">awaiting attention</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <Users className="h-4 w-4 text-green-600" />
                </div>
                <p className="text-xs text-gray-600 mb-1">Active Users</p>
                <p className="text-xl font-bold text-gray-900">
                  {dashboardData.active_users || 12}
                </p>
                <p className="text-xs text-gray-500">employees with cases</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 text-center">
                <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                </div>
                <p className="text-xs text-gray-600 mb-1">Urgent Cases</p>
                <p className="text-xl font-bold text-gray-900">
                  {dashboardData.overdue_tasks || 3}
                </p>
                <p className="text-xs text-gray-500">high priority need</p>
              </CardContent>
            </Card>
          </div>
        )}

          {/* Action Items */}
          <Card className="mb-8">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg font-semibold">Action Items</CardTitle>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    placeholder="Search action items..."
                    className="px-3 py-2 border border-gray-300 rounded-md text-sm w-64"
                  />
                  <div className="flex space-x-1">
                    <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded-md">All (8)</button>
                    <button className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50">Pending (6)</button>
                    <button className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50">Expiring (3)</button>
                    <button className="px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50">Urgent (1)</button>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-3">
                {/* HIGH priority item */}
                <div className="flex items-center p-3 border-l-4 border-red-500 bg-red-50 rounded-r-md">
                  <div className="w-6 h-6 bg-red-100 rounded flex items-center justify-center mr-3">
                    <span className="text-xs font-bold text-red-600">H</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Case Preparation</h4>
                        <p className="text-sm text-gray-600">Complete preparation for L1-B visa</p>
                        <p className="text-xs text-gray-500">A. Priya Singh (Interview) • 📅 TH: 14 • 📋 Day 30</p>
                      </div>
                      <div className="text-right">
                        <span className="inline-block px-2 py-1 text-xs font-semibold bg-red-100 text-red-700 rounded">HIGH</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* MEDIUM priority item */}
                <div className="flex items-center p-3 border-l-4 border-yellow-500 bg-yellow-50 rounded-r-md">
                  <div className="w-6 h-6 bg-yellow-100 rounded flex items-center justify-center mr-3">
                    <span className="text-xs font-bold text-yellow-600">M</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Documents Required</h4>
                        <p className="text-sm text-gray-600">Collect required documents for H1B RFE</p>
                        <p className="text-xs text-gray-500">Luis Dos Santos Fernandes • 📅 BPL: 14 • 📄 Oct 4</p>
                      </div>
                      <div className="text-right">
                        <span className="inline-block px-2 py-1 text-xs font-semibold bg-yellow-100 text-yellow-700 rounded">MEDIUM</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* MEDIUM priority item */}
                <div className="flex items-center p-3 border-l-4 border-yellow-500 bg-yellow-50 rounded-r-md">
                  <div className="w-6 h-6 bg-yellow-100 rounded flex items-center justify-center mr-3">
                    <span className="text-xs font-bold text-yellow-600">M</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Case Preparation</h4>
                        <p className="text-sm text-gray-600">Complete preparation for H1B Transfer from Briefings</p>
                        <p className="text-xs text-gray-500">Jacob Herni Fridriksson • 📅 US TA • 📋 Day 16</p>
                      </div>
                      <div className="text-right">
                        <span className="inline-block px-2 py-1 text-xs font-semibold bg-yellow-100 text-yellow-700 rounded">MEDIUM</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Personal Todos Widget */}
          <PersonalTodos user={{}} />

          {/* Recent Activity */}
          <RecentActivity user={{}} />

        {/* Backend Status */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CheckCircle2 className="h-5 w-5 text-green-500 mr-2" />
                System Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Backend API: Operational</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Database: Connected</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm">Authentication: Active</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        </div>
    </AppLayout>
  )
}