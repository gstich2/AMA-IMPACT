'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { auditAPI } from '@/lib/api'
import { 
  Clock, 
  CheckCircle2, 
  FileText, 
  AlertTriangle, 
  UserPlus,
  Shield,
  Trash2,
  Edit,
  Eye
} from 'lucide-react'

interface RecentActivityProps {
  user: any
}

interface AuditActivity {
  timestamp: string
  user_name: string
  action: string
  resource_type: string
  resource_name: string
  changes_summary: string
}

const getActionIcon = (action: string) => {
  switch (action.toLowerCase()) {
    case 'create':
      return { icon: UserPlus, color: 'text-green-600', bgColor: 'bg-green-100' }
    case 'update':
      return { icon: Edit, color: 'text-blue-600', bgColor: 'bg-blue-100' }
    case 'delete':
      return { icon: Trash2, color: 'text-red-600', bgColor: 'bg-red-100' }
    case 'login':
      return { icon: Shield, color: 'text-purple-600', bgColor: 'bg-purple-100' }
    case 'view':
    case 'read':
      return { icon: Eye, color: 'text-gray-600', bgColor: 'bg-gray-100' }
    default:
      return { icon: FileText, color: 'text-blue-600', bgColor: 'bg-blue-100' }
  }
}

const formatTimeAgo = (timestamp: string) => {
  const now = new Date()
  const then = new Date(timestamp)
  const diffMs = now.getTime() - then.getTime()
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffDays > 0) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

export default function RecentActivity({ user }: RecentActivityProps) {
  const [activities, setActivities] = useState<AuditActivity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchRecentActivity = async () => {
      try {
        const response = await auditAPI.getStats()
        setActivities(response.recent_activity_summary || [])
      } catch (err) {
        console.error('Failed to fetch recent activity:', err)
        setError('Failed to load recent activity')
      } finally {
        setLoading(false)
      }
    }

    fetchRecentActivity()
  }, [])

  if (loading) {
    return (
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 text-ama-blue-600 mr-2" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-ama-blue-600"></div>
              <span className="ml-2 text-sm text-gray-600">Loading activity...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="h-5 w-5 text-ama-blue-600 mr-2" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
              <p className="text-sm text-gray-600">{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mt-8">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="h-5 w-5 text-ama-blue-600 mr-2" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activities.length === 0 ? (
            <div className="text-center py-8">
              <Clock className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-600">No recent activity to display</p>
            </div>
          ) : (
            <>
              <div className="max-h-64 overflow-y-auto space-y-3">
                {activities.slice(0, 10).map((activity, index) => {
                  const { icon: Icon, color, bgColor } = getActionIcon(activity.action)
                  
                  return (
                    <div key={index} className="flex items-start space-x-3 p-2 hover:bg-gray-50 rounded-md">
                      <div className={`w-8 h-8 ${bgColor} rounded-full flex items-center justify-center`}>
                        <Icon className={`h-4 w-4 ${color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">
                          <span className="font-medium">{activity.user_name}</span>{' '}
                          {activity.action.toLowerCase()}d{' '}
                          {activity.resource_name ? (
                            <span className="font-medium">{activity.resource_name}</span>
                          ) : (
                            <span className="font-medium">{activity.resource_type}</span>
                          )}
                          {activity.changes_summary && (
                            <span className="text-xs text-gray-500 block mt-1">
                              {activity.changes_summary}
                            </span>
                          )}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatTimeAgo(activity.timestamp)}
                        </p>
                      </div>
                    </div>
                  )
                })}
              </div>
              
              <div className="mt-4 pt-4 border-t">
                <button className="text-sm text-ama-blue-600 hover:text-ama-blue-700 font-medium">
                  View All Activity →
                </button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}