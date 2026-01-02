import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { User, Key, Bell, Shield, Loader2, Plus, Trash2, Copy, CheckCircle2, AlertCircle } from 'lucide-react'

interface APIKey {
  id: string
  name: string
  key: string
  created_at: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function SettingsPage() {
  const { data: session } = useSession()
  const [activeTab, setActiveTab] = useState('profile')
  const [apiKeys, setApiKeys] = useState<APIKey[]>([])
  const [loadingKeys, setLoadingKeys] = useState(false)
  const [showCreateKey, setShowCreateKey] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string | null>(null)
  const [copiedKey, setCopiedKey] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Profile form state
  const [name, setName] = useState(session?.user?.name || '')
  const [email, setEmail] = useState(session?.user?.email || '')

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [passwordSuccess, setPasswordSuccess] = useState(false)

  // Notification settings
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    executionFailures: true,
    weeklyDigest: false,
  })

  const getAuthHeader = () => {
    const token = (session as any)?.accessToken
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  useEffect(() => {
    if (session?.user) {
      setName(session.user.name || '')
      setEmail(session.user.email || '')
    }
  }, [session])

  // Fetch API keys when tab is selected
  useEffect(() => {
    if (activeTab === 'api-keys' && session) {
      fetchApiKeys()
    }
  }, [activeTab, session])

  const fetchApiKeys = async () => {
    setLoadingKeys(true)
    try {
      const response = await fetch(`${API_URL}/v1/auth/api-keys`, {
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
      })
      if (response.ok) {
        const data = await response.json()
        setApiKeys(data)
      }
    } catch (err) {
      console.error('Failed to fetch API keys:', err)
    } finally {
      setLoadingKeys(false)
    }
  }

  const handleSaveProfile = async () => {
    setSaving(true)
    setError(null)
    try {
      const response = await fetch(`${API_URL}/v1/auth/me`, {
        method: 'PATCH',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      })
      if (response.ok) {
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 3000)
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to update profile')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleCreateApiKey = async () => {
    if (!newKeyName.trim()) return
    setError(null)

    try {
      const response = await fetch(`${API_URL}/v1/auth/api-keys`, {
        method: 'POST',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newKeyName }),
      })
      if (response.ok) {
        const newKey = await response.json()
        setApiKeys([...apiKeys, newKey])
        setNewlyCreatedKey(newKey.key) // Show full key only once
        setNewKeyName('')
      } else {
        const data = await response.json()
        setError(data.detail || 'Failed to create API key')
        setShowCreateKey(false)
      }
    } catch (err) {
      setError('Network error. Please try again.')
      setShowCreateKey(false)
    }
  }

  const handleDeleteApiKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key? This action cannot be undone.')) return

    try {
      const response = await fetch(`${API_URL}/v1/auth/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: getAuthHeader(),
      })
      if (response.ok || response.status === 204) {
        setApiKeys(apiKeys.filter(k => k.id !== keyId))
      }
    } catch (err) {
      console.error('Failed to delete API key:', err)
    }
  }

  const handleCopyKey = (key: string) => {
    navigator.clipboard.writeText(key)
    setCopiedKey(key)
    setTimeout(() => setCopiedKey(null), 2000)
  }

  const handleChangePassword = async () => {
    setPasswordError(null)
    setPasswordSuccess(false)

    if (newPassword !== confirmPassword) {
      setPasswordError('Passwords do not match')
      return
    }
    if (newPassword.length < 8) {
      setPasswordError('Password must be at least 8 characters')
      return
    }

    try {
      const response = await fetch(`${API_URL}/v1/auth/me`, {
        method: 'PATCH',
        headers: { ...getAuthHeader(), 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: newPassword }),
      })
      if (response.ok) {
        setPasswordSuccess(true)
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
        setTimeout(() => setPasswordSuccess(false), 3000)
      } else {
        const data = await response.json()
        setPasswordError(data.detail || 'Failed to update password')
      }
    } catch (err) {
      setPasswordError('Network error. Please try again.')
    }
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'api-keys', label: 'API Keys', icon: Key },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your account and preferences</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-48 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <Card>
              <CardHeader>
                <CardTitle>Profile</CardTitle>
                <CardDescription>Update your personal information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full max-w-md px-3 py-2 border rounded-md bg-background"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Email</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full max-w-md px-3 py-2 border rounded-md bg-background"
                    disabled
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Contact support to change your email address
                  </p>
                </div>
                <div className="flex items-center gap-2 pt-4">
                  <Button onClick={handleSaveProfile} disabled={saving}>
                    {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Save Changes
                  </Button>
                  {saveSuccess && (
                    <span className="flex items-center gap-1 text-sm text-green-600">
                      <CheckCircle2 className="h-4 w-4" />
                      Saved
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'api-keys' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>API Keys</CardTitle>
                    <CardDescription>Manage your API keys for programmatic access</CardDescription>
                  </div>
                  <Button onClick={() => setShowCreateKey(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Key
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {apiKeys.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8">
                    <Key className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium">No API keys</h3>
                    <p className="text-muted-foreground mb-4">Create an API key to access the API programmatically</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {apiKeys.map((apiKey) => (
                      <div
                        key={apiKey.id}
                        className="flex items-center justify-between p-4 rounded-lg border"
                      >
                        <div>
                          <div className="font-medium">{apiKey.name}</div>
                          <div className="flex items-center gap-2 mt-1">
                            <code className="text-sm text-muted-foreground bg-muted px-2 py-0.5 rounded">
                              {apiKey.key.slice(0, 12)}...
                            </code>
                            <button
                              onClick={() => handleCopyKey(apiKey.key)}
                              className="text-muted-foreground hover:text-foreground"
                            >
                              {copiedKey === apiKey.key ? (
                                <CheckCircle2 className="h-4 w-4 text-green-500" />
                              ) : (
                                <Copy className="h-4 w-4" />
                              )}
                            </button>
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Created {new Date(apiKey.created_at).toLocaleDateString()}
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-destructive"
                          onClick={() => handleDeleteApiKey(apiKey.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Create Key Modal */}
                {showCreateKey && (
                  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
                    <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-lg">
                      <h2 className="text-xl font-bold mb-4">Create API Key</h2>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium mb-1">Key Name</label>
                          <input
                            type="text"
                            value={newKeyName}
                            onChange={(e) => setNewKeyName(e.target.value)}
                            className="w-full px-3 py-2 border rounded-md bg-background"
                            placeholder="My API Key"
                          />
                        </div>
                        <div className="flex items-center gap-2 p-3 rounded-lg bg-yellow-50 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200">
                          <AlertCircle className="h-4 w-4 flex-shrink-0" />
                          <p className="text-sm">
                            Make sure to copy your API key - you won't be able to see it again!
                          </p>
                        </div>
                        <div className="flex gap-2 justify-end">
                          <Button variant="outline" onClick={() => setShowCreateKey(false)}>
                            Cancel
                          </Button>
                          <Button onClick={handleCreateApiKey} disabled={!newKeyName.trim()}>
                            Create Key
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {activeTab === 'notifications' && (
            <Card>
              <CardHeader>
                <CardTitle>Notifications</CardTitle>
                <CardDescription>Configure how you receive updates</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b">
                  <div>
                    <div className="font-medium">Email Alerts</div>
                    <div className="text-sm text-muted-foreground">
                      Receive important alerts via email
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.emailAlerts}
                      onChange={(e) => setNotifications({ ...notifications, emailAlerts: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between py-3 border-b">
                  <div>
                    <div className="font-medium">Execution Failures</div>
                    <div className="text-sm text-muted-foreground">
                      Get notified when an execution fails
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.executionFailures}
                      onChange={(e) => setNotifications({ ...notifications, executionFailures: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between py-3">
                  <div>
                    <div className="font-medium">Weekly Digest</div>
                    <div className="text-sm text-muted-foreground">
                      Receive a weekly summary of activity
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notifications.weeklyDigest}
                      onChange={(e) => setNotifications({ ...notifications, weeklyDigest: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                  </label>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'security' && (
            <Card>
              <CardHeader>
                <CardTitle>Security</CardTitle>
                <CardDescription>Manage your account security</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h3 className="font-medium mb-2">Change Password</h3>
                  <div className="space-y-3 max-w-md">
                    {passwordError && (
                      <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-950 rounded-md">
                        {passwordError}
                      </div>
                    )}
                    {passwordSuccess && (
                      <div className="p-3 text-sm text-green-500 bg-green-50 dark:bg-green-950 rounded-md flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4" />
                        Password updated successfully
                      </div>
                    )}
                    <div>
                      <label className="block text-sm font-medium mb-1">Current Password</label>
                      <input
                        type="password"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md bg-background"
                        placeholder="••••••••"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">New Password</label>
                      <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md bg-background"
                        placeholder="••••••••"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Confirm New Password</label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="w-full px-3 py-2 border rounded-md bg-background"
                        placeholder="••••••••"
                      />
                    </div>
                    <Button onClick={handleChangePassword}>Update Password</Button>
                  </div>
                </div>

                <hr />

                <div>
                  <h3 className="font-medium mb-2">Two-Factor Authentication</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    Add an extra layer of security to your account
                  </p>
                  <Button variant="outline">Enable 2FA</Button>
                </div>

                <hr />

                <div>
                  <h3 className="font-medium mb-2 text-destructive">Danger Zone</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    Permanently delete your account and all associated data
                  </p>
                  <Button variant="outline" className="text-destructive border-destructive hover:bg-destructive hover:text-destructive-foreground">
                    Delete Account
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
