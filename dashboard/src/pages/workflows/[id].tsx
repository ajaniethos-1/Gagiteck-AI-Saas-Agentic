import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Workflow, ArrowLeft, Play, Settings, Trash2, Loader2, Save, Plus, GripVertical, ArrowRight, X } from 'lucide-react'
import { api, Workflow as WorkflowType, ApiError } from '@/lib/api'

interface WorkflowStep {
  id: string
  type: 'agent' | 'condition' | 'delay' | 'webhook'
  name: string
  config: Record<string, any>
}

export default function WorkflowDetailPage() {
  const router = useRouter()
  const { id } = router.query

  const [workflow, setWorkflow] = useState<WorkflowType | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  // Form state
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [steps, setSteps] = useState<WorkflowStep[]>([])
  const [showAddStep, setShowAddStep] = useState(false)

  const fetchWorkflow = async () => {
    if (!id || typeof id !== 'string') return

    try {
      setLoading(true)
      setError(null)
      const result = await api.workflows.get(id)
      setWorkflow(result)
      setName(result.name)
      setDescription(result.description || '')
      setSteps(result.steps || [])
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to fetch workflow')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkflow()
  }, [id])

  const handleSave = async () => {
    if (!workflow) return

    try {
      setSaving(true)
      const updated = await api.workflows.update(workflow.id, {
        name,
        description,
        steps,
      })
      setWorkflow(updated)
      setIsEditing(false)
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!workflow) return
    if (!confirm('Are you sure you want to delete this workflow?')) return

    try {
      await api.workflows.delete(workflow.id)
      router.push('/workflows')
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    }
  }

  const handleTrigger = async () => {
    if (!workflow) return

    try {
      const execution = await api.workflows.trigger(workflow.id)
      alert(`Workflow triggered! Execution ID: ${execution.id}`)
      router.push('/executions')
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    }
  }

  const addStep = (type: WorkflowStep['type']) => {
    const newStep: WorkflowStep = {
      id: `step_${Date.now()}`,
      type,
      name: `${type.charAt(0).toUpperCase() + type.slice(1)} Step`,
      config: {},
    }
    setSteps([...steps, newStep])
    setShowAddStep(false)
  }

  const removeStep = (stepId: string) => {
    setSteps(steps.filter(s => s.id !== stepId))
  }

  const updateStep = (stepId: string, updates: Partial<WorkflowStep>) => {
    setSteps(steps.map(s => s.id === stepId ? { ...s, ...updates } : s))
  }

  const moveStep = (index: number, direction: 'up' | 'down') => {
    const newSteps = [...steps]
    const newIndex = direction === 'up' ? index - 1 : index + 1
    if (newIndex < 0 || newIndex >= steps.length) return
    [newSteps[index], newSteps[newIndex]] = [newSteps[newIndex], newSteps[index]]
    setSteps(newSteps)
  }

  const getStepIcon = (type: WorkflowStep['type']) => {
    switch (type) {
      case 'agent': return '🤖'
      case 'condition': return '🔀'
      case 'delay': return '⏱️'
      case 'webhook': return '🔗'
      default: return '📦'
    }
  }

  const getStepColor = (type: WorkflowStep['type']) => {
    switch (type) {
      case 'agent': return 'border-blue-500 bg-blue-50 dark:bg-blue-950'
      case 'condition': return 'border-yellow-500 bg-yellow-50 dark:bg-yellow-950'
      case 'delay': return 'border-purple-500 bg-purple-50 dark:bg-purple-950'
      case 'webhook': return 'border-green-500 bg-green-50 dark:bg-green-950'
      default: return 'border-gray-500 bg-gray-50 dark:bg-gray-950'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !workflow) {
    return (
      <div className="space-y-6">
        <Link href="/workflows" className="flex items-center gap-2 text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
          Back to Workflows
        </Link>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-red-600">{error || 'Workflow not found'}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/workflows" className="text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-3">
              <Workflow className="h-6 w-6 text-primary" />
            </div>
            <div>
              {isEditing ? (
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="text-2xl font-bold bg-transparent border-b border-primary focus:outline-none"
                />
              ) : (
                <h1 className="text-2xl font-bold">{workflow.name}</h1>
              )}
              <p className="text-sm text-muted-foreground">{workflow.id}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleTrigger}>
            <Play className="mr-2 h-4 w-4" />
            Trigger
          </Button>
          {isEditing ? (
            <>
              <Button variant="outline" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={saving}>
                {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                <Save className="mr-2 h-4 w-4" />
                Save
              </Button>
            </>
          ) : (
            <Button variant="outline" onClick={() => setIsEditing(true)}>
              <Settings className="mr-2 h-4 w-4" />
              Edit
            </Button>
          )}
          <Button variant="outline" className="text-destructive" onClick={handleDelete}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Description */}
      <Card>
        <CardHeader>
          <CardTitle>Description</CardTitle>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full h-24 px-3 py-2 border rounded-md bg-background"
              placeholder="Describe what this workflow does..."
            />
          ) : (
            <p className="text-muted-foreground">{workflow.description || 'No description'}</p>
          )}
        </CardContent>
      </Card>

      {/* Workflow Builder */}
      <Card>
        <CardHeader>
          <CardTitle>Workflow Steps</CardTitle>
          <CardDescription>
            {isEditing ? 'Drag to reorder, click to edit' : `${steps.length} steps configured`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {steps.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Workflow className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">No steps configured</h3>
              <p className="text-muted-foreground mb-4">Add steps to build your workflow</p>
              {isEditing && (
                <Button onClick={() => setShowAddStep(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Step
                </Button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center gap-4">
                  {/* Step card */}
                  <div className={`flex-1 p-4 rounded-lg border-2 ${getStepColor(step.type)}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {isEditing && (
                          <div className="flex flex-col gap-1">
                            <button
                              onClick={() => moveStep(index, 'up')}
                              disabled={index === 0}
                              className="text-muted-foreground hover:text-foreground disabled:opacity-30"
                            >
                              ▲
                            </button>
                            <button
                              onClick={() => moveStep(index, 'down')}
                              disabled={index === steps.length - 1}
                              className="text-muted-foreground hover:text-foreground disabled:opacity-30"
                            >
                              ▼
                            </button>
                          </div>
                        )}
                        <span className="text-2xl">{getStepIcon(step.type)}</span>
                        <div>
                          {isEditing ? (
                            <input
                              type="text"
                              value={step.name}
                              onChange={(e) => updateStep(step.id, { name: e.target.value })}
                              className="font-medium bg-transparent border-b focus:outline-none"
                            />
                          ) : (
                            <h4 className="font-medium">{step.name}</h4>
                          )}
                          <p className="text-sm text-muted-foreground capitalize">{step.type}</p>
                        </div>
                      </div>
                      {isEditing && (
                        <button
                          onClick={() => removeStep(step.id)}
                          className="text-destructive hover:text-destructive/80"
                        >
                          <X className="h-5 w-5" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Arrow to next step */}
                  {index < steps.length - 1 && (
                    <ArrowRight className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                  )}
                </div>
              ))}

              {isEditing && (
                <Button variant="outline" className="w-full" onClick={() => setShowAddStep(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Step
                </Button>
              )}
            </div>
          )}

          {/* Add Step Modal */}
          {showAddStep && (
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
              <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-lg">
                <h2 className="text-xl font-bold mb-4">Add Step</h2>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => addStep('agent')}
                    className="p-4 rounded-lg border-2 hover:border-primary text-center"
                  >
                    <span className="text-3xl block mb-2">🤖</span>
                    <span className="font-medium">Agent</span>
                    <p className="text-xs text-muted-foreground">Run an AI agent</p>
                  </button>
                  <button
                    onClick={() => addStep('condition')}
                    className="p-4 rounded-lg border-2 hover:border-primary text-center"
                  >
                    <span className="text-3xl block mb-2">🔀</span>
                    <span className="font-medium">Condition</span>
                    <p className="text-xs text-muted-foreground">Branch logic</p>
                  </button>
                  <button
                    onClick={() => addStep('delay')}
                    className="p-4 rounded-lg border-2 hover:border-primary text-center"
                  >
                    <span className="text-3xl block mb-2">⏱️</span>
                    <span className="font-medium">Delay</span>
                    <p className="text-xs text-muted-foreground">Wait before next</p>
                  </button>
                  <button
                    onClick={() => addStep('webhook')}
                    className="p-4 rounded-lg border-2 hover:border-primary text-center"
                  >
                    <span className="text-3xl block mb-2">🔗</span>
                    <span className="font-medium">Webhook</span>
                    <p className="text-xs text-muted-foreground">Call external API</p>
                  </button>
                </div>
                <Button variant="outline" className="w-full mt-4" onClick={() => setShowAddStep(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground">Status</label>
            <p className={`inline-flex rounded-full px-2 py-1 text-xs ${
              workflow.status === 'active'
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-700'
            }`}>
              {workflow.status}
            </p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Steps</label>
            <p>{steps.length}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Created</label>
            <p>{new Date(workflow.created_at).toLocaleString()}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-muted-foreground">Updated</label>
            <p>{new Date(workflow.updated_at).toLocaleString()}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
