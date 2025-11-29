<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type {
  Alert,
  AttendanceRecord,
  Student,
  SubmissionRecord,
  SurveyResponse,
} from '@/types'
import {
  fetchAlerts,
  fetchAttendance,
  fetchStudents,
  fetchSubmissions,
  fetchSurveys,
} from '@/services/api'

const students = ref<Student[]>([])
const attendance = ref<AttendanceRecord[]>([])
const submissions = ref<SubmissionRecord[]>([])
const surveys = ref<SurveyResponse[]>([])
const alerts = ref<Alert[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// 4.3: aggregate attendance metric for analysis overview.
const averageAttendance = computed(() => {
  if (!attendance.value.length) return 0
  const rates = attendance.value
    .map((r) => {
      if (r.totalSessions) return Math.min(100, Math.max(0, Math.round((r.attendedSessions / r.totalSessions) * 100)))
      return 0
    })
    .filter((r) => !Number.isNaN(r))
  if (!rates.length) return 0
  return Math.round(rates.reduce((a, b) => a + b, 0) / rates.length)
})

// 4.3: surface recent wellbeing pulse via average stress.
const averageStress = computed(() => {
  if (!surveys.value.length) return 0
  const sum = surveys.value.reduce((acc, s) => acc + (s.stressLevel || 0), 0)
  return sum / surveys.value.length
})

// 4.3: on-time submission rate for analysis overview.
const submissionOnTimeRate = computed(() => {
  if (!submissions.value.length) return 0
  const submitted = submissions.value.filter((s) => s.isSubmitted)
  if (!submitted.length) return 0
  const onTime = submitted.filter((s) => !s.isLate).length
  return Math.round((onTime / submitted.length) * 100)
})

const activeAlerts = computed(() => alerts.value.filter((a) => !a.resolved))
const moduleCount = computed(() => {
  const ids = new Set<number>()
  attendance.value.forEach((r) => ids.add(r.moduleId))
  submissions.value.forEach((r) => ids.add(r.moduleId))
  alerts.value.forEach((r) => r.moduleId && ids.add(r.moduleId))
  return ids.size
})
// 4.3: combine stress signals and alerts to show at-risk students.
const highRiskStudents = computed(() => {
  const stressIds = new Set(surveys.value.filter((s) => s.stressLevel >= 4).map((s) => s.studentId))
  const alertIds = new Set(activeAlerts.value.map((a) => a.studentId))
  const ids = new Set([...stressIds, ...alertIds])
  return students.value.filter((s) => ids.has(s.id))
})

const upcomingSubmissions = computed(() => {
  return [...submissions.value]
    .filter((s) => !s.isSubmitted)
    .sort((a, b) => (a.dueDate || '').localeCompare(b.dueDate || ''))
    .slice(0, 6)
})

// 4.4.1: pull most recent wellbeing check-ins.
const recentSurveys = computed(() => [...surveys.value].reverse().slice(0, 4))

function formatHours(hours?: number | null) {
  if (hours === undefined || hours === null) return ''
  return Number(hours).toFixed(2)
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const [studentList, attendanceList, submissionList, surveyList, alertList] = await Promise.all([
      fetchStudents(),
      fetchAttendance(),
      fetchSubmissions(),
      fetchSurveys(),
      fetchAlerts(),
    ])
    students.value = studentList
    attendance.value = attendanceList
    submissions.value = submissionList
    surveys.value = surveyList
    alerts.value = alertList
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

onMounted(load)

const stats = computed(() => [
  { label: 'Average attendance', value: `${averageAttendance.value}%`, accent: 'primary' },
  { label: 'Average stress (1-5)', value: averageStress.value.toFixed(1), accent: 'accent' },
  { label: 'On-time submissions', value: `${submissionOnTimeRate.value}%`, accent: 'primary' },
  { label: 'Open alerts', value: `${activeAlerts.value.length}`, accent: 'danger' },
])
</script>

<template>
  <div class="page">
    <p v-if="loading" class="muted">Loading dashboard data...</p>
    <p v-else-if="error" class="error">Error: {{ error }}</p>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">4.3 Analysis overview</p>
          <h2>Key signals</h2>
        </div>
        <div class="pill pill--primary">{{ students.length }} students • {{ moduleCount }} modules</div>
      </div>
      <div class="stats">
        <div v-for="stat in stats" :key="stat.label" class="stat-card" :data-accent="stat.accent">
          <p class="stat-label">{{ stat.label }}</p>
          <p class="stat-value">{{ stat.value }}</p>
        </div>
      </div>
    </section>

    <section class="grid">
      <div class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">4.4.1 Wellbeing check-ins</p>
            <h3>Recent wellbeing check-ins</h3>
          </div>
          <div class="pill pill--accent">{{ recentSurveys.length }} entries</div>
        </div>
        <div class="list">
          <article v-for="survey in recentSurveys" :key="survey.id" class="list-row">
            <div>
              <p class="strong">
                Student {{ survey.studentId }} • Week {{ survey.weekNumber }}
              </p>
              <p class="muted">{{ survey.moodComment || 'No comment provided' }}</p>
            </div>
            <div class="tags">
              <span class="pill">Stress: {{ survey.stressLevel }}</span>
              <span class="pill pill--primary" v-if="survey.hoursSlept">Sleep: {{ formatHours(survey.hoursSlept) }}h</span>
            </div>
          </article>
        </div>
      </div>

      <div class="panel">
        <div class="panel-head">
          <div>
            <p class="eyebrow">4.3.2 Risk detection</p>
            <h3>At-risk students</h3>
          </div>
          <div class="pill pill--danger">{{ highRiskStudents.length }} flagged</div>
        </div>
        <div v-if="highRiskStudents.length" class="list">
          <article v-for="student in highRiskStudents" :key="student.id" class="list-row">
            <div>
              <p class="strong">{{ student.fullName }}</p>
              <p class="muted">{{ student.courseName }} • Year {{ student.yearOfStudy }}</p>
            </div>
            <span class="pill pill--danger">High stress signal</span>
          </article>
        </div>
        <p v-else class="muted">No students flagged as high risk.</p>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">4.3.3 Submission deadlines</p>
          <h3>Upcoming submissions</h3>
        </div>
        <div class="pill pill--primary">Sorted by due date</div>
      </div>
      <div class="table">
        <div class="table-head">
          <span>Assessment</span>
          <span>Student</span>
          <span>Module</span>
          <span>Due date</span>
          <span>Status</span>
        </div>
        <div v-for="record in upcomingSubmissions" :key="record.id" class="table-row">
          <span>{{ record.assessmentName }}</span>
          <span>#{{ record.studentId }}</span>
          <span>#{{ record.moduleId }}</span>
          <span>{{ record.dueDate }}</span>
          <span>
            <span class="pill" :class="record.isLate ? 'pill--danger' : 'pill--accent'">
              {{ record.isLate ? 'Late' : 'Pending' }}
            </span>
          </span>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page {
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

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.stat-card {
  padding: 16px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface-muted);
}

.stat-card[data-accent='primary'] {
  background: rgba(14, 165, 233, 0.12);
  border-color: rgba(14, 165, 233, 0.22);
}

.stat-card[data-accent='accent'] {
  background: rgba(249, 115, 22, 0.12);
  border-color: rgba(249, 115, 22, 0.22);
}

.stat-card[data-accent='danger'] {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.22);
}

.stat-label {
  color: var(--muted);
  font-size: 14px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface-muted);
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.table {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
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

@media (max-width: 860px) {
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
