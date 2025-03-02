<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useDevicesStore } from '@/stores/devices'
import OfflineStatus from './components/OfflineStatus.vue'

const route = useRoute()
const store = useDevicesStore()

// 在應用程式初始化時連接 WebSocket
onMounted(() => {
  store.initializeWebSocket()
})

// 在應用程式卸載前斷開 WebSocket
onBeforeUnmount(() => {
  store.disconnectWebSocket()
})
</script>

<template>
  <OfflineStatus />
  <div id="app" class="font-sans">
    <!-- 頂部導航欄 -->
    <nav class="bg-gray-800 text-white shadow-md">
      <div class="max-w-[1920px] mx-auto px-4 py-3">
        <div class="flex justify-between items-center">
          <div class="text-xl font-bold">教練系統</div>
          <div class="flex space-x-2">
            <router-link 
              to="/" 
              class="px-4 py-2 rounded-md transition-all duration-200 flex items-center"
              :class="route.path === '/' ? 
                'bg-blue-600 text-white shadow-md' : 
                'text-gray-200 hover:bg-gray-700 hover:text-white'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
              </svg>
              儀表板
            </router-link>
            <router-link 
              to="/racing" 
              class="px-4 py-2 rounded-md transition-all duration-200 flex items-center"
              :class="route.path === '/racing' ? 
                'bg-blue-600 text-white shadow-md' : 
                'text-gray-200 hover:bg-gray-700 hover:text-white'"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
              </svg>
              競速模式
            </router-link>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- 主内容區 -->
    <div class="pt-4">
      <router-view></router-view>
    </div>
  </div>
</template>

<style>
body {
  background-color: #f3f4f6;
  margin: 0;
  padding: 0;
}
</style>
