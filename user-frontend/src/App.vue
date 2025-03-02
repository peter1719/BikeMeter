<script setup>
import BikeSpeedDashboard from './components/BikeSpeedDashboard.vue';
</script>

<template>
  <div class="max-w-800px mx-auto p-5 font-sans">
    <header class="text-center mb-8">
      <h1 class="text-2xl font-bold text-gray-800">腳踏車運動儀表板</h1>
    </header>
    
    <main class="mb-10">
      <BikeSpeedDashboard />
    </main>
  </div>
</template>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Microsoft JhengHei', Arial, sans-serif;
}

header {
  text-align: center;
  margin-bottom: 30px;
}

h1 {
  color: #2c3e50;
}

main {
  margin-bottom: 40px;
}

footer {
  text-align: center;
  color: #6c757d;
  font-size: 14px;
  margin-top: 40px;
}
</style>
