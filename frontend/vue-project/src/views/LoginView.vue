<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = ref({
  email: 'wellbeing.officer@uni.edu',
  password: 'demo-login',
  remember: true,
})

const error = ref('')
const isSubmitting = ref(false)

const shortcuts = [
  { role: 'Wellbeing officer', email: 'wellbeing.officer@uni.edu', password: 'demo-login' },
  { role: 'Course director', email: 'director@uni.edu', password: 'demo-login' },
  { role: 'Tutor', email: 'tutor@uni.edu', password: 'demo-login' },
]

function applyShortcut(preset: (typeof shortcuts)[number]) {
  form.value.email = preset.email
  form.value.password = preset.password
}

async function handleSubmit() {
  if (!form.value.email || !form.value.password) {
    error.value = '请输入邮箱和密码'
    return
  }
  error.value = ''
  isSubmitting.value = true
  // Mock authentication for prototype
  await new Promise((resolve) => setTimeout(resolve, 650))
  isSubmitting.value = false
  router.push('/dashboard')
}
</script>

<template>
  <div class="login-page">
    <div class="glow glow-one"></div>
    <div class="glow glow-two"></div>
    <div class="panel hero">
      <div class="badge">Student Wellbeing Platform</div>
      <h1>
        Wellbeing, attendance,
        <span>and early alerts</span>
        in one pane.
      </h1>
      <p class="lede">
        Log in to monitor attendance, surface students with consecutive absences, and launch
        outreach before stress turns into risk. Designed for wellbeing officers and course teams.
      </p>
      <div class="hero-grid">
        <div class="hero-card">
          <p class="label">Live watchlist</p>
          <p class="stat">6 students</p>
          <p class="muted">flagged for 2+ consecutive absences</p>
        </div>
        <div class="hero-card">
          <p class="label">Early warning</p>
          <p class="stat">84%</p>
          <p class="muted">interventions before week 4</p>
        </div>
        <div class="hero-card">
          <p class="label">Engagement</p>
          <p class="stat">92%</p>
          <p class="muted">average attendance (current sprint)</p>
        </div>
      </div>
    </div>

    <div class="panel form-panel">
      <div class="form-head">
        <div>
          <p class="eyebrow">Secure access</p>
          <h2>Sign in to wellbeing workspace</h2>
          <p class="muted">Use your role-based demo account to explore the prototype.</p>
        </div>
        <div class="pill pill--accent">FR0 • Authentication</div>
      </div>

      <form class="form" @submit.prevent="handleSubmit">
        <label class="field">
          <span>Email</span>
          <input v-model="form.email" type="email" placeholder="you@university.edu" autocomplete="username" />
        </label>
        <label class="field">
          <span>Password</span>
          <input
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
          />
        </label>

        <div class="actions">
          <label class="remember">
            <input v-model="form.remember" type="checkbox" />
            <span>保持登录状态</span>
          </label>
          <a class="link" href="#">Forgot access?</a>
        </div>

        <button class="primary full" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Signing in...' : 'Enter workspace' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>

      <div class="shortcuts">
        <p class="label">Quick demo personas</p>
        <div class="chip-row">
          <button v-for="shortcut in shortcuts" :key="shortcut.role" class="chip" @click="applyShortcut(shortcut)">
            <span class="dot"></span>
            {{ shortcut.role }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 26px;
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.glow {
  position: absolute;
  filter: blur(80px);
  opacity: 0.35;
  z-index: 0;
}

.glow-one {
  width: 360px;
  height: 360px;
  background: #0ea5e9;
  top: -120px;
  left: -80px;
}

.glow-two {
  width: 380px;
  height: 380px;
  background: #f97316;
  bottom: -160px;
  right: -120px;
}

.panel {
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(226, 232, 240, 0.8);
  border-radius: 24px;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12);
  backdrop-filter: blur(10px);
}

.hero {
  padding: 32px;
  display: grid;
  gap: 18px;
  align-content: start;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.12);
  color: #075985;
  font-weight: 600;
  width: fit-content;
}

h1 {
  font-size: 32px;
  line-height: 1.2;
  color: var(--ink);
}

h1 span {
  color: #0ea5e9;
}

.lede {
  color: var(--muted);
  max-width: 620px;
}

.hero-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.hero-card {
  padding: 14px;
  border-radius: 16px;
  background: linear-gradient(150deg, rgba(14, 165, 233, 0.08), rgba(249, 115, 22, 0.08));
  border: 1px solid rgba(226, 232, 240, 0.8);
}

.label {
  color: var(--muted);
  font-size: 13px;
  letter-spacing: 0.02em;
}

.stat {
  font-size: 26px;
  font-weight: 700;
  margin-top: 4px;
  color: var(--ink);
}

.form-panel {
  padding: 26px;
  display: grid;
  gap: 16px;
}

.form-head {
  display: flex;
  align-items: flex-start;
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
  color: var(--ink);
}

.field input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.field input:focus {
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.18);
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.remember {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
}

.link {
  color: #0ea5e9;
  font-weight: 600;
}

.primary.full {
  width: 100%;
  justify-content: center;
}

.error {
  color: var(--danger);
  font-weight: 600;
}

.shortcuts {
  border-top: 1px dashed var(--border);
  padding-top: 14px;
  display: grid;
  gap: 8px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 12px;
  background: var(--surface-muted);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
}

.chip:hover {
  border-color: #0ea5e9;
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.16);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #0ea5e9;
}

@media (max-width: 1080px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 24px;
  }

  .hero {
    order: 2;
  }

  .form-panel {
    order: 1;
  }
}
</style>
