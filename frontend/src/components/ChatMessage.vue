<template>
  <div class="flex" :class="{ 'justify-end': isUser }">
    <div class="flex gap-3 max-w-[80%]" :class="{ 'flex-row-reverse': isUser }">
      <!-- Avatar dengan efek glow -->
      <div class="flex-shrink-0 relative">
        <div v-if="isUser" 
             class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg">
          <i class="ri-user-line text-lg"></i>
        </div>
        <div v-else class="relative">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white shadow-lg">
            <i class="ri-robot-line text-lg"></i>
          </div>
          <!-- Online indicator -->
          <div class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
        </div>
      </div>
      
      <!-- Message Content dengan efek typing -->
      <div class="space-y-1">
        <div :class="isUser ? 'message-bubble-user' : 'message-bubble-ai'">
          <!-- Efek typing untuk pesan AI -->
          <div v-if="!isUser && isTyping" class="flex items-center gap-1 min-w-[60px]">
            <span class="typing-dot" style="animation-delay: 0s"></span>
            <span class="typing-dot" style="animation-delay: 0.2s"></span>
            <span class="typing-dot" style="animation-delay: 0.4s"></span>
          </div>
          <p v-else class="whitespace-pre-wrap leading-relaxed" :class="{ 'text-white': isUser }">
            {{ displayMessage }}
          </p>
        </div>
        
        <!-- Message info dengan icon -->
        <div class="flex items-center gap-2 text-xs" :class="{ 'justify-end': isUser }">
          <span class="text-gray-400">{{ formattedTime }}</span>
          <i v-if="isUser" class="ri-check-double-line text-blue-500"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';

export default {
  name: 'ChatMessage',
  props: {
    message: {
      type: String,
      required: true
    },
    isUser: {
      type: Boolean,
      default: false
    },
    timestamp: {
      type: Date,
      default: () => new Date()
    },
    shouldType: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const displayMessage = ref('');
    const isTyping = ref(false);
    
    const typeMessage = async () => {
      if (!props.shouldType || props.isUser) {
        displayMessage.value = props.message;
        return;
      }
      
      isTyping.value = true;
      displayMessage.value = '';
      
      // Efek typing karakter per karakter
      const words = props.message.split(' ');
      let currentText = '';
      
      for (let i = 0; i < words.length; i++) {
        // Random delay antara 50-150ms per kata
        await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100));
        currentText += (i > 0 ? ' ' : '') + words[i];
        displayMessage.value = currentText;
      }
      
      isTyping.value = false;
    };
    
    watch(() => props.message, () => {
      typeMessage();
    }, { immediate: true });
    
    const formattedTime = props.timestamp.toLocaleTimeString('id-ID', {
      hour: '2-digit',
      minute: '2-digit'
    });
    
    return {
      displayMessage,
      isTyping,
      formattedTime
    };
  }
};
</script>