import { defineConfig } from "vite";

// The Property Predictor calls the FastAPI inference backend. In dev, Vite
// proxies /api -> the uvicorn server so the frontend stays same-origin and
// needs no CORS or hardcoded host. Start the backend with:
//   pip install -r api/requirements.txt
//   npm run api        (uvicorn on 127.0.0.1:8000)
export default defineConfig({
  server: {
    host: "127.0.0.1",
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
