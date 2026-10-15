// Textes des pages objets, panoplies, métiers, donjons, mises à jour, FAQ et pages légales.
import type { Category, Lang } from "./ui";

type CatText = {
  name: string; // nom de la rubrique (menu)
  h1: (v: string) => string;
  title: (v: string, now: string) => string;
  description: (v: string, now: string, m: number, a: number, r: number) => string;
  intro: string;
};

type ContentDict = {
  nav: { classes: string; updates: string; label: string };
  cats: Record<Category, CatText>;
  since: string; // « depuis la »
  statut: { all: string; modified: string; added: string; removed: string };
  counts: (m: number, a: number, r: number) => string;
  search: string;
  type: string;
  allTypes: string;
  job: string;
  allJobs: string;
  verdict: string;
  allVerdicts: string;
  col: { name: string; level: string; type: string; changes: string; boss: string; recipe: string };
  showMore: (n: number) => string;
  noResult: string;
  empty: string;
  labels: Record<string, string>;
  setBonus: (n: number) => string;
  bossStat: (boss: string, stat: string) => string;
  bossSpell: (boss: string) => string;
  recipeLevel: (a: number, b: number) => string;
  newItemEffects: string;
  setItems: string;
  jobH1: (job: string, v: string) => string;
  jobTitle: (job: string, v: string, now: string) => string;
  jobDescription: (job: string, v: string, now: string, m: number, a: number, r: number) => string;
  jobsIntro: string;
  jobCount: (n: number) => string;
  patchJobsNote: (prev: string) => string;
  // mises à jour
  updatesTitle: string;
  updatesDescription: string;
  updatesH1: string;
  updatesIntro: string;
  patchH1: (v: string) => string;
  patchTitle: (v: string, d: string) => string;
  patchDescription: (v: string, prev: string, s: number, o: number) => string;
  patchIntro: (v: string, prev: string, d: string) => string;
  patchClasses: string;
  patchSpellCount: (n: number) => string;
  patchSummary: (s: number, o: number, p: number, d: number, m: number) => string;
  seeAll: string;
  // accueil
  homeCats: (v: string) => string;
  homeUpdates: string;
  faqTitle: string;
  faq: { q: string; a: string }[];
  // pied de page et légal
  support: string;
  supportPitch: string;
  privacy: string;
  privacyTitle: string;
  breadcrumbHome: string;
  notFoundTitle: string;
  notFoundText: string;
  notFoundBack: string;
};

