<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()

const navItems = [
  { label: 'Dashboard', to: '/dashboard', icon: 'dashboard' },
  { label: 'Students', to: '/students', icon: 'users' },
  { label: 'Modules', to: '/modules', icon: 'modules' },
  { label: 'Attendance', to: '/attendance', icon: 'attendance' },
  { label: 'Submissions', to: '/submissions', icon: 'submissions' },
  { label: 'Surveys', to: '/surveys', icon: 'surveys' },
  { label: 'Analytics', to: '/analytics', icon: 'analytics' },
  { label: 'Alerts', to: '/alerts', icon: 'alerts' },
]

const activePath = computed(() => route.path)
const isAuthLayout = computed(() => route.meta?.layout === 'auth')
</script>

<template>
  <div v-if="isAuthLayout" class="auth-shell">
    <RouterView />
  </div>
  <div v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <div class="brand-icon">SW</div>
        <div>
          <p class="brand-title">Student Wellbeing</p>
          <p class="brand-subtitle">Analytics prototype</p>
        </div>
      </div>

      <nav class="nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="nav-link"
          :class="{ active: activePath === item.to }"
        >
          <span class="icon" :data-icon="item.icon"></span>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <p class="muted">Last sync</p>
        <p class="strong">2m ago • Demo data</p>
      </div>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <p class="eyebrow">Prototype sprint</p>
          <h1>Wellbeing Analytics</h1>
          <p class="muted">Attendance, submissions, wellbeing pulse, and alerts in one place.</p>
        </div>
        <div class="top-actions">
          <button class="ghost">Share</button>
          <button class="primary">New alert</button>
        </div>
      </header>

      <section class="view">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<style scoped>
.auth-shell {
  min-height: 100vh;
}

.app-shell {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  gap: 22px;
  padding: 22px;
}

.sidebar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow);
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(249, 115, 22, 0.1));
}

.brand-icon {
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: #0ea5e9;
  color: #ffffff;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.brand-title {
  font-weight: 700;
  color: var(--ink);
}

.brand-subtitle {
  color: var(--muted);
  font-size: 13px;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  color: var(--muted);
  border: 1px solid transparent;
  transition: all 0.2s ease;
}

.nav-link:hover {
  border-color: var(--border);
  color: var(--ink);
}

.nav-link.active {
  background: rgba(14, 165, 233, 0.12);
  color: #075985;
  border-color: rgba(14, 165, 233, 0.18);
  font-weight: 600;
}

.icon {
  width: 16px;
  height: 16px;
  display: inline-flex;
  border-radius: 6px;
  background: var(--surface-muted);
  position: relative;
}

.icon::after {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 4px;
  background: var(--border);
}

.sidebar-footer {
  padding: 12px;
  border-radius: 14px;
  background: var(--surface-muted);
  border: 1px dashed var(--border);
}

.muted {
  color: var(--muted);
  font-size: 13px;
}

.strong {
  font-weight: 600;
}

.main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.topbar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 20px;
  box-shadow: var(--shadow);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  color: #075985;
  font-weight: 600;
}

.topbar h1 {
  font-size: 26px;
  margin-top: 4px;
}

.top-actions {
  display: flex;
  gap: 10px;
}

.ghost,
.primary {
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 10px 14px;
  font-weight: 600;
  cursor: pointer;
  background: var(--surface);
  color: var(--ink);
}

.ghost:hover {
  border-color: var(--ink);
}

.primary {
  background: linear-gradient(135deg, #0ea5e9, #0ea5e9 40%, #f97316);
  color: #ffffff;
  border: none;
}

.view {
  flex: 1;
}

@media (max-width: 1100px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .nav {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
