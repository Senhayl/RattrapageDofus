import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// Domaine du site : sert aux URL canoniques, aux liens hreflang et au sitemap.
export default defineConfig({
  site: "https://backfromafk.com",
  trailingSlash: "ignore",
  integrations: [
    sitemap({
      filter: (page) => !page.includes("/404"),
      lastmod: new Date(),
    }),
  ],
});
