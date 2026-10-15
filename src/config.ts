// Réglages du site à modifier à la main. Laisser une valeur vide désactive la fonction.
export const SITE = {
  name: "Back from AFK",

  /** Lien de soutien (Ko-fi, Tipeee…). Ex. "https://ko-fi.com/backfromafk" */
  supportUrl: "",

  /** Email de contact affiché sur la page Confidentialité. Ex. "contact@backfromafk.com" */
  contactEmail: "",

  /**
   * Google AdSense. Une fois le site accepté :
   * - client : l'identifiant « ca-pub-XXXXXXXXXXXXXXXX » (sert aussi à générer /ads.txt) ;
   * - slots : identifiants des blocs d'annonces créés dans AdSense (Annonces → Par bloc d'annonces).
   * Sans client, aucun script publicitaire n'est chargé.
   */
  adsense: {
    client: "",
    slots: { sidebar: "", inline: "" },
  },
};
