#!/usr/bin/env python3
"""
Compare entre deux versions de Dofus 3 : équipements, panoplies, recettes (métiers) et donjons.

S'appuie sur diff_spells.GameData pour les textes (3 langues) et le rendu des effets.
Utilisé par build_site_data.py ; peut aussi se lancer seul :

    python3 scripts/diff_content.py 3.6.12.16 3.7.10.10 --lang fr

Format de sortie (voir aussi src/lib/content.ts) :
    {"objets":     [ {id, nom, type, niveau, statut, changements:[...] , verdict} ],
     "panoplies":  [ {id, nom, niveau, statut, changements:[...], verdict} ],
     "metiers":    [ {id, nom, lignes:[ {id, nom, niveau, statut, avant, apres} ]} ],
     "donjons":    [ {id, nom, niveau, boss, statut, changements:[...], verdict} ]}
statut : "added" | "removed" | "modified"
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diff_spells as D  # noqa: E402

CONTENT_TABLES = ["items", "item_sets", "item_types", "recipes", "dungeons", "monsters"]
EQUIPMENT_CATEGORY = 0  # item_types.categoryId : 0 = équipements (armes, chapeaux, familiers…)

# Statistiques de boss suivies (grade maximal). Ancien nom -> nom actuel.
BOSS_STATS = {
    "level": "level", "lifePoints": "lifePoints", "actionPoints": "actionPoints",
    "movementPoints": "movementPoints",
    "earthResistance": "reductionEarth", "fireResistance": "reductionFire",
    "waterResistance": "reductionWater", "airResistance": "reductionAir",
    "neutralResistance": "reductionNeutral",
}
BOSS_STAT_KEYS = ["level", "lifePoints", "actionPoints", "movementPoints", "reductionEarth",
                  "reductionFire", "reductionWater", "reductionAir", "reductionNeutral"]


def load_objects(vdir, name):
    """Table complète : clé -> données, en résolvant les références internes (rid)."""
    with open(os.path.join(vdir, name + ".json"), encoding="utf-8") as fh:
        raw = json.load(fh)
    by_rid = {r["rid"]: r.get("data") for r in raw["references"]["RefIds"]}
    o = raw["objectsById"]
    vals = o["m_values"]
    vals = vals.get("Array", vals) if isinstance(vals, dict) else vals
    table = {k: by_rid.get(v["rid"]) for k, v in zip(o["m_keys"]["Array"], vals)}
    return table, by_rid


def norm_effect(e):
    e = dict(e)
    if "actionId" not in e:
        e["actionId"] = e.get("effectId")
    return e


def ensure_content(version):
    vdir = os.path.join(D.DATA_DIR, version)
    for f in CONTENT_TABLES:
        path = os.path.join(vdir, f + ".json")
        if not os.path.exists(path):
            print(f"  téléchargement {version}/{f}.json ...", file=sys.stderr)
            tmp = path + ".part"
            import urllib.request
            urllib.request.urlretrieve(D.RELEASE_URL.format(v=version, f=f), tmp)
            os.replace(tmp, path)
    return vdir


class ContentData:
    """Équipements, panoplies, recettes et donjons d'une version, en forme compacte."""

    def __init__(self, gd: D.GameData):
        self.gd = gd
        vdir = ensure_content(gd.version)
        print(f"Chargement contenu {gd.version} ...", file=sys.stderr)

        types, _ = load_objects(vdir, "item_types")
        self.types = {k: v for k, v in types.items() if v}
        equip_types = {k for k, v in self.types.items() if v.get("categoryId") == EQUIPMENT_CATEGORY}

        items, by_rid = load_objects(vdir, "items")
        self.item_names = {}  # tous les objets (pour les ingrédients et panoplies)
        self.items = {}       # équipements seulement, avec effets
        for iid, it in items.items():
            if not it:
                continue
            self.item_names[iid] = it.get("nameId")
            if it.get("typeId") in equip_types:
                effects = []
                for ref in it.get("possibleEffects", {}).get("Array", []):
                    e = by_rid.get(ref["rid"]) if "rid" in ref else ref
                    if e:
                        effects.append(norm_effect(e))
                self.items[iid] = {"nameId": it.get("nameId"), "typeId": it.get("typeId"),
                                   "level": it.get("level"), "setId": it.get("itemSetId", -1),
                                   "effects": effects}
        del items, by_rid

        sets, by_rid = load_objects(vdir, "item_sets")
        self.sets = {}
        self.all_sets = {k for k, v in sets.items() if v}
        self.cosmetic_sets = {k for k, v in sets.items() if v and v.get("isCosmetic")}
        for sid, s in sets.items():
            if not s or s.get("isCosmetic"):
                continue
            bonuses = []
            for slot in s.get("effects", {}).get("Array", []):
                bonuses.append([norm_effect(by_rid[r["rid"]]) for r in slot.get("values", {}).get("Array", [])
                                if by_rid.get(r["rid"])])
            self.sets[sid] = {"nameId": s.get("nameId"), "items": s.get("items", {}).get("Array", []),
                              "bonuses": bonuses}
        del sets, by_rid

        recipes, _ = load_objects(vdir, "recipes")
        self.recipes = {}
        for rid_, r in recipes.items():
            if not r:
                continue
            self.recipes[r["resultId"]] = {
                "jobId": r.get("jobId"), "level": r.get("resultLevel"),
                "ingredients": tuple(sorted(zip(r.get("ingredientIds", {}).get("Array", []),
                                                r.get("quantities", {}).get("Array", [])))),
            }
        del recipes

        dungeons, _ = load_objects(vdir, "dungeons")
        self.dungeons = {k: v for k, v in dungeons.items() if v}
        monsters, _ = load_objects(vdir, "monsters")
        # tous les monstres en forme compacte : les anciennes versions n'indiquent pas
        # toujours les boss des donjons, on compare donc à partir de la version récente
        self.bosses = {}
        for mid, m in monsters.items():
            if not m:
                continue
            grades = m.get("grades", {}).get("Array", [])
            g = grades[-1] if grades else {}
            stats = {}
            for old, new in BOSS_STATS.items():
                if new in g:
                    stats[new] = g[new]
                elif old in g:
                    stats[new] = g[old]
            self.bosses[mid] = {"nameId": m.get("nameId"), "stats": stats,
                                "spells": m.get("spells", {}).get("Array", [])}
        del monsters

    # textes dans la langue courante de self.gd
    def name(self, text_id):
        return self.gd.t(text_id)

    def item_name(self, iid):
        return self.name(self.item_names.get(iid)) or f"#{iid}"

    def type_name(self, tid):
        t = self.types.get(tid)
        return self.name(t.get("nameId")) if t else ""

    def set_level(self, sid):
        s = self.sets.get(sid)
        lv = [self.items[i]["level"] for i in s["items"] if i in self.items] if s else []
        return max(lv) if lv else None


