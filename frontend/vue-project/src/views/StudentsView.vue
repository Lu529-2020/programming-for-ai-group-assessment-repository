<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { Student, StudentPayload } from '@/types'
import { createStudent, deleteStudent, fetchStudents, updateStudent } from '@/services/api'

const students = ref<Student[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)
const editingId = ref<number | null>(null)

const blankForm: StudentPayload = {
  studentNumber: '',
  fullName: '',
  courseName: '',
  yearOfStudy: 1,
  email: '',
}
const form = ref<StudentPayload>({ ...blankForm })

const riskCopy: Record<string, string> = {
  low: 'Stable',
  medium: 'Monitor',
  high: 'At risk',
}

const formTitle = computed(() => (editingId.value ? 'Edit student' : 'Add student'))
const submitLabel = computed(() => (editingId.value ? 'Save changes' : 'Add student'))

function resetForm() {
  form.value = { ...blankForm }
  editingId.value = null
}

async function loadStudents() {
  loading.value = true
  error.value = null
  try {
    students.value = await fetchStudents()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function startEdit(student: Student) {
  editingId.value = student.id
  form.value = {
    studentNumber: student.studentNumber,
    fullName: student.fullName,
    courseName: student.courseName,
    yearOfStudy: student.yearOfStudy,
    email: student.email ?? '',
  }
  notice.value = null
  error.value = null
}

async function handleSubmit() {
  saving.value = true
  notice.value = null
  error.value = null
  try {
    if (editingId.value) {
      const updated = await updateStudent(editingId.value, form.value)
      students.value = students.value.map((s) => (s.id === updated.id ? updated : s))
      notice.value = 'Student updated'
    } else {
      const created = await createStudent(form.value)
      students.value = [created, ...students.value]
      notice.value = 'Student added'
    }
    resetForm()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('Delete this student?')) return
  deletingId.value = id
  error.value = null
  notice.value = null
  try {
    await deleteStudent(id)
    students.value = students.value.filter((s) => s.id !== id)
    notice.value = 'Student removed'
    if (editingId.value === id) {
      resetForm()
    }
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    deletingId.value = null
  }
}

onMounted(loadStudents)
</script>

<template>
  <div class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">FR2</p>
        <h2>Students</h2>
        <p class="muted">Basic profile plus current risk sentiment.</p>
      </div>
      <div class="pill pill--primary">{{ students.length }} records</div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="card-head">
          <div>
            <p class="eyebrow">{{ editingId ? 'Editing' : 'Create' }}</p>
            <h3>{{ formTitle }}</h3>
          </div>
          <button v-if="editingId" class="link" type="button" @click="resetForm">Cancel</button>
        </div>
        <form class="form" @submit.prevent="handleSubmit">
          <label>
            <span>Full name *</span>
            <input v-model="form.fullName" type="text" required placeholder="Student name" />
          </label>
          <label>
            <span>Student number *</span>
            <input v-model="form.studentNumber" type="text" required placeholder="e.g. S0001" />
          </label>
          <label>
            <span>Course</span>
            <input v-model="form.courseName" type="text" placeholder="Programme" />
          </label>
          <label>
            <span>Year</span>
            <input v-model.number="form.yearOfStudy" type="number" min="1" max="5" />
          </label>
          <label>
            <span>Email</span>
            <input v-model="form.email" type="email" placeholder="student@example.com" />
          </label>
          <button class="btn btn--primary" type="submit" :disabled="saving">
            {{ saving ? 'Saving…' : submitLabel }}
          </button>
        </form>
        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="error">Error: {{ error }}</p>
      </div>

      <div class="card card--list">
        <div v-if="loading" class="muted">Loading...</div>
        <div v-else-if="error" class="muted">Error: {{ error }}</div>
        <div v-else class="table">
          <div class="table-head">
            <span>Name</span>
            <span>Student #</span>
            <span>Course</span>
            <span>Year</span>
            <span>Risk</span>
            <span></span>
          </div>
          <div v-for="student in students" :key="student.id" class="table-row">
            <span class="strong">{{ student.fullName }}</span>
            <span>{{ student.studentNumber }}</span>
            <span>{{ student.courseName }}</span>
            <span>Year {{ student.yearOfStudy }}</span>
            <span>
              <span class="pill" :class="`pill--${student.riskLevel === 'high' ? 'danger' : 'accent'}`">
                {{ riskCopy[student.riskLevel] }}
              </span>
            </span>
            <span class="actions">
              <button class="link" type="button" @click="startEdit(student)">Edit</button>
              <button
                class="link link--danger"
                type="button"
                :disabled="deletingId === student.id"
                @click="handleDelete(student.id)"
              >
                {{ deletingId === student.id ? 'Removing…' : 'Delete' }}
              </button>
            </span>
          </div>
        </div>
      </div>
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
}

.card--list {
  min-height: 300px;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.form {
  display: grid;
  gap: 10px;
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

@media (max-width: 1100px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .card--list {
    order: -1;
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

  .actions {
    justify-content: flex-start;
  }
}
</style>
