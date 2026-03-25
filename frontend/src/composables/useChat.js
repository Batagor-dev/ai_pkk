import { ref } from "vue";
import axios from "axios";

const API_BASE_URL = "/api";

export function useChat() {
  const messages = ref([]);
  const isTyping = ref(false);
  const sessionId = ref(null);
  const currentMode = ref("free");

  // Initialize session
  const initSession = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/start-session`);
      sessionId.value = response.data.session_id;

      // Add welcome message
      messages.value = [];
      addMessage(
        "assistant",
        "Halo! Saya KANUT. Ada yang bisa saya bantu? 😊",
      );
    } catch (error) {
      console.error("Failed to start session:", error);
      addMessage(
        "assistant",
        "Maaf, terjadi kesalahan. Silakan refresh halaman.",
      );
    }
  };

  // Add message to chat
  const addMessage = (role, content) => {
    messages.value.push({
      role,
      content,
      timestamp: new Date().toISOString(),
    });
  };

  // Send message
  const sendMessage = async (userInput) => {
    if (!userInput.trim()) return;

    // Add user message
    addMessage("user", userInput);

    // Show typing indicator
    isTyping.value = true;

    try {
      // If no session, create one first
      if (!sessionId.value) {
        await initSession();
      }

      const response = await axios.post(`${API_BASE_URL}/chat`, {
        session_id: sessionId.value,
        message: userInput,
      });

      const data = response.data;

      // Handle different response types
      if (data.type === "structured_start") {
        // Show structured mode questions
        addMessage("assistant", data.question);
        currentMode.value = data.mode;
      } else if (data.type === "structured_next") {
        // Show next question
        addMessage("assistant", data.question);
      } else if (data.type === "structured_complete") {
        // Show recommendation
        addMessage("assistant", data.reply);
        currentMode.value = "free";
      } else if (data.reply) {
        // Normal response
        addMessage("assistant", data.reply);
      } else {
        addMessage(
          "assistant",
          "Maaf, saya tidak dapat memproses permintaan Anda.",
        );
      }
    } catch (error) {
      console.error("Chat error:", error);
      addMessage(
        "assistant",
        "Maaf, terjadi kesalahan. Silakan coba lagi nanti.",
      );
    } finally {
      isTyping.value = false;
    }
  };

  // Reset session
  const resetSession = async () => {
    if (sessionId.value) {
      try {
        await axios.post(`${API_BASE_URL}/session/${sessionId.value}/reset`);
      } catch (error) {
        console.error("Reset session error:", error);
      }
    }

    // Clear messages
    messages.value = [];
    sessionId.value = null;
    currentMode.value = "free";

    // Initialize new session
    await initSession();
  };

  // Auto initialize on load
  initSession();

  return {
    messages,
    isTyping,
    sessionId,
    currentMode,
    sendMessage,
    resetSession,
  };
}