# ---------------------------------------------------------------- effets d'objets

def visible_effect(gd, e):
    return e["actionId"] in gd.effects and D.is_visible(item_effect_text(gd, e))


def item_effect_text(gd, e):
    """Texte d'un effet d'objet ou de panoplie (sans zone, qui n'a pas de sens ici)."""
    return D.effect_text(gd, dict(e, zoneDescr={}))


def is_malus(gd, e):
    meta = gd.effects.get(e["actionId"]) or {}
    return meta.get("characteristicOperator") == "-" or item_effect_text(gd, e).startswith("-")


def effect_magnitude(e):
    lo, hi = e.get("diceNum", 0), e.get("diceSide", 0)
    return max(abs(lo), abs(hi))


def stat_verdict(gd, oe, ne):
    """Bonus d'objet : une valeur plus haute est un up, sauf pour les malus (opérateur « - »)."""
    if oe["actionId"] != ne["actionId"]:
        return None
    a, b = effect_magnitude(oe), effect_magnitude(ne)
    if a == b:
        return None
    malus = is_malus(gd, ne)
    return ("up" if b > a else "nerf") if not malus else ("nerf" if b > a else "up")


def diff_effect_lists(old_cd, new_cd, old_list, new_list):
    """Effets d'objet ou de panoplie : appariés par type d'effet, puis dans l'ordre pour les
    dégâts d'arme dont seul l'élément change (ex. « dommages Feu » -> « dommages Neutre »)."""
    ogd, ngd = old_cd.gd, new_cd.gd
    old_list = [e for e in old_list if visible_effect(ogd, e)]
    new_list = [e for e in new_list if visible_effect(ngd, e)]
    rest_old = list(old_list)
    out = []
    rest_new = []
    for ne in new_list:
        oe = next((o for o in rest_old if o["actionId"] == ne["actionId"]), None)
        if oe is None:
            rest_new.append(ne)
            continue
        rest_old.remove(oe)
        before, after = item_effect_text(ogd, oe), item_effect_text(ngd, ne)
        if before != after:
            out.append({"cle": "effect", "type": "modified", "avant": before, "apres": after,
                        "verdict": stat_verdict(ngd, oe, ne)})

    def is_damage(gd, e):
        return (gd.effects.get(e["actionId"]) or {}).get("category") == 2
    for ne in list(rest_new):
        if not is_damage(ngd, ne):
            continue
        oe = next((o for o in rest_old if is_damage(ogd, o)), None)
        if oe is not None:
            rest_old.remove(oe)
            rest_new.remove(ne)
            out.append({"cle": "effect", "type": "modified", "avant": item_effect_text(ogd, oe),
                        "apres": item_effect_text(ngd, ne), "verdict": None})
    # un bonus gagné ou un malus retiré est un up, et inversement
    for ne in rest_new:
        out.append({"cle": "effect", "type": "added", "avant": None, "apres": item_effect_text(ngd, ne),
                    "verdict": "nerf" if is_malus(ngd, ne) else "up"})
    for oe in rest_old:
        out.append({"cle": "effect", "type": "removed", "avant": item_effect_text(ogd, oe), "apres": None,
                    "verdict": "up" if is_malus(ogd, oe) else "nerf"})
    return [c for c in out if D.is_visible(c["avant"]) and D.is_visible(c["apres"])]


