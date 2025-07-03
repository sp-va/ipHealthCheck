import { createRouter, createWebHistory } from 'vue-router'
import TablePage from '../views/TablePage.vue'

const routes = [
  {
    path: '/',
    name: 'Table',
    component: TablePage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
