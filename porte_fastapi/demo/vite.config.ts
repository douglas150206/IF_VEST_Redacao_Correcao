import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Os componentes vivem em ../web, fora da raiz do Vite.
    fs: { allow: [".."] },
    proxy: {
      // O backend FastAPI. 127.0.0.1 e não localhost: o uvicorn escuta só em
      // IPv4, e no Windows localhost resolve ::1 primeiro.
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
