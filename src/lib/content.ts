// Données des rubriques objets / panoplies / métiers / donjons et des pages de mise à jour.
// Lues sur le disque au moment du build (fichiers volumineux, inutile de les embarquer).
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { CT } from "../i18n/content";
import { ROUTES, UI, monthLabel, type Category, type Lang } from "../i18n/ui";
import { DEFAULT_START, versionSlug, versions, type ClassDiff, type Verdict } from "./data";

type RawChange = {
  cle: string;
  type?: "modified" | "added" | "removed";
  avant: string | number | null;
  apres: string | number | null;
  verdict?: Verdict;
  n?: number;
  boss?: string;
};
type RawRow = {
  id: number;
  nom: string;
  niveau: number | null;
  statut: "added" | "removed" | "modified";
  changements: RawChange[];
  verdict?: Verdict | "mixte";
  type?: string;
  boss?: string[];
  objets?: string[];
};
type RawJob = {
  id: number;
  nom: string;
  lignes: { id: number; nom: string; niveau: number; statut: Row["statut"]; avant: string | null; apres: string | null; niveauAvant?: number }[];
};
export type Content = { objets: RawRow[]; panoplies: RawRow[]; donjons: RawRow[]; metiers: RawJob[]; contenu?: (RawRow & { meta?: string })[] };
export type Patch = { depuis: { version: string; date: string }; jusqua: { version: string; date: string }; classes: ClassDiff[]; contenu: Content };

const DATA = join(process.cwd(), "src", "data");
const cache = new Map<string, unknown>();
function readJson<T>(...parts: string[]): T {
  const p = join(DATA, ...parts);
  if (!cache.has(p)) cache.set(p, JSON.parse(readFileSync(p, "utf-8")));
  return cache.get(p) as T;
}

export const getContent = (lang: Lang, version: string) => readJson<Content>(lang, "content", `${version}.json`);
export const getPatch = (lang: Lang, version: string) => readJson<Patch>(lang, "patches", `${version}.json`);
export const patches = (versions as unknown as { patches: { version: string; depuis: string; date: string }[] }).patches;

// ------------------------------------------------------------------ URL

export function categoryUrl(lang: Lang, cat: Category, version: string) {
  const r = ROUTES[lang];
  const base = `${r.prefix}/${r[cat]}/`;
  return version === DEFAULT_START ? base : `${base}${r.since}-${versionSlug(version)}/`;
}
export const updatesUrl = (lang: Lang) => `${ROUTES[lang].prefix}/${ROUTES[lang].updates}/`;
export const patchUrl = (lang: Lang, version: string) => `${updatesUrl(lang)}${versionSlug(version)}/`;
export const privacyUrl = (lang: Lang) => `${ROUTES[lang].prefix}/${ROUTES[lang].privacy}/`;

export function versionDate(lang: Lang, version: string) {
  const all = [versions.actuelle, ...versions.depart];
  const v = all.find((x) => x.version === version);
  return v ? monthLabel(lang, v.date) : "";
}

// ------------------------------------------------------------------ lignes de tableau

export type Line = { label: string; avant: string | null; apres: string | null; verdict?: Verdict };
export type Row = {
  id: number;
  nom: string;
  niveau: number | null;
  statut: "added" | "removed" | "modified";
  verdict: Verdict | "mixte" | null;
  filtre?: string; // type d'objet ou métier, pour le filtre
  meta?: string; // texte secondaire (boss, objets de panoplie…)
  lines: Line[];
};

const str = (v: string | number | null) => (v === null || v === undefined ? null : String(v));

function lineOf(lang: Lang, c: RawChange): Line {
  const t = CT[lang];
  let label: string;
  if (c.cle === "effect") label = UI[lang].effectTypes[c.type ?? "modified"];
  else if (c.cle === "setBonus") label = t.setBonus(c.n ?? 0);
  else if (c.cle === "setItem") label = `${t.setItems} (${t.labels[c.type ?? "added"]})`;
  else if (c.cle === "bossSpell") label = `${t.bossSpell(c.boss ?? "")} (${t.labels[c.type ?? "added"]})`;
  else if (c.cle.startsWith("boss_")) label = t.bossStat(c.boss ?? "", t.labels[c.cle] ?? c.cle);
  else label = t.labels[c.cle] ?? c.cle;
  return { label, avant: str(c.avant), apres: str(c.apres), verdict: c.verdict ?? undefined };
}

