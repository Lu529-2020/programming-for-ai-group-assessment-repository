<script setup lang="ts">
import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useDemoDataStore } from '@/stores/demoData'

const store = useDemoDataStore()
const {
  moduleAttendance,
  submissionRecords,
  modules,
  attendanceRecords,
  students,
  averageAttendance,
  averageStress,
  submissionOnTimeRate,
} = storeToRefs(store)

const absenceThreshold = ref(2)

const moduleEngagement = computed(() =>
  modules.value
    .map((module) => {
      const attendanceRate = moduleAttendance.value.find((item) => item.module.id === module.id)?.attendanceRate ?? 0
      const submissions = submissionRecords.value.filter((record) => record.moduleId === module.id)
      const submitted = submissions.filter((record) => record.isSubmitted).length
      const submissionRate = submissions.length ? Math.round((submitted / submissions.length) * 100) : 0
      return { module, attendanceRate, submissionRate }
    })
    .sort((a, b) => b.attendanceRate - a.attendanceRate),
)

const absenceWatchlist = computed(() => {
  const stats: Record<
    number,
    { absences: number; attended: number; total: number }
  > = {}
  attendanceRecords.value.forEach((record) => {
    const absences = Math.max(record.totalSessions - record.attendedSessions, 0)
    const entry = stats[record.studentId] ?? { absences: 0, attended: 0, total: 0 }
    stats[record.studentId] = {
      absences: entry.absences + absences,
      attended: entry.attended + record.attendedSessions,
      total: entry.total + record.totalSessions,
    }
  })
  return students.value
    .map((student) => {
      const studentStats = stats[student.id] ?? { absences: 0, attended: 0, total: 0 }
      const attendanceRate =
        studentStats.total > 0 ? Math.round((studentStats.attended / studentStats.total) * 100) : 100
      return {
        student,
        absences: studentStats.absences,
        attendanceRate,
      }
    })
    .filter((item) => item.absences >= absenceThreshold.value)
    .sort((a, b) => b.absences - a.absences)
})
</script>

<template>
  <div class="stack">
    <section class="panel head">
      <div>
        <p class="eyebrow">Analytics cockpit</p>
        <h2>Engagement, submissions, alerts at a glance</h2>
        <p class="muted">
          Prioritise outreach with attendance + submission blending, and surface consecutive absences for early
          intervention.
        </p>
      </div>
      <div class="chips">
        <span class="pill pill--primary">Avg attendance {{ averageAttendance }}%</span>
        <span class="pill pill--accent">On-time submissions {{ submissionOnTimeRate }}%</span>
        <span class="pill pill--danger">Mean stress {{ averageStress }}/5</span>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">FR8</p>
          <h3>Attendance vs submission completion</h3>
          <p class="muted">Blended engagement score by module. Sorts by attendance to focus on lagging cohorts.</p>
        </div>
        <div class="legend">
          <span><span class="dot blue"></span>Attendance</span>
          <span><span class="dot orange"></span>Submission completion</span>
        </div>
      </div>

      <div class="bars">
        <div v-for="row in moduleEngagement" :key="row.module.id" class="bar-row">
          <div class="label-cell">
            <p class="strong">{{ row.module.moduleTitle }}</p>
            <p class="muted small">{{ row.module.moduleCode }}</p>
          </div>
          <div class="bar-track">
            <div class="bar-fill attendance" :style="{ width: `${row.attendanceRate}%` }">
              <span>{{ row.attendanceRate }}%</span>
            </div>
            <div class="bar-fill submissions" :style="{ width: `${row.submissionRate}%` }">
              <span>{{ row.submissionRate }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">FR10</p>
          <h3>Absence watchlist</h3>
          <p class="muted">Highlight students with repeated absences. Adjust the threshold to tune alerts.</p>
        </div>
        <div class="threshold">
          <label>Absences ≥ {{ absenceThreshold }}</label>
          <input v-model.number="absenceThreshold" type="range" min="1" max="6" />
        </div>
      </div>

      <div v-if="!absenceWatchlist.length" class="empty">No one crosses this threshold right now.</div>
      <div v-else class="watchlist">
        <div v-for="item in absenceWatchlist" :key="item.student.id" class="watch-card">
          <div>
            <p class="strong">{{ item.student.fullName }}</p>
            <p class="muted small">Student #{{ item.student.studentNumber }}</p>
          </div>
          <div class="absences">
            <div class="count">{{ item.absences }}</div>
            <div class="muted small">missed sessions</div>
          </div>
          <div class="meter">
            <div class="meter-fill" :style="{ width: `${item.attendanceRate}%` }"></div>
          </div>
          <p class="muted tiny">Attendance {{ item.attendanceRate }}%</p>
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

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.legend {
  display: flex;
  gap: 12px;
  color: var(--muted);
  font-size: 13px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

.dot.blue {
  background: #0ea5e9;
}

.dot.orange {
  background: #f97316;
}

.bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-row {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 14px;
  background: var(--surface-muted);
}

.label-cell .small {
  font-size: 13px;
}

.bar-track {
  position: relative;
  height: 48px;
  background: #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.bar-fill {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
  color: #0f172a;
  font-weight: 700;
  height: 100%;
  position: absolute;
  inset: 0;
}

.bar-fill.attendance {
  background: linear-gradient(90deg, rgba(14, 165, 233, 0.9), rgba(14, 165, 233, 0.7));
  z-index: 1;
}

.bar-fill.submissions {
  background: linear-gradient(90deg, rgba(249, 115, 22, 0.9), rgba(249, 115, 22, 0.7));
  opacity: 0.9;
  z-index: 2;
  mix-blend-mode: multiply;
}

.threshold {
  display: grid;
  gap: 4px;
  align-items: center;
  text-align: right;
  font-weight: 600;
}

.threshold input {
  accent-color: #0ea5e9;
}

.watchlist {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.watch-card {
  padding: 12px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface-muted);
  display: grid;
  gap: 8px;
}

.absences {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.count {
  font-size: 28px;
  font-weight: 800;
  color: #ef4444;
}

.meter {
  width: 100%;
  height: 6px;
  background: var(--border);
  border-radius: 999px;
  overflow: hidden;
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, #0ea5e9, #f97316);
}

.empty {
  padding: 14px;
  border-radius: 12px;
  background: var(--surface-muted);
  color: var(--muted);
  font-weight: 600;
}

.tiny {
  font-size: 12px;
}

@media (max-width: 900px) {
  .bar-row {
    grid-template-columns: 1fr;
  }

  .head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
