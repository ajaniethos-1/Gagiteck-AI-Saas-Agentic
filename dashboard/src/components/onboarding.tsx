import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { Bot, Workflow, Zap, CheckCircle2, ArrowRight, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface OnboardingStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  action: string
  href: string
  completed: boolean
}

export function Onboarding() {
  const router = useRouter()
  const [isVisible, setIsVisible] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [dismissed, setDismissed] = useState(false)

  const [steps, setSteps] = useState<OnboardingStep[]>([
    {
      id: 'create-agent',
      title: 'Create Your First Agent',
      description: 'Build an AI agent with custom instructions and tools to automate tasks.',
      icon: <Bot className="h-8 w-8 text-blue-500" />,
      action: 'Create Agent',
      href: '/agents',
      completed: false,
    },
    {
      id: 'create-workflow',
      title: 'Build a Workflow',
      description: 'Chain multiple agents and actions together to create powerful automations.',
      icon: <Workflow className="h-8 w-8 text-purple-500" />,
      action: 'Create Workflow',
      href: '/workflows',
      completed: false,
    },
    {
      id: 'run-execution',
      title: 'Run Your First Execution',
      description: 'Execute your agent or workflow and monitor the results in real-time.',
      icon: <Zap className="h-8 w-8 text-green-500" />,
      action: 'View Executions',
      href: '/executions',
      completed: false,
    },
  ])

  // Check if onboarding should be shown
  useEffect(() => {
    const onboardingDismissed = localStorage.getItem('onboarding-dismissed')
    const onboardingCompleted = localStorage.getItem('onboarding-completed')

    if (onboardingDismissed === 'true' || onboardingCompleted === 'true') {
      setDismissed(true)
      return
    }

    // Show onboarding after a short delay
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  // Load completed steps from localStorage
  useEffect(() => {
    const savedSteps = localStorage.getItem('onboarding-steps')
    if (savedSteps) {
      try {
        const parsed = JSON.parse(savedSteps)
        setSteps(prev => prev.map(step => ({
          ...step,
          completed: parsed[step.id] || false,
        })))
      } catch (e) {
        // Ignore parse errors
      }
    }
  }, [])

  const handleStepAction = (step: OnboardingStep) => {
    // Mark step as completed
    const updatedSteps = steps.map(s =>
      s.id === step.id ? { ...s, completed: true } : s
    )
    setSteps(updatedSteps)

    // Save to localStorage
    const completedMap = updatedSteps.reduce((acc, s) => ({
      ...acc,
      [s.id]: s.completed,
    }), {})
    localStorage.setItem('onboarding-steps', JSON.stringify(completedMap))

    // Check if all steps are completed
    if (updatedSteps.every(s => s.completed)) {
      localStorage.setItem('onboarding-completed', 'true')
    }

    // Navigate to the step's page
    router.push(step.href)
    setIsVisible(false)
  }

  const handleDismiss = () => {
    localStorage.setItem('onboarding-dismissed', 'true')
    setDismissed(true)
    setIsVisible(false)
  }

  const handleSkip = () => {
    setIsVisible(false)
  }

  const completedCount = steps.filter(s => s.completed).length
  const progress = (completedCount / steps.length) * 100

  if (dismissed || !isVisible) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={handleSkip} />

      {/* Modal */}
      <div className="relative w-full max-w-lg bg-background rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="relative p-6 pb-0">
          <button
            onClick={handleDismiss}
            className="absolute top-4 right-4 text-muted-foreground hover:text-foreground"
          >
            <X className="h-5 w-5" />
          </button>

          <h2 className="text-2xl font-bold mb-2">Welcome to Gagiteck!</h2>
          <p className="text-muted-foreground">
            Let's get you started with a quick setup guide.
          </p>

          {/* Progress bar */}
          <div className="mt-4 h-2 bg-muted rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            {completedCount} of {steps.length} steps completed
          </p>
        </div>

        {/* Steps */}
        <div className="p-6 space-y-4">
          {steps.map((step, index) => (
            <div
              key={step.id}
              className={`relative p-4 rounded-xl border-2 transition-all ${
                step.completed
                  ? 'border-green-500 bg-green-50 dark:bg-green-950'
                  : index === currentStep
                  ? 'border-primary bg-primary/5'
                  : 'border-muted hover:border-muted-foreground/50'
              }`}
              onClick={() => !step.completed && setCurrentStep(index)}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  {step.completed ? (
                    <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center">
                      <CheckCircle2 className="h-5 w-5 text-white" />
                    </div>
                  ) : (
                    step.icon
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className={`font-semibold ${step.completed ? 'text-green-700 dark:text-green-300' : ''}`}>
                    {step.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {step.description}
                  </p>
                  {!step.completed && index === currentStep && (
                    <Button
                      size="sm"
                      className="mt-3"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleStepAction(step)
                      }}
                    >
                      {step.action}
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-6 pt-0 flex items-center justify-between">
          <button
            onClick={handleDismiss}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Don't show again
          </button>
          <Button variant="outline" onClick={handleSkip}>
            I'll explore on my own
          </Button>
        </div>
      </div>
    </div>
  )
}

// Compact onboarding checklist for dashboard
export function OnboardingChecklist() {
  const router = useRouter()
  const [isVisible, setIsVisible] = useState(false)
  const [steps, setSteps] = useState([
    { id: 'create-agent', title: 'Create an agent', href: '/agents', completed: false },
    { id: 'create-workflow', title: 'Build a workflow', href: '/workflows', completed: false },
    { id: 'run-execution', title: 'Run an execution', href: '/executions', completed: false },
  ])

  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('onboarding-completed')
    const checklistDismissed = localStorage.getItem('onboarding-checklist-dismissed')

    if (onboardingCompleted === 'true' || checklistDismissed === 'true') {
      return
    }

    const savedSteps = localStorage.getItem('onboarding-steps')
    if (savedSteps) {
      try {
        const parsed = JSON.parse(savedSteps)
        setSteps(prev => prev.map(step => ({
          ...step,
          completed: parsed[step.id] || false,
        })))
      } catch (e) {
        // Ignore parse errors
      }
    }

    setIsVisible(true)
  }, [])

  const handleDismiss = () => {
    localStorage.setItem('onboarding-checklist-dismissed', 'true')
    setIsVisible(false)
  }

  const completedCount = steps.filter(s => s.completed).length

  if (!isVisible || completedCount === steps.length) return null

  return (
    <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">Getting Started</h3>
        <button onClick={handleDismiss} className="text-muted-foreground hover:text-foreground">
          <X className="h-4 w-4" />
        </button>
      </div>
      <div className="space-y-2">
        {steps.map((step) => (
          <button
            key={step.id}
            onClick={() => router.push(step.href)}
            className={`flex items-center gap-3 w-full text-left p-2 rounded-lg transition-colors ${
              step.completed
                ? 'text-green-600 dark:text-green-400'
                : 'text-foreground hover:bg-muted'
            }`}
          >
            <div className={`h-5 w-5 rounded-full border-2 flex items-center justify-center ${
              step.completed
                ? 'border-green-500 bg-green-500'
                : 'border-muted-foreground'
            }`}>
              {step.completed && <CheckCircle2 className="h-3 w-3 text-white" />}
            </div>
            <span className={step.completed ? 'line-through' : ''}>{step.title}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
