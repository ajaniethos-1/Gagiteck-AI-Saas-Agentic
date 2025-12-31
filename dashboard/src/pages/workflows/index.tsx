import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Workflow, Plus, Play, Settings, Trash2, Loader2, RefreshCw, AlertCircle } from 'lucide-react'
import { api, Workflow as WorkflowType, ApiError } from '@/lib/api'

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowType[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [triggeringWorkflow, setTriggeringWorkflow] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  const fetchWorkflows = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.workflows.list()
      setWorkflows(result.data)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to fetch workflows')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const handleTriggerWorkflow = async (workflowId: string) => {
    try {
      setTriggeringWorkflow(workflowId)
      await api.workflows.trigger(workflowId)
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    } finally {
      setTriggeringWorkflow(null)
    }
  }

  const handleDeleteWorkflow = async (workflowId: string) => {
    if (!confirm('Are you sure you want to delete this workflow?')) return

    try {
      await api.workflows.delete(workflowId)
      setWorkflows(workflows.filter(w => w.id !== workflowId))
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    }
  }

  const handleCreateWorkflow = async (name: string, description: string) => {
    try {
      const newWorkflow = await api.workflows.create({ name, description, steps: [] })
      setWorkflows([...workflows, newWorkflow])
      setShowCreateModal(false)
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    }
  }

  if (loading) {
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
          <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
          <p className="text-muted-foreground">Automate multi-step processes</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchWorkflows}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Workflow
          </Button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 text-red-600 bg-red-50 rounded-lg">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
          <Button variant="ghost" size="sm" onClick={fetchWorkflows}>
            Retry
          </Button>
        </div>
      )}

      {workflows.length === 0 && !error ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Workflow className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No workflows yet</h3>
            <p className="text-muted-foreground mb-4">Create your first workflow to automate tasks</p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Workflow
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {workflows.map((workflow) => (
            <Card key={workflow.id}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <Workflow className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{workflow.name}</CardTitle>
                    <CardDescription>{workflow.steps.length} steps</CardDescription>
                  </div>
                </div>
                <span className={`rounded-full px-2 py-1 text-xs ${
                  workflow.status === 'active'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                }`}>
                  {workflow.status}
                </span>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    {workflow.description || 'No description'}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleTriggerWorkflow(workflow.id)}
                      disabled={triggeringWorkflow === workflow.id}
                    >
                      {triggeringWorkflow === workflow.id ? (
                        <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                      ) : (
                        <Play className="mr-1 h-3 w-3" />
                      )}
                      Trigger
                    </Button>
                    <Button size="sm" variant="outline">
                      <Settings className="h-3 w-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="text-destructive"
                      onClick={() => handleDeleteWorkflow(workflow.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {showCreateModal && (
        <CreateWorkflowModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateWorkflow}
        />
      )}
    </div>
  )
}

function CreateWorkflowModal({
  onClose,
  onCreate,
}: {
  onClose: () => void
  onCreate: (name: string, description: string) => void
}) {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-lg">
        <h2 className="text-xl font-bold mb-4">Create New Workflow</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md bg-background"
              placeholder="My Workflow"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border rounded-md bg-background h-24"
              placeholder="Describe what this workflow does..."
            />
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={() => onCreate(name, description)} disabled={!name}>
              Create
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