const FR: ContentDict = {
  nav: { classes: "Classes", updates: "Mises à jour", label: "Rubriques" },
  cats: {
    objets: {
      name: "Objets",
      h1: (v) => `Équipements modifiés`,
      title: (v, now) => `Objets Dofus modifiés depuis la ${v} : up, nerfs, nouveautés (${now})`,
      description: (v, now, m, a, r) =>
        `Tous les équipements Dofus qui ont changé entre la ${v} et la ${now} : ${m} modifiés, ${a} nouveaux, ${r} retirés. Statistiques avant et après, filtres par type et niveau.`,
      intro: "Armes, chapeaux, capes, anneaux, familiers… Chaque ligne montre les caractéristiques avant et après.",
    },
    panoplies: {
      name: "Panoplies",
      h1: (v) => `Panoplies modifiées`,
      title: (v, now) => `Panoplies Dofus modifiées depuis la ${v} : bonus avant et après (${now})`,
      description: (v, now, m, a, r) =>
        `Les panoplies Dofus qui ont changé entre la ${v} et la ${now} : ${m} modifiées, ${a} nouvelles, ${r} retirées. Bonus par nombre d'objets, avant et après.`,
      intro: "Bonus de panoplie par nombre d'objets portés, et objets ajoutés ou retirés des panoplies.",
    },
    metiers: {
      name: "Métiers",
      h1: (v) => `Recettes de métiers modifiées`,
      title: (v, now) => `Recettes Dofus modifiées depuis la ${v}, par métier (${now})`,
      description: (v, now, m, a, r) =>
        `Toutes les recettes Dofus qui ont changé entre la ${v} et la ${now}, métier par métier : ${m} modifiées, ${a} nouvelles, ${r} retirées. Ingrédients avant et après.`,
      intro: "Ingrédients et quantités avant et après, pour chaque métier.",
    },
    donjons: {
      name: "Donjons",
      h1: (v) => `Donjons et boss modifiés`,
      title: (v, now) => `Donjons Dofus modifiés depuis la ${v} : nouveaux donjons et boss (${now})`,
      description: (v, now, m, a, r) =>
        `Les donjons Dofus qui ont changé entre la ${v} et la ${now} : ${a} nouveaux, ${m} modifiés. Points de vie, PA, PM, résistances et sorts des boss, avant et après.`,
      intro: "Nouveaux donjons, niveau conseillé, et pour chaque boss : points de vie, PA, PM, résistances et sorts.",
    },
  },
  since: "depuis la",
  statut: { all: "Tous", modified: "Modifiés", added: "Nouveaux", removed: "Retirés" },
  counts: (m, a, r) => `${m} modifiés, ${a} nouveaux, ${r} retirés`,
  search: "Rechercher",
  type: "Type",
  allTypes: "Tous les types",
  job: "Métier",
  allJobs: "Tous les métiers",
  verdict: "Sens",
  allVerdicts: "Up et nerfs",
  col: { name: "Nom", level: "Niv.", type: "Type", changes: "Changements", boss: "Boss", recipe: "Recette" },
  showMore: (n) => `Afficher ${n} de plus`,
  noResult: "Aucun résultat avec ces filtres.",
  empty: "Aucun changement dans cette rubrique sur cette période.",
  labels: {
    name: "Nom", level: "Niveau", effect: "Effet", dungeonLevel: "Niveau conseillé", boss: "Nouveau boss",
    added: "ajouté", removed: "retiré",
    boss_level: "niveau", boss_lifePoints: "PV", boss_actionPoints: "PA", boss_movementPoints: "PM",
    boss_reductionEarth: "% rés. Terre", boss_reductionFire: "% rés. Feu", boss_reductionWater: "% rés. Eau",
    boss_reductionAir: "% rés. Air", boss_reductionNeutral: "% rés. Neutre",
  },
  setBonus: (n) => `Bonus ${n} objet${n > 1 ? "s" : ""}`,
  bossStat: (boss, stat) => `${boss} : ${stat}`,
  bossSpell: (boss) => `${boss} : sort`,
  recipeLevel: (a, b) => `niveau ${a} → ${b}`,
  newItemEffects: "Effets",
  setItems: "Objets",
  jobH1: (j, v) => `Recettes ${j} modifiées`,
  jobTitle: (j, v, now) => `Recettes ${j} Dofus modifiées depuis la ${v} (${now})`,
  jobDescription: (j, v, now, m, a, r) =>
    `Toutes les recettes du métier ${j} qui ont changé entre la ${v} et la ${now} : ${m} modifiées, ${a} nouvelles, ${r} retirées. Ingrédients avant et après.`,
  jobsIntro: "Choisis un métier pour voir ses recettes modifiées, ajoutées ou retirées, avec les ingrédients avant et après.",
  jobCount: (n) => `${n} recette${n > 1 ? "s" : ""}`,
  patchJobsNote: (prev) => `Nombre de recettes concernées par métier. Le détail s'ouvre sur la page du métier (changements depuis la ${prev}).`,
  updatesTitle: "Notes de patch Dofus 3 : toutes les mises à jour, résumées",
  updatesDescription:
    "Chaque mise à jour de Dofus 3 résumée : sorts de classe, équipements, panoplies, donjons et recettes modifiés, avant et après.",
  updatesH1: "Mises à jour de Dofus 3",
  updatesIntro: "Ce que chaque mise à jour a changé par rapport à la précédente, calculé à partir des données du jeu.",
  patchH1: (v) => `Mise à jour ${v} : tout ce qui a changé`,
  patchTitle: (v, d) => `Dofus ${v} : notes de patch résumées (${d}) – sorts, objets, donjons`,
  patchDescription: (v, prev, s, o) =>
    `Résumé de la mise à jour Dofus ${v} par rapport à la ${prev} : ${s} sorts de classe et ${o} équipements modifiés, avec les valeurs avant et après.`,
  patchIntro: (v, prev, d) => `Changements entre la ${prev} et la ${v} (${d}), classe par classe et rubrique par rubrique.`,
  patchClasses: "Sorts de classe",
  patchSpellCount: (n) => `${n} sort${n > 1 ? "s" : ""}`,
  patchSummary: (s, o, p, d, m) =>
    `${s} sorts, ${o} objets, ${p} panoplies, ${d} donjons et ${m} recettes concernés.`,
  seeAll: "Voir le détail",
  homeCats: (v) => `Et le reste du jeu depuis la ${v}`,
  homeUpdates: "Mises à jour récentes",
  faqTitle: "Questions fréquentes",
  faq: [
    {
      q: "Qu'est-ce qui a changé sur Dofus depuis ma dernière partie ?",
      a: "Choisis ta dernière version jouée et ta classe en haut de la page : tu verras chaque sort modifié, avec les valeurs avant et après. Les rubriques Objets, Panoplies, Donjons et Métiers couvrent le reste du jeu.",
    },
    {
      q: "D'où viennent les données ?",
      a: "Elles sont extraites des fichiers du jeu à chaque mise à jour, grâce au projet open source dofusdude, puis comparées automatiquement. Rien n'est recopié à la main, ce qui évite les oublis des résumés classiques.",
    },
    {
      q: "Que veulent dire « up » et « nerf » ?",
      a: "Un up rend un sort ou un objet plus fort (dégâts en hausse, coût en PA en baisse…), un nerf le rend plus faible. Le badge n'est affiché que quand le sens ne fait aucun doute ; sinon le changement est montré sans jugement.",
    },
    {
      q: "Le site est-il à jour ?",
      a: "Oui : il vérifie chaque jour si une nouvelle version de Dofus est sortie et se met à jour peu après. La version utilisée est indiquée en haut de chaque page.",
    },
  ],
  support: "Soutenir le site",
  supportPitch: "Back from AFK est gratuit, sans compte et sans pub. Si le site t'a fait gagner du temps, un petit don aide à couvrir ses frais pour qu'il reste en ligne.",
  privacy: "Confidentialité et mentions légales",
  privacyTitle: "Confidentialité et mentions légales",
  breadcrumbHome: "Accueil",
  notFoundTitle: "Page introuvable",
  notFoundText: "Cette page n'existe pas, ou plus. Le contenu change à chaque mise à jour du jeu.",
  notFoundBack: "Retour à l'accueil",
};

