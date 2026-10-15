import { defineConfig } from "astro/config";

// Remplacer par le vrai domaine au moment de la mise en ligne (sert aux URL canoniques).
export default defineConfig({
  site: "https://rattrapage-dofus.example",
  trailingSlash: "ignore",
});
