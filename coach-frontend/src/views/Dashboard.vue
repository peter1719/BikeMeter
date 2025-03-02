<template>
  <div class="p-2 max-w-[1920px] mx-auto">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">教練儀表板</h1>
          <div class="bg-white rounded-lg shadow px-4 py-3">
            <div class="text-sm text-gray-500">總設備數</div>
            <div class="text-2xl font-bold text-gray-900">{{ deviceCount }}</div>
          </div>
        </div>

        <!-- 新增排序和過濾控制項 -->
        <div class="flex gap-4">
          <div class="flex items-center gap-2">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜尋設備 ID"
              class="px-3 py-2 border rounded-lg"
            />
          </div>
          
          <select
            v-model="sortBy"
            class="px-3 py-2 border rounded-lg"
          >
            <option value="id">依照 ID 排序</option>
            <option value="speed">依照速度排序</option>
          </select>

          <!-- 新增顯示設備選擇器按鈕 -->
          <button
            @click="showDeviceSelector = !showDeviceSelector"
            class="px-3 py-2 border rounded-lg bg-blue-500 text-white hover:bg-blue-600"
          >
            選擇顯示設備
          </button>

          <!-- 新增關閉離線設備按鈕 -->
          <button
            @click="removeOfflineDevices"
            class="px-3 py-2 border rounded-lg bg-red-500 text-white hover:bg-red-600"
          >
            關閉離線設備
          </button>

        </div>
      </div>

      <!-- 設備選擇器面板 -->
      <div v-if="showDeviceSelector" class="mt-4 bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold">設備顯示設定</h3>
          <div class="flex items-center gap-2">
            <button
              @click="selectAllDevices"
              class="px-3 py-1 text-sm border rounded hover:bg-gray-100"
            >
              全選
            </button>
            <button
              @click="deselectAllDevices"
              class="px-3 py-1 text-sm border rounded hover:bg-gray-100"
            >
              取消全選
            </button>
            <button
              @click="showDeviceSelector = false"
              class="px-3 py-1 text-sm border rounded hover:bg-gray-100"
            >
              關閉列表
            </button>
          </div>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          <label
            v-for="(device, id) in allDevices"
            :key="id"
            class="flex items-center gap-2 p-2 border rounded hover:bg-gray-50 cursor-pointer"
          >
            <input
              type="checkbox"
              v-model="selectedDevices"
              :value="id"
            >
            <span>{{ id }}</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 使用 transition-group 添加動畫效果 -->
    <TransitionGroup
      name="device-list"
      tag="div"
      class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
    >
      <DeviceCard
        v-for="(device, id) in sortedAndFilteredDevices"
        :key="id"
        :device_id="id"
        :device="device"
        @remove="removeDevice"
      />
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useDevicesStore } from '@/stores/devices'
import DeviceCard from '@/components/DeviceCard.vue'
import { storeToRefs } from 'pinia'

const store = useDevicesStore()
const { removeDevice, checkDeviceActive } = store
const { allDevices, deviceCount } = storeToRefs(store)

// 排序和過濾狀態
const sortBy = ref('id')
const searchQuery = ref('')
const showDeviceSelector = ref(false)
const selectedDevices = ref([])
// 新增：記錄用戶手動取消選擇的設備
const manuallyDeselected = ref(new Set())

// 監聽 selectedDevices 的變化，記錄手動取消的設備
watch(selectedDevices, (newSelected, oldSelected) => {
  if (!oldSelected) return
  
  // 找出被取消選擇的設備
  const deselected = oldSelected.filter(id => !newSelected.includes(id))
  deselected.forEach(id => manuallyDeselected.value.add(id))
  
  // 找出重新被選擇的設備
  const reselected = newSelected.filter(id => !oldSelected.includes(id))
  reselected.forEach(id => manuallyDeselected.value.delete(id))
})

// 監聽 allDevices 的變化
watch(allDevices, (newDevices) => {
  // 獲取新增的設備 ID，排除手動取消選擇的設備
  const currentDeviceIds = Object.keys(newDevices)
  const newDeviceIds = currentDeviceIds.filter(id => 
    !selectedDevices.value.includes(id) && 
    !manuallyDeselected.value.has(id)
  )
  
  // 將新設備添加到已選擇的列表中
  if (newDeviceIds.length > 0) {
    selectedDevices.value = [...selectedDevices.value, ...newDeviceIds]
  }
}, { deep: true })

// 初始化選中所有設備
onMounted(() => {
  // 初始化選中所有設備
  selectedDevices.value = Object.keys(allDevices.value)
})

// 修改全選/取消全選功能
const selectAllDevices = () => {
  selectedDevices.value = Object.keys(allDevices.value)
  manuallyDeselected.value.clear() // 清空手動取消的記錄
}

const deselectAllDevices = () => {
  const currentIds = Object.keys(allDevices.value)
  currentIds.forEach(id => manuallyDeselected.value.add(id))
  selectedDevices.value = []
}

// 計算排序和過濾後的設備列表
const sortedAndFilteredDevices = computed(() => {
  let devices = Object.entries(allDevices.value)
    .filter(([id]) => selectedDevices.value.includes(id))
    .map(([id, device]) => ({
      id,
      ...device
    }))

  // 根據搜尋條件過濾
  if (searchQuery.value) {
    devices = devices.filter(device => 
      device.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // 根據選擇的方式排序
  devices.sort((a, b) => {
    if (sortBy.value === 'speed') {
      return b.speed - a.speed
    }
    return a.id.localeCompare(b.id)
  })

  // 轉回物件格式
  return Object.fromEntries(
    devices.map(device => [device.id, { ...device }])
  )
})

// 新增關閉離線設備的函數
const removeOfflineDevices = () => {
  Object.entries(allDevices.value).forEach(([id, device]) => {
    if (!checkDeviceActive(device)) {
      removeDevice(id)
    }
  })
}

onBeforeUnmount(() => {
  // 不再需要在這裡斷開 WebSocket
})
</script>

<style scoped>
/* 設備列表動畫 */
.device-list-move,
.device-list-enter-active,
.device-list-leave-active {
  transition: all 0.1s ease;
}

.device-list-enter-from,
.device-list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.device-list-leave-active {
  position: absolute;
}
</style> 