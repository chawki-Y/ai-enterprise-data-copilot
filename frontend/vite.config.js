import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: true,
    proxy: {
      "/ask": "http://127.0.0.1:8000",
      "/api": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
      "/query-history": "http://127.0.0.1:8000",
      "/sample-questions": "http://127.0.0.1:8000",
      "/schema": "http://127.0.0.1:8000",
    },
  },
});
