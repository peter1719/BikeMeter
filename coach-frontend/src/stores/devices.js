import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import io from 'socket.io-client'

export const useDevicesStore = defineStore('devices', () => {
  const allDevices = ref({})
  const deviceCount = computed(() => Object.keys(allDevices.value).length)
  const socket = ref(null)
  const isSocketConnected = ref(false)
  
  // 初始化 Socket.IO 連接
  const initializeWebSocket = () => {
    // 如果已經連接，則不需要重複連接
    if (isSocketConnected.value && socket.value) return
    
    // 建立 Socket.IO 連接
    const newSocket = io('http://localhost:5000', {
      transports: ['polling', 'websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000
    })
    
    newSocket.on('connect', () => {
      console.log('Socket.IO 連接已建立')
      isSocketConnected.value = true
      socket.value = newSocket
    })
    
    newSocket.on('connect_error', (error) => {
      console.error('Socket.IO 連接錯誤:', error)
      isSocketConnected.value = false
    })
    
    newSocket.on('disconnect', (reason) => {
      console.log('Socket.IO 連接已關閉:', reason)
      isSocketConnected.value = false
    })
    
    newSocket.on('mqtt_message', (data) => {
      const deviceId = data.device_id || 'unknown'
      // 更新設備數據
      allDevices.value = { 
        ...allDevices.value, 
        [deviceId]: {
          ...data,
          lastUpdate: new Date().toISOString()
        }
      }
    })
    
    socket.value = newSocket
  }
  
  // 斷開 Socket.IO 連接
  const disconnectWebSocket = () => {
    if (socket.value) {
      socket.value.disconnect()
      isSocketConnected.value = false
      socket.value = null
    }
  }
  
  // 移除設備
  const removeDevice = (id) => {
    const devices = { ...allDevices.value }
    delete devices[id]
    allDevices.value = devices
  }
  
  // 檢查設備是否活躍
  const checkDeviceActive = (device) => {
    if (!device.lastUpdate) return false
    return (new Date() - new Date(device.lastUpdate)) < 3000 // 3秒內有更新視為活躍
  }
  
  return {
    allDevices,
    deviceCount,
    isSocketConnected,
    initializeWebSocket,
    disconnectWebSocket,
    removeDevice,
    checkDeviceActive
  }
}) 