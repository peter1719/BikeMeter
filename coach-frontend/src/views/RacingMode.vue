<template>
  <div class="p-2 max-w-[1920px] mx-auto">
    <div class="mb-8">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">競速模式</h1>
          <p class="text-gray-600">設定距離挑戰，實時追蹤參賽者進度</p>
        </div>

        <div class="flex gap-4 items-center">
          <!-- 比賽設置區域 -->
          <div v-if="!raceStarted && !countdownActive && !raceEnded" class="flex gap-4">
            <div class="flex items-center gap-2">
              <label class="text-gray-700">競賽距離 (公里):</label>
              <input
                v-model.number="raceDistance"
                type="number"
                min="0.1"
                step="0.1"
                class="px-3 py-2 border rounded-lg w-24"
              />
            </div>
            
            <button
              @click="showDeviceSelector = !showDeviceSelector"
              class="px-3 py-2 border rounded-lg bg-blue-500 text-white hover:bg-blue-600"
            >
              選擇參賽設備
            </button>
            
            <button
              @click="startRace"
              :disabled="selectedDevices.length === 0 || raceDistance <= 0"
              class="px-6 py-2 border rounded-lg bg-green-500 text-white hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              開始競賽
            </button>
          </div>

          <!-- 倒數計時器 -->
          <div v-if="countdownActive" class="flex items-center justify-center">
            <div class="text-5xl font-bold text-red-500">{{ countdown }}</div>
          </div>

          <!-- 比賽進行中狀態 -->
          <div v-if="raceStarted && !countdownActive" class="flex gap-4">
            <div class="px-4 py-2 bg-yellow-100 border border-yellow-300 rounded-lg">
              <span class="font-bold">競賽進行中</span> - 距離: {{ raceDistance }}公里
            </div>
            
            <button
              @click="endRace"
              class="px-4 py-2 border rounded-lg bg-red-500 text-white hover:bg-red-600"
            >
              結束競賽
            </button>
          </div>
          
          <!-- 比賽已結束但結果仍在顯示 -->
          <div v-if="raceEnded && !raceStarted" class="flex gap-4">
            <div class="px-4 py-2 bg-green-100 border border-green-300 rounded-lg">
              <span class="font-bold">競賽已結束</span> - 距離: {{ raceDistance }}公里
            </div>
            
            
            <button
              @click="confirmCloseResults"
              class="px-4 py-2 border rounded-lg bg-blue-500 text-white hover:bg-blue-600"
            >
              關閉結果
            </button>
          </div>
        </div>
      </div>

      <!-- 設備選擇器面板 -->
      <div v-if="showDeviceSelector && !raceStarted && !raceEnded" class="mt-4 bg-white rounded-lg shadow p-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold">選擇參賽設備</h3>
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
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <label
            v-for="(device, id) in connectedDevices"
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

    <!-- 競賽結果區域 -->
    <div v-if="raceStarted || countdownActive || raceEnded" class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-bold">競賽排行榜</h2>
        
        <!-- 添加顯示模式切換 -->
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">顯示模式:</span>
          <button
            @click="displayMode = 'detailed'"
            :class="['px-3 py-1 text-sm border rounded', 
                    displayMode === 'detailed' ? 'bg-blue-100 border-blue-300' : 'hover:bg-gray-100']"
          >
            詳細
          </button>
          <button
            @click="displayMode = 'compact'"
            :class="['px-3 py-1 text-sm border rounded', 
                    displayMode === 'compact' ? 'bg-blue-100 border-blue-300' : 'hover:bg-gray-100']"
          >
            緊湊
          </button>
        </div>
      </div>
      
      <!-- 排序按鈕 -->
      <div class="flex gap-4 mb-4">
        <button
          @click="sortBy = 'progress'"
          :class="['px-3 py-1 border rounded', sortBy === 'progress' ? 'bg-blue-100 border-blue-300' : 'hover:bg-gray-100']"
        >
          按進度排序
        </button>
        <button
          @click="sortBy = 'id'"
          :class="['px-3 py-1 border rounded', sortBy === 'id' ? 'bg-blue-100 border-blue-300' : 'hover:bg-gray-100']"
        >
          按ID排序
        </button>
      </div>
      
      <!-- 詳細顯示模式 -->
      <div v-if="displayMode === 'detailed'" class="max-h-[70vh] overflow-y-auto">
        <transition-group name="rank-change" tag="div">
          <div v-for="(participant, index) in displayParticipants" :key="participant.id" class="mb-3 border-b pb-3">
            <div class="flex justify-between items-center mb-1">
              <div class="flex items-center">
                <div class="w-6 h-6 flex items-center justify-center bg-gray-200 rounded-full mr-2 text-sm font-bold">
                  {{ index + 1 }}
                </div>
                <div class="text-sm font-medium w-20 truncate">{{ participant.id }}</div>
              </div>
              <div class="text-sm text-gray-500">
                {{ (participant.distance).toFixed(2) }} / {{ raceDistance }} 公里
                ({{ (participant.progress * 100).toFixed(0) }}%)
              </div>
              <div class="flex flex-col items-end">
                <div class="text-sm font-semibold">
                  速度: {{ participant.speed.toFixed(1) }} km/h
                </div>
                <div v-if="participant.finished" class="text-xs text-green-600">
                  完賽時間: {{ formatFinishTime(participant.finishTime) }}
                </div>
              </div>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-4">
              <div 
                class="h-4 rounded-full" 
                :class="{'bg-green-500': participant.finished, 'bg-blue-500': !participant.finished}"
                :style="{ width: `${participant.progress * 100}%` }"
              ></div>
            </div>
          </div>
        </transition-group>
      </div>
      
      <!-- 緊湊顯示模式 -->
      <div v-if="displayMode === 'compact'" class="max-h-[70vh] overflow-y-auto">
        <transition-group name="rank-change" tag="div" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">
          <div 
            v-for="(participant, index) in displayParticipants" 
            :key="participant.id" 
            class="border rounded p-2 flex flex-col"
            :class="{'bg-yellow-50': index < 3 && sortBy === 'progress'}"
          >
            <div class="flex items-center mb-1">
              <div class="w-6 h-6 flex items-center justify-center rounded-full mr-2 text-xs font-bold"
                   :class="[
                     sortBy === 'progress' ? (
                       index === 0 ? 'bg-yellow-200 text-yellow-800' : 
                       index === 1 ? 'bg-gray-200 text-gray-800' : 
                       index === 2 ? 'bg-orange-200 text-orange-800' : 
                       'bg-gray-100 text-gray-600'
                     ) : 'bg-gray-100 text-gray-600'
                   ]">
                {{ index + 1 }}
              </div>
              <div class="flex-1">
                <div class="flex items-center">
                  <div class="text-xs font-medium truncate">{{ participant.id }}</div>
                  <div v-if="participant.finished" class="ml-1 px-1 text-xs bg-green-100 text-green-800 rounded">完賽</div>
                </div>
                <div class="flex justify-between items-center">
                  <div class="text-xs text-gray-500">{{ (participant.progress * 100).toFixed(0) }}%</div>
                  <div class="text-xs font-semibold">{{ participant.speed.toFixed(1) }} km/h</div>
                </div>
              </div>
            </div>
            
            <!-- 添加小型進度條 -->
            <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div 
                class="h-2 rounded-full transition-all duration-300" 
                :style="{ width: `${participant.progress * 100}%` }"
                :class="{
                  'bg-green-500': participant.finished,
                  'bg-blue-500': !participant.finished && participant.progress > 0,
                  'bg-gray-400': participant.progress === 0
                }"
              ></div>
            </div>
          </div>
        </transition-group>
      </div>
    </div>
    
    <!-- 未開始比賽時顯示說明 -->
    <div v-if="!raceStarted && !countdownActive && !raceEnded" class="bg-white rounded-lg shadow p-4">
      <h2 class="text-xl font-bold mb-4">競賽說明</h2>
      <ul class="list-disc pl-5 space-y-2">
        <li>選擇欲參與競賽的設備 (最多 100 台)</li>
        <li>設定競賽距離後點擊「開始競賽」</li>
        <li>競賽開始後，將不能新增更多設備</li>
        <li>系統會實時追蹤所有參賽者的進度並顯示排名</li>
      </ul>
    </div>

    <!-- 確認對話框 -->
    <div v-if="showConfirmDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">關閉結果</h3>
        <p class="mb-6">是否要在關閉前儲存結果為CSV檔案？</p>
        <div class="flex justify-end gap-4">
          <button 
            @click="closeWithoutSave" 
            class="px-4 py-2 border rounded-lg hover:bg-gray-100"
          >
            直接關閉
          </button>
          <button 
            @click="saveAndClose" 
            class="px-4 py-2 border rounded-lg bg-green-500 text-white hover:bg-green-600"
          >
            儲存並關閉
          </button>
          <button 
            @click="cancelClose" 
            class="px-4 py-2 border rounded-lg bg-blue-500 text-white hover:bg-blue-600"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useDevicesStore } from '@/stores/devices'
