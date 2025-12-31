import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bot, Plus, Play, Settings, Trash2 } from 'lucide-react'

interface Agent {
  id: string
  name: string
  model: string
  status: 'active' | 'inactive'
  executions: number
  lastRun: string
}

export default function AgentsPage() {
  const [agents] = useState<Agent[]>([
    { id: 'agent_1', name: 'Research Assistant', model: 'claude-3-opus', status: 'active', executions: 342, lastRun: '2 min ago' },
    { id: 'agent_2', name: 'Data Processor', model: 'claude-3-sonnet', status: 'active', executions: 528, lastRun: '5 min ago' },
    { id: 'agent_3', name: 'Customer Support', model: 'claude-3-sonnet', status: 'active', executions: 1205, lastRun: '1 min ago' },
    { id: 'agent_4', name: 'Code Reviewer', model: 'claude-3-opus', status: 'inactive', executions: 89, lastRun: '1 hour ago' },
  ])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agents</h1>
          <p className="text-muted-foreground">Manage your AI agents</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Agent
        </Button>
      </div>

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
                  <CardDescription>{agent.model}</CardDescription>
                </div>
              </div>
              <span className={`rounded-full px-2 py-1 text-xs ${
                agent.status === 'active'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700'
              }`}>
                {agent.status}
              </span>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                <span>{agent.executions} executions</span>
                <span>Last run: {agent.lastRun}</span>
              </div>
              <div className="flex gap-2">
                <Button size="sm" className="flex-1">
                  <Play className="mr-1 h-3 w-3" />
                  Run
                </Button>
                <Button size="sm" variant="outline">
                  <Settings className="h-3 w-3" />
                </Button>
                <Button size="sm" variant="outline" className="text-destructive">
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