def overall(changes):
    vs = [c.get("verdict") for c in changes if c.get("verdict")]
    ups, nerfs = vs.count("up"), vs.count("nerf")
    return "mixte" if ups and nerfs else "up" if ups else "nerf" if nerfs else None


# ---------------------------------------------------------------- catégories

def diff_items(o, n):
    rows = []
    for iid, it in n.items.items():
        old = o.items.get(iid)
        base = {"id": iid, "nom": n.item_name(iid), "type": n.type_name(it["typeId"]), "niveau": it["level"]}
        if old is None and iid in o.item_names:
            continue  # objet qui existait déjà mais a changé de catégorie
        if old is None:
            effects = [item_effect_text(n.gd, e) for e in it["effects"] if visible_effect(n.gd, e)]
            rows.append({**base, "statut": "added",
                         "changements": [{"cle": "effect", "type": "added", "avant": None, "apres": t}
                                         for t in effects if D.is_visible(t)]})
            continue
        ch = []
        if o.item_name(iid) != n.item_name(iid):
            ch.append({"cle": "name", "avant": o.item_name(iid), "apres": n.item_name(iid)})
        if old["level"] != it["level"]:
            ch.append({"cle": "level", "avant": old["level"], "apres": it["level"]})
        ch += diff_effect_lists(o, n, old["effects"], it["effects"])
        if ch:
            rows.append({**base, "statut": "modified", "changements": ch, "verdict": overall(ch)})
    for iid, it in o.items.items():
        if iid not in n.item_names:  # réellement supprimé du jeu
            rows.append({"id": iid, "nom": o.item_name(iid), "type": o.type_name(it["typeId"]),
                         "niveau": it["level"], "statut": "removed", "changements": []})
    rows.sort(key=lambda r: (-(r["niveau"] or 0), r["nom"]))
    return rows


