import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: 600000, // 10 minutes — enough for qwen2.5:14b on CPU
});

// Request interceptor
API.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// Response interceptor — friendly logging
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === "ECONNABORTED") {
      console.error(
        "⏱️ Request timed out — the model is still thinking. " +
        "Try a lighter mode (Auto/Moderate) or wait longer."
      );
    } else if (error.code === "ERR_CANCELED") {
      // User clicked Stop — not an error
    } else if (!error.response) {
      console.error(
        "🔌 Network error — backend unreachable at " + API.defaults.baseURL
      );
    } else {
      console.error("API error:", error.response.status, error.response.data);
    }
    return Promise.reject(error);
  }
);

export default API;
