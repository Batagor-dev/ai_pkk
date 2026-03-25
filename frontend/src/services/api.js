import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

let currentSessionId = null;

export const chatService = {
  // Start new session
  async startSession() {
    try {
      const response = await api.post("/start-session");
      currentSessionId = response.data.session_id;
      return response.data;
    } catch (error) {
      console.error("Error starting session:", error);
      throw error;
    }
  },

  // Send message
  async sendMessage(message, sessionId = currentSessionId) {
    try {
      const response = await api.post("/chat", {
        session_id: sessionId,
        message: message,
      });
      return response.data;
    } catch (error) {
      console.error("Error sending message:", error);
      throw error;
    }
  },

  // Get session info
  async getSessionInfo(sessionId = currentSessionId) {
    try {
      const response = await api.get(`/session/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error("Error getting session info:", error);
      throw error;
    }
  },

  // Get chat history
  async getChatHistory(sessionId = currentSessionId) {
    try {
      const response = await api.get(`/session/${sessionId}/history`);
      return response.data;
    } catch (error) {
      console.error("Error getting chat history:", error);
      throw error;
    }
  },

  // Reset session
  async resetSession(sessionId = currentSessionId) {
    try {
      const response = await api.post(`/session/${sessionId}/reset`);
      return response.data;
    } catch (error) {
      console.error("Error resetting session:", error);
      throw error;
    }
  },

  getSessionId() {
    return currentSessionId;
  },
};

export const bppiService = {
  // Get BPPI info
  async getInfo(query = "general") {
    try {
      const response = await api.get("/bppi/info", {
        params: { query },
      });
      return response.data;
    } catch (error) {
      console.error("Error getting BPPI info:", error);
      throw error;
    }
  },

  // Get jurusan list
  async getJurusan() {
    try {
      const response = await api.get("/bppi/jurusan");
      return response.data;
    } catch (error) {
      console.error("Error getting jurusan:", error);
      throw error;
    }
  },

  // Get biaya info
  async getBiaya() {
    try {
      const response = await api.get("/bppi/biaya");
      return response.data;
    } catch (error) {
      console.error("Error getting biaya:", error);
      throw error;
    }
  },

  // Get kontak info
  async getKontak() {
    try {
      const response = await api.get("/bppi/kontak");
      return response.data;
    } catch (error) {
      console.error("Error getting kontak:", error);
      throw error;
    }
  },
};

export const healthService = {
  async check() {
    try {
      const response = await api.get("/health");
      return response.data;
    } catch (error) {
      console.error("Error checking health:", error);
      throw error;
    }
  },
};