def diff_sets(o, n):
    rows = []
    cosmetic = o.cosmetic_sets | n.cosmetic_sets

    def skip(cd, sid):
        # panoplies d'apparat, ou sans aucun équipement (cosmétiques non marquées)
        return sid in cosmetic or cd.set_level(sid) is None

    for sid, s in n.sets.items():
        if skip(n, sid):
            continue
        old = o.sets.get(sid)
        base = {"id": sid, "nom": n.name(s["nameId"]), "niveau": n.set_level(sid)}
        if old is None and sid in o.all_sets:
            continue
        if old is None:
            rows.append({**base, "statut": "added",
                         "objets": [n.item_name(i) for i in s["items"]], "changements": []})
            continue
        ch = []
        for i in s["items"]:
            if i not in old["items"]:
                ch.append({"cle": "setItem", "type": "added", "avant": None, "apres": n.item_name(i)})
        for i in old["items"]:
            if i not in s["items"]:
                ch.append({"cle": "setItem", "type": "removed", "avant": o.item_name(i), "apres": None})
        for count in range(max(len(s["bonuses"]), len(old["bonuses"]))):
            nb = s["bonuses"][count] if count < len(s["bonuses"]) else []
            ob = old["bonuses"][count] if count < len(old["bonuses"]) else []
            for c in diff_effect_lists(o, n, ob, nb):
                ch.append({**c, "cle": "setBonus", "n": count})
        if ch:
            rows.append({**base, "statut": "modified", "changements": ch, "verdict": overall(ch)})
    for sid, s in o.sets.items():
        if sid not in n.all_sets and not skip(o, sid):
            rows.append({"id": sid, "nom": o.name(s["nameId"]), "niveau": o.set_level(sid),
                         "statut": "removed", "changements": []})
    rows.sort(key=lambda r: (-(r["niveau"] or 0), r["nom"]))
    return rows


def diff_recipes(o, n, job_names):
    def fmt(cd, ingr):
        return ", ".join(f"{q}× {cd.item_name(i)}" for i, q in ingr)

    jobs = {}
    for rid, r in n.recipes.items():
        old = o.recipes.get(rid)
        row = {"id": rid, "nom": n.item_name(rid), "niveau": r["level"]}
        if old is None:
            row.update(statut="added", avant=None, apres=fmt(n, r["ingredients"]))
        elif old["ingredients"] != r["ingredients"] or old["level"] != r["level"]:
            row.update(statut="modified", avant=fmt(o, old["ingredients"]), apres=fmt(n, r["ingredients"]))
            if old["level"] != r["level"]:
                row["niveauAvant"] = old["level"]
        else:
            continue
        jobs.setdefault(r["jobId"], []).append(row)
    for rid, r in o.recipes.items():
        if rid not in n.recipes:
            jobs.setdefault(r["jobId"], []).append({"id": rid, "nom": o.item_name(rid), "niveau": r["level"],
                                                    "statut": "removed", "avant": fmt(o, r["ingredients"]),
                                                    "apres": None})
    out = []
    for jid, rows in jobs.items():
        rows.sort(key=lambda x: (-(x["niveau"] or 0), x["nom"]))
        out.append({"id": jid, "nom": job_names.get(jid) or f"#{jid}", "lignes": rows})
    out.sort(key=lambda j: j["nom"])
    return out


