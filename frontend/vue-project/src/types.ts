export interface Student {
  id: number
  studentNumber: string
  fullName: string
  courseName: string
  yearOfStudy: number
  email?: string
  riskLevel: 'low' | 'medium' | 'high'
}

export interface StudentPayload {
  studentNumber: string
  fullName: string
  courseName?: string
  yearOfStudy?: number
  email?: string
}

export interface Module {
  id: number
  moduleCode: string
  moduleTitle: string
  credit?: number
  academicYear?: string
}

export interface Enrolment {
  id: number
  studentId: number
  moduleId: number
  enrolDate?: string
}

export interface AttendanceRecord {
  id: number
  studentId: number
  moduleId: number
  weekNumber: number
  attendedSessions: number
  totalSessions: number
}

export interface AttendancePayload {
  studentId: number
  moduleId: number
  weekNumber: number
  attendedSessions?: number
  totalSessions?: number
}

export interface SubmissionRecord {
  id: number
  studentId: number
  moduleId: number
  assessmentName: string
  dueDate: string
  submittedDate?: string
  isSubmitted: boolean
  isLate: boolean
}

export interface SubmissionPayload {
  studentId: number
  moduleId: number
  assessmentName: string
  dueDate?: string
  submittedDate?: string
  isSubmitted?: boolean
  isLate?: boolean
}

export interface SurveyResponse {
  id: number
  studentId: number
  moduleId?: number
  weekNumber: number
  stressLevel: number
  hoursSlept?: number
  moodComment?: string
  createdAt?: string
}

export interface SurveyPayload {
  studentId: number
  moduleId?: number
  weekNumber: number
  stressLevel: number
  hoursSlept?: number
  moodComment?: string
  createdAt?: string
}

export interface Alert {
  id: number
  studentId: number
  moduleId?: number
  weekNumber?: number
  reason: string
  createdAt?: string
  resolved: boolean
  severity: 'low' | 'medium' | 'high'
}

export interface AlertPayload {
  studentId: number
  moduleId?: number
  weekNumber?: number
  reason: string
  createdAt?: string
  resolved?: boolean
  severity?: 'low' | 'medium' | 'high'
}
