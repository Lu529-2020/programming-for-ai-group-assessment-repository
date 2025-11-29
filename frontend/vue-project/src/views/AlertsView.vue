<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { Alert, AlertPayload } from '@/types'
import { createAlert, deleteAlert, fetchAlerts, updateAlert } from '@/services/api'

const alerts = ref<Alert[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)

const blankForm: AlertPayload = {
  studentId: 0,
  moduleId: undefined,
  weekNumber: undefined,
  reason: '',
  severity: 'medium',
  resolved: false,
}
const form = ref<AlertPayload>({ ...blankForm })

const severityColor: Record<string, string> = {
  low: 'pill--primary',
  medium: 'pill--accent',
  high: 'pill--danger',
}

async function load() {
  loading.value = true
  error.value = null
  try {
    alerts.value = await fetchAlerts()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function startEdit(alert: Alert) {
  editingId.value = alert.id
  form.value = {
    studentId: alert.studentId,
    moduleId: alert.moduleId,
    weekNumber: alert.weekNumber,
    reason: alert.reason,
    severity: alert.severity,
    resolved: alert.resolved,
    createdAt: alert.createdAt,
  }
}

function resetForm() {
  editingId.value = null
  form.value = { ...blankForm }
}

async function handleSubmit() {
  saving.value = true
  notice.value = null
  error.value = null
  try {
    if (editingId.value) {
      const updated = await updateAlert(editingId.value, form.value)
      alerts.value = alerts.value.map((a) => (a.id === updated.id ? updated : a))
      notice.value = 'Alert updated'
    } else {
      const created = await createAlert(form.value)
      alerts.value = [created, ...alerts.value]
      notice.value = 'Alert added'
    }
    resetForm()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('Delete this alert?')) return
  deletingId.value = id
  notice.value = null
  error.value = null
  try {
    await deleteAlert(id)
    alerts.value = alerts.value.filter((a) => a.id !== id)
    notice.value = 'Alert removed'
    if (editingId.value === id) resetForm()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    deletingId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">4.2.6 Alerts</p>
        <h2>Early warnings</h2>
      </div>
      <div class="pill pill--primary">{{ alerts.length }} total</div>
    </div>

    <div class="grid">
      <section class="card">
        <div class="card-head">
          <div>
            <p class="eyebrow">{{ editingId ? 'Editing' : 'Create' }}</p>
            <h3>{{ editingId ? 'Edit alert' : 'Add alert' }}</h3>
          </div>
          <button v-if="editingId" class="link" type="button" @click="resetForm">Cancel</button>
        </div>
        <form class="form" @submit.prevent="handleSubmit">
          <label>
            <span>Student ID *</span>
            <input v-model.number="form.studentId" type="number" min="1" required />
          </label>
          <label>
            <span>Module ID</span>
            <input v-model.number="form.moduleId" type="number" min="0" />
          </label>
          <label>
            <span>Week</span>
            <input v-model.number="form.weekNumber" type="number" min="1" />
          </label>
          <label class="full">
            <span>Reason *</span>
            <textarea v-model="form.reason" rows="3" required />
          </label>
          <label>
            <span>Severity</span>
            <select v-model="form.severity">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <label class="inline">
            <input v-model="form.resolved" type="checkbox" />
            <span>Resolved</span>
          </label>
          <button class="btn btn--primary" type="submit" :disabled="saving">
            {{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Add alert' }}
          </button>
        </form>
        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="error">Error: {{ error }}</p>
      </section>

      <section class="card card--list">
        <div v-if="loading" class="muted">Loading...</div>
        <div v-else-if="error" class="muted">Error: {{ error }}</div>
        <div v-else class="list">
          <article v-for="alert in alerts" :key="alert.id" class="row">
            <div>
              <p class="strong">{{ alert.reason }}</p>
              <p class="muted">Student #{{ alert.studentId }} • Module #{{ alert.moduleId ?? 'N/A' }}</p>
              <p class="muted">Week {{ alert.weekNumber ?? '—' }}</p>
            </div>
            <div class="tags">
              <span class="pill" :class="severityColor[alert.severity]">Severity: {{ alert.severity }}</span>
              <span class="pill" :class="alert.resolved ? 'pill--primary' : 'pill--danger'">
                {{ alert.resolved ? 'Resolved' : 'Open' }}
              </span>
              <button class="link" type="button" @click="startEdit(alert)">Edit</button>
              <button
                class="link link--danger"
                type="button"
                :disabled="deletingId === alert.id"
                @click="handleDelete(alert.id)"
              >
                {{ deletingId === alert.id ? 'Removing…' : 'Delete' }}
              </button>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
  box-shadow: var(--shadow);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
}

.card {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  background: var(--surface-muted);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card--list {
  min-height: 220px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.form label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.form input,
.form textarea,
.form select {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px 10px;
  background: var(--surface);
}

.inline {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.full {
  grid-column: 1 / -1;
}

.btn {
  padding: 10px 12px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
}

.btn--primary {
  background: var(--primary);
  color: #fff;
}

.link {
  background: none;
  border: none;
  color: var(--primary);
  cursor: pointer;
  padding: 4px 6px;
}

.link--danger {
  color: var(--danger, #d22);
}

.notice {
  color: var(--success, #0a8f55);
}

.error {
  color: var(--danger, #d22);
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--surface);
  align-items: center;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 780px) {
  .row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
