// Accès aux données générées par scripts/build_site_data.py
import versionsJson from "../data/versions.json";
import { LANGS, ROUTES, UI, monthLabel, type Lang } from "../i18n/ui";

export type Verdict = "up" | "nerf" | null;
export type Element = "terre" | "feu" | "eau" | "air" | "neutre";
export type Change = {
  note?: string; // ce que fait l'état posé ou retiré par l'effet
  cle: string; // "apCost", "range", ..., "name", "description", "castFlags", "effect"
  type?: "modified" | "added" | "removed";
  critique?: boolean;
  avant: string | number | null;
  apres: string | number | null;
  verdict?: Verdict;
  element?: Element | null;
  note?: string | null;
};
export type ModifiedSpell = { spellId: number; nom: string; changements: Change[]; ancienSpellId?: number };
export type ClassDiff = {
  classeId: number;
  classe: string;
  slug: string;
  sorts_ajoutes: { spellId: number; nom: string; description: string }[];
  sorts_retires: { spellId: number; nom: string }[];
  sorts_modifies: ModifiedSpell[];
};
export type Version = { version: string; build: string; nom: string; date: string };
export type Diff = { depuis: Version; jusqua: Version; classes: ClassDiff[] };
export type ClassInfo = { id: number; nom: string; slug: string };

export const versions = versionsJson as { actuelle: Version; depart: Version[] };

/**
 * Version de départ par défaut (celle de /classes/<classe>/) : la plus récente sortie
 * au moins 12 mois avant la version actuelle. Recalculée à chaque build.
 */
export const DEFAULT_START = (() => {
  const months = (ym: string) => {
    const [y, m] = ym.split("-").map(Number);
    return y * 12 + m;
  };
  const target = months(versions.actuelle.date) - 12;
  const sorted = versions.depart.slice().sort((a, b) => months(b.date) - months(a.date));
  return (sorted.find((v) => months(v.date) <= target) ?? sorted[sorted.length - 1]).version;
})();

const classModules = import.meta.glob<ClassInfo[]>("../data/*/classes.json", { eager: true, import: "default" });
const diffModules = import.meta.glob<Diff>("../data/*/diffs/*.json", { eager: true, import: "default" });

export function getClasses(lang: Lang): ClassInfo[] {
  return classModules[`../data/${lang}/classes.json`].slice().sort((a, b) => a.nom.localeCompare(b.nom, lang));
}
export function getDiff(lang: Lang, version: string): Diff {
  const d = diffModules[`../data/${lang}/diffs/${version}.json`];
  if (!d) throw new Error(`Pas de données pour ${lang} ${version}`);
  return d;
}
export function getClassDiff(lang: Lang, version: string, classId: number): ClassDiff {
  const c = getDiff(lang, version).classes.find((x) => x.classeId === classId);
  if (!c) throw new Error(`Classe inconnue : ${classId}`);
  return c;
}

export const versionSlug = (v: string) => v.replace(/\./g, "-");

export function homeUrl(lang: Lang) {
  return `${ROUTES[lang].prefix}/`;
}
export function classUrl(lang: Lang, classId: number, version: string) {
  const r = ROUTES[lang];
  const slug = getClasses(lang).find((c) => c.id === classId)!.slug;
  const base = `${r.prefix}/${r.classes}/${slug}/`;
  return version === DEFAULT_START ? base : `${base}${r.since}-${versionSlug(version)}/`;
}
/** Même page dans chaque langue (pour hreflang et le sélecteur de langue). */
export function alternates(build: (lang: Lang) => string) {
  return LANGS.map((lang) => ({ lang, href: build(lang) }));
}

export function versionLabel(lang: Lang, v: Version) {
  return `${v.version} (${monthLabel(lang, v.date)})`;
}

export function countChanges(c: ClassDiff) {
  return c.sorts_modifies.length + c.sorts_ajoutes.length + c.sorts_retires.length;
}

// ------------------------------------------------------------------ affichage

const UNLIMITED = new Set(["maxCastPerTurn", "maxCastPerTarget", "maxStack"]);
const NONE = new Set(["globalCooldown", "initialCooldown", "minCastInterval"]);

