// Génère les images de partage (1200×630) dans public/og/<langue>/ : accueil + une par classe.
// À relancer seulement si les classes ou le nom du site changent :
//   npm i -D playwright && npx playwright install chromium && node scripts/og-images.mjs
import { chromium } from "playwright";
import { mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
const font = (p) => `data:font/woff2;base64,${readFileSync(join(ROOT, "node_modules", p)).toString("base64")}`;
const serif = font("@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2");
const body = font("@fontsource/outfit/files/outfit-latin-400-normal.woff2");
const bodyMedium = font("@fontsource/outfit/files/outfit-latin-500-normal.woff2");

const TEXT = {
  fr: { home: ["Je n'ai pas joué depuis…", "Tous les changements de Dofus, avant et après."], cls: "Tous les changements de sorts, avant et après", sub: "pour Dofus" },
  en: { home: ["I haven't played since…", "Every Dofus change, before and after."], cls: "Every spell change, before and after", sub: "for Dofus" },
  es: { home: ["No he jugado desde…", "Todos los cambios de Dofus, antes y después."], cls: "Todos los cambios de hechizos, antes y después", sub: "para Dofus" },
};

const page = (big, small, sub) => `<!doctype html><html><head><style>
@font-face{font-family:S;src:url(${serif})}@font-face{font-family:B;font-weight:400;src:url(${body})}@font-face{font-family:B;font-weight:500;src:url(${bodyMedium})}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#0b0d14;color:#eceae4;font-family:B;padding:72px 80px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}
.brand{font-weight:500;font-size:32px;color:#fff}.brand span{color:rgba(255,255,255,.7);font-weight:400;font-size:28px;margin-left:10px}
h1{font-family:S;font-weight:400;font-size:${big.length > 16 ? 104 : 150}px;line-height:.98;letter-spacing:-1px;max-width:1000px;color:#fff}
p{font-size:34px;color:#9a9caa;margin-top:22px;max-width:900px}
.bar{display:flex;gap:4px;height:6px;width:520px}.bar i{border-radius:2px}
.arrow{position:absolute;right:60px;top:60px;width:150px;height:150px}
</style></head><body>
<div class="brand">Back from AFK<span>${sub}</span></div>
<svg class="arrow" viewBox="0 0 64 64"><path d="M27 18 17 28l10 10M17 28h18a11 11 0 0 1 0 22h-6" fill="none" stroke="#e9d9b0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div><h1>${big}</h1><p>${small}</p></div>
<div class="bar"><i style="flex:5;background:#7fbf9a"></i><i style="flex:2;background:#d9877a"></i><i style="flex:2;background:#d8b46a"></i><i style="flex:3;background:#2e3247"></i></div>
</body></html>`;

const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const tab = await browser.newPage({ viewport: { width: 1200, height: 630 } });
for (const lang of ["fr", "en", "es"]) {
  const dir = join(ROOT, "public", "og", lang);
  mkdirSync(dir, { recursive: true });
  const t = TEXT[lang];
  await tab.setContent(page(t.home[0], t.home[1], t.sub));
  await tab.screenshot({ path: join(dir, "home.png") });
  const classes = JSON.parse(readFileSync(join(ROOT, "src", "data", lang, "classes.json"), "utf-8"));
  for (const c of classes) {
    await tab.setContent(page(c.nom, t.cls, t.sub));
    await tab.screenshot({ path: join(dir, `${c.slug}.png`) });
  }
}
await browser.close();
console.log("Images écrites dans public/og/");
