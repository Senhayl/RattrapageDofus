# Back from AFK (pour Dofus)

Site statique pour les joueurs qui reviennent sur Dofus : on choisit sa classe et sa dernière
version jouée, et on voit tout ce qui a changé, avant et après. En français, anglais et espagnol.
En ligne sur https://backfromafk.com.

- **Classes** : sorts modifiés, ajoutés, retirés, avec badges up / nerf.
- **Objets, Panoplies, Donjons, Métiers** : tableaux filtrables (recherche, statut, up/nerf, type, métier).
- **Mises à jour** : une page par version (notes de patch résumées), version précédente → celle-ci.
- **Site** : [Astro](https://astro.build), 100 % statique (~830 pages), hébergé sur Cloudflare Workers.
- **Données** : scripts Python qui comparent les données du jeu entre versions, à partir des releases
  de [dofusdude/dofus3-main](https://github.com/dofusdude/dofus3-main).
- **Mises à jour automatiques** : une GitHub Action détecte chaque nouvelle version de Dofus et ouvre
  une pull request avec les nouvelles données. Tu relis, tu fusionnes, le site se redéploie.

## Lancer le site en local

Node 22 :

```bash
npm install
npm run dev        # http://localhost:4321 (FR), /en/, /es/
npm run build      # génère dist/
```

Les données sont déjà générées dans `src/data/` : pas besoin de Python pour travailler sur le site.

## Réglages : `src/config.ts`

| Réglage | Effet |
|---|---|
| `supportUrl` | Lien « Soutenir le site » en bas de chaque page (Ko-fi, Tipeee…) |
| `contactEmail` | Email affiché sur la page Confidentialité |
| `adsense.client` | Identifiant AdSense `ca-pub-…` : charge le script et génère `/ads.txt` |
| `adsense.slots.sidebar` / `inline` | Blocs d'annonces : colonne latérale (pages de classe, grand écran) et bloc dans le contenu |

Une valeur vide désactive la fonction. Rien de publicitaire n'est chargé tant que `adsense.client` est vide.

### Activer AdSense

1. Demande l'inscription sur adsense.google.com avec `backfromafk.com`. Google vérifie le site
   (quelques jours à quelques semaines) ; il faut du contenu et une page de confidentialité (déjà là).
2. Mets ton `ca-pub-…` dans `adsense.client`, pousse : `/ads.txt` est généré automatiquement.
3. Crée deux blocs d'annonces « display » (un vertical, un responsive) et colle leurs identifiants dans `slots`.
4. **Obligatoire en Europe** : dans AdSense, *Confidentialité et messages → RGPD*, active le message de
   consentement de Google (gratuit). C'est lui qui affiche la bannière cookies.

## URL

| Rubrique | FR | EN | ES |
|---|---|---|---|
| Accueil | `/` | `/en/` | `/es/` |
| Classe (≈ 1 an) | `/classes/iop/` | `/en/classes/iop/` | `/es/clases/yopuka/` |
| Classe depuis une version | `/classes/iop/depuis-3-5/` | `/en/classes/iop/since-3-5/` | `/es/clases/yopuka/desde-3-5/` |
| Objets | `/objets/` | `/en/items/` | `/es/objetos/` |
| Panoplies | `/panoplies/` | `/en/sets/` | `/es/panoplias/` |
| Donjons | `/donjons/` | `/en/dungeons/` | `/es/mazmorras/` |
| Métiers | `/metiers/`, `/metiers/bijoutier/` | `/en/professions/…` | `/es/oficios/…` |
| Mises à jour | `/mises-a-jour/3-7/` | `/en/updates/3-7/` | `/es/actualizaciones/3-7/` |
| Confidentialité | `/confidentialite/` | `/en/privacy/` | `/es/privacidad/` |

Chaque rubrique existe aussi « depuis » chaque version de départ. La version « ≈ 1 an » est recalculée
à chaque build : la plus récente sortie au moins 12 mois avant la version actuelle.

## Référencement

- `sitemap-index.xml` (toutes les pages, avec date de mise à jour) et `robots.txt`.
- Liens canoniques, `hreflang` entre FR / EN / ES, titres et descriptions par page.
- Données structurées : fil d'Ariane sur chaque page, `WebSite` et `FAQPage` sur l'accueil,
  `Article` sur les pages de classe et de mise à jour.
- Images de partage (Discord, réseaux) : `public/og/<langue>/` (accueil + une par classe),
  regénérables avec `scripts/og-images.mjs`.
- Maillage interne : menu des rubriques, liens vers toutes les classes en pied de page, liens entre versions.

## Mise en ligne (déjà faite)

1. **GitHub** : dépôt `Senhayl/RattrapageDofus`.
2. **Actions** : *Settings → Actions → General → Workflow permissions* → *Read and write* +
   *Allow GitHub Actions to create and approve pull requests*.
3. **Cloudflare Workers** (Worker `rattrapagedofus`) : build `npm run build`, deploy `npx wrangler deploy`,
   non-production `npx wrangler versions upload`. `wrangler.jsonc` sert `dist/` et la page 404.
4. **Domaine** : `backfromafk.com` (+ `www`), défini dans `astro.config.mjs` et `public/robots.txt`.

## Mises à jour automatiques

`.github/workflows/update-data.yml` tourne tous les jours (et à la demande : onglet *Actions* → *Run workflow*) :

1. `scripts/check_new_version.py` compare la dernière version publiée par dofusdude avec `scripts/versions.json`.
   - Nouveau build de la même mise à jour (3.7.10 → 3.7.11) : le build actuel est remplacé.
   - Nouvelle mise à jour (3.7 → 3.8) : la 3.7 devient une version de départ, la 3.8 devient l'actuelle,
     datée du mois en cours.
2. Si c'est le cas : régénération des données (sorts, objets, panoplies, donjons, recettes, notes de patch,
   3 langues), build du site pour vérifier, puis pull request `Données : Dofus <build>`.
3. Tu relis l'aperçu Cloudflare, tu corriges la date si besoin, tu fusionnes. Le site est en ligne.

### En local

```bash
python3 scripts/check_new_version.py --dry-run   # y a-t-il du nouveau ?
npm run data                                     # régénère src/data/ (Python 3.9+, sans dépendance, ~3 min, 2 Go de RAM)
```

Le premier lancement télécharge environ 400 Mo par version dans `data/` (ignoré par git).

## Arborescence

```
.github/workflows/      update-data.yml (détection + PR), ci.yml (build)
scripts/
  diff_spells.py        sorts de classe : compare deux versions, dans une langue (utilisable seul)
  diff_content.py       objets, panoplies, recettes, donjons (utilisable seul)
  build_site_data.py    génère src/data/ : diffs depuis chaque version de départ + notes de patch
  check_new_version.py  détecte une nouvelle version et met à jour versions.json
  og-images.mjs         images de partage
  versions.json         versions proposées sur le site (dates approximatives, à corriger si besoin)
src/
  config.ts             soutien, contact, AdSense
  data/                 JSON générés : versions.json + fr/, en/, es/ (classes, diffs, content, patches)
  i18n/                 ui.ts (interface, URL), content.ts (rubriques, FAQ, pages légales)
  lib/                  data.ts (classes), content.ts (rubriques, métiers, mises à jour)
  components/           pages (Home, Class, Category, Job, Patch, Updates, Privacy) et briques
  pages/                routes FR à la racine, /en/ et /es/, ads.txt, apercu/<langue>.json, 404
```

## Limites connues

- Sorts : seul le grade maximal est comparé ; les « conditions de lancer » sont signalées sans détail.
- Badges up / nerf : posés seulement quand le sens ne fait pas de doute.
- Diff net entre deux versions : un changement annulé entre-temps n'apparaît pas.
- Les dates des versions sont approximatives (mois de sortie).
- Avant d'afficher de la publicité, vérifie les conditions d'Ankama pour les sites de fans.
