// API location comes from the build environment (see .env.example).
// Falls back to the local backend for development.
const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");
const WS_URL = API_URL.replace(/^http/, "ws") + "/ws";

export { API_URL, WS_URL };
