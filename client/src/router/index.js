import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dash',
      component: () => import('../views/DashView.vue')
    },
    {
      path: '/record',
      name: 'record',
      component: () => import('../views/RecordView.vue')
    },
    {
      path: '/config',
      name: 'config',
      component: () => import('../views/ConfigView.vue')
    }
  ]
})

export default router