const EN: ContentDict = {
  nav: { classes: "Classes", updates: "Updates", label: "Sections" },
  cats: {
    objets: {
      name: "Items",
      h1: (v) => `Equipment changed`,
      title: (v, now) => `Dofus items changed since ${v}: buffs, nerfs, new items (${now})`,
      description: (v, now, m, a, r) =>
        `Every Dofus equipment change between ${v} and ${now}: ${m} changed, ${a} new, ${r} removed. Stats before and after, filter by type and level.`,
      intro: "Weapons, hats, cloaks, rings, pets… Each row shows the stats before and after.",
    },
    panoplies: {
      name: "Sets",
      h1: (v) => `Sets changed`,
      title: (v, now) => `Dofus sets changed since ${v}: bonuses before and after (${now})`,
      description: (v, now, m, a, r) =>
        `Dofus item sets that changed between ${v} and ${now}: ${m} changed, ${a} new, ${r} removed. Bonuses per number of items, before and after.`,
      intro: "Set bonuses per number of items worn, and items added to or removed from sets.",
    },
    metiers: {
      name: "Professions",
      h1: (v) => `Profession recipes changed`,
      title: (v, now) => `Dofus recipes changed since ${v}, by profession (${now})`,
      description: (v, now, m, a, r) =>
        `Every Dofus recipe that changed between ${v} and ${now}, profession by profession: ${m} changed, ${a} new, ${r} removed. Ingredients before and after.`,
      intro: "Ingredients and quantities before and after, for every profession.",
    },
    donjons: {
      name: "Dungeons",
      h1: (v) => `Dungeons and bosses changed`,
      title: (v, now) => `Dofus dungeons changed since ${v}: new dungeons and bosses (${now})`,
      description: (v, now, m, a, r) =>
        `Dofus dungeons that changed between ${v} and ${now}: ${a} new, ${m} changed. Boss HP, AP, MP, resistances and spells, before and after.`,
      intro: "New dungeons, recommended level, and for every boss: HP, AP, MP, resistances and spells.",
    },
  },
  since: "since",
  statut: { all: "All", modified: "Changed", added: "New", removed: "Removed" },
  counts: (m, a, r) => `${m} changed, ${a} new, ${r} removed`,
  search: "Search",
  type: "Type",
  allTypes: "All types",
  job: "Profession",
  allJobs: "All professions",
  verdict: "Direction",
  allVerdicts: "Buffs and nerfs",
  col: { name: "Name", level: "Lvl", type: "Type", changes: "Changes", boss: "Bosses", recipe: "Recipe" },
  showMore: (n) => `Show ${n} more`,
  noResult: "No results with these filters.",
  empty: "No changes in this section over this period.",
  labels: {
    name: "Name", level: "Level", effect: "Effect", dungeonLevel: "Recommended level", boss: "New boss",
    added: "added", removed: "removed",
    boss_level: "level", boss_lifePoints: "HP", boss_actionPoints: "AP", boss_movementPoints: "MP",
    boss_reductionEarth: "% Earth res.", boss_reductionFire: "% Fire res.", boss_reductionWater: "% Water res.",
    boss_reductionAir: "% Air res.", boss_reductionNeutral: "% Neutral res.",
  },
  setBonus: (n) => `${n}-item bonus`,
  bossStat: (boss, stat) => `${boss}: ${stat}`,
  bossSpell: (boss) => `${boss}: spell`,
  recipeLevel: (a, b) => `level ${a} → ${b}`,
  newItemEffects: "Effects",
  setItems: "Items",
  jobH1: (j, v) => `${j} recipes changed`,
  jobTitle: (j, v, now) => `Dofus ${j} recipes changed since ${v} (${now})`,
  jobDescription: (j, v, now, m, a, r) =>
    `Every ${j} recipe that changed between ${v} and ${now}: ${m} changed, ${a} new, ${r} removed. Ingredients before and after.`,
  jobsIntro: "Pick a profession to see its changed, new or removed recipes, with ingredients before and after.",
  jobCount: (n) => `${n} recipe${n > 1 ? "s" : ""}`,
  patchJobsNote: (prev) => `Number of recipes affected per profession. Details open on the profession page (changes since ${prev}).`,
  updatesTitle: "Dofus 3 patch notes: every update, summarised",
  updatesDescription:
    "Every Dofus 3 update summarised: class spells, equipment, sets, dungeons and recipes that changed, before and after.",
  updatesH1: "Dofus 3 updates",
  updatesIntro: "What each update changed compared with the previous one, computed from the game data.",
  patchH1: (v) => `Update ${v}: everything that changed`,
  patchTitle: (v, d) => `Dofus ${v} patch notes summarised (${d}): spells, items, dungeons`,
  patchDescription: (v, prev, s, o) =>
    `Summary of Dofus update ${v} compared with ${prev}: ${s} class spells and ${o} items changed, with values before and after.`,
  patchIntro: (v, prev, d) => `Changes between ${prev} and ${v} (${d}), class by class and section by section.`,
  patchClasses: "Class spells",
  patchSpellCount: (n) => `${n} spell${n > 1 ? "s" : ""}`,
  patchSummary: (s, o, p, d, m) => `${s} spells, ${o} items, ${p} sets, ${d} dungeons and ${m} recipes affected.`,
  seeAll: "See details",
  homeCats: (v) => `And the rest of the game since ${v}`,
  homeUpdates: "Recent updates",
  faqTitle: "Frequently asked questions",
  faq: [
    {
      q: "What changed in Dofus since I last played?",
      a: "Pick the last version you played and your class at the top of the page: you'll see every changed spell with its values before and after. The Items, Sets, Dungeons and Professions sections cover the rest of the game.",
    },
    {
      q: "Where does the data come from?",
      a: "It's extracted from the game files at every update, thanks to the open source dofusdude project, then compared automatically. Nothing is copied by hand, so nothing gets left out.",
    },
    {
      q: "What do “buff” and “nerf” mean?",
      a: "A buff makes a spell or item stronger (more damage, lower AP cost…), a nerf makes it weaker. The badge only appears when the direction is unambiguous; otherwise the change is shown without a verdict.",
    },
    {
      q: "Is the site up to date?",
      a: "Yes: it checks every day for a new Dofus version and updates shortly after. The version used is shown at the top of every page.",
    },
  ],
  support: "Support the site",
  supportPitch: "Back from AFK is free, with no account and no ads. If it saved you some time, a small tip helps cover its costs so it can stay online.",
  privacy: "Privacy and legal notice",
  privacyTitle: "Privacy and legal notice",
  breadcrumbHome: "Home",
  notFoundTitle: "Page not found",
  notFoundText: "This page doesn't exist, or no longer does. Content changes with every game update.",
  notFoundBack: "Back to home",
};

