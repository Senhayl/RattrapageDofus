// Textes d'interface et structure des URL par langue.
export const LANGS = ["fr", "en", "es"] as const;
export type Lang = (typeof LANGS)[number];

export const ROUTES: Record<Lang, { prefix: string; classes: string; since: string }> = {
  fr: { prefix: "", classes: "classes", since: "depuis" },
  en: { prefix: "/en", classes: "classes", since: "since" },
  es: { prefix: "/es", classes: "clases", since: "desde" },
};

type Dict = {
  langName: string;
  brand: string;
  brandSub: string;
  updated: (v: string) => string;
  sentenceA: string;
  sentenceB: string;
  versionLabel: string;
  classLabel: string;
  cta: string;
  lede: string;
  homeTitle: string;
  homeDescription: string;
  perClass: (v: string) => string;
  classTitle: (c: string, from: string, to: string) => string;
  classDescription: (c: string, from: string, to: string, m: number, a: number, r: number) => string;
  summary: (from: string, to: string) => string;
  counts: (m: number, a: number, r: number) => [string, string];
  verdicts: (up: number, nerf: number) => string;
  filters: { carac: string; effets: string; critique: string; texte: string; legend: string };
  newSpells: string;
  removedSpells: string;
  modifiedSpells: string;
  nothing: (c: string, v: string) => string;
  otherTitle: string;
  otherLink: (c: string, v: string) => string;
  wasNamed: (n: string) => string;
  before: string;
  now: string;
  becomes: string;
  castFlags: string;
  unlimited: string;
  none: string;
  up: string;
  nerf: string;
  mixed: string;
  fields: Record<string, string>;
  effectTypes: { modified: string; added: string; removed: string };
  crit: string;
  footer: string;
  adDev: string;
  adLabel: string;
  previewTitle: (c: string, v: string) => string;
  previewMore: (n: number) => string;
  previewEmpty: string;
  balance: { up: string; nerf: string; mixte: string; neutre: string; label: string };
  verdictFilter: { all: string; up: string; nerf: string };
  index: string;
};

