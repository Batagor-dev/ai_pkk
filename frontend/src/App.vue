<template>
  <div class="h-screen w-screen overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
    <!-- Full Screen Chat Container -->
    <div class="h-full w-full flex flex-col">
      <!-- Header with Glassmorphism Effect -->
      <div class="glass-header px-6 py-4 flex items-center justify-between z-10">
        <div class="flex items-center space-x-4">
          <div class="relative">
            <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center shadow-lg animate-pulse-slow">
              <i class="ri-chat-smile-2-line text-white text-2xl"></i>
            </div>
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900 animate-ping"></div>
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900"></div>
          </div>
          <div>
            <h1 class="text-white font-bold text-xl md:text-2xl tracking-tight">
              KANUT<span class="text-primary-400"> AI</span>
            </h1>
            <p class="text-gray-300 text-xs md:text-sm flex items-center">
              <span class="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
              SMK BPPI Virtual Assistant • Always Here for You
            </p>
          </div>
        </div>
        
        <div class="flex items-center space-x-2">
          <!-- Status Badge -->
          <div class="hidden md:flex items-center space-x-2 px-3 py-1.5 bg-white/10 rounded-full backdrop-blur-sm">
            <i class="ri-cpu-line text-primary-400 text-sm"></i>
            <span class="text-white text-xs">AI Ready</span>
          </div>
          
          <!-- Reset Button -->
          <button 
            @click="resetSession"
            class="relative group px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all duration-300"
            title="Reset Session"
          >
            <i class="ri-refresh-line text-white text-xl group-hover:rotate-180 transition-transform duration-500"></i>
          </button>
          
          <!-- Fullscreen Button -->
          <button 
            @click="toggleFullscreen"
            class="px-3 py-2 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm transition-all duration-300"
            title="Fullscreen"
          >
            <i :class="isFullscreen ? 'ri-fullscreen-exit-line' : 'ri-fullscreen-line'" class="text-white text-xl"></i>
          </button>
        </div>
      </div>

      <!-- Chat Interface -->
      <ChatInterface 
        ref="chatInterface"
        :messages="messages"
        :is-typing="isTyping"
        :session-id="sessionId"
        @send-message="sendMessage"
        @reset-session="resetSession"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ChatInterface from './components/ChatInterface.vue'
import { useChat } from './composables/useChat'

const { 
  messages, 
  isTyping, 
  sessionId,
  sendMessage, 
  resetSession 
} = useChat()

const chatInterface = ref(null)
const isFullscreen = ref(false)

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// Listen for fullscreen change
onMounted(() => {
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement
  })
})
</script>

<style scoped>
.glass-header {
  background: rgba(17, 24, 39, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes pulse-slow {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
    transform: scale(1.02);
  }
}

.animate-pulse-slow {
  animation: pulse-slow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>