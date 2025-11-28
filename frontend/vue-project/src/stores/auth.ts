import { defineStore } from 'pinia'

type UserRole = 'wellbeing-officer' | 'course-director'

export interface AuthUser {
  name: string
  email: string
  role: UserRole
  passwordHash: string
}

interface SessionUser {
  name: string
  email: string
  role: UserRole
}

const USERS_KEY = 'wellbeing:auth:users'
const SESSION_KEY = 'wellbeing:auth:session'

const defaultUsers: AuthUser[] = [
  {
    name: 'Wellbeing Officer',
    email: 'wellbeing.officer@uni.edu',
    role: 'wellbeing-officer',
    // sha256("demo-login")
    passwordHash: 'b9770df7c695fa66633a0d603d0b1afbe0e00800a6c1d55a6036e0408cf05864',
  },
  {
    name: 'Course Director',
    email: 'director@uni.edu',
    role: 'course-director',
    // sha256("demo-login")
    passwordHash: 'b9770df7c695fa66633a0d603d0b1afbe0e00800a6c1d55a6036e0408cf05864',
  },
]

function readUsers(): AuthUser[] {
  if (typeof window === 'undefined') return defaultUsers
  try {
    const raw = localStorage.getItem(USERS_KEY)
    if (!raw) return defaultUsers
    const parsed = JSON.parse(raw) as AuthUser[]
    return parsed.length ? parsed : defaultUsers
  } catch {
    return defaultUsers
  }
}

function readSession(): SessionUser | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    return raw ? (JSON.parse(raw) as SessionUser) : null
  } catch {
    return null
  }
}

async function sha256(input: string): Promise<string> {
  const data = new TextEncoder().encode(input)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('')
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    users: readUsers() as AuthUser[],
    currentUser: readSession() as SessionUser | null,
    error: '' as string,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.currentUser),
    role: (state) => state.currentUser?.role ?? null,
  },
  actions: {
    persistUsers() {
      if (typeof window === 'undefined') return
      localStorage.setItem(USERS_KEY, JSON.stringify(this.users))
    },
    persistSession(user: SessionUser | null) {
      if (typeof window === 'undefined') return
      if (user) localStorage.setItem(SESSION_KEY, JSON.stringify(user))
      else localStorage.removeItem(SESSION_KEY)
    },
    async login(email: string, password: string) {
      this.error = ''
      const pwdHash = await sha256(password)
      const user = this.users.find((u) => u.email === email && u.passwordHash === pwdHash)
      if (!user) {
        this.error = 'Invalid credentials'
        throw new Error(this.error)
      }
      const session: SessionUser = { name: user.name, email: user.email, role: user.role }
      this.currentUser = session
      this.persistSession(session)
      return session
    },
    async register(name: string, email: string, password: string, role: UserRole) {
      this.error = ''
      const exists = this.users.some((u) => u.email === email)
      if (exists) {
        this.error = 'Email already registered'
        throw new Error(this.error)
      }
      const passwordHash = await sha256(password)
      const user: AuthUser = { name, email, passwordHash, role }
      this.users = [...this.users, user]
      this.persistUsers()
      const session: SessionUser = { name, email, role }
      this.currentUser = session
      this.persistSession(session)
      return session
    },
    logout() {
      this.currentUser = null
      this.persistSession(null)
    },
    clearError() {
      this.error = ''
    },
  },
})
