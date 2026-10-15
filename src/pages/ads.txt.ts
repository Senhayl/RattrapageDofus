// /ads.txt : déclare le compte AdSense autorisé à vendre les espaces du site.
import type { APIRoute } from "astro";
import { SITE } from "../config";

export const GET: APIRoute = () => {
  const pub = SITE.adsense.client.replace(/^ca-/, "");
  const body = pub ? `google.com, ${pub}, DIRECT, f08c47fec0942fa0\n` : "# AdSense non configuré\n";
  return new Response(body, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
};
