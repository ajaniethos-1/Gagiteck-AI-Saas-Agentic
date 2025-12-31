import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bot, Workflow, Zap, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const [stats] = useState({
    agents: 12,
    workflows: 8,
    executions: 1247,
    successRate: 98.5,
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to the Gagiteck AI Platform
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.agents}</div>
            <p className="text-xs text-muted-foreground">+2 from last week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
            <Workflow className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.workflows}</div>
            <p className="text-xs text-muted-foreground">+1 from last week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Executions</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.executions.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">+180 from yesterday</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.successRate}%</div>
            <p className="text-xs text-muted-foreground">+0.5% from last week</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to get started</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Button>
            <Bot className="mr-2 h-4 w-4" />
            Create Agent
          </Button>
          <Button variant="outline">
            <Workflow className="mr-2 h-4 w-4" />
            New Workflow
          </Button>
          <Button variant="outline">
            <Zap className="mr-2 h-4 w-4" />
            Run Agent
          </Button>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest agent executions and workflow runs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { agent: 'Research Assistant', status: 'completed', time: '2 min ago' },
              { agent: 'Data Processor', status: 'completed', time: '5 min ago' },
              { agent: 'Customer Support', status: 'running', time: '8 min ago' },
              { agent: 'Code Reviewer', status: 'completed', time: '15 min ago' },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between border-b pb-2 last:border-0">
                <div className="flex items-center gap-3">
                  <Bot className="h-5 w-5 text-primary" />
                  <span className="font-medium">{item.agent}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-sm ${
                    item.status === 'completed' ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {item.status}
                  </span>
                  <span className="text-sm text-muted-foreground">{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
