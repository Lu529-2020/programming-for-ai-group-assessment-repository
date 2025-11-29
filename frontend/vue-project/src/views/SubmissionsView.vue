<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { SubmissionRecord, SubmissionPayload } from '@/types'
import {
  createSubmission,
  deleteSubmission,
  fetchSubmissions,
  updateSubmission,
} from '@/services/api'

const records = ref<SubmissionRecord[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)

const blankForm: SubmissionPayload = {
  studentId: 0,
  moduleId: 0,
  assessmentName: '',
  dueDate: '',
  submittedDate: '',
  isSubmitted: false,
  isLate: false,
}
const form = ref<SubmissionPayload>({ ...blankForm })

async function load() {
  loading.value = true
  error.value = null
  try {
    records.value = await fetchSubmissions()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function startEdit(record: SubmissionRecord) {
  editingId.value = record.id
  form.value = {
    studentId: record.studentId,
    moduleId: record.moduleId,
    assessmentName: record.assessmentName,
    dueDate: record.dueDate,
    submittedDate: record.submittedDate,
    isSubmitted: record.isSubmitted,
    isLate: record.isLate,
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
      const updated = await updateSubmission(editingId.value, form.value)
      records.value = records.value.map((r) => (r.id === updated.id ? updated : r))
      notice.value = 'Submission updated'
    } else {
      const created = await createSubmission(form.value)
      records.value = [created, ...records.value]
      notice.value = 'Submission added'
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
    await deleteSubmission(id)
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
  <div class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">4.2.4 Submissions</p>
        <h2>Coursework submissions</h2>
      </div>
      <div class="pill pill--primary">{{ records.length }} records</div>
    </div>

    <div class="grid">
      <section class="card">
        <div class="card-head">
          <div>
            <p class="eyebrow">{{ editingId ? 'Editing' : 'Create' }}</p>
            <h3>{{ editingId ? 'Edit submission' : 'Add submission' }}</h3>
          </div>
          <button v-if="editingId" class="link" type="button" @click="resetForm">Cancel</button>
        </div>
        <form class="form" @submit.prevent="handleSubmit">
          <label>
            <span>Assessment *</span>
            <input v-model="form.assessmentName" type="text" required />
          </label>
          <label>
            <span>Student ID *</span>
            <input v-model.number="form.studentId" type="number" min="1" required />
          </label>
          <label>
            <span>Module ID *</span>
            <input v-model.number="form.moduleId" type="number" min="1" required />
          </label>
          <label>
            <span>Due date</span>
            <input v-model="form.dueDate" type="date" />
          </label>
          <label>
            <span>Submitted date</span>
            <input v-model="form.submittedDate" type="date" />
          </label>
          <label class="inline">
            <input v-model="form.isSubmitted" type="checkbox" />
            <span>Submitted</span>
          </label>
          <label class="inline">
            <input v-model="form.isLate" type="checkbox" />
            <span>Late</span>
          </label>
          <button class="btn btn--primary" type="submit" :disabled="saving">
            {{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Add record' }}
          </button>
        </form>
        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="error">Error: {{ error }}</p>
      </section>

      <section class="card card--list">
        <div v-if="loading" class="muted">Loading...</div>
        <div v-else-if="error" class="muted">Error: {{ error }}</div>
        <div v-else class="table">
          <div class="table-head">
            <span>Assessment</span>
            <span>Student</span>
            <span>Module</span>
            <span>Due</span>
            <span>Status</span>
            <span></span>
          </div>
          <div v-for="record in records" :key="record.id" class="table-row">
            <span class="strong">{{ record.assessmentName }}</span>
            <span>#{{ record.studentId }}</span>
            <span>#{{ record.moduleId }}</span>
            <span>{{ record.dueDate || '—' }}</span>
            <span>
              <span
                class="pill"
                :class="record.isSubmitted ? (record.isLate ? 'pill--danger' : 'pill--primary') : 'pill--accent'"
              >
                {{ record.isSubmitted ? (record.isLate ? 'Late' : 'Submitted') : 'Not submitted' }}
              </span>
            </span>
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
  grid-template-columns: 340px 1fr;
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
  min-height: 240px;
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

.form input[type='text'],
.form input[type='number'],
.form input[type='date'] {
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
  background: var(--surface);
}

.actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }
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
