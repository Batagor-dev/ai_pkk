<template>
  <div class="chat-container">
    <!-- Header dengan efek glass -->
    <div class="glass-effect rounded-2xl shadow-lg mb-4">
      <div class="flex items-center justify-between p-4">
        <div class="flex items-center gap-4">
          <!-- Logo dengan animasi -->
          <div class="relative">
            <div class="w-12 h-12 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg hover-scale">
              <span class="text-white text-2xl font-bold">K</span>
            </div>
            <div class="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
          </div>
          
          <div>
            <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              KANUT AI
            </h1>
            <div class="flex items-center gap-2 text-sm">
              <span class="text-gray-500">Terminal AI Engine</span>
              <span class="w-1 h-1 bg-gray-300 rounded-full"></span>
              <div class="flex items-center gap-1">
                <span class="relative flex h-2 w-2">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span class="text-gray-600">{{ statusText }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Action buttons -->
        <div class="flex items-center gap-2">
          <button @click="showSettings = !showSettings" 
                  class="p-2 hover:bg-gray-100 rounded-lg transition-colors relative group">
            <i class="ri-settings-3-line text-xl text-gray-600"></i>
            <span class="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              Pengaturan
            </span>
          </button>
          
          <button @click="resetChat" 
                  class="p-2 hover:bg-red-50 rounded-lg transition-colors relative group">
            <i class="ri-refresh-line text-xl text-red-500"></i>
            <span class="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              Reset Chat
            </span>
          </button>
        </div>
      </div>
      
      <!-- Settings panel (toggle) -->
      <div v-if="showSettings" class="border-t border-gray-200 p-4 bg-gray-50/50">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700">Efek Typing</span>
          <button @click="typingEffect = !typingEffect" 
                  class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors"
                  :class="typingEffect ? 'bg-blue-600' : 'bg-gray-300'">
            <span class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                  :class="typingEffect ? 'translate-x-6' : 'translate-x-1'"></span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="flex-1 flex gap-4 overflow-hidden">
      <!-- Chat Area -->
      <div class="flex-1 flex flex-col bg-white/60 backdrop-blur-sm rounded-2xl shadow-lg overflow-hidden border border-white/20">
        <!-- Messages -->
        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4 scroll-smooth">
          <ChatMessage
            v-for="(msg, index) in messages"
            :key="index"
            :message="msg.content"
            :is-user="msg.role === 'user'"
            :timestamp="msg.timestamp"
            :should-type="msg.role === 'assistant' && typingEffect && index === messages.length - 1"
          />
          <TypingIndicator v-if="isTyping" />
        </div>
        
        <!-- Input Area dengan efek glass -->
        <div class="glass-effect border-t border-gray-200 p-4">
          <!-- Quick Actions dengan icon -->
          <div class="flex gap-2 mb-3 flex-wrap">
            <button
              v-for="action in quickActions"
              :key="action.text"
              @click="quickActionClick(action.text)"
              class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition-all hover:shadow-md flex items-center gap-2 group"
            >
              <i :class="action.icon" class="text-blue-500 group-hover:scale-110 transition-transform"></i>
              {{ action.label }}
            </button>
          </div>
          
          <div class="flex gap-3">
            <div class="flex-1 relative">
              <input
                v-model="newMessage"
                @keyup.enter="sendMessage"
                type="text"
                placeholder="Ketik pesan... (Enter untuk kirim)"
                class="w-full px-5 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12 shadow-sm"
                :disabled="isTyping"
              />
              <div class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                <i class="ri-edit-line"></i>
              </div>
            </div>
            
            <button
              @click="sendMessage"
              :disabled="!newMessage.trim() || isTyping"
              class="px-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 group"
            >
              <span>Kirim</span>
              <i class="ri-send-plane-fill group-hover:translate-x-1 transition-transform"></i>
            </button>
          </div>
          
          <!-- Typing hint -->
          <div class="mt-2 text-xs text-gray-400 flex items-center gap-2">
            <i class="ri-information-line"></i>
            <span>Tekan Enter untuk mengirim • Shift + Enter untuk baris baru</span>
          </div>
        </div>
      </div>
      
      <!-- BPPI Info Sidebar (toggle) -->
      <div v-if="showBPPI" class="w-80 overflow-y-auto">
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-5 border border-white/20">
          <div class="flex items-center justify-between mb-4">
            <h2 class="font-bold text-lg flex items-center gap-2">
              <i class="ri-school-line text-blue-600"></i>
              <span class="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                SMK BPPI
              </span>
            </h2>
            <button @click="showBPPI = false" class="text-gray-400 hover:text-gray-600">
              <i class="ri-close-line text-xl"></i>
            </button>
          </div>
          
          <!-- Quick info cards -->
          <div class="space-y-3">
            <div @click="quickActionClick('info bppi')" 
                 class="p-3 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl cursor-pointer hover:shadow-md transition-all group">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white group-hover:scale-110 transition-transform">
                  <i class="ri-information-line"></i>
                </div>
                <div>
                  <p class="font-medium text-gray-800">Info Umum</p>
                  <p class="text-xs text-gray-500">Profil sekolah</p>
                </div>
              </div>
            </div>
            
            <div @click="quickActionClick('jurusan bppi')" 
                 class="p-3 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl cursor-pointer hover:shadow-md transition-all group">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center text-white group-hover:scale-110 transition-transform">
                  <i class="ri-book-open-line"></i>
                </div>
                <div>
                  <p class="font-medium text-gray-800">Jurusan</p>
                  <p class="text-xs text-gray-500">RPL, TKJ, Akuntansi</p>
                </div>
              </div>
            </div>
            
            <div @click="quickActionClick('berapa spp bppi')" 
                 class="p-3 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl cursor-pointer hover:shadow-md transition-all group">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center text-white group-hover:scale-110 transition-transform">
                  <i class="ri-money-dollar-circle-line"></i>
                </div>
                <div>
                  <p class="font-medium text-gray-800">Biaya</p>
                  <p class="text-xs text-gray-500">SPP & Pendaftaran</p>
                </div>
              </div>
            </div>
            
            <div @click="quickActionClick('kontak bppi')" 
                 class="p-3 bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl cursor-pointer hover:shadow-md transition-all group">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center text-white group-hover:scale-110 transition-transform">
                  <i class="ri-contacts-line"></i>
                </div>
                <div>
                  <p class="font-medium text-gray-800">Kontak</p>
                  <p class="text-xs text-gray-500">Telepon & Email</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Toggle BPPI button -->
          <button @click="showBPPI = false" 
                  class="mt-4 w-full py-2 text-sm text-gray-500 hover:text-gray-700 flex items-center justify-center gap-1">
            <i class="ri-arrow-left-s-line"></i>
            <span>Sembunyikan</span>
          </button>
        </div>
      </div>
      
      <!-- Show BPPI button (when hidden) -->
      <button v-if="!showBPPI" @click="showBPPI = true"
              class="fixed right-4 top-1/2 transform -translate-y-1/2 bg-white rounded-l-xl shadow-lg p-3 border border-r-0 border-gray-200 hover:bg-gray-50 group">
        <div class="flex items-center gap-2">
          <i class="ri-school-line text-blue-600 text-xl"></i>
          <span class="text-sm font-medium text-gray-700">Info BPPI</span>
          <i class="ri-arrow-right-s-line group-hover:translate-x-1 transition-transform"></i>
        </div>
      </button>
    </div>
    
    <!-- Footer -->
    <div class="mt-4 text-center text-xs text-gray-400 flex items-center justify-center gap-4">
      <span>© 2024 KANUT AI</span>
      <span class="w-1 h-1 bg-gray-300 rounded-full"></span>
      <span>Powered by OpenRouter</span>
      <span class="w-1 h-1 bg-gray-300 rounded-full"></span>
      <span>v1.0.0</span>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue';
import ChatMessage from '../components/ChatMessage.vue';
import TypingIndicator from '../components/TypingIndicator.vue';
import { chatService, healthService } from '../services/api';

export default {
  name: 'ChatView',
  components: {
    ChatMessage,
    TypingIndicator,
  },
  setup() {
    const messages = ref([]);
    const newMessage = ref('');
    const isTyping = ref(false);
    const showSettings = ref(false);
    const showBPPI = ref(true);
    const typingEffect = ref(true);
    const messagesContainer = ref(null);
    const statusText = ref('Offline');
    
    // Quick actions dengan icon Remix
    const quickActions = [
      { label: 'Info BPPI', text: 'info bppi', icon: 'ri-school-line' },
      { label: 'Jurusan', text: 'jurusan bppi', icon: 'ri-book-open-line' },
      { label: 'Biaya', text: 'berapa spp bppi', icon: 'ri-money-dollar-circle-line' },
      { label: 'Kontak', text: 'kontak bppi', icon: 'ri-contacts-line' },
      { label: 'Rekomendasi Jurusan', text: 'saya bingung pilih jurusan smk', icon: 'ri-question-line' }
    ];
    
    const scrollToBottom = async () => {
      await nextTick();
      if (messagesContainer.value) {
        messagesContainer.value.scrollTo({
          top: messagesContainer.value.scrollHeight,
          behavior: 'smooth'
        });
      }
    };
    
    const quickActionClick = (text) => {
      newMessage.value = text;
      sendMessage();
    };
    
    const sendMessage = async () => {
      if (!newMessage.value.trim() || isTyping.value) return;
      
      const userMessage = newMessage.value;
      messages.value.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date()
      });
      
      newMessage.value = '';
      isTyping.value = true;
      
      await scrollToBottom();
      
      try {
        const response = await chatService.sendMessage(userMessage);
        
        // Tambah delay untuk efek natural
        setTimeout(async () => {
          messages.value.push({
            role: 'assistant',
            content: response.reply,
            timestamp: new Date()
          });
          
          // Handle structured mode questions
          if (response.type === 'structured_start' || response.type === 'structured_next') {
            setTimeout(() => {
              messages.value.push({
                role: 'assistant',
                content: response.question,
                timestamp: new Date()
              });
            }, 500);
          }
          
          isTyping.value = false;
          await scrollToBottom();
        }, 800);
        
      } catch (error) {
        console.error('Error:', error);
        messages.value.push({
          role: 'assistant',
          content: 'Maaf, terjadi kesalahan. Silakan coba lagi.',
          timestamp: new Date()
        });
        isTyping.value = false;
        await scrollToBottom();
      }
    };
    
    const resetChat = async () => {
      if (confirm('Reset percakapan? Semua history akan hilang.')) {
        try {
          await chatService.resetSession();
          messages.value = [];
          await chatService.startSession();
          
          // Welcome message
          messages.value.push({
            role: 'assistant',
            content: 'Halo! Ada yang bisa saya bantu? 👋',
            timestamp: new Date()
          });
        } catch (error) {
          console.error('Error resetting chat:', error);
        }
      }
    };
    
    onMounted(async () => {
      try {
        const health = await healthService.check();
        statusText.value = health.status === 'online' ? 'Online' : 'Offline';
        
        await chatService.startSession();
        
        messages.value.push({
          role: 'assistant',
          content: 'Halo! Ada yang bisa saya bantu? 👋\n\nSaya bisa membantu:\n• Informasi SMK BPPI\n• Rekomendasi jurusan\n• Konsultasi karir\n• Dan lainnya!',
          timestamp: new Date()
        });
      } catch (error) {
        console.error('Error:', error);
        statusText.value = 'Error';
        messages.value.push({
          role: 'assistant',
          content: 'Maaf, tidak dapat terhubung ke server. Pastikan backend Python sudah berjalan.',
          timestamp: new Date()
        });
      }
    });
    
    return {
      messages,
      newMessage,
      isTyping,
      showSettings,
      showBPPI,
      typingEffect,
      messagesContainer,
      statusText,
      quickActions,
      quickActionClick,
      sendMessage,
      resetChat
    };
  }
};
</script>