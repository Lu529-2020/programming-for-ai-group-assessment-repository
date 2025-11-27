import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type {
  Alert,
  AttendanceRecord,
  Enrolment,
  Module,
  Student,
  SubmissionRecord,
  SurveyResponse,
} from '@/types'

export const useDemoDataStore = defineStore('demoData', () => {
  const students = ref<Student[]>([
    {
      id: 1,
      studentNumber: 'S0001',
      fullName: 'Alice Wong',
      courseName: 'MSc Applied AI',
      yearOfStudy: 1,
      email: 'alice.wong@example.edu',
      riskLevel: 'medium',
    },
    {
      id: 2,
      studentNumber: 'S0002',
      fullName: 'Ben Carter',
      courseName: 'MSc Applied AI',
      yearOfStudy: 1,
      email: 'ben.carter@example.edu',
      riskLevel: 'low',
    },
    {
      id: 3,
      studentNumber: 'S0003',
      fullName: 'Priya Singh',
      courseName: 'MSc Data Science',
      yearOfStudy: 2,
      email: 'priya.singh@example.edu',
      riskLevel: 'high',
    },
    {
      id: 4,
      studentNumber: 'S0004',
      fullName: 'Linh Tran',
      courseName: 'MSc Data Science',
      yearOfStudy: 2,
      email: 'linh.tran@example.edu',
      riskLevel: 'medium',
    },
  ])

  const modules = ref<Module[]>([
    { id: 1, moduleCode: 'WM9QF-15', moduleTitle: 'Programming for AI', credit: 15, academicYear: '2025/26' },
    { id: 2, moduleCode: 'DS9001', moduleTitle: 'Data Science Foundations', credit: 15, academicYear: '2025/26' },
    { id: 3, moduleCode: 'WB8002', moduleTitle: 'Wellbeing Analytics', credit: 10, academicYear: '2025/26' },
  ])

  const enrolments = ref<Enrolment[]>([
    { id: 1, studentId: 1, moduleId: 1 },
    { id: 2, studentId: 1, moduleId: 3 },
    { id: 3, studentId: 2, moduleId: 1 },
    { id: 4, studentId: 2, moduleId: 2 },
    { id: 5, studentId: 3, moduleId: 1 },
    { id: 6, studentId: 3, moduleId: 2 },
    { id: 7, studentId: 4, moduleId: 2 },
    { id: 8, studentId: 4, moduleId: 3 },
  ])

  const attendanceRecords = ref<AttendanceRecord[]>([
    { id: 1, studentId: 1, moduleId: 1, weekNumber: 1, attendedSessions: 3, totalSessions: 4 },
    { id: 2, studentId: 2, moduleId: 1, weekNumber: 1, attendedSessions: 4, totalSessions: 4 },
    { id: 3, studentId: 3, moduleId: 1, weekNumber: 1, attendedSessions: 2, totalSessions: 4 },
    { id: 4, studentId: 1, moduleId: 3, weekNumber: 2, attendedSessions: 3, totalSessions: 4 },
    { id: 5, studentId: 4, moduleId: 3, weekNumber: 2, attendedSessions: 2, totalSessions: 4 },
    { id: 6, studentId: 3, moduleId: 2, weekNumber: 2, attendedSessions: 3, totalSessions: 4 },
    { id: 7, studentId: 2, moduleId: 2, weekNumber: 2, attendedSessions: 4, totalSessions: 4 },
  ])

  const submissionRecords = ref<SubmissionRecord[]>([
    {
      id: 1,
      studentId: 1,
      moduleId: 1,
      assessmentName: 'Coursework 1',
      dueDate: '2025-02-14',
      submittedDate: '2025-02-13',
      isSubmitted: true,
      isLate: false,
    },
    {
      id: 2,
      studentId: 3,
      moduleId: 1,
      assessmentName: 'Coursework 1',
      dueDate: '2025-02-14',
      submittedDate: '2025-02-15',
      isSubmitted: true,
      isLate: true,
    },
    {
      id: 3,
      studentId: 2,
      moduleId: 2,
      assessmentName: 'Essay Draft',
      dueDate: '2025-02-10',
      submittedDate: undefined,
      isSubmitted: false,
      isLate: true,
    },
    {
      id: 4,
      studentId: 4,
      moduleId: 3,
      assessmentName: 'Reflection',
      dueDate: '2025-02-18',
      submittedDate: undefined,
      isSubmitted: false,
      isLate: false,
    },
  ])

  const surveyResponses = ref<SurveyResponse[]>([
    {
      id: 1,
      studentId: 1,
      moduleId: 1,
      weekNumber: 1,
      stressLevel: 3,
      hoursSlept: 7,
      moodComment: 'Balancing workload but okay',
    },
    {
      id: 2,
      studentId: 3,
      moduleId: 1,
      weekNumber: 1,
      stressLevel: 5,
      hoursSlept: 5,
      moodComment: 'Struggling with deadlines',
    },
    {
      id: 3,
      studentId: 4,
      moduleId: 3,
      weekNumber: 2,
      stressLevel: 4,
      hoursSlept: 6,
      moodComment: 'Need support on attendance',
    },
    {
      id: 4,
      studentId: 2,
      moduleId: 2,
      weekNumber: 2,
      stressLevel: 2,
      hoursSlept: 8,
    },
  ])

  const alerts = ref<Alert[]>([
    {
      id: 1,
      studentId: 3,
      moduleId: 1,
      weekNumber: 1,
      reason: 'Low attendance and high stress',
      createdAt: '2025-02-16',
      resolved: false,
      severity: 'high',
    },
    {
      id: 2,
      studentId: 4,
      moduleId: 3,
      weekNumber: 2,
      reason: 'Attendance drop in wellbeing module',
      createdAt: '2025-02-16',
      resolved: false,
      severity: 'medium',
    },
    {
      id: 3,
      studentId: 2,
      moduleId: 2,
      weekNumber: 2,
      reason: 'Pending submission: Essay Draft',
      createdAt: '2025-02-12',
      resolved: true,
      severity: 'low',
    },
  ])

  const averageAttendance = computed(() => {
    if (!attendanceRecords.value.length) return 0
    const ratios = attendanceRecords.value
      .filter((record) => record.totalSessions > 0)
      .map((record) => record.attendedSessions / record.totalSessions)
    const average = ratios.reduce((sum, ratio) => sum + ratio, 0) / ratios.length
    return Math.round(average * 100)
  })

  const moduleAttendance = computed(() => {
    const aggregate: Record<number, { total: number; attended: number }> = {}
    attendanceRecords.value.forEach((record) => {
      if (!aggregate[record.moduleId]) {
        aggregate[record.moduleId] = { total: 0, attended: 0 }
      }
      aggregate[record.moduleId].total += record.totalSessions
      aggregate[record.moduleId].attended += record.attendedSessions
    })
    return modules.value.map((module) => {
      const stats = aggregate[module.id]
      const attendanceRate = stats ? Math.round((stats.attended / stats.total) * 100) : 0
      return { module, attendanceRate }
    })
  })

  const averageStress = computed(() => {
    if (!surveyResponses.value.length) return 0
    const total = surveyResponses.value.reduce((sum, response) => sum + response.stressLevel, 0)
    return Math.round((total / surveyResponses.value.length) * 10) / 10
  })

  const submissionOnTimeRate = computed(() => {
    const submitted = submissionRecords.value.filter((record) => record.isSubmitted)
    if (!submitted.length) return 0
    const onTimeCount = submitted.filter((record) => !record.isLate).length
    return Math.round((onTimeCount / submitted.length) * 100)
  })

  const activeAlerts = computed(() => alerts.value.filter((alert) => !alert.resolved))

  const highRiskStudents = computed(() => students.value.filter((student) => student.riskLevel === 'high'))

  const stressByWeek = computed(() => {
    const grouped: Record<number, { total: number; count: number }> = {}
    surveyResponses.value.forEach((response) => {
      if (!grouped[response.weekNumber]) {
        grouped[response.weekNumber] = { total: 0, count: 0 }
      }
      grouped[response.weekNumber].total += response.stressLevel
      grouped[response.weekNumber].count += 1
    })
    return Object.entries(grouped)
      .map(([week, values]) => ({
        weekNumber: Number(week),
        averageStress: Math.round((values.total / values.count) * 10) / 10,
      }))
      .sort((a, b) => a.weekNumber - b.weekNumber)
  })

  const attendanceByWeek = computed(() => {
    const grouped: Record<number, { attended: number; total: number }> = {}
    attendanceRecords.value.forEach((record) => {
      if (!grouped[record.weekNumber]) {
        grouped[record.weekNumber] = { attended: 0, total: 0 }
      }
      grouped[record.weekNumber].attended += record.attendedSessions
      grouped[record.weekNumber].total += record.totalSessions
    })
    return Object.entries(grouped)
      .map(([week, values]) => ({
        weekNumber: Number(week),
        attendanceRate: Math.round((values.attended / values.total) * 100),
      }))
      .sort((a, b) => a.weekNumber - b.weekNumber)
  })

  const attendanceVsStress = computed(() => {
    return attendanceByWeek.value.map((attendance) => {
      const stress = stressByWeek.value.find((item) => item.weekNumber === attendance.weekNumber)
      return {
        weekNumber: attendance.weekNumber,
        attendanceRate: attendance.attendanceRate,
        stressLevel: stress?.averageStress ?? 0,
      }
    })
  })

  const moduleEnrollmentCounts = computed(() => {
    const counts: Record<number, number> = {}
    enrolments.value.forEach((enrolment) => {
      counts[enrolment.moduleId] = (counts[enrolment.moduleId] || 0) + 1
    })
    return counts
  })

  const upcomingSubmissions = computed(() =>
    submissionRecords.value
      .filter((record) => !record.isSubmitted)
      .sort((a, b) => a.dueDate.localeCompare(b.dueDate)),
  )

  return {
    students,
    modules,
    enrolments,
    attendanceRecords,
    submissionRecords,
    surveyResponses,
    alerts,
    averageAttendance,
    moduleAttendance,
    averageStress,
    submissionOnTimeRate,
    activeAlerts,
    highRiskStudents,
    stressByWeek,
    attendanceByWeek,
    attendanceVsStress,
    moduleEnrollmentCounts,
    upcomingSubmissions,
  }
})