import { storeToRefs } from 'pinia'

const store = useDevicesStore()
const { checkDeviceActive } = store
const { allDevices, deviceCount } = storeToRefs(store)

// 比賽設置
const raceDistance = ref(5) // 預設5公里
const selectedDevices = ref([])
const showDeviceSelector = ref(false)
const raceStarted = ref(false)
const countdownActive = ref(false)
const countdown = ref(3)
const sortBy = ref('progress')
const raceEnded = ref(false)
const displayMode = ref('detailed') // 新增：顯示模式（詳細/緊湊）

// 參賽者數據
const participants = ref({})
// 用於顯示的參賽者排序結果（每秒更新一次）
const displayParticipants = ref([])

// 添加確認對話框狀態
const showConfirmDialog = ref(false)

// 計算出目前連接的設備
const connectedDevices = computed(() => {
  const devices = {}
  Object.entries(allDevices.value).forEach(([id, device]) => {
    if (checkDeviceActive(device)) {
      devices[id] = device
    }
  })
  return devices
})

// 計算排序後的參賽者列表（但不直接用於顯示）
const sortedParticipants = computed(() => {
  let result = Object.entries(participants.value).map(([id, data]) => ({
    id,
    ...data
  }))
  
  if (sortBy.value === 'progress') {
    // 新的排序邏輯：已完賽者按完賽時間排序，未完賽者按進度排序
    result.sort((a, b) => {
      // 如果兩者都已完賽，按完賽時間排序
      if (a.finished && b.finished) {
        return a.finishTime - b.finishTime; // 較早完成的排前面
      }
      // 已完賽者排在未完賽者前面
      if (a.finished && !b.finished) return -1;
      if (!a.finished && b.finished) return 1;
      
      // 兩者都未完賽，按進度排序
      return b.progress - a.progress;
    })
  } else if (sortBy.value === 'id') {
    result.sort((a, b) => a.id.localeCompare(b.id))
  }
  
  return result
})

