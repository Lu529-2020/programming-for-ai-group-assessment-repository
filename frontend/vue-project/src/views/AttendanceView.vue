<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { AttendanceRecord, AttendancePayload } from '@/types'
import { createAttendance, deleteAttendance, fetchAttendance, updateAttendance } from '@/services/api'

const records = ref<AttendanceRecord[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)

const blankForm: AttendancePayload = {
  studentId: 0,
  moduleId: 0,
  weekNumber: 1,
  attendedSessions: 0,
  totalSessions: 0,
}
const form = ref<AttendancePayload>({ ...blankForm })

const attendanceByWeek = computed(() => {
  const grouped: Record<number, { total: number; attended: number }> = {}
  records.value.forEach((r) => {
    if (!grouped[r.weekNumber]) {
      grouped[r.weekNumber] = { total: 0, attended: 0 }
    }
    grouped[r.weekNumber].total += r.totalSessions || 0
    grouped[r.weekNumber].attended += r.attendedSessions || 0
  })
  return Object.entries(grouped).map(([week, data]) => ({
    weekNumber: Number(week),
    attendanceRate: data.total ? Math.round((data.attended / data.total) * 100) : 0,
  }))
})

async function load() {
  loading.value = true
  error.value = null
  try {
    records.value = await fetchAttendance()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function startEdit(record: AttendanceRecord) {
  editingId.value = record.id
  form.value = {
    studentId: record.studentId,
    moduleId: record.moduleId,
    weekNumber: record.weekNumber,
    attendedSessions: record.attendedSessions,
    totalSessions: record.totalSessions,
  }
}

function resetForm() {
  form.value = { ...blankForm }
  editingId.value = null
}

async function handleSubmit() {
  saving.value = true
  notice.value = null
  error.value = null
  try {
    if (editingId.value) {
      const updated = await updateAttendance(editingId.value, form.value)
      records.value = records.value.map((r) => (r.id === updated.id ? updated : r))
      notice.value = 'Attendance updated'
    } else {
      const created = await createAttendance(form.value)
      records.value = [created, ...records.value]
      notice.value = 'Attendance added'
    }
    resetForm()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('Delete this record?')) return
  deletingId.value = id
  error.value = null
  notice.value = null
  try {
    await deleteAttendance(id)
    records.value = records.value.filter((r) => r.id !== id)
    notice.value = 'Record removed'
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
  <div class="stack">
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">FR4</p>
          <h2>Attendance by week</h2>
        </div>
        <div class="pill pill--primary">{{ attendanceByWeek.length }} weeks tracked</div>
      </div>

      <div v-if="loading" class="muted">Loading...</div>
      <div v-else-if="error" class="muted">Error: {{ error }}</div>
      <div v-else class="trend">
        <div v-for="week in attendanceByWeek" :key="week.weekNumber" class="trend-row">
          <span class="muted">Week {{ week.weekNumber }}</span>
          <div class="meter">
            <div class="meter-fill" :style="{ width: `${week.attendanceRate}%` }"></div>
          </div>
          <span class="strong">{{ week.attendanceRate }}%</span>
        </div>
      </div>
    </section>

    <section class="panel form-panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">{{ editingId ? 'Editing' : 'Create' }}</p>
          <h3>{{ editingId ? 'Edit attendance' : 'Add attendance' }}</h3>
        </div>
        <button v-if="editingId" class="link" type="button" @click="resetForm">Cancel</button>
      </div>
      <form class="form" @submit.prevent="handleSubmit">
        <label>
          <span>Student ID *</span>
          <input v-model.number="form.studentId" type="number" min="1" required />
        </label>
        <label>
          <span>Module ID *</span>
          <input v-model.number="form.moduleId" type="number" min="1" required />
        </label>
        <label>
          <span>Week *</span>
          <input v-model.number="form.weekNumber" type="number" min="1" required />
        </label>
        <label>
          <span>Attended</span>
          <input v-model.number="form.attendedSessions" type="number" min="0" />
        </label>
        <label>
          <span>Total</span>
          <input v-model.number="form.totalSessions" type="number" min="0" />
        </label>
        <button class="btn btn--primary" type="submit" :disabled="saving">
          {{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Add record' }}
        </button>
      </form>
      <p v-if="notice" class="notice">{{ notice }}</p>
      <p v-if="error" class="error">Error: {{ error }}</p>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">Per student • module</p>
          <h3>Captured records</h3>
        </div>
        <div class="pill pill--accent">{{ records.length }} entries</div>
      </div>
      <div v-if="loading" class="muted">Loading...</div>
      <div v-else-if="error" class="muted">Error: {{ error }}</div>
      <div v-else class="table">
        <div class="table-head">
          <span>Student</span>
          <span>Module</span>
          <span>Week</span>
          <span>Attended</span>
          <span>Total</span>
          <span></span>
        </div>
        <div v-for="record in records" :key="record.id" class="table-row">
          <span>#{{ record.studentId }}</span>
          <span>#{{ record.moduleId }}</span>
          <span>{{ record.weekNumber }}</span>
          <span>{{ record.attendedSessions }}</span>
          <span>{{ record.totalSessions }}</span>
          <span class="actions">
            <button class="link" type="button" @click="startEdit(record)">Edit</button>
            <button
              class="link link--danger"
              type="button"
              :disabled="deletingId === record.id"
              @click="handleDelete(record.id)"
            >
              {{ deletingId === record.id ? 'Removing…' : 'Delete' }}
            </button>
          </span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

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

.form-panel .form {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.form label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.form input {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px 10px;
  background: var(--surface);
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
  margin-top: 8px;
}

.error {
  color: var(--danger, #d22);
  margin-top: 8px;
}

.trend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.trend-row {
  display: grid;
  grid-template-columns: 120px 1fr 80px;
  align-items: center;
  gap: 10px;
}

.meter {
  width: 100%;
  height: 8px;
  background: var(--border);
  border-radius: 999px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, #0ea5e9, #f97316);
}

.table {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
  align-items: center;
}

.table-head {
  color: var(--muted);
  font-size: 13px;
}

.table-row {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface-muted);
}

.actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

@media (max-width: 880px) {
  .table-head,
  .table-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .table-head span:nth-child(n + 4),
  .table-row span:nth-child(n + 4) {
    display: none;
  }
}
</style>
