// Données de l'aperçu de l'accueil, chargées à la demande par le navigateur :
// pour chaque classe et chaque version de départ, le nombre de sorts concernés
// et quelques changements marquants.
import type { APIRoute, GetStaticPaths } from "astro";
import { LANGS, type Lang } from "../../i18n/ui";
import { getClasses, getClassDiff, versions, classUrl, countChanges, highlightsOf, balanceOf } from "../../lib/data";

export const getStaticPaths: GetStaticPaths = () => LANGS.map((lang) => ({ params: { lang } }));

export const GET: APIRoute = ({ params }) => {
  const lang = params.lang as Lang;
  const out: Record<string, Record<string, unknown>> = {};
  for (const c of getClasses(lang)) {
    out[c.slug] = {};
    for (const v of versions.depart) {
      const d = getClassDiff(lang, v.version, c.id);
      out[c.slug][v.version] = {
        n: countChanges(d),
        url: classUrl(lang, c.id, v.version),
        balance: balanceOf(d),
        lines: highlightsOf(lang, d),
      };
    }
  }
  return new Response(JSON.stringify(out), { headers: { "Content-Type": "application/json" } });
};
