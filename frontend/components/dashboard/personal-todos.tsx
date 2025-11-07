'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  CheckCircle2,
  Circle,
  Plus,
  X,
  Calendar,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

interface TodoItem {
  id: string
  title: string
  description?: string
  completed: boolean
  priority: 'low' | 'medium' | 'high'
  dueDate?: string
  createdAt: string
}

interface PersonalTodosProps {
  user: any
}

export default function PersonalTodos({ user }: PersonalTodosProps) {
  const [todos, setTodos] = useState<TodoItem[]>([])
  const [newTodo, setNewTodo] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [newTodoPriority, setNewTodoPriority] = useState<'low' | 'medium' | 'high'>('medium')

  // Load todos from localStorage on component mount
  useEffect(() => {
    if (!user?.username) return // Don't load until user is available
    
    const savedTodos = localStorage.getItem(`todos_${user.username}`)
    if (savedTodos) {
      setTodos(JSON.parse(savedTodos))
    } else {
      // Set some default todos for demonstration
      const defaultTodos: TodoItem[] = [
        {
          id: '1',
          title: 'Review pending H1B applications',
          description: 'Check 3 applications waiting for approval',
          completed: false,
          priority: 'high',
          dueDate: '2025-11-08',
          createdAt: new Date().toISOString()
        },
        {
          id: '2', 
          title: 'Update visa status reports',
          description: 'Generate monthly report for management',
          completed: false,
          priority: 'medium',
          dueDate: '2025-11-10',
          createdAt: new Date().toISOString()
        },
        {
          id: '3',
          title: 'Call client about L1 renewal',
          description: 'Follow up on documentation requirements',
          completed: true,
          priority: 'low',
          createdAt: new Date().toISOString()
        }
      ]
      setTodos(defaultTodos)
    }
  }, [user])

  // Save todos to localStorage whenever todos change
  useEffect(() => {
    if (user?.username) {
      localStorage.setItem(`todos_${user.username}`, JSON.stringify(todos))
    }
  }, [todos, user])

  const addTodo = () => {
    if (!newTodo.trim()) return

    const todo: TodoItem = {
      id: Date.now().toString(),
      title: newTodo.trim(),
      completed: false,
      priority: newTodoPriority,
      createdAt: new Date().toISOString()
    }

    setTodos([todo, ...todos])
    setNewTodo('')
    setShowAddForm(false)
    setNewTodoPriority('medium')
  }

  const toggleTodo = (id: string) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ))
  }

  const deleteTodo = (id: string) => {
    setTodos(todos.filter(todo => todo.id !== id))
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200'
      case 'medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200'
      case 'low': return 'bg-green-100 text-green-700 border-green-200'
      default: return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertCircle className="h-3 w-3" />
      case 'medium': return <Clock className="h-3 w-3" />
      case 'low': return <Circle className="h-3 w-3" />
      default: return <Circle className="h-3 w-3" />
    }
  }

  const completedCount = todos.filter(t => t.completed).length
  const totalCount = todos.length

  return (
    <Card className="mt-6">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-blue-600" />
              <span>My Tasks</span>
            </CardTitle>
            <CardDescription>
              {completedCount} of {totalCount} completed
            </CardDescription>
          </div>
          <Button
            size="sm"
            onClick={() => setShowAddForm(!showAddForm)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-1" />
            Add Task
          </Button>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Add new todo form */}
        {showAddForm && (
          <div className="p-4 bg-gray-50 rounded-lg border border-dashed border-gray-300">
            <div className="space-y-3">
              <input
                type="text"
                placeholder="Enter task description..."
                value={newTodo}
                onChange={(e) => setNewTodo(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addTodo()}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">Priority:</span>
                  <select
                    value={newTodoPriority}
                    onChange={(e) => setNewTodoPriority(e.target.value as 'low' | 'medium' | 'high')}
                    className="px-2 py-1 border border-gray-300 rounded text-sm"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div className="space-x-2">
                  <Button size="sm" variant="outline" onClick={() => setShowAddForm(false)}>
                    Cancel
                  </Button>
                  <Button size="sm" onClick={addTodo}>
                    Add Task
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Todo list */}
        <div className="space-y-2 max-h-80 overflow-y-auto">
          {todos.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No tasks yet. Add your first task above!</p>
            </div>
          ) : (
            todos.map((todo) => (
              <div
                key={todo.id}
                className={`flex items-start space-x-3 p-3 rounded-lg border transition-colors ${
                  todo.completed 
                    ? 'bg-gray-50 border-gray-200' 
                    : 'bg-white border-gray-200 hover:bg-gray-50'
                }`}
              >
                <button
                  onClick={() => toggleTodo(todo.id)}
                  className={`mt-0.5 rounded-full p-1 transition-colors ${
                    todo.completed
                      ? 'text-green-600 hover:bg-green-100'
                      : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'
                  }`}
                >
                  {todo.completed ? (
                    <CheckCircle2 className="h-4 w-4" />
                  ) : (
                    <Circle className="h-4 w-4" />
                  )}
                </button>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 
                      className={`text-sm font-medium ${
                        todo.completed 
                          ? 'line-through text-gray-500' 
                          : 'text-gray-900'
                      }`}
                    >
                      {todo.title}
                    </h4>
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${getPriorityColor(todo.priority)}`}
                    >
                      <span className="flex items-center space-x-1">
                        {getPriorityIcon(todo.priority)}
                        <span>{todo.priority}</span>
                      </span>
                    </Badge>
                  </div>
                  
                  {todo.description && (
                    <p className={`text-xs ${
                      todo.completed ? 'text-gray-400' : 'text-gray-600'
                    }`}>
                      {todo.description}
                    </p>
                  )}
                  
                  {todo.dueDate && (
                    <div className="flex items-center space-x-1 mt-1">
                      <Calendar className="h-3 w-3 text-gray-400" />
                      <span className="text-xs text-gray-500">
                        Due: {new Date(todo.dueDate).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => deleteTodo(todo.id)}
                  className="text-gray-400 hover:text-red-600 transition-colors p-1"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))
          )}
        </div>

        {todos.length > 0 && (
          <div className="pt-3 border-t border-gray-200">
            <div className="flex items-center justify-between text-sm text-gray-500">
              <span>{todos.filter(t => !t.completed).length} remaining tasks</span>
              <span>{Math.round((completedCount / totalCount) * 100)}% complete</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(completedCount / totalCount) * 100}%` }}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}