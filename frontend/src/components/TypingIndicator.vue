<template>
  <div class="flex gap-3 items-start">
    <div class="flex-shrink-0 relative">
      <div class="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white shadow-lg">
        <i class="ri-robot-line text-lg"></i>
      </div>
    </div>
    
    <div class="bg-white rounded-2xl rounded-tl-none px-6 py-4 shadow-md border border-gray-100">
      <div class="flex items-center gap-2">
        <div class="flex gap-1.5">
          <span class="typing-dot" style="animation-delay: 0s"></span>
          <span class="typing-dot" style="animation-delay: 0.2s"></span>
          <span class="typing-dot" style="animation-delay: 0.4s"></span>
        </div>
        <span class="text-sm text-gray-400 font-medium">AI sedang mengetik...</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TypingIndicator'
};
</script>