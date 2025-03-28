<template>
  <div class="w-full">
    <!-- 未連接狀態：顯示完整表單 -->
    <div v-if="!isConnected" class="bg-gray-50 p-4 rounded-lg shadow mb-5">
      <form @submit.prevent="submitForm" class="flex items-center gap-3">
        <div class="flex items-center flex-1">
          <label for="deviceId" class="font-bold mr-3 whitespace-nowrap">設備 ID：</label>
          <div class="relative flex-1">
            <input 
              type="text" 
              id="deviceId" 
              v-model="deviceId" 
              placeholder="請輸入設備 ID" 
              maxlength="5"
              required
              class="input-field"
            />
            <div v-if="inputError" class="text-red-500 text-xs absolute left-0 mt-1">{{ inputError }}</div>
          </div>
        </div>
        <button type="submit" :disabled="loading || !!inputError" class="btn btn-primary whitespace-nowrap flex-shrink-0">
          {{ loading ? '連接中...' : '連接裝置' }}
        </button>
      </form>
      <div class="text-gray-500 text-xs mt-2">請輸入 1-5 位數字</div>
    </div>
    
    <!-- 已連接狀態：只顯示切換按鈕 -->
    <div v-else class="flex justify-between items-center bg-gray-50 p-4 rounded-lg shadow mb-5">
      <div class="text-base">
        已連接到設備：<span class="font-bold text-green-500">{{ formattedDeviceId }}</span>
      </div>
      <button @click="disconnectDevice" class="btn btn-secondary">
        更改連接裝置
      </button>
    </div>
    
    <!-- 數據顯示區域 - 新設計 -->
    <div v-if="isConnected" class="bg-white p-5 rounded-lg shadow">
      <div v-if="error" class="flex items-center justify-between text-red-500 p-3 bg-red-100 rounded mb-4">
        {{ error }}
        <button @click="reconnect" class="btn btn-blue text-sm py-1 px-3 ml-3">重新連接</button>
      </div>
      
      <div v-else class="data-container">
        <!-- 速度顯示 -->
        <div class="flex justify-between items-center border-b pb-3 mb-3">
          <div class="text-gray-700">速度</div>
          <div class="text-right">
            <span class="text-2xl font-bold">{{ numericSpeed }}</span>
            <span class="text-gray-500 ml-1">km/h</span>
          </div>
        </div>
        
        <!-- 更新時間顯示 -->
        <div class="text-gray-500 text-sm text-right">
          最後更新: {{ formattedTime }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, watch, computed } from 'vue';

const deviceId = ref('');
const formattedDeviceId = ref('');
const speed = ref('-');
const timestamp = ref('-');
const loading = ref(false);
const error = ref('');
const inputError = ref('');
const intervalId = ref(null);
const isConnected = ref(false);

// 計算屬性：提取數字部分的速度
const numericSpeed = computed(() => {
  if (speed.value === '無數據' || speed.value === '-') {
    return '-';
  }
  
  // 從 "25.5 km/h" 中提取 "25.5"
  const match = speed.value.match(/^([\d.]+)/);
  return match ? match[1] : '-';
});

// 計算屬性：格式化時間顯示
const formattedTime = computed(() => {
  if (timestamp.value === '無數據' || timestamp.value === '-') {
    return '無數據';
  }
  
  return timestamp.value;
});

// 監聽輸入變化，進行實時驗證
watch(deviceId, (newValue) => {
  validateInput(newValue);
});

// 驗證輸入
const validateInput = (value) => {
  if (!value) {
    inputError.value = '';
    return;
  }
  
  // 檢查是否只包含數字
  if (!/^\d*$/.test(value)) {
    inputError.value = '請只輸入數字';
    return;
  }
  
  // 檢查長度
  if (value.length > 5) {
    inputError.value = '最多輸入 5 位數字';
    return;
  }
  
  inputError.value = '';
};

// 格式化時間戳記
const formatTimestamp = (isoTimestamp) => {
  if (isoTimestamp === -1) return '無數據';
  try {
    const date = new Date(isoTimestamp);
    // 使用更簡潔的時間格式：上午/下午 HH:MM:SS.mmm
    return `上午${date.toLocaleTimeString('zh-TW', { hour12: false })}`;
  } catch (e) {
    return '無效時間';
  }
};

// 獲取設備狀態
const fetchDeviceStatus = async () => {
  if (!formattedDeviceId.value) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    const response = await fetch(`/api/device/status?device_id=${formattedDeviceId.value}`);
    if (!response.ok) {
      throw new Error('無法獲取設備數據');
    }
    
    const data = await response.json();
    
    if (data.speed === -1 && data.timestamp === -1) {
      speed.value = '無數據';
      timestamp.value = '無數據';
    } else {
      speed.value = `${data.speed} km/h`;
      timestamp.value = formatTimestamp(data.timestamp);
    }
  } catch (e) {
    error.value = e.message || '發生錯誤';
    speed.value = '-';
    timestamp.value = '-';
  } finally {
    loading.value = false;
  }
};

// 提交表單 - 連接設備
const submitForm = () => {
  // 再次驗證輸入
  validateInput(deviceId.value);
  if (inputError.value) return;
  
  // 將輸入的 ID 轉換為 bike_XXX 格式
  const paddedId = deviceId.value.padStart(3, '0');
  formattedDeviceId.value = `bike_${paddedId}`;
  
  // 獲取設備狀態
  fetchDeviceStatus();
  
  // 清除之前的定時器
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
  
  // 設置定時器，每 300 毫秒更新一次數據
  intervalId.value = setInterval(fetchDeviceStatus, 300);
  
  // 設置為已連接狀態
  isConnected.value = true;
};

// 斷開連接
const disconnectDevice = () => {
  // 清除定時器
  if (intervalId.value) {
    clearInterval(intervalId.value);
    intervalId.value = null;
  }
  
  // 重置狀態
  isConnected.value = false;
  formattedDeviceId.value = '';
  speed.value = '-';
  timestamp.value = '-';
  error.value = '';
};

// 重新連接
const reconnect = () => {
  error.value = '';
  fetchDeviceStatus();
};

// 組件卸載時清除定時器
onUnmounted(() => {
  if (intervalId.value) {
    clearInterval(intervalId.value);
  }
});
</script>

<style scoped>
/* 自定義樣式補充 */
.data-container {
  padding: 10px;
}

@media (max-width: 480px) {
  .input-field {
    font-size: 14px;
    padding: 8px;
  }
  
  .btn {
    font-size: 14px;
    padding: 8px 12px;
  }
}
</style> 