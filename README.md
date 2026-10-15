# Back from AFK (pour Dofus)

Site statique pour les joueurs qui reviennent sur Dofus : on choisit sa classe et sa
dernière version jouée, et on voit tous les changements de sorts, avant et après.
En français, anglais et espagnol.

- **Site** : [Astro](https://astro.build), 100 % statique. Une page par langue, classe et version de départ.
- **Données** : scripts Python qui comparent les données du jeu entre deux versions, à partir des
  releases de [dofusdude/dofus3-main](https://github.com/dofusdude/dofus3-main).
- **Mises à jour** : une GitHub Action détecte chaque nouvelle version de Dofus et ouvre une
  pull request avec les nouvelles données. Tu relis, tu fusionnes, le site se redéploie.

## Lancer le site en local

Node 22 :

```bash
npm install
npm run dev        # http://localhost:4321 (FR), /en/, /es/
npm run build      # génère dist/
```

Les données sont déjà générées dans `src/data/` : pas besoin de Python pour travailler sur le site.

## URL

| Langue | Accueil | Classe (≈ 1 an) | Classe depuis une version |
|---|---|---|---|
| FR | `/` | `/classes/iop/` | `/classes/iop/depuis-3-5/` |
| EN | `/en/` | `/en/classes/iop/` | `/en/classes/iop/since-3-5/` |
| ES | `/es/` | `/es/clases/yopuka/` | `/es/clases/yopuka/desde-3-5/` |

Les noms de classe viennent des traductions officielles du jeu (Yopuka, Ocra, Zurcarák…).
Chaque page déclare ses équivalents dans les autres langues (`hreflang`).
La version « ≈ 1 an » est recalculée à chaque build : c'est la plus récente sortie au moins
12 mois avant la version actuelle.

## Mise en ligne (une seule fois)

1. **GitHub** : crée un dépôt et pousse le projet.

   ```bash
   git init && git add . && git commit -m "Premier commit"
   git branch -M main
   git remote add origin git@github.com:<toi>/dofus-patch-tracker.git
   git push -u origin main
   ```

2. **Autoriser l'Action à ouvrir des pull requests** : dans le dépôt, *Settings → Actions →
   General → Workflow permissions*, choisir *Read and write permissions* et cocher
   *Allow GitHub Actions to create and approve pull requests*.

3. **Cloudflare Workers** : *Workers & Pages → Create → Import a repository*, choisir le dépôt, puis :
   - Build command : `npm run build`
   - Deploy command : `npx wrangler deploy`
   - Non-production branch deploy command : `npx wrangler versions upload`

   `wrangler.jsonc` indique à Cloudflare de servir le dossier `dist/`. Cloudflare redéploie à
   chaque push sur `main` et publie une version d'aperçu pour les autres branches (donc pour
   les pull requests de données) : c'est là que tu vérifies avant de fusionner.

4. **Domaine** : `backfromafk.com`, défini dans `astro.config.mjs` (URL canoniques, hreflang, sitemap) et dans `public/robots.txt`. À brancher sur le Worker : *Settings → Domains & Routes → Add → Custom domain*.

## Mises à jour automatiques

`.github/workflows/update-data.yml` tourne tous les jours (et à la demande depuis l'onglet
*Actions*, bouton *Run workflow*) :

1. `scripts/check_new_version.py` compare la dernière version publiée par dofusdude avec
   `scripts/versions.json`.
   - Nouveau build de la même mise à jour (3.7.10 → 3.7.11) : le build actuel est remplacé.
   - Nouvelle mise à jour (3.7 → 3.8) : la 3.7 devient une version de départ, la 3.8 devient
     l'actuelle, datée du mois en cours.
2. Si c'est le cas : régénération des données dans les 3 langues, build du site pour vérifier,
   puis ouverture d'une pull request `Données : Dofus <build>`.
3. Tu relis l'aperçu Cloudflare, tu corriges la date si besoin, tu fusionnes. Le site est en ligne.

`.github/workflows/ci.yml` vérifie que le site se construit à chaque pull request.

### En local

```bash
python3 scripts/check_new_version.py --dry-run   # y a-t-il du nouveau ?
npm run data                                     # régénère src/data/ (Python 3.9+, sans dépendance)
```

Le premier lancement télécharge environ 250 Mo par version dans `data/` (ignoré par git).

## Arborescence

```
.github/workflows/      update-data.yml (détection + PR), ci.yml (build)
scripts/
  diff_spells.py        compare deux versions, dans une langue (utilisable seul)
  build_site_data.py    génère src/data/<langue>/ pour toutes les versions de départ
  check_new_version.py  détecte une nouvelle version et met à jour versions.json
  versions.json         versions proposées sur le site (dates approximatives, à corriger si besoin)
src/
  data/                 JSON générés : versions.json + fr/, en/, es/ (classes et un diff par version)
  i18n/ui.ts            textes d'interface et structure des URL par langue
  lib/data.ts           lecture des données, URL, version par défaut
  components/           HomePage, ClassPage, Picker (la phrase à compléter), SpellChanges, AdSlot
  pages/                routes FR à la racine, /en/ et /es/
```

### Utiliser le comparateur seul

```bash
python3 scripts/diff_spells.py 3.3.20.19 3.7.10.10 --classe Iop --lang fr
python3 scripts/diff_spells.py 3.3.20.19 3.7.10.10 --classe Iop --lang en
```

Sortie dans `out/` (ignoré par git) : un JSON structuré et un rapport Markdown.

## Ajouter une langue

Les données du jeu existent aussi en allemand et en portugais (`de`, `pt`). Il faut :
ajouter la langue à `LANGS` et `L10N` dans `scripts/diff_spells.py`, à `LANGS`, `ROUTES` et `UI`
dans `src/i18n/ui.ts`, créer `src/pages/<langue>/` sur le modèle de `src/pages/en/`, puis
lancer `npm run data`.

## Publicité

`src/components/AdSlot.astro` réserve une colonne latérale (300×600) sur les pages de classe,
sur grand écran uniquement. En dev, un cadre pointillé la montre. En production, rien ne
s'affiche tant que `PUBLIC_ADS_ENABLED=true` n'est pas défini (variable de build,
dans Cloudflare : Settings → Build → Variables) et que le code de la régie n'est pas collé dans le composant.

## Limites connues

- Seul le grade maximal de chaque sort est comparé.
- Les « conditions de lancer » (ligne de vue, lancer en ligne…) sont signalées sans détail :
  le champ `m_flags` reste à décoder.
- Les badges up / nerf ne sont posés que lorsque le sens ne fait pas de doute : coût, portée,
  relance, ou valeur d'un même effet de dégâts, de soin ou de bonus de sort. Le reste est
  montré sans jugement.
- Le diff est net entre deux versions : un changement annulé entre-temps n'apparaît pas.
- Les dates des versions sont approximatives (mois de sortie).
- Avant d'afficher de la publicité, vérifie les conditions d'Ankama pour les sites de fans.
