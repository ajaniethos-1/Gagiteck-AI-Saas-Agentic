import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bot, Plus, Play, Settings, Trash2, Loader2, RefreshCw, AlertCircle } from 'lucide-react'
import { api, Agent, ApiError } from '@/lib/api'

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [runningAgent, setRunningAgent] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  const fetchAgents = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.agents.list()
      setAgents(result.data)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('Failed to fetch agents')
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAgents()
  }, [])

  const handleRunAgent = async (agentId: string) => {
    try {
      setRunningAgent(agentId)
      await api.agents.run(agentId, { message: 'Hello, agent!' })
      // Optionally show success message or redirect to execution
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    } finally {
      setRunningAgent(null)
    }
  }

  const handleDeleteAgent = async (agentId: string) => {
    if (!confirm('Are you sure you want to delete this agent?')) return

    try {
      await api.agents.delete(agentId)
      setAgents(agents.filter(a => a.id !== agentId))
    } catch (err) {
      if (err instanceof ApiError) {
        alert(`Error: ${err.message}`)
      }
    }
  }

  const handleCreateAgent = async (name: string, systemPrompt: string) => {
    try {
      const newAgent = await api.agents.create({
        name,
        system_prompt: systemPrompt,
      })
      setAgents([...agents, newAgent])
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
          <h1 className="text-3xl font-bold tracking-tight">Agents</h1>
          <p className="text-muted-foreground">Manage your AI agents</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchAgents}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button onClick={() => setShowCreateModal(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Create Agent
          </Button>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 p-4 text-red-600 bg-red-50 rounded-lg">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
          <Button variant="ghost" size="sm" onClick={fetchAgents}>
            Retry
          </Button>
        </div>
      )}

      {agents.length === 0 && !error ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Bot className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No agents yet</h3>
            <p className="text-muted-foreground mb-4">Create your first AI agent to get started</p>
            <Button onClick={() => setShowCreateModal(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Agent
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <Card key={agent.id}>
              <CardHeader className="flex flex-row items-start justify-between space-y-0">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-primary/10 p-2">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <CardDescription>{agent.config.model}</CardDescription>
                  </div>
                </div>
                <span className={`rounded-full px-2 py-1 text-xs ${
                  agent.status === 'active'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                }`}>
                  {agent.status}
                </span>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground mb-4 line-clamp-2">
                  {agent.system_prompt || 'No system prompt configured'}
                </div>
                <div className="text-xs text-muted-foreground mb-4">
                  {agent.tools.length} tools configured
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    className="flex-1"
                    onClick={() => handleRunAgent(agent.id)}
                    disabled={runningAgent === agent.id}
                  >
                    {runningAgent === agent.id ? (
                      <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                    ) : (
                      <Play className="mr-1 h-3 w-3" />
                    )}
                    Run
                  </Button>
                  <Button size="sm" variant="outline">
                    <Settings className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-destructive"
                    onClick={() => handleDeleteAgent(agent.id)}
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Agent Modal */}
      {showCreateModal && (
        <CreateAgentModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateAgent}
        />
      )}
    </div>
  )
}

function CreateAgentModal({
  onClose,
  onCreate,
}: {
  onClose: () => void
  onCreate: (name: string, systemPrompt: string) => void
}) {
  const [name, setName] = useState('')
  const [systemPrompt, setSystemPrompt] = useState('')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-lg">
        <h2 className="text-xl font-bold mb-4">Create New Agent</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border rounded-md bg-background"
              placeholder="My Agent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">System Prompt</label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              className="w-full px-3 py-2 border rounded-md bg-background h-32"
              placeholder="You are a helpful assistant..."
            />
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={() => onCreate(name, systemPrompt)} disabled={!name}>
              Create
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