export const UI: Record<Lang, Dict> = {
  fr: {
    langName: "Français",
    brand: "Rattrapage",
    brandSub: "Dofus",
    updated: (v) => `Données à jour : ${v}`,
    sentenceA: "Je n'ai pas joué depuis la",
    sentenceB: "avec mon",
    versionLabel: "Dernière version jouée",
    classLabel: "Classe",
    cta: "Voir ce qui a changé",
    lede: "Tous les changements de sorts de ta classe, avant et après, sur une seule page. Pas besoin de lire les notes de patch une par une.",
    homeTitle: "Rattrapage Dofus : ce qui a changé pour ta classe depuis ta dernière partie",
    homeDescription:
      "Tu reviens sur Dofus après une pause ? Choisis ta classe et ta dernière version jouée : tous les changements de sorts, avant et après, sans lire des dizaines de notes de patch.",
    perClass: (v) => `Sorts modifiés par classe depuis la ${v}`,
    classTitle: (c, from, to) => `${c} : tous les changements depuis la ${from} (Dofus ${to})`,
    classDescription: (c, from, to, m, a, r) =>
      `Ce qui a changé pour le ${c} entre Dofus ${from} et ${to} : ${m} sorts modifiés, ${a} nouveaux, ${r} retirés. Coûts, portées, dégâts, avant et après.`,
    summary: (from, to) => `De la ${from} à la ${to} :`,
    counts: (m, a, r) => [`${m} sorts modifiés`, `${a} nouveaux, ${r} retirés.`],
    verdicts: (u, n) => `Dont ${u} clairement renforcés et ${n} clairement affaiblis.`,
    filters: {
      legend: "Afficher",
      carac: "Coût, portée, relance",
      effets: "Dégâts et effets",
      critique: "Coups critiques",
      texte: "Descriptions",
    },
    newSpells: "Nouveaux sorts",
    removedSpells: "Sorts retirés",
    modifiedSpells: "Sorts modifiés",
    nothing: (c, v) => `Aucun changement sur les sorts du ${c} depuis la ${v}. Tu peux reprendre là où tu t'étais arrêté.`,
    otherTitle: "Revenu à un autre moment ?",
    otherLink: (c, v) => `${c} depuis la ${v}`,
    wasNamed: (n) => `anciennement ${n}`,
    before: "Avant",
    now: "Maintenant",
    becomes: "devient",
    castFlags: "Conditions de lancer modifiées (ligne de vue, lancer en ligne…)",
    unlimited: "illimité",
    none: "aucune",
    up: "up",
    nerf: "nerf",
    mixed: "up et nerf",
    fields: {
      description: "Description",
      apCost: "Coût en PA",
      minRange: "Portée min",
      range: "Portée max",
      criticalHitProbability: "Critique (%)",
      maxCastPerTurn: "Lancers par tour",
      maxCastPerTarget: "Lancers par cible",
      minCastInterval: "Relance (tours)",
      initialCooldown: "Relance initiale",
      globalCooldown: "Relance globale",
      maxStack: "Cumul max",
      minPlayerLevel: "Niveau requis",
      castFlags: "Lancer",
    },
    effectTypes: { modified: "Effet", added: "Nouvel effet", removed: "Effet retiré" },
    crit: "critique",
    footer:
      "Site de fan, non affilié à Ankama. Dofus est une marque d'Ankama Games. Les changements sont calculés automatiquement en comparant les données du jeu entre deux versions, grâce au projet open source dofusdude. Une erreur ? Les notes de patch officielles font foi.",
    adDev: "Emplacement pub (300×600), visible en dev uniquement",
    adLabel: "Publicité",
    previewTitle: (c, v) => `${c} depuis la ${v}`,
    previewMore: (n) => `Voir les ${n} sorts concernés`,
    previewEmpty: "Aucun changement de sort sur cette période.",
    balance: { up: "up", nerf: "nerf", mixte: "up et nerf", neutre: "autres changements", label: "Bilan des sorts modifiés" },
    verdictFilter: { all: "Tous", up: "Up", nerf: "Nerf" },
    index: "Aller au sort",
  },
  en: {
    langName: "English",
    brand: "Catch-up",
    brandSub: "Dofus",
    updated: (v) => `Data up to date: ${v}`,
    sentenceA: "I haven't played since",
    sentenceB: "with my",
    versionLabel: "Last version played",
    classLabel: "Class",
    cta: "See what changed",
    lede: "Every spell change for your class, before and after, on one page. No need to read the patch notes one by one.",
    homeTitle: "Dofus Catch-up: what changed for your class since you last played",
    homeDescription:
      "Coming back to Dofus after a break? Pick your class and the last version you played: every spell change, before and after, without reading dozens of patch notes.",
    perClass: (v) => `Spells changed per class since ${v}`,
    classTitle: (c, from, to) => `${c}: every change since ${from} (Dofus ${to})`,
    classDescription: (c, from, to, m, a, r) =>
      `What changed for the ${c} between Dofus ${from} and ${to}: ${m} spells changed, ${a} new, ${r} removed. AP costs, ranges, damage, before and after.`,
    summary: (from, to) => `From ${from} to ${to}:`,
    counts: (m, a, r) => [`${m} spells changed`, `${a} new, ${r} removed.`],
    verdicts: (u, n) => `${u} clearly buffed and ${n} clearly nerfed.`,
    filters: {
      legend: "Show",
      carac: "Cost, range, cooldown",
      effets: "Damage and effects",
      critique: "Critical hits",
      texte: "Descriptions",
    },
    newSpells: "New spells",
    removedSpells: "Removed spells",
    modifiedSpells: "Changed spells",
    nothing: (c, v) => `No spell changes for the ${c} since ${v}. You can pick up right where you left off.`,
    otherTitle: "Came back at a different time?",
    otherLink: (c, v) => `${c} since ${v}`,
    wasNamed: (n) => `formerly ${n}`,
    before: "Before",
    now: "Now",
    becomes: "becomes",
    castFlags: "Casting conditions changed (line of sight, cast in line…)",
    unlimited: "unlimited",
    none: "none",
    up: "buff",
    nerf: "nerf",
    mixed: "buff and nerf",
    fields: {
      description: "Description",
      apCost: "AP cost",
      minRange: "Min range",
      range: "Max range",
      criticalHitProbability: "Critical (%)",
      maxCastPerTurn: "Casts per turn",
      maxCastPerTarget: "Casts per target",
      minCastInterval: "Cooldown (turns)",
      initialCooldown: "Initial cooldown",
      globalCooldown: "Global cooldown",
      maxStack: "Max stacks",
      minPlayerLevel: "Required level",
      castFlags: "Casting",
    },
    effectTypes: { modified: "Effect", added: "New effect", removed: "Removed effect" },
    crit: "critical",
    footer:
      "Fan site, not affiliated with Ankama. Dofus is a trademark of Ankama Games. Changes are computed automatically by comparing game data between two versions, thanks to the open source dofusdude project. Spotted a mistake? The official patch notes are the reference.",
    adDev: "Ad slot (300×600), shown in dev only",
    adLabel: "Advertisement",
    previewTitle: (c, v) => `${c} since ${v}`,
    previewMore: (n) => `See all ${n} affected spells`,
    previewEmpty: "No spell changes over this period.",
    balance: { up: "buffs", nerf: "nerfs", mixte: "buff and nerf", neutre: "other changes", label: "Changed spells at a glance" },
    verdictFilter: { all: "All", up: "Buffs", nerf: "Nerfs" },
    index: "Jump to spell",
  },
  es: {
    langName: "Español",
    brand: "Ponte al día",
    brandSub: "Dofus",
    updated: (v) => `Datos actualizados: ${v}`,
    sentenceA: "No he jugado desde la",
    sentenceB: "con mi",
    versionLabel: "Última versión jugada",
    classLabel: "Clase",
    cta: "Ver qué ha cambiado",
    lede: "Todos los cambios de hechizos de tu clase, antes y después, en una sola página. Sin leer las notas de parche una por una.",
    homeTitle: "Ponte al día en Dofus: qué ha cambiado para tu clase desde tu última partida",
    homeDescription:
      "¿Vuelves a Dofus tras una pausa? Elige tu clase y la última versión que jugaste: todos los cambios de hechizos, antes y después, sin leer decenas de notas de parche.",
    perClass: (v) => `Hechizos modificados por clase desde la ${v}`,
    classTitle: (c, from, to) => `${c}: todos los cambios desde la ${from} (Dofus ${to})`,
    classDescription: (c, from, to, m, a, r) =>
      `Qué ha cambiado para el ${c} entre Dofus ${from} y ${to}: ${m} hechizos modificados, ${a} nuevos, ${r} eliminados. Coste, alcance, daños, antes y después.`,
    summary: (from, to) => `De la ${from} a la ${to}:`,
    counts: (m, a, r) => [`${m} hechizos modificados`, `${a} nuevos, ${r} eliminados.`],
    verdicts: (u, n) => `${u} claramente mejorados y ${n} claramente debilitados.`,
    filters: {
      legend: "Mostrar",
      carac: "Coste, alcance, reutilización",
      effets: "Daños y efectos",
      critique: "Golpes críticos",
      texte: "Descripciones",
    },
    newSpells: "Hechizos nuevos",
    removedSpells: "Hechizos eliminados",
    modifiedSpells: "Hechizos modificados",
    nothing: (c, v) => `Ningún cambio en los hechizos del ${c} desde la ${v}. Puedes seguir donde lo dejaste.`,
    otherTitle: "¿Volviste en otro momento?",
    otherLink: (c, v) => `${c} desde la ${v}`,
    wasNamed: (n) => `antes ${n}`,
    before: "Antes",
    now: "Ahora",
    becomes: "pasa a",
    castFlags: "Condiciones de lanzamiento modificadas (línea de visión, lanzamiento en línea…)",
    unlimited: "ilimitado",
    none: "ninguna",
    up: "mejora",
    nerf: "nerf",
    mixed: "mejora y nerf",
    fields: {
      description: "Descripción",
      apCost: "Coste en PA",
      minRange: "Alcance mín.",
      range: "Alcance máx.",
      criticalHitProbability: "Crítico (%)",
      maxCastPerTurn: "Lanzamientos por turno",
      maxCastPerTarget: "Lanzamientos por objetivo",
      minCastInterval: "Reutilización (turnos)",
      initialCooldown: "Reutilización inicial",
      globalCooldown: "Reutilización global",
      maxStack: "Acumulación máx.",
      minPlayerLevel: "Nivel requerido",
      castFlags: "Lanzamiento",
    },
    effectTypes: { modified: "Efecto", added: "Efecto nuevo", removed: "Efecto eliminado" },
    crit: "crítico",
    footer:
      "Sitio de fans, no afiliado a Ankama. Dofus es una marca de Ankama Games. Los cambios se calculan automáticamente comparando los datos del juego entre dos versiones, gracias al proyecto de código abierto dofusdude. ¿Ves un error? Las notas de parche oficiales son la referencia.",
    adDev: "Espacio publicitario (300×600), solo visible en desarrollo",
    adLabel: "Publicidad",
    previewTitle: (c, v) => `${c} desde la ${v}`,
    previewMore: (n) => `Ver los ${n} hechizos afectados`,
    previewEmpty: "Ningún cambio de hechizos en este periodo.",
    balance: { up: "mejoras", nerf: "nerfs", mixte: "mejora y nerf", neutre: "otros cambios", label: "Resumen de los hechizos modificados" },
    verdictFilter: { all: "Todos", up: "Mejoras", nerf: "Nerfs" },
    index: "Ir al hechizo",
  },
};

export function monthLabel(lang: Lang, ym: string) {
  const [y, m] = ym.split("-").map(Number);
  return new Intl.DateTimeFormat(lang, { month: "short", year: "numeric", timeZone: "UTC" }).format(
    new Date(Date.UTC(y, m - 1, 15))
  );
}
