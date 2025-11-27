import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
    },
    {
      path: '/students',
      name: 'students',
      component: () => import('../views/StudentsView.vue'),
    },
    {
      path: '/modules',
      name: 'modules',
      component: () => import('../views/ModulesView.vue'),
    },
    {
      path: '/attendance',
      name: 'attendance',
      component: () => import('../views/AttendanceView.vue'),
    },
    {
      path: '/submissions',
      name: 'submissions',
      component: () => import('../views/SubmissionsView.vue'),
    },
    {
      path: '/surveys',
      name: 'surveys',
      component: () => import('../views/SurveysView.vue'),
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: () => import('../views/AnalyticsView.vue'),
    },
    {
      path: '/alerts',
      name: 'alerts',
      component: () => import('../views/AlertsView.vue'),
    },
  ],
})

export default router
