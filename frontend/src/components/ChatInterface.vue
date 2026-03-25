<template>
  <div class="flex-1 flex flex-col bg-gray-50 overflow-hidden">
    <!-- Messages Container -->
    <div 
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4"
    >
      <div v-if="messages.length === 0" class="h-full flex items-center justify-center">
        <div class="text-center animate-fade-in">
          <div class="w-20 h-20 bg-gradient-to-br from-primary-100 to-primary-200 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="ri-robot-line text-4xl text-primary-600"></i>
          </div>
          <h3 class="text-gray-700 font-medium text-lg mb-2">Halo! Ada yang bisa saya bantu?</h3>
          <p class="text-gray-500 text-sm max-w-md">
            Tanyakan tentang SMK BPPI, jurusan, biaya, atau konsultasi karir
          </p>
          
          <!-- Suggested Questions -->
          <div class="mt-6 grid grid-cols-2 gap-2 max-w-md mx-auto">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              @click="$emit('send-message', suggestion)"
              class="text-xs bg-white hover:bg-gray-50 text-gray-700 px-3 py-2 rounded-lg shadow-sm border border-gray-200 transition-all hover:shadow-md"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="(message, index) in messages" :key="index" class="animate-slide-up">
        <div v-if="message.role === 'user'" class="flex justify-end">
          <div class="max-w-[80%] lg:max-w-[70%]">
            <div class="message-bubble-user px-4 py-2">
              <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
            </div>
            <div class="text-right mt-1">
              <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
            </div>
          </div>
        </div>

        <div v-else class="flex justify-start">
          <div class="max-w-[80%] lg:max-w-[70%]">
            <div class="flex items-start space-x-2">
              <div class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                <i class="ri-robot-line text-white text-sm"></i>
              </div>
              <div class="message-bubble-ai px-4 py-2">
                <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
              </div>
            </div>
            <div class="ml-10 mt-1">
              <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isTyping" class="flex justify-start animate-fade-in">
        <div class="flex items-start space-x-2">
          <div class="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
            <i class="ri-robot-line text-white text-sm"></i>
          </div>
          <div class="bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-md border border-gray-100">
            <div class="typing-indicator">
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
              <span class="typing-dot"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t border-gray-200 bg-white p-4">
      <div class="flex items-end space-x-2">
        <div class="flex-1">
          <textarea
            ref="textareaRef"
            v-model="inputMessage"
            @keydown.enter.prevent="handleSend"
            @input="autoResize"
            placeholder="Ketik pesanmu di sini..."
            rows="1"
            class="w-full px-4 py-2 border border-gray-200 rounded-2xl focus:outline-none focus:border-primary-400 focus:ring-1 focus:ring-primary-400 resize-none transition-all"
            :disabled="isTyping"
          ></textarea>
        </div>
        <button
        @click="handleSend"
        :disabled="!inputMessage.trim() || isTyping"
        class="p-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95"
        >
        <i class="ri-send-plane-fill text-xl"></i>
        </button>
      </div>
      <div class="mt-2 text-center">
        <p class="text-xs text-gray-400">
          Tekan Enter untuk mengirim
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  isTyping: {
    type: Boolean,
    default: false
  },
  sessionId: {
    type: String,
    default: null
  }
})

// Fokus saat pertama kali render
onMounted(() => {
  nextTick(() => {
    textareaRef.value?.focus()
  })
})

const emit = defineEmits(['send-message', 'reset-session'])

const messagesContainer = ref(null)
const textareaRef = ref(null)
const inputMessage = ref('')

const suggestions = [
  'Apa saja jurusan di SMK BPPI?',
  'Berapa biaya SPP?',
  'Info alamat sekolah',
  'Rekomendasi jurusan untuk saya'
]

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTo({
      top: messagesContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

// Auto resize textarea function
const autoResize = () => {
  if (!textareaRef.value) return
  
  // Reset height to auto to get the correct scrollHeight
  textareaRef.value.style.height = 'auto'
  
  // Calculate new height (with max limit of 120px)
  const maxHeight = 120
  const newHeight = Math.min(textareaRef.value.scrollHeight, maxHeight)
  textareaRef.value.style.height = newHeight + 'px'
}

const handleSend = () => {
  const message = inputMessage.value.trim()
  if (!message) return
  
  emit('send-message', message)
  inputMessage.value = ''
  
  // Reset textarea height after sending
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

// Scroll to bottom when messages change
watch(() => props.messages.length, () => {
  scrollToBottom()
})

watch(() => props.isTyping, () => {
  scrollToBottom()
})

watch(
  () => props.isTyping,
  (typing) => {
    nextTick(() => {
      if (!typing && textareaRef.value) {
        textareaRef.value.focus()
      }
    })
  }
)

</script>

<style scoped>
textarea {
  max-height: 120px;
  overflow-y: auto;
  transition: height 0.1s ease;
}

.message-bubble-user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1.5rem;
  border-bottom-right-radius: 0.25rem;
  color: white;
}

.message-bubble-ai {
  background: white;
  border-radius: 1.5rem;
  border-bottom-left-radius: 0.25rem;
  color: #1f2937;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: center;
}

.typing-dot {
  width: 6px;
  height: 6px;
  background-color: #9ca3af;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typingBounce {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-slide-up {
  animation: slide-up 0.3s ease-out;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}
</style>