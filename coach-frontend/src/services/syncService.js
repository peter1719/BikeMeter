import { useLocalStorage } from '@vueuse/core'

// 存储离线数据
const offlineData = useLocalStorage('offline-data', [])

// 检查并同步数据
export async function syncOfflineData(apiService) {
  if (!navigator.onLine) return false
  
  if (offlineData.value.length > 0) {
    try {
      // 遍历所有离线数据并同步
      for (const item of offlineData.value) {
        await apiService.syncData(item)
      }
      
      // 同步成功后清空离线数据
      offlineData.value = []
      return true
    } catch (error) {
      console.error('同步数据失败:', error)
      return false
    }
  }
  
  return true
}

// 保存离线数据
export function saveOfflineData(data) {
  offlineData.value.push({
    ...data,
    timestamp: Date.now()
  })
} 