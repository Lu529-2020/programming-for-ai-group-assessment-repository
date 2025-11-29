<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const form = ref({
  name: '',
  email: '',
  password: '',
  role: 'wellbeing-officer',
})

const isSubmitting = ref(false)
const error = ref('')

const roles = [
  { value: 'wellbeing-officer', label: 'Student Wellbeing Officer' },
  { value: 'course-director', label: 'Course Director' },
]

async function handleSubmit() {
  error.value = ''
  if (!form.value.email || !form.value.password || !form.value.name) {
    error.value = 'Please fill all fields'
    return
  }
  isSubmitting.value = true
  try {
    await auth.register(form.value.name, form.value.email, form.value.password, form.value.role as any)
    router.push('/dashboard')
  } catch (e) {
    error.value = (e as Error).message || 'Registration failed'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="panel form-panel">
      <div class="form-head">
        <div>
          <p class="eyebrow">Create access</p>
          <h2>Register an account</h2>
          <p class="muted">Pick a role and the workspace will filter data accordingly.</p>
        </div>
        <div class="pill pill--primary">Access • Registration</div>
      </div>

      <form class="form" @submit.prevent="handleSubmit">
        <label class="field">
          <span>Full name</span>
          <input v-model="form.name" type="text" placeholder="Your name" />
        </label>
        <label class="field">
          <span>Email</span>
          <input v-model="form.email" type="email" placeholder="you@university.edu" autocomplete="username" />
        </label>
        <label class="field">
          <span>Password</span>
          <input v-model="form.password" type="password" placeholder="••••••••" autocomplete="new-password" />
        </label>
        <label class="field">
          <span>Role</span>
          <select v-model="form.role">
            <option v-for="r in roles" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
        </label>
        <button class="primary full" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Creating...' : 'Register & enter' }}
        </button>
        <p class="muted tiny">
          Already have an account?
          <RouterLink class="link" to="/login">Go to login</RouterLink>
        </p>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>

    <div class="panel hero">
      <p class="badge">Role-based access</p>
      <h1>Course data or wellbeing insights — you decide.</h1>
      <p class="lede">
        After sign-up, views adapt to your role:
        <strong>Wellbeing Officer</strong> focuses stress/mood/alerts;
        <strong>Course Director</strong> focuses modules, attendance, grades, submissions.
      </p>
      <div class="hero-grid">
        <div class="hero-card">
          <p class="label">Privacy first</p>
          <p class="stat">Hashed</p>
          <p class="muted">Passwords are hashed in-browser, never stored plain</p>
        </div>
        <div class="hero-card">
          <p class="label">Targeted views</p>
          <p class="stat">2 roles</p>
          <p class="muted">Fields and modules filtered by role</p>
        </div>
        <div class="hero-card">
          <p class="label">Faster onboarding</p>
          <p class="stat">1 step</p>
          <p class="muted">Enter the dashboard right after sign-up</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 26px;
  padding: 40px;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 26px;
  box-shadow: var(--shadow);
}

.form-panel {
  display: grid;
  gap: 16px;
}

.form-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.form {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
  font-weight: 600;
}

.field input,
.field select {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.primary.full {
  width: 100%;
  justify-content: center;
}

.error {
  color: var(--danger);
  font-weight: 600;
}

.hero {
  display: grid;
  gap: 14px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.08), rgba(249, 115, 22, 0.08));
}

.badge {
  display: inline-flex;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.12);
  color: #075985;
  font-weight: 700;
}

.hero-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.hero-card {
  padding: 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.label {
  color: var(--muted);
  font-size: 13px;
}

.stat {
  font-size: 26px;
  font-weight: 800;
}

@media (max-width: 1024px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
