import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// Domaine du site : sert aux URL canoniques, aux liens hreflang et au sitemap.
export default defineConfig({
  site: "https://backfromafk.com",
  trailingSlash: "ignore",
  // Précharge les pages au survol des liens : navigation quasi instantanée
  // Scripts toujours en fichiers séparés (jamais en ligne) : permet une
  // Content-Security-Policy stricte « script-src 'self' » (voir public/_headers).
  vite: { build: { assetsInlineLimit: 0 } },
  prefetch: { prefetchAll: true, defaultStrategy: "hover" },
  integrations: [
    sitemap({
      filter: (page) => !page.includes("/404"),
      lastmod: new Date(),
    }),
  ],
});
