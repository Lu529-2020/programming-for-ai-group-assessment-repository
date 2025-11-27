<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useDemoDataStore } from '@/stores/demoData'

const store = useDemoDataStore()
const { stressByWeek, attendanceVsStress } = storeToRefs(store)
</script>

<template>
  <div class="stack">
    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">FR8</p>
          <h2>Stress trend by week</h2>
        </div>
        <div class="pill pill--accent">Mean stress levels</div>
      </div>
      <div class="trend">
        <div v-for="week in stressByWeek" :key="week.weekNumber" class="trend-row">
          <span class="muted">Week {{ week.weekNumber }}</span>
          <div class="meter">
            <div class="meter-fill" :style="{ width: `${(week.averageStress / 5) * 100}%` }"></div>
          </div>
          <span class="strong">{{ week.averageStress }}</span>
        </div>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head">
        <div>
          <p class="eyebrow">FR9</p>
          <h2>Attendance vs stress</h2>
          <p class="muted">Quick view of how stress moves with attendance.</p>
        </div>
        <div class="pill pill--primary">{{ attendanceVsStress.length }} weeks compared</div>
      </div>

      <div class="table">
        <div class="table-head">
          <span>Week</span>
          <span>Attendance</span>
          <span>Stress</span>
        </div>
        <div v-for="row in attendanceVsStress" :key="row.weekNumber" class="table-row">
          <span>Week {{ row.weekNumber }}</span>
          <span>
            <div class="meter meter-sm">
              <div class="meter-fill" :style="{ width: `${row.attendanceRate}%` }"></div>
            </div>
            <small>{{ row.attendanceRate }}%</small>
          </span>
          <span>
            <div class="meter meter-sm accent">
              <div class="meter-fill" :style="{ width: `${(row.stressLevel / 5) * 100}%` }"></div>
            </div>
            <small>{{ row.stressLevel }}</small>
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

.meter-sm {
  height: 6px;
  margin-bottom: 6px;
}

.meter-fill {
  height: 100%;
  background: linear-gradient(90deg, #0ea5e9, #f97316);
}

.accent .meter-fill {
  background: linear-gradient(90deg, #f97316, #ef4444);
}

.table {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
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

@media (max-width: 840px) {
  .trend-row {
    grid-template-columns: 1fr;
  }
}
</style>