export function formatValue(lang: Lang, c: Change, v: string | number | null): string | null {
  if (v === null) return null;
  if (typeof v === "number") {
    if (UNLIMITED.has(c.cle) && (v === 0 || v === -1)) return UI[lang].unlimited;
    if (NONE.has(c.cle) && (v === 0 || v === -1)) return UI[lang].none;
  }
  return String(v);
}

export function changeLabel(lang: Lang, c: Change) {
  const t = UI[lang];
  if (c.cle === "effect") {
    const base = t.effectTypes[c.type ?? "modified"];
    return c.critique ? `${base} (${t.crit})` : base;
  }
  return t.fields[c.cle] ?? c.cle;
}

/** Groupe utilisé par les filtres de la page. */
export function changeGroup(c: Change) {
  if (c.cle === "name" || c.cle === "description") return "texte";
  if (c.cle === "effect") return c.critique ? "critique" : "effets";
  return "carac";
}

export function spellVerdict(s: ModifiedSpell): Verdict | "mixte" {
  const vs = s.changements.map((c) => c.verdict).filter(Boolean);
  const ups = vs.filter((v) => v === "up").length;
  const nerfs = vs.filter((v) => v === "nerf").length;
  if (ups && nerfs) return "mixte";
  return ups ? "up" : nerfs ? "nerf" : null;
}

// ------------------------------------------------------------------ résumés

export type Balance = { up: number; nerf: number; mixte: number; neutre: number };

/** Répartition des sorts modifiés selon leur verdict. */
export function balanceOf(c: ClassDiff): Balance {
  const b: Balance = { up: 0, nerf: 0, mixte: 0, neutre: 0 };
  for (const s of c.sorts_modifies) b[spellVerdict(s) ?? "neutre"]++;
  return b;
}

export type Highlight = {
  sort: string;
  label: string;
  avant: string | null;
  apres: string | null;
  verdict: Verdict;
  element?: Element | null;
};

/**
 * Quelques changements marquants pour l'aperçu de l'accueil : d'abord ceux dont
 * le sens est clair (up / nerf), un seul par sort, caractéristiques avant effets.
 */
export function highlightsOf(lang: Lang, c: ClassDiff, max = 3): Highlight[] {
  const rank = (ch: Change) => (ch.verdict ? 0 : 2) + (ch.cle === "effect" ? 1 : 0);
  const candidates = c.sorts_modifies
    .flatMap((s) =>
      s.changements
        .filter((ch) => !["name", "description", "castFlags", "minPlayerLevel"].includes(ch.cle) && !ch.critique)
        .filter((ch) => ch.avant !== null && ch.apres !== null)
        .map((ch) => ({ s, ch }))
    )
    .sort((a, b) => rank(a.ch) - rank(b.ch));
  // une ligne par sort, et des types de changement variés tant que possible
  const picked: { s: ModifiedSpell; ch: Change }[] = [];
  const spells = new Set<number>();
  const kinds = new Set<string>();
  for (const pass of [0, 1]) {
    for (const x of candidates) {
      if (picked.length >= max) break;
      if (spells.has(x.s.spellId) || (pass === 0 && kinds.has(x.ch.cle))) continue;
      spells.add(x.s.spellId);
      kinds.add(x.ch.cle);
      picked.push(x);
    }
  }
  const out: Highlight[] = [];
  for (const { s, ch } of picked) {
    const strip = (v: string | null) => (v === null ? null : v.replace(new RegExp(`^${escapeRe(s.nom)}\\s?:\\s`), ""));
    out.push({
      sort: s.nom,
      label: changeLabel(lang, ch),
      avant: strip(formatValue(lang, ch, ch.avant)),
      apres: strip(formatValue(lang, ch, ch.apres)),
      verdict: ch.verdict ?? null,
      element: ch.element,
      note: ch.note ?? null,
    });
  }
  return out;
}

export const escapeRe = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Écart chiffré entre deux valeurs numériques (« +2 », « −1 »), sinon null. */
export function deltaOf(c: Change): string | null {
  if (typeof c.avant !== "number" || typeof c.apres !== "number") return null;
  if (formatValue("fr", c, c.avant) !== String(c.avant) || formatValue("fr", c, c.apres) !== String(c.apres)) return null;
  const d = c.apres - c.avant;
  if (!d) return null;
  return d > 0 ? `+${d}` : `−${Math.abs(d)}`;
}
