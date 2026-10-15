// Génère les images de partage (1200×630) dans public/og/<langue>/ : accueil + une par classe.
// À relancer seulement si les classes ou le nom du site changent :
//   npm i -D playwright && npx playwright install chromium && node scripts/og-images.mjs
import { chromium } from "playwright";
import { mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
const font = (p) => `data:font/woff2;base64,${readFileSync(join(ROOT, "node_modules", p)).toString("base64")}`;
const display = font("@fontsource-variable/bricolage-grotesque/files/bricolage-grotesque-latin-wght-normal.woff2");
const body = font("@fontsource-variable/figtree/files/figtree-latin-wght-normal.woff2");

const TEXT = {
  fr: { home: ["Je n'ai pas joué depuis…", "Tous les changements de Dofus, avant et après."], cls: "Tous les changements de sorts, avant et après", sub: "pour Dofus" },
  en: { home: ["I haven't played since…", "Every Dofus change, before and after."], cls: "Every spell change, before and after", sub: "for Dofus" },
  es: { home: ["No he jugado desde…", "Todos los cambios de Dofus, antes y después."], cls: "Todos los cambios de hechizos, antes y después", sub: "para Dofus" },
};

const page = (big, small, sub) => `<!doctype html><html><head><style>
@font-face{font-family:D;src:url(${display})}@font-face{font-family:B;src:url(${body})}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:#12202c;color:#e9eef2;font-family:B;padding:72px 80px;display:flex;flex-direction:column;justify-content:space-between;position:relative;overflow:hidden}
.brand{font-family:D;font-weight:800;font-size:34px}.brand span{color:#e8b64c;font-weight:500;font-size:28px;margin-left:10px}
h1{font-family:D;font-weight:700;font-size:${big.length > 16 ? 92 : 128}px;line-height:1.02;letter-spacing:-3px;max-width:980px}
p{font-size:34px;color:#9bb0c0;margin-top:22px;max-width:900px}
.bar{display:flex;gap:6px;height:14px;width:520px}.bar i{border-radius:7px}
.arrow{position:absolute;right:60px;top:60px;width:150px;height:150px}
</style></head><body>
<div class="brand">Back from AFK<span>${sub}</span></div>
<svg class="arrow" viewBox="0 0 64 64"><path d="M27 18 17 28l10 10M17 28h18a11 11 0 0 1 0 22h-6" fill="none" stroke="#e8b64c" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>
<div><h1>${big}</h1><p>${small}</p></div>
<div class="bar"><i style="flex:5;background:#6fd39a"></i><i style="flex:2;background:#ff8a7a"></i><i style="flex:2;background:#e8b64c"></i><i style="flex:3;background:#2f4a5f"></i></div>
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
