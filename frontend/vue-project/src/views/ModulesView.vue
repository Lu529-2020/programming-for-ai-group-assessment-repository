<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useDemoDataStore } from '@/stores/demoData'

const store = useDemoDataStore()
const { modules, moduleAttendance, moduleEnrollmentCounts } = storeToRefs(store)

const rows = computed(() =>
  modules.value.map((module) => {
    const attendance = moduleAttendance.value.find((row) => row.module.id === module.id)?.attendanceRate ?? 0
    const enrolments = moduleEnrollmentCounts.value[module.id] || 0
    return { module, attendance, enrolments }
  }),
)
</script>

<template>
  <div class="panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">4.2.2 Modules</p>
        <h2>Modules and enrolments</h2>
      </div>
      <div class="pill pill--primary">{{ modules.length }} modules</div>
    </div>

    <div class="cards">
      <article v-for="row in rows" :key="row.module.id" class="card">
        <div>
          <p class="strong">{{ row.module.moduleTitle }}</p>
          <p class="muted">{{ row.module.moduleCode }} • {{ row.module.academicYear }}</p>
        </div>
        <div class="meta">
          <span class="pill pill--accent">{{ row.enrolments }} enrolments</span>
          <div class="meter">
            <div class="meter-fill" :style="{ width: `${row.attendance}%` }"></div>
          </div>
          <p class="muted">Avg attendance {{ row.attendance }}%</p>
        </div>
      </article>
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

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.card {
  border: 1px solid var(--border);
  background: var(--surface-muted);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
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
  border-radius: 999px;
}
</style>
