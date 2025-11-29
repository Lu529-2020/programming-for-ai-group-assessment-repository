<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import type { Student, StudentPayload } from '@/types'
import { createStudent, deleteStudent, fetchStudents, updateStudent } from '@/services/api'
import { useDemoDataStore } from '@/stores/demoData'
import { useAuthStore } from '@/stores/auth'

const students = ref<Student[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)
const editingId = ref<number | null>(null)
const selectedId = ref<number | null>(null)

const demoStore = useDemoDataStore()
const auth = useAuthStore()
const { enrolments, modules, attendanceRecords, submissionRecords, surveyResponses, grades, alerts } =
  storeToRefs(demoStore)

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

const selectedStudent = computed(() => students.value.find((s) => s.id === selectedId.value) || null)
const showWellbeing = computed(() => !auth.role || auth.role === 'wellbeing-officer')
const showAcademic = computed(() => !auth.role || auth.role === 'course-director')

// 4.2: aggregate enrolments with attendance/submission/grade/stress for selected student.
const studentModules = computed(() => {
  if (!selectedStudent.value) return []
  return enrolments.value
    .filter((e) => e.studentId === selectedStudent.value?.id)
    .map((enrol) => {
      const module = modules.value.find((m) => m.id === enrol.moduleId)
      const attendance = attendanceRecords.value.filter(
        (r) => r.studentId === enrol.studentId && r.moduleId === enrol.moduleId,
      )
      const attended = attendance.reduce((sum, r) => sum + r.attendedSessions, 0)
      const total = attendance.reduce((sum, r) => sum + r.totalSessions, 0)
      const attendanceRate = total ? Math.round((attended / total) * 100) : 0
      const submission = submissionRecords.value.filter(
        (s) => s.studentId === enrol.studentId && s.moduleId === enrol.moduleId,
      )
      const submittedCount = submission.filter((s) => s.isSubmitted).length
      const submissionRate = submission.length ? Math.round((submittedCount / submission.length) * 100) : 0
      const moduleGrades = grades.value.filter(
        (g) => g.studentId === enrol.studentId && g.moduleId === enrol.moduleId,
      )
      const avgGrade = moduleGrades.length
        ? Math.round((moduleGrades.reduce((sum, g) => sum + g.grade, 0) / moduleGrades.length) * 10) / 10
        : null
      const stressEntries = surveyResponses.value.filter(
        (s) => s.studentId === enrol.studentId && s.moduleId === enrol.moduleId,
      )
      const avgStress = stressEntries.length
        ? Math.round(
            (stressEntries.reduce((sum, s) => sum + s.stressLevel, 0) / stressEntries.length) * 10,
          ) / 10
        : null
      return { module, attendanceRate, submissionRate, avgGrade, avgStress }
    })
    .filter((item) => item.module)
})

// 4.4.1: stress trend per student for wellbeing officer view.
const studentStressTrend = computed(() => {
  if (!selectedStudent.value) return []
  return surveyResponses.value
    .filter((s) => s.studentId === selectedStudent.value?.id)
    .sort((a, b) => a.weekNumber - b.weekNumber)
})

const studentAttendanceSummary = computed(() => {
  if (!selectedStudent.value) return { absences: 0, attendanceRate: 0 }
  const records = attendanceRecords.value.filter((r) => r.studentId === selectedStudent.value?.id)
  const attended = records.reduce((sum, r) => sum + r.attendedSessions, 0)
  const total = records.reduce((sum, r) => sum + r.totalSessions, 0)
  const absences = Math.max(total - attended, 0)
  const attendanceRate = total ? Math.round((attended / total) * 100) : 0
  return { absences, attendanceRate }
})

const studentSubmissionSummary = computed(() => {
  if (!selectedStudent.value) return { total: 0, submitted: 0, onTime: 0 }
  const records = submissionRecords.value.filter((r) => r.studentId === selectedStudent.value?.id)
  const submitted = records.filter((r) => r.isSubmitted).length
  const onTime = records.filter((r) => r.isSubmitted && !r.isLate).length
  return { total: records.length, submitted, onTime }
})

const studentGradeSummary = computed(() => {
  if (!selectedStudent.value) return { average: null, entries: [] }
  const entries = grades.value.filter((g) => g.studentId === selectedStudent.value?.id)
  const average = entries.length
    ? Math.round((entries.reduce((sum, g) => sum + g.grade, 0) / entries.length) * 10) / 10
    : null
  return { average, entries }
})

const studentAlerts = computed(() => {
  if (!selectedStudent.value) return []
  return alerts.value.filter((a) => a.studentId === selectedStudent.value?.id)
})

function resetForm() {
  form.value = { ...blankForm }
  editingId.value = null
}

async function loadStudents() {
  loading.value = true
  error.value = null
  try {
    students.value = await fetchStudents()
    if (!selectedId.value && students.value.length) {
      selectedId.value = students.value[0].id
    }
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
    if (selectedId.value === id) {
      selectedId.value = students.value[0]?.id ?? null
    }
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    deletingId.value = null
  }
}

function selectStudent(student: Student) {
  selectedId.value = student.id
}

watch(
  () => students.value.length,
  (len) => {
    if (len && !selectedId.value) {
      selectedId.value = students.value[0].id
    }
  },
)

