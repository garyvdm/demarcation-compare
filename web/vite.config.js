import { defineConfig } from "vite";
import path from "path";
import sirv from "sirv";

export default defineConfig({
  build: { sourcemap: true },
  server: {
    forwardConsole: {
      logLevels: ["log", "warn", "error", "info"],
    },
  },
  plugins: [
    {
      name: "serve-custom-directory",
      configureServer(server) {
        const data_sirv = sirv(path.resolve(__dirname, "../data"), {
          dev: true,
          single: false,
          dotfiles: true,
          extensions: [],
          etag: true,
        });

        server.middlewares.use("/data", (req, res, next) =>
          data_sirv(req, res, null),
        );
      },
    },
  ],
});