// 監視所有參賽者是否都已完成比賽
watch(participants, (newParticipants) => {
  // 如果比賽未開始或已結束，不執行檢查
  if (!raceStarted.value || raceEnded.value) return
  
  // 檢查是否有參賽者
  const participantCount = Object.keys(newParticipants).length
  if (participantCount === 0) return
  
  // 檢查所有參賽者是否都已完成
  const finishedCount = Object.values(newParticipants).filter(p => p.finished).length
  
  // 如果所有參賽者都已完成，自動結束競賽
  if (finishedCount === participantCount) {
    console.log('所有參賽者都已完成比賽，自動結束競賽')
    endRace()
  }
}, { deep: true })

// 移除 WebSocket 相關初始化
onMounted(() => {
  // 只保留需要的初始化邏輯
})

// 開始比賽
const startRace = () => {
  if (selectedDevices.value.length === 0 || raceDistance.value <= 0) return
  
  // 獲取當前時間作為比賽開始時間
  const raceStartTime = Date.now()
  
  // 初始化參賽者數據
  participants.value = {}
  selectedDevices.value.forEach(id => {
    participants.value[id] = {
      distance: 0,
      speed: 0,
      progress: 0,
      finished: false,
      lastUpdateTime: raceStartTime, // 初始化最後更新時間為比賽開始時間
      finishTime: null // 完賽時間，初始為null
    }
  })
  
  // 重置狀態
  raceEnded.value = false
  
  // 開始倒數
  countdownActive.value = true
  countdown.value = 3
  
  // 初始化顯示參賽者
  displayParticipants.value = []
  
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      countdownActive.value = false
      raceStarted.value = true
      // 開始處理速度數據
      startProcessingSpeed(raceStartTime)
      // 開始定時更新排名顯示
      startRankingUpdates()
    }
  }, 1000)
}