onMounted(loadStudents)
</script>

<template>
  <div class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">4.2.1 Students</p>
        <h2>Students</h2>
        <p class="muted">Basic profile plus current risk sentiment.</p>
      </div>
      <div class="pill pill--primary">{{ students.length }} records</div>
    </div>

    <div v-if="selectedStudent" class="detail">
      <div class="detail-head">
        <div>
          <p class="eyebrow">Profile</p>
          <h3>{{ selectedStudent.fullName }}</h3>
          <p class="muted">Student #{{ selectedStudent.studentNumber }}</p>
        </div>
        <div class="pills">
          <span class="pill pill--accent">Course: {{ selectedStudent.courseName || 'N/A' }}</span>
          <span class="pill pill--primary">Year {{ selectedStudent.yearOfStudy }}</span>
          <span class="pill pill--danger">Absences: {{ studentAttendanceSummary.absences }}</span>
        </div>
      </div>

      <div class="detail-grid">
        <div v-if="showAcademic" class="detail-card">
          <h4>Academic snapshot</h4>
          <p class="muted small">Attendance / Submissions / Grades</p>
          <div class="metrics">
            <div class="metric">
              <p class="label">Attendance</p>
              <p class="value">{{ studentAttendanceSummary.attendanceRate }}%</p>
            </div>
            <div class="metric">
              <p class="label">Submissions</p>
              <p class="value">
                {{ studentSubmissionSummary.submitted }}/{{ studentSubmissionSummary.total }}
                <span class="muted tiny">({{ studentSubmissionSummary.onTime }} on time)</span>
              </p>
            </div>
            <div class="metric">
              <p class="label">Avg grade</p>
              <p class="value">{{ studentGradeSummary.average ?? '—' }}</p>
            </div>
          </div>
          <div class="module-list">
            <div v-for="item in studentModules" :key="item.module?.id" class="module-row">
              <div>
                <p class="strong">{{ item.module?.moduleTitle }}</p>
                <p class="muted tiny">{{ item.module?.moduleCode }}</p>
              </div>
              <div class="bars">
                <div class="bar">
                  <span class="muted tiny">Attendance</span>
                  <div class="meter">
                    <div class="meter-fill" :style="{ width: `${item.attendanceRate}%` }"></div>
                  </div>
                  <span class="muted tiny">{{ item.attendanceRate }}%</span>
                </div>
                <div class="bar">
                  <span class="muted tiny">Submission</span>
                  <div class="meter">
                    <div class="meter-fill" :style="{ width: `${item.submissionRate}%` }"></div>
                  </div>
                  <span class="muted tiny">{{ item.submissionRate }}%</span>
                </div>
                <div class="bar">
                  <span class="muted tiny">Grade</span>
                  <div class="meter">
                    <div class="meter-fill" :style="{ width: `${item.avgGrade ?? 0}%` }"></div>
                  </div>
                  <span class="muted tiny">{{ item.avgGrade ?? '—' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showWellbeing" class="detail-card">
          <h4>Wellbeing</h4>
          <p class="muted small">Stress trend & alerts</p>
          <div class="trend">
            <div v-for="entry in studentStressTrend" :key="entry.weekNumber" class="trend-row">
              <span class="muted tiny">Week {{ entry.weekNumber }}</span>
              <div class="meter">
                <div class="meter-fill" :style="{ width: `${(entry.stressLevel / 5) * 100}%` }"></div>
              </div>
              <span class="strong">{{ entry.stressLevel }}</span>
            </div>
          </div>
          <div v-if="studentAlerts.length" class="alerts">
            <div v-for="alert in studentAlerts" :key="alert.id" class="alert-row">
              <span class="pill pill--danger">High risk</span>
              <div>
                <p class="strong">{{ alert.reason }}</p>
                <p class="muted tiny">Week {{ alert.weekNumber }} • Module {{ alert.moduleId ?? '-' }}</p>
              </div>
            </div>
          </div>
          <p v-else class="muted tiny">No active alerts.</p>
        </div>
      </div>
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
          <div v-for="student in students" :key="student.id" class="table-row" @click="selectStudent(student)">
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
  cursor: pointer;
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

.detail {
  margin-top: 16px;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  background: var(--surface);
}

.detail-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.detail-card {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: var(--surface-muted);
  display: grid;
  gap: 10px;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}

.metric .label {
  color: var(--muted);
  font-size: 13px;
}

.metric .value {
  font-weight: 700;
  font-size: 18px;
}

.module-list {
  display: grid;
  gap: 10px;
}

.module-row {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px;
  display: grid;
  gap: 8px;
  background: var(--surface);
}

.bars {
  display: grid;
  gap: 6px;
}

.bar {
  display: grid;
  gap: 4px;
}

.meter {
  height: 6px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: #475569;
}

.trend {
  display: grid;
  gap: 8px;
}

.trend-row {
  display: grid;
  grid-template-columns: 80px 1fr 50px;
  gap: 8px;
  align-items: center;
}

.meter.stress .meter-fill {
  background: linear-gradient(90deg, #f97316, #ef4444);
}

.alerts {
  display: grid;
  gap: 8px;
}

.alert-row {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
}
</style>