function rowOf(lang: Lang, r: RawRow, filtre?: string, meta?: string): Row {
  return {
    id: r.id,
    nom: r.nom,
    niveau: r.niveau,
    statut: r.statut,
    verdict: r.verdict ?? null,
    filtre,
    meta,
    lines: r.changements.map((c) => lineOf(lang, c)),
  };
}

export function itemRows(lang: Lang, c: Content): Row[] {
  return c.objets.map((r) => rowOf(lang, r, r.type, r.type));
}
export function setRows(lang: Lang, c: Content): Row[] {
  return c.panoplies.map((r) => rowOf(lang, r, undefined, r.objets?.join(", ")));
}
export function dungeonRows(lang: Lang, c: Content): Row[] {
  return c.donjons.map((r) => rowOf(lang, r, undefined, r.boss?.join(", ")));
}
export function recipeRows(lang: Lang, c: Content, jobId?: number): Row[] {
  const t = CT[lang];
  return c.metiers.filter((j) => jobId === undefined || j.id === jobId).flatMap((j) =>
    j.lignes.map((l) => ({
      id: l.id,
      nom: l.nom,
      niveau: l.niveau,
      statut: l.statut,
      verdict: null,
      filtre: j.nom,
      meta: j.nom,
      lines: [
        {
          label: l.niveauAvant ? `${t.col.recipe} (${t.recipeLevel(l.niveauAvant, l.niveau)})` : t.col.recipe,
          avant: l.avant,
          apres: l.apres,
        },
      ],
    }))
  );
}

// ------------------------------------------------------------------ métiers

const slugify = (t: string) =>
  t.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export type Job = { id: number; nom: string; slug: string };
/** Tous les métiers présents dans au moins une version de départ. */
export function jobsOf(lang: Lang): Job[] {
  const map = new Map<number, Job>();
  for (const v of versions.depart)
    for (const j of getContent(lang, v.version).metiers) map.set(j.id, { id: j.id, nom: j.nom, slug: slugify(j.nom) });
  return [...map.values()].sort((a, b) => a.nom.localeCompare(b.nom, lang));
}
export function jobUrl(lang: Lang, jobId: number, version: string) {
  const r = ROUTES[lang];
  const slug = jobsOf(lang).find((j) => j.id === jobId)!.slug;
  const base = `${r.prefix}/${r.metiers}/${slug}/`;
  return version === DEFAULT_START ? base : `${base}${r.since}-${versionSlug(version)}/`;
}
export function jobCounts(c: Content) {
  return new Map(c.metiers.map((j) => [j.id, j.lignes.length]));
}

export function miscRows(lang: Lang, c: Content): Row[] {
  return (c.contenu ?? []).map((r) => rowOf(lang, r, r.type, [r.type, r.meta].filter(Boolean).join(" · ")));
}

export function rowsFor(lang: Lang, cat: Category, c: Content): Row[] {
  if (cat === "objets") return itemRows(lang, c);
  if (cat === "panoplies") return setRows(lang, c);
  if (cat === "donjons") return dungeonRows(lang, c);
  if (cat === "contenu") return miscRows(lang, c);
  return recipeRows(lang, c);
}

export const interfaceUrl = (lang: Lang) => `${ROUTES[lang].prefix}/${ROUTES[lang].interface}/`;

export function countsOf(rows: Row[]) {
  return {
    m: rows.filter((r) => r.statut === "modified").length,
    a: rows.filter((r) => r.statut === "added").length,
    r: rows.filter((r) => r.statut === "removed").length,
  };
}

export function balanceOfRows(rows: Row[]) {
  const b = { up: 0, nerf: 0, mixte: 0, neutre: 0 };
  for (const r of rows) if (r.statut === "modified") b[r.verdict ?? "neutre"]++;
  return b;
}

// ------------------------------------------------------------------ interface (notes rédigées à la main)

export type IfaceNote = { titre: string; texte: string };
type IfaceFile = { versions: Record<string, { sources: string[] } & Record<Lang, IfaceNote[]>> };
export function interfaceNotes(lang: Lang, version: string): { notes: IfaceNote[]; sources: string[] } {
  const f = readJson<IfaceFile>("interface.json");
  const v = f.versions[version];
  return { notes: v?.[lang] ?? [], sources: v?.sources ?? [] };
}
