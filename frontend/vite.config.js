import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: true,
    proxy: {
      "/health": "http://127.0.0.1:8000",
      "/agent": "http://127.0.0.1:8000",
    },
  },
});
