import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Zap, RefreshCw, Loader2, AlertCircle, CheckCircle2, XCircle, Clock, StopCircle } from 'lucide-react'
import { api, Execution, ApiError } from '@/lib/api'

export default function ExecutionsPage() {
  const [executions, setExecutions] = useState<Execution[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [cancellingId, setCancellingId] = useState<string | null>(null)

  const fetchExecutions = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.executions.list()
      setExecutions(result.data)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to fetch executions')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchExecutions()
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchExecutions, 10000)
    return () => clearInterval(interval)
  }, [])

  const handleCancel = async (executionId: string) => {
    try {
      setCancellingId(executionId)
      await api.executions.cancel(executionId)
      await fetchExecutions()
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    } finally {
      setCancellingId(null)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'running':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />
      case 'cancelled':
        return <StopCircle className="h-4 w-4 text-gray-500" />
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      completed: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      failed: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
      running: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
      cancelled: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
      pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
    }
    return styles[status] || styles.pending
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  const formatDuration = (startedAt: string, completedAt: string | null) => {
    if (!completedAt) return 'In progress...'
    const start = new Date(startedAt).getTime()
    const end = new Date(completedAt).getTime()
    const durationMs = end - start
    if (durationMs < 1000) return `${durationMs}ms`
    if (durationMs < 60000) return `${(durationMs / 1000).toFixed(1)}s`
    return `${(durationMs / 60000).toFixed(1)}m`
  }

  if (loading && executions.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Executions</h1>
          <p className="text-muted-foreground">Monitor agent and workflow runs</p>
        </div>
        <Button variant="outline" onClick={fetchExecutions} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 text-red-600 bg-red-50 rounded-lg">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
          <Button variant="ghost" size="sm" onClick={fetchExecutions}>
            Retry
          </Button>
        </div>
      )}

      {executions.length === 0 && !error ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Zap className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No executions yet</h3>
            <p className="text-muted-foreground mb-4">Run an agent or trigger a workflow to see executions</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {/* Summary cards */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total</CardDescription>
                <CardTitle className="text-2xl">{executions.length}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Running</CardDescription>
                <CardTitle className="text-2xl text-blue-600">
                  {executions.filter(e => e.status === 'running').length}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Completed</CardDescription>
                <CardTitle className="text-2xl text-green-600">
                  {executions.filter(e => e.status === 'completed').length}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Failed</CardDescription>
                <CardTitle className="text-2xl text-red-600">
                  {executions.filter(e => e.status === 'failed').length}
                </CardTitle>
              </CardHeader>
            </Card>
          </div>

          {/* Executions list */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Executions</CardTitle>
              <CardDescription>Auto-refreshes every 10 seconds</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {executions.map((execution) => (
                  <div
                    key={execution.id}
                    className="flex items-center justify-between p-4 rounded-lg border bg-card"
                  >
                    <div className="flex items-center gap-4">
                      <div className="rounded-lg bg-primary/10 p-2">
                        {getStatusIcon(execution.status)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{execution.id}</span>
                          <span className={`rounded-full px-2 py-0.5 text-xs ${getStatusBadge(execution.status)}`}>
                            {execution.status}
                          </span>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {execution.type === 'agent' ? 'Agent' : 'Workflow'}: {execution.resource_id}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right text-sm">
                        <div className="text-muted-foreground">
                          {formatDate(execution.started_at)}
                        </div>
                        <div className="font-medium">
                          {formatDuration(execution.started_at, execution.completed_at)}
                        </div>
                      </div>
                      {execution.status === 'running' && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-destructive"
                          onClick={() => handleCancel(execution.id)}
                          disabled={cancellingId === execution.id}
                        >
                          {cancellingId === execution.id ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <StopCircle className="h-3 w-3" />
                          )}
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
