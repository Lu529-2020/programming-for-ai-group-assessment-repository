<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { SurveyResponse, SurveyPayload } from '@/types'
import { createSurvey, deleteSurvey, fetchSurveys, updateSurvey } from '@/services/api'

const records = ref<SurveyResponse[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)

const blankForm: SurveyPayload = {
  studentId: 0,
  moduleId: undefined,
  weekNumber: 1,
  stressLevel: 3,
  hoursSlept: undefined,
  moodComment: '',
}
const form = ref<SurveyPayload>({ ...blankForm })

async function load() {
  loading.value = true
  error.value = null
  try {
    records.value = await fetchSurveys()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

function startEdit(record: SurveyResponse) {
  editingId.value = record.id
  form.value = {
    studentId: record.studentId,
    moduleId: record.moduleId,
    weekNumber: record.weekNumber,
    stressLevel: record.stressLevel,
    hoursSlept: record.hoursSlept,
    moodComment: record.moodComment,
    createdAt: record.createdAt,
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
      const updated = await updateSurvey(editingId.value, form.value)
      records.value = records.value.map((r) => (r.id === updated.id ? updated : r))
      notice.value = 'Survey updated'
    } else {
      const created = await createSurvey(form.value)
      records.value = [created, ...records.value]
      notice.value = 'Survey added'
    }
    resetForm()
  } catch (e) {
    error.value = (e as Error).message
  } finally {
    saving.value = false
  }
}

async function handleDelete(id: number) {
  if (!confirm('Delete this survey?')) return
  deletingId.value = id
  error.value = null
  notice.value = null
  try {
    await deleteSurvey(id)
    records.value = records.value.filter((r) => r.id !== id)
    notice.value = 'Survey removed'
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
        <p class="eyebrow">FR7</p>
        <h2>Wellbeing survey responses</h2>
      </div>
      <div class="pill pill--primary">{{ records.length }} entries</div>
    </div>

    <div class="grid">
      <section class="card card--form">
        <div class="card-head">
          <div>
            <p class="eyebrow">{{ editingId ? 'Editing' : 'Create' }}</p>
            <h3>{{ editingId ? 'Edit response' : 'Add response' }}</h3>
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
            <span>Week *</span>
            <input v-model.number="form.weekNumber" type="number" min="1" required />
          </label>
          <label>
            <span>Stress level (1-5) *</span>
            <input v-model.number="form.stressLevel" type="number" min="1" max="5" required />
          </label>
          <label>
            <span>Hours slept</span>
            <input v-model.number="form.hoursSlept" type="number" min="0" step="0.5" />
          </label>
          <label class="full">
            <span>Mood comment</span>
            <textarea v-model="form.moodComment" rows="3" />
          </label>
          <button class="btn btn--primary" type="submit" :disabled="saving">
            {{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Add response' }}
          </button>
        </form>
        <p v-if="notice" class="notice">{{ notice }}</p>
        <p v-if="error" class="error">Error: {{ error }}</p>
      </section>

      <section class="card card--list">
        <div v-if="loading" class="muted">Loading...</div>
        <div v-else-if="error" class="muted">Error: {{ error }}</div>
        <div v-else class="grid-list">
          <article v-for="response in records" :key="response.id" class="item">
            <div class="pill">Week {{ response.weekNumber }}</div>
            <h3>Student #{{ response.studentId }}</h3>
            <p class="muted">Module: {{ response.moduleId ?? 'N/A' }}</p>
            <div class="tags">
              <span class="pill pill--accent">Stress {{ response.stressLevel }}/5</span>
              <span v-if="response.hoursSlept" class="pill pill--primary">Sleep {{ response.hoursSlept }}h</span>
            </div>
            <p class="comment">{{ response.moodComment || 'No comment recorded.' }}</p>
            <div class="actions">
              <button class="link" type="button" @click="startEdit(response)">Edit</button>
              <button
                class="link link--danger"
                type="button"
                :disabled="deletingId === response.id"
                @click="handleDelete(response.id)"
              >
                {{ deletingId === response.id ? 'Removing…' : 'Delete' }}
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
  grid-template-columns: 340px 1fr;
  gap: 16px;
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

.card--list {
  min-height: 260px;
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
.form textarea {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px 10px;
  background: var(--surface);
}

.form textarea {
  resize: vertical;
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

.grid-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.item {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.comment {
  border-left: 3px solid var(--border);
  padding-left: 10px;
  color: var(--muted);
}

.actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
