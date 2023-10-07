import { createRouter, createWebHistory } from 'vue-router'
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