const ES: ContentDict = {
  nav: { classes: "Clases", updates: "Actualizaciones", label: "Secciones" },
  cats: {
    objets: {
      name: "Objetos",
      h1: (v) => `Equipamiento modificado`,
      title: (v, now) => `Objetos de Dofus modificados desde la ${v}: mejoras, nerfs, novedades (${now})`,
      description: (v, now, m, a, r) =>
        `Todos los equipamientos de Dofus que han cambiado entre la ${v} y la ${now}: ${m} modificados, ${a} nuevos, ${r} eliminados. Estadísticas antes y después.`,
      intro: "Armas, sombreros, capas, anillos, mascotas… Cada fila muestra las características antes y después.",
    },
    panoplies: {
      name: "Panoplias",
      h1: (v) => `Panoplias modificadas`,
      title: (v, now) => `Panoplias de Dofus modificadas desde la ${v}: bonus antes y después (${now})`,
      description: (v, now, m, a, r) =>
        `Las panoplias de Dofus que han cambiado entre la ${v} y la ${now}: ${m} modificadas, ${a} nuevas, ${r} eliminadas. Bonus por número de objetos, antes y después.`,
      intro: "Bonus de panoplia por número de objetos equipados, y objetos añadidos o retirados.",
    },
    metiers: {
      name: "Oficios",
      h1: (v) => `Recetas de oficios modificadas`,
      title: (v, now) => `Recetas de Dofus modificadas desde la ${v}, por oficio (${now})`,
      description: (v, now, m, a, r) =>
        `Todas las recetas de Dofus que han cambiado entre la ${v} y la ${now}, oficio por oficio: ${m} modificadas, ${a} nuevas, ${r} eliminadas. Ingredientes antes y después.`,
      intro: "Ingredientes y cantidades antes y después, para cada oficio.",
    },
    donjons: {
      name: "Mazmorras",
      h1: (v) => `Mazmorras y jefes modificados`,
      title: (v, now) => `Mazmorras de Dofus modificadas desde la ${v}: nuevas mazmorras y jefes (${now})`,
      description: (v, now, m, a, r) =>
        `Las mazmorras de Dofus que han cambiado entre la ${v} y la ${now}: ${a} nuevas, ${m} modificadas. PV, PA, PM, resistencias y hechizos de los jefes, antes y después.`,
      intro: "Nuevas mazmorras, nivel recomendado y, para cada jefe: PV, PA, PM, resistencias y hechizos.",
    },
  },
  since: "desde la",
  statut: { all: "Todos", modified: "Modificados", added: "Nuevos", removed: "Eliminados" },
  counts: (m, a, r) => `${m} modificados, ${a} nuevos, ${r} eliminados`,
  search: "Buscar",
  type: "Tipo",
  allTypes: "Todos los tipos",
  job: "Oficio",
  allJobs: "Todos los oficios",
  verdict: "Sentido",
  allVerdicts: "Mejoras y nerfs",
  col: { name: "Nombre", level: "Niv.", type: "Tipo", changes: "Cambios", boss: "Jefes", recipe: "Receta" },
  showMore: (n) => `Mostrar ${n} más`,
  noResult: "Ningún resultado con estos filtros.",
  empty: "Ningún cambio en esta sección durante este periodo.",
  labels: {
    name: "Nombre", level: "Nivel", effect: "Efecto", dungeonLevel: "Nivel recomendado", boss: "Nuevo jefe",
    added: "añadido", removed: "eliminado",
    boss_level: "nivel", boss_lifePoints: "PV", boss_actionPoints: "PA", boss_movementPoints: "PM",
    boss_reductionEarth: "% res. Tierra", boss_reductionFire: "% res. Fuego", boss_reductionWater: "% res. Agua",
    boss_reductionAir: "% res. Aire", boss_reductionNeutral: "% res. Neutral",
  },
  setBonus: (n) => `Bonus ${n} objeto${n > 1 ? "s" : ""}`,
  bossStat: (boss, stat) => `${boss}: ${stat}`,
  bossSpell: (boss) => `${boss}: hechizo`,
  recipeLevel: (a, b) => `nivel ${a} → ${b}`,
  newItemEffects: "Efectos",
  setItems: "Objetos",
  jobH1: (j, v) => `Recetas de ${j} modificadas`,
  jobTitle: (j, v, now) => `Recetas de ${j} en Dofus modificadas desde la ${v} (${now})`,
  jobDescription: (j, v, now, m, a, r) =>
    `Todas las recetas del oficio ${j} que han cambiado entre la ${v} y la ${now}: ${m} modificadas, ${a} nuevas, ${r} eliminadas. Ingredientes antes y después.`,
  jobsIntro: "Elige un oficio para ver sus recetas modificadas, nuevas o eliminadas, con los ingredientes antes y después.",
  jobCount: (n) => `${n} receta${n > 1 ? "s" : ""}`,
  patchJobsNote: (prev) => `Número de recetas afectadas por oficio. El detalle se abre en la página del oficio (cambios desde la ${prev}).`,
  updatesTitle: "Notas de parche de Dofus 3: todas las actualizaciones, resumidas",
  updatesDescription:
    "Cada actualización de Dofus 3 resumida: hechizos de clase, equipamiento, panoplias, mazmorras y recetas modificados, antes y después.",
  updatesH1: "Actualizaciones de Dofus 3",
  updatesIntro: "Lo que cambió cada actualización respecto a la anterior, calculado a partir de los datos del juego.",
  patchH1: (v) => `Actualización ${v}: todo lo que ha cambiado`,
  patchTitle: (v, d) => `Dofus ${v}: notas de parche resumidas (${d}) – hechizos, objetos, mazmorras`,
  patchDescription: (v, prev, s, o) =>
    `Resumen de la actualización ${v} de Dofus respecto a la ${prev}: ${s} hechizos de clase y ${o} objetos modificados, con los valores antes y después.`,
  patchIntro: (v, prev, d) => `Cambios entre la ${prev} y la ${v} (${d}), clase por clase y sección por sección.`,
  patchClasses: "Hechizos de clase",
  patchSpellCount: (n) => `${n} hechizo${n > 1 ? "s" : ""}`,
  patchSummary: (s, o, p, d, m) =>
    `${s} hechizos, ${o} objetos, ${p} panoplias, ${d} mazmorras y ${m} recetas afectados.`,
  seeAll: "Ver el detalle",
  homeCats: (v) => `Y el resto del juego desde la ${v}`,
  homeUpdates: "Actualizaciones recientes",
  faqTitle: "Preguntas frecuentes",
  faq: [
    {
      q: "¿Qué ha cambiado en Dofus desde mi última partida?",
      a: "Elige la última versión que jugaste y tu clase arriba de la página: verás cada hechizo modificado con sus valores antes y después. Las secciones Objetos, Panoplias, Mazmorras y Oficios cubren el resto del juego.",
    },
    {
      q: "¿De dónde vienen los datos?",
      a: "Se extraen de los archivos del juego en cada actualización, gracias al proyecto de código abierto dofusdude, y se comparan automáticamente. Nada se copia a mano, así que no se olvida nada.",
    },
    {
      q: "¿Qué significan «mejora» y «nerf»?",
      a: "Una mejora hace un hechizo u objeto más fuerte (más daño, menos coste en PA…), un nerf lo hace más débil. La etiqueta solo aparece cuando el sentido no deja dudas; si no, el cambio se muestra sin valoración.",
    },
    {
      q: "¿Está actualizado el sitio?",
      a: "Sí: comprueba cada día si ha salido una nueva versión de Dofus y se actualiza poco después. La versión usada se indica arriba de cada página.",
    },
  ],
  support: "Apoyar el sitio",
  supportPitch: "Back from AFK es gratis, sin cuenta y sin publicidad. Si te ha ahorrado tiempo, una pequeña aportación ayuda a cubrir sus gastos para que siga en línea.",
  privacy: "Privacidad y aviso legal",
  privacyTitle: "Privacidad y aviso legal",
  breadcrumbHome: "Inicio",
  notFoundTitle: "Página no encontrada",
  notFoundText: "Esta página no existe, o ya no existe. El contenido cambia con cada actualización del juego.",
  notFoundBack: "Volver al inicio",
};

export const CT: Record<Lang, ContentDict> = { fr: FR, en: EN, es: ES };
