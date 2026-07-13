import axios from "axios";

// Em dev, o proxy do Vite (vite.config.js) encaminha /api pro backend local.
// Em produção (Vercel), VITE_API_URL precisa apontar pra URL do backend (Render).
const baseURL = import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : "/api";

export const api = axios.create({ baseURL });