// 每秒更新一次排名顯示
const startRankingUpdates = () => {
  // 立即進行第一次更新
  displayParticipants.value = [...sortedParticipants.value]
  
  // 設置定時器，每秒更新一次
  const rankingTimer = setInterval(() => {
    if (!raceStarted.value && !raceEnded.value) {
      // 如果比賽已結束且結果已關閉，停止更新
      clearInterval(rankingTimer)
      return
    }
    
    // 更新顯示的參賽者排序
    displayParticipants.value = [...sortedParticipants.value]
  }, 1000)
  
  // 在組件卸載時清除定時器
  onBeforeUnmount(() => {
    clearInterval(rankingTimer)
  })
}

// 計算距離和進度
const startProcessingSpeed = (raceStartTime) => {
  // 監聽設備數據更新
  watch(allDevices, (newDevices) => {
    if (!raceStarted.value) return
    
    const currentTime = Date.now()
    
    selectedDevices.value.forEach(id => {
      if (participants.value[id] && newDevices[id]) {
        const device = newDevices[id]
        // 更新速度
        participants.value[id].speed = device.speed || 0
        
        // 獲取當前時間戳（毫秒）- 優先使用設備提供的時間戳，否則使用系統時間
        const currentTimestamp = device.timestamp || currentTime
        
        // 獲取上次更新時間
        const lastUpdateTime = participants.value[id].lastUpdateTime
        
        // 計算時間差（秒），並確保在合理範圍內（最大5秒）
        const timeDiffSeconds = Math.min((currentTimestamp - lastUpdateTime) / 1000, 5)
        
        // 只有當時間差為正且合理時才計算距離
        if (timeDiffSeconds > 0 && timeDiffSeconds <= 5) {
          // 計算行駛距離增量 (km)
          const distanceIncrement = ((device.speed || 0) * timeDiffSeconds) / 3600
          
          // 更新距離和進度
          if (!participants.value[id].finished) {
            participants.value[id].distance += distanceIncrement
            participants.value[id].progress = Math.min(participants.value[id].distance / raceDistance.value, 1)
            
            // 檢查是否完成比賽
            if (participants.value[id].progress >= 1) {
              participants.value[id].finished = true
              participants.value[id].progress = 1
              // 記錄完賽時間（精確到毫秒）
              participants.value[id].finishTime = currentTimestamp
            }
          }
        }
        
        // 更新最後更新時間
        participants.value[id].lastUpdateTime = currentTimestamp
      }
    })
  }, { deep: true })
}

// 確認關閉結果
const confirmCloseResults = () => {
  showConfirmDialog.value = true
}