def diff_dungeons(o, n):
    def boss_names(cd, d):
        ids = d.get("bosses", {}).get("Array", [])
        if not ids and d.get("id") in n.dungeons:  # ancienne version sans liste de boss
            ids = n.dungeons[d["id"]].get("bosses", {}).get("Array", [])
        return [cd.name(cd.bosses[b]["nameId"]) for b in ids if b in cd.bosses]

    rows = []
    for did, d in n.dungeons.items():
        old = o.dungeons.get(did)
        base = {"id": did, "nom": n.name(d.get("nameId")), "niveau": d.get("optimalPlayerLevel"),
                "boss": boss_names(n, d)}
        if old is None:
            rows.append({**base, "statut": "added", "changements": []})
            continue
        ch = []
        if old.get("optimalPlayerLevel") != d.get("optimalPlayerLevel"):
            ch.append({"cle": "dungeonLevel", "avant": old.get("optimalPlayerLevel"),
                       "apres": d.get("optimalPlayerLevel")})
        old_listed = old.get("bosses", {}).get("Array")
        for b in d.get("bosses", {}).get("Array", []):
            nb, ob = n.bosses.get(b), o.bosses.get(b)
            if not nb:
                continue
            bname = n.name(nb["nameId"])
            if not ob or (old_listed and b not in old_listed):
                ch.append({"cle": "boss", "type": "added", "avant": None, "apres": bname})
                continue
            for k in BOSS_STAT_KEYS:
                a, c = ob["stats"].get(k), nb["stats"].get(k)
                if a is not None and c is not None and a != c:
                    # pour le joueur, un boss plus faible est un « up »
                    v = None if k == "level" else ("nerf" if c > a else "up")
                    ch.append({"cle": "boss_" + k, "boss": bname, "avant": a, "apres": c, "verdict": v})
            new_spells = [s for s in nb["spells"] if s not in ob["spells"]]
            gone_spells = [s for s in ob["spells"] if s not in nb["spells"]]
            for s in new_spells:
                ch.append({"cle": "bossSpell", "boss": bname, "type": "added", "avant": None,
                           "apres": n.gd.spell_name(s)})
            for s in gone_spells:
                ch.append({"cle": "bossSpell", "boss": bname, "type": "removed", "avant": o.gd.spell_name(s),
                           "apres": None})
        if ch:
            rows.append({**base, "statut": "modified", "changements": ch, "verdict": overall(ch)})
    for did, d in o.dungeons.items():
        if did not in n.dungeons:
            rows.append({"id": did, "nom": o.name(d.get("nameId")), "niveau": d.get("optimalPlayerLevel"),
                         "boss": boss_names(o, d), "statut": "removed", "changements": []})
    rows.sort(key=lambda r: (-(r["niveau"] or 0), r["nom"]))
    return rows


def diff_content(o: ContentData, n: ContentData, job_names):
    return {"objets": diff_items(o, n), "panoplies": diff_sets(o, n),
            "metiers": diff_recipes(o, n, job_names), "donjons": diff_dungeons(o, n)}


def job_names_for(gd):
    """Noms des métiers (jobs.json n'existe que dans les versions récentes)."""
    path = os.path.join(D.DATA_DIR, gd.version, "jobs.json")
    if not os.path.exists(path):
        try:
            import urllib.request
            urllib.request.urlretrieve(D.RELEASE_URL.format(v=gd.version, f="jobs"), path)
        except Exception:
            return {}
    jobs, _ = load_objects(os.path.dirname(path), "jobs")
    return {k: gd.t(v.get("nameId")) for k, v in jobs.items() if v}


def summary(content):
    return {
        "objets": len(content["objets"]), "panoplies": len(content["panoplies"]),
        "metiers": sum(len(j["lignes"]) for j in content["metiers"]), "donjons": len(content["donjons"]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--lang", choices=D.LANGS, default="fr")
    args = ap.parse_args()
    langs = ["fr"] if args.lang == "fr" else ["fr", args.lang]
    og, ng = D.GameData(args.old, langs), D.GameData(args.new, langs)
    og.lang = ng.lang = args.lang
    oc, nc = ContentData(og), ContentData(ng)
    res = diff_content(oc, nc, job_names_for(ng))
    print(json.dumps(summary(res)), file=sys.stderr)
    json.dump(res, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
