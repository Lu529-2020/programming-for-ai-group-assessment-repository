import type {
  Student,
  StudentPayload,
  AttendanceRecord,
  AttendancePayload,
  SubmissionRecord,
  SubmissionPayload,
  SurveyResponse,
  SurveyPayload,
  Alert,
  AlertPayload,
} from '@/types'

const base = '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${base}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }
  if (res.status === 204) {
    // No Content responses should not be parsed
    return undefined as T
  }
  return res.json() as Promise<T>
}

export async function fetchStudents(): Promise<Student[]> {
  return request<Student[]>('/students')
}

export async function createStudent(payload: StudentPayload): Promise<Student> {
  return request<Student>('/students', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateStudent(id: number, payload: StudentPayload): Promise<Student> {
  return request<Student>(`/students/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteStudent(id: number): Promise<void> {
  await request<void>(`/students/${id}`, { method: 'DELETE' })
}

// Attendance
export async function fetchAttendance(): Promise<AttendanceRecord[]> {
  return request<AttendanceRecord[]>('/attendance')
}

export async function createAttendance(payload: AttendancePayload): Promise<AttendanceRecord> {
  return request<AttendanceRecord>('/attendance', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateAttendance(id: number, payload: AttendancePayload): Promise<AttendanceRecord> {
  return request<AttendanceRecord>(`/attendance/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteAttendance(id: number): Promise<void> {
  await request<void>(`/attendance/${id}`, { method: 'DELETE' })
}

// Submissions
export async function fetchSubmissions(): Promise<SubmissionRecord[]> {
  return request<SubmissionRecord[]>('/submissions')
}

export async function createSubmission(payload: SubmissionPayload): Promise<SubmissionRecord> {
  return request<SubmissionRecord>('/submissions', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateSubmission(id: number, payload: SubmissionPayload): Promise<SubmissionRecord> {
  return request<SubmissionRecord>(`/submissions/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteSubmission(id: number): Promise<void> {
  await request<void>(`/submissions/${id}`, { method: 'DELETE' })
}

// Surveys
export async function fetchSurveys(): Promise<SurveyResponse[]> {
  return request<SurveyResponse[]>('/surveys')
}

export async function createSurvey(payload: SurveyPayload): Promise<SurveyResponse> {
  return request<SurveyResponse>('/surveys', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateSurvey(id: number, payload: SurveyPayload): Promise<SurveyResponse> {
  return request<SurveyResponse>(`/surveys/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteSurvey(id: number): Promise<void> {
  await request<void>(`/surveys/${id}`, { method: 'DELETE' })
}

// Alerts
export async function fetchAlerts(): Promise<Alert[]> {
  return request<Alert[]>('/alerts')
}

export async function createAlert(payload: AlertPayload): Promise<Alert> {
  return request<Alert>('/alerts', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateAlert(id: number, payload: AlertPayload): Promise<Alert> {
  return request<Alert>(`/alerts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export async function deleteAlert(id: number): Promise<void> {
  await request<void>(`/alerts/${id}`, { method: 'DELETE' })
}
