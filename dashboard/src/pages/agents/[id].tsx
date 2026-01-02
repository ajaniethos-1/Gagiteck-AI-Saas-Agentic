import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bot, ArrowLeft, Play, Settings, Trash2, Loader2, Save, Plus, X, RefreshCw } from 'lucide-react'
import { api, Agent, ApiError } from '@/lib/api'

export default function AgentDetailPage() {
  const router = useRouter()
  const { id } = router.query

  const [agent, setAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)

  // Form state
  const [name, setName] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')
  const [model, setModel] = useState('claude-3-sonnet')
  const [maxTokens, setMaxTokens] = useState(4096)
  const [temperature, setTemperature] = useState(0.7)
  const [tools, setTools] = useState<string[]>([])
  const [newTool, setNewTool] = useState('')

  const fetchAgent = async () => {
    if (!id || typeof id !== 'string') return

    try {
      setLoading(true)
      setError(null)
      const result = await api.agents.get(id)
      setAgent(result)
      // Populate form
      setName(result.name)
      setSystemPrompt(result.system_prompt || '')
      setModel(result.config.model)
      setMaxTokens(result.config.max_tokens)
      setTemperature(result.config.temperature)
      setTools(result.tools)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to fetch agent')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgent()
  }, [id])

  const handleSave = async () => {
    if (!agent) return

    try {
      setSaving(true)
      const updated = await api.agents.update(agent.id, {
        name,
        system_prompt: systemPrompt,
        config: {
          model,
          max_tokens: maxTokens,
          temperature,
          max_iterations: agent.config.max_iterations,
          timeout_ms: agent.config.timeout_ms,
        },
        tools,
      })
      setAgent(updated)
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
    if (!agent) return
    if (!confirm('Are you sure you want to delete this agent? This action cannot be undone.')) return

    try {
      await api.agents.delete(agent.id)
      router.push('/agents')
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    }
  }

  const handleRun = async () => {
    if (!agent) return

    const message = prompt('Enter a message for the agent:')
    if (!message) return

    try {
      const result = await api.agents.run(agent.id, { message })
      alert(`Agent response:\n\n${result.content}`)
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    }
  }

  const addTool = () => {
    if (newTool && !tools.includes(newTool)) {
      setTools([...tools, newTool])
      setNewTool('')
    }
  }

  const removeTool = (tool: string) => {
    setTools(tools.filter(t => t !== tool))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !agent) {
    return (
      <div className="space-y-6">
        <Link href="/agents" className="flex items-center gap-2 text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
          Back to Agents
        </Link>
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <p className="text-red-600">{error || 'Agent not found'}</p>
            <Button variant="outline" className="mt-4" onClick={fetchAgent}>
              Retry
            </Button>
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
          <Link href="/agents" className="text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-primary/10 p-3">
              <Bot className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">{agent.name}</h1>
              <p className="text-sm text-muted-foreground">{agent.id}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchAgent}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={handleRun}>
            <Play className="mr-2 h-4 w-4" />
            Run
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

      <div className="grid gap-6 md:grid-cols-2">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Agent name and status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name</label>
              {isEditing ? (
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md bg-background"
                />
              ) : (
                <p className="text-foreground">{agent.name}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <span className={`inline-flex rounded-full px-2 py-1 text-xs ${
                agent.status === 'active'
                  ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                  : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
              }`}>
                {agent.status}
              </span>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Created</label>
              <p className="text-muted-foreground">{new Date(agent.created_at).toLocaleString()}</p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Updated</label>
              <p className="text-muted-foreground">{new Date(agent.updated_at).toLocaleString()}</p>
            </div>
          </CardContent>
        </Card>

        {/* Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>Model and generation settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Model</label>
              {isEditing ? (
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md bg-background"
                >
                  <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                  <option value="claude-3-opus">Claude 3 Opus</option>
                  <option value="claude-3-haiku">Claude 3 Haiku</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                </select>
              ) : (
                <p className="text-foreground">{agent.config.model}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Max Tokens</label>
              {isEditing ? (
                <input
                  type="number"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  min={1}
                  max={100000}
                  className="w-full px-3 py-2 border rounded-md bg-background"
                />
              ) : (
                <p className="text-foreground">{agent.config.max_tokens.toLocaleString()}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Temperature</label>
              {isEditing ? (
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    min={0}
                    max={2}
                    step={0.1}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">{temperature}</span>
                </div>
              ) : (
                <p className="text-foreground">{agent.config.temperature}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Max Iterations</label>
              <p className="text-foreground">{agent.config.max_iterations}</p>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Timeout</label>
              <p className="text-foreground">{agent.config.timeout_ms / 1000}s</p>
            </div>
          </CardContent>
        </Card>

        {/* System Prompt */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>System Prompt</CardTitle>
            <CardDescription>Instructions that define the agent's behavior</CardDescription>
          </CardHeader>
          <CardContent>
            {isEditing ? (
              <textarea
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="w-full h-48 px-3 py-2 border rounded-md bg-background font-mono text-sm"
                placeholder="You are a helpful assistant..."
              />
            ) : (
              <pre className="w-full h-48 px-3 py-2 border rounded-md bg-muted overflow-auto font-mono text-sm whitespace-pre-wrap">
                {agent.system_prompt || 'No system prompt configured'}
              </pre>
            )}
          </CardContent>
        </Card>

        {/* Tools */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Tools</CardTitle>
            <CardDescription>Tools available to the agent</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-4">
              {tools.length === 0 ? (
                <p className="text-muted-foreground">No tools configured</p>
              ) : (
                tools.map((tool) => (
                  <span
                    key={tool}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm"
                  >
                    {tool}
                    {isEditing && (
                      <button onClick={() => removeTool(tool)} className="hover:text-destructive">
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </span>
                ))
              )}
            </div>
            {isEditing && (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newTool}
                  onChange={(e) => setNewTool(e.target.value)}
                  placeholder="Add a tool..."
                  className="flex-1 px-3 py-2 border rounded-md bg-background"
                  onKeyDown={(e) => e.key === 'Enter' && addTool()}
                />
                <Button onClick={addTool}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
