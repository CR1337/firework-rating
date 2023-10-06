import { createRouter, createWebHistory } from 'vue-router'
import Overview from '../components/Overview.vue'
import Product from '../components/Product.vue'
import Index from '../components/Index.vue'
import Search from '../components/Search.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'index',
      component: Index
    },
    {
      path: '/overview',
      name: 'overview',
      component: Overview
    },
    {
      path: '/product/:id',
      name: 'product',
      component: Product
    },
    {
      path: '/search/',
      name: 'search',
      component: Search
    }
  ]
})

export default router
