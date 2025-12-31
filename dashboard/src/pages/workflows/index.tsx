import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Workflow, Plus, Play, Settings, Trash2 } from 'lucide-react'

interface WorkflowItem {
  id: string
  name: string
  steps: number
  status: 'active' | 'inactive'
  runs: number
  lastRun: string
}

export default function WorkflowsPage() {
  const [workflows] = useState<WorkflowItem[]>([
    { id: 'wf_1', name: 'Customer Onboarding', steps: 4, status: 'active', runs: 156, lastRun: '10 min ago' },
    { id: 'wf_2', name: 'Data Pipeline', steps: 6, status: 'active', runs: 89, lastRun: '1 hour ago' },
    { id: 'wf_3', name: 'Support Ticket Router', steps: 3, status: 'active', runs: 432, lastRun: '2 min ago' },
    { id: 'wf_4', name: 'Weekly Report Generator', steps: 5, status: 'inactive', runs: 52, lastRun: '1 week ago' },
  ])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
          <p className="text-muted-foreground">Automate multi-step processes</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Workflow
        </Button>
      </div>

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
                  <CardDescription>{workflow.steps} steps</CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className={`rounded-full px-2 py-1 text-xs ${
                  workflow.status === 'active'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {workflow.status}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  <span>{workflow.runs} runs</span>
                  <span className="mx-2">•</span>
                  <span>Last run: {workflow.lastRun}</span>
                </div>
                <div className="flex gap-2">
                  <Button size="sm">
                    <Play className="mr-1 h-3 w-3" />
                    Trigger
                  </Button>
                  <Button size="sm" variant="outline">
                    <Settings className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="outline" className="text-destructive">
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