// 取消關閉
const cancelClose = () => {
  showConfirmDialog.value = false
}

// 直接關閉不儲存
const closeWithoutSave = () => {
  showConfirmDialog.value = false
  closeResults()
}

// 儲存並關閉
const saveAndClose = () => {
  saveResults()
  showConfirmDialog.value = false
  closeResults()
}

// 儲存結果為CSV
const saveResults = () => {
  // 獲取排序後的參賽者數據
  const sortedData = [...sortedParticipants.value]
  
  // 創建CSV內容
  let csvContent = "排名,ID,距離(公里),進度(%),完賽時間,完賽狀態\n"
  
  sortedData.forEach((participant, index) => {
    // 格式化完賽時間（如果已完成）
    let finishTimeStr = '未完成'
    let finishStatus = '未完成'
    
    if (participant.finished && participant.finishTime) {
      const finishDate = new Date(participant.finishTime)
      // 格式化為時:分:秒.毫秒
      finishTimeStr = finishDate.toLocaleTimeString() + '.' + 
                      finishDate.getMilliseconds().toString().padStart(3, '0')
      finishStatus = '已完成'
    }
    
    // 添加一行數據
    csvContent += `${index + 1},${participant.id},${participant.distance.toFixed(2)},${(participant.progress * 100).toFixed(0)}%,${finishTimeStr},${finishStatus}\n`
  })
  
  // 創建Blob對象
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  
  // 創建下載鏈接
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  // 設置下載屬性
  const date = new Date().toISOString().slice(0, 10)
  link.setAttribute('href', url)
  link.setAttribute('download', `競賽結果_${date}.csv`)
  link.style.visibility = 'hidden'
  
  // 添加到文檔並觸發下載
  document.body.appendChild(link)
  link.click()
  
  // 清理
  document.body.removeChild(link)
}

// 修改結束競賽函數，記錄完賽時間
const endRace = () => {
  raceStarted.value = false
  raceEnded.value = true
  
  // 記錄結束時間
  const endTime = Date.now()
  
  // 為每個參賽者添加完賽時間（如果已完成但尚未記錄時間）
  Object.values(participants.value).forEach(participant => {
    if (participant.finished && !participant.finishTime) {
      participant.finishTime = endTime
    }
  })
  
  // 最後更新一次排名顯示
  displayParticipants.value = [...sortedParticipants.value]
}

// 關閉結果
const closeResults = () => {
  raceEnded.value = false
  participants.value = {}
  displayParticipants.value = []
}

// 修改取消比賽函數名稱和實現
const cancelRace = closeResults

// 全選設備
const selectAllDevices = () => {
  selectedDevices.value = Object.keys(connectedDevices.value)
}

// 取消全選設備
const deselectAllDevices = () => {
  selectedDevices.value = []
}

// 移除 WebSocket 斷開連接
onBeforeUnmount(() => {
  // 不再需要在這裡斷開 WebSocket
})

// 格式化完賽時間顯示
const formatFinishTime = (timestamp) => {
  if (!timestamp) return '未完成';
  
  const date = new Date(timestamp);
  // 格式化為時:分:秒.毫秒
  return date.toLocaleTimeString() + '.' + 
         date.getMilliseconds().toString().padStart(3, '0');
}
</script>

<style scoped>
/* 進度條動畫 */
.bg-blue-500 {
  transition: width 0.5s ease-in-out;
}

/* 排行榜條目動畫 */
.mb-3 {
  transition: all 0.3s ease;
}

/* 倒數計時動畫 */
.text-5xl {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

/* 排名變換動畫 */
.rank-change-move {
  transition: transform 0.5s ease;
}

/* 確保項目在移動時不會被其他項目覆蓋 */
.rank-change-leave-active {
  position: absolute;
}

/* 新項目進入的動畫 */
.rank-change-enter-active,
.rank-change-leave-active {
  transition: all 0.5s;
}

.rank-change-enter-from,
.rank-change-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>