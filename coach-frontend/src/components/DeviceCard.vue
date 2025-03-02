<template>
  <div class="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 p-2" style="border: 1px solid #e0e0e0;">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-base font-semibold text-gray-900">
        裝置 ID: 
        <span class="font-mono text-blue-600">{{ device_id }}</span>
      </h2>
      <span 
        class="px-2 py-0.5 rounded-full text-xs font-medium"
        :class="deviceStatus.isActive 
          ? 'bg-green-50 text-green-700 ring-1 ring-green-600/20' 
          : 'bg-red-50 text-red-700 ring-1 ring-red-600/20'"
      >
        {{ deviceStatus.isActive ? '活動中' : '離線' }}
      </span>
    </div>

    <div class="bg-gray-50 rounded-lg p-3 mb-3">
      <div class="flex items-center justify-between">
        <div class="text-sm text-gray-600">速度</div>
        <div class="text-xl font-bold text-gray-900">
          {{ device.speed || 0 }}
          <span class="text-xs text-gray-500 ml-1">km/h</span>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between text-xs">
      <div class="text-gray-500">
        <i class="i-carbon-time mr-1"></i>
        最後更新: {{ formattedTime }}
      </div>

      <button
        v-if="!deviceStatus.isActive"
        @click="$emit('remove', device_id)"
        class="
          inline-flex items-center px-2 py-1
          text-xs font-medium text-white 
          bg-red-500 hover:bg-red-600 
          rounded-md transition-colors duration-200
        "
        style="border: 1px solid #999;"
      >
        <i class="i-carbon-close mr-1"></i>
        關閉
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useDevicesStore } from '@/stores/devices'

const store = useDevicesStore()
const { checkDeviceActive } = store

const props = defineProps({
  device_id: {
    type: String,
    required: true
  },
  device: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['remove'])

const statusCheckInterval = ref(null)
const deviceStatus = ref({
  isActive: checkDeviceActive(props.device)
})

function updateStatus() {
  deviceStatus.value.isActive = checkDeviceActive(props.device)
}

const formattedTime = computed(() => {
  if (!props.device.lastUpdate) return '未知'
  return new Date(props.device.lastUpdate).toLocaleTimeString('zh-TW', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    fractionalSecondDigits: 3
  })
})

onMounted(() => {
  statusCheckInterval.value = setInterval(() => {
    updateStatus()
  }, 1000)
})

onBeforeUnmount(() => {
  if (statusCheckInterval.value) {
    clearInterval(statusCheckInterval.value)
  }
})
</script> 