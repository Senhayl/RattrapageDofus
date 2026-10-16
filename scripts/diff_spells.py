#!/usr/bin/env python3
"""
Compare les sorts de classe entre deux versions de Dofus 3, en français, anglais ou espagnol.

Source : releases GitHub de dofusdude/dofus3-main (données extraites du client).

Usage :
    python3 scripts/diff_spells.py 3.3.20.19 3.7.10.10
    python3 scripts/diff_spells.py 3.3.20.19 3.7.10.10 --classe Iop --lang en
Sorties (dossier out/) :
    changes_<old>_<new>[_<classe>]_<lang>.json   données structurées
    report_<old>_<new>[_<classe>]_<lang>.md      rapport lisible

Format d'un changement (voir aussi src/lib/data.ts) :
    {"cle": "apCost" | "range" | ... | "name" | "description" | "castFlags" | "effect",
     "type": "modified" | "added" | "removed",       # effets uniquement
     "critique": true,                               # effet de coup critique
     "avant": ..., "apres": ...,                     # nombre brut ou texte dans la langue
     "verdict": "up" | "nerf" | null,                # quand le sens ne fait pas de doute
     "element": "terre" | "feu" | "eau" | "air" | "neutre" | null}
"""
import argparse
import json
import os
import re
import sys
import urllib.request

RELEASE_URL = "https://github.com/dofusdude/dofus3-main/releases/download/{v}/{f}.json"
LANGS = ["fr", "en", "es"]
TABLES = ["breeds", "spells", "spell_levels", "spell_variants", "effects", "spell_states"]
DATA_DIR = os.environ.get("DOFUS_DATA_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"))

# Caractéristiques d'un grade de sort. Valeur : True si une hausse est bonne pour le joueur,
# False si une baisse est bonne, None si neutre.
LEVEL_FIELDS = {
    "apCost": False,
    "minRange": False,
    "range": True,
    "criticalHitProbability": True,
    "maxCastPerTurn": True,
    "maxCastPerTarget": True,
    "minCastInterval": False,
    "initialCooldown": False,
    "globalCooldown": False,
    "maxStack": True,
    "minPlayerLevel": None,
}
UNLIMITED_ZERO = {"maxCastPerTurn", "maxCastPerTarget", "maxStack"}  # 0 ou -1 = illimité
NONE_ZERO = {"globalCooldown", "initialCooldown", "minCastInterval"}  # 0 ou -1 = aucune

ELEMENTS = {0: "neutre", 1: "terre", 2: "feu", 3: "eau", 4: "air"}

# Effets « modificateur de sort » (#1 : +#3 ...) : sens d'une hausse de la valeur
SPELL_MODIFIER_HIGHER_IS_BETTER = {
    281: True, 283: True, 284: True, 285: True, 286: True, 287: True, 290: True, 291: True,
    293: True, 295: True, 280: False, 294: False, 296: False,
}

# Ce que fait un état, quand le jeu ne fournit pas de description (avant la 3.7)
STATE_FLAGS = {
    "fr": {"preventsFight": "empêche d'utiliser son arme", "preventsSpellCast": "empêche de lancer des sorts",
           "cantDealDamage": "empêche d'infliger des dommages", "invulnerable": "rend invulnérable",
           "invulnerableMelee": "rend invulnérable au corps à corps", "invulnerableRange": "rend invulnérable à distance",
           "incurable": "empêche d'être soigné", "cantBeMoved": "empêche d'être déplacé",
           "cantBePushed": "empêche d'être poussé", "cantSwitchPosition": "empêche d'échanger de place",
           "cantTackle": "empêche de tacler", "cantBeTackled": "empêche d'être taclé"},
    "en": {"preventsFight": "prevents using a weapon", "preventsSpellCast": "prevents casting spells",
           "cantDealDamage": "prevents dealing damage", "invulnerable": "makes invulnerable",
           "invulnerableMelee": "makes invulnerable in melee", "invulnerableRange": "makes invulnerable at range",
           "incurable": "prevents being healed", "cantBeMoved": "prevents being moved",
           "cantBePushed": "prevents being pushed", "cantSwitchPosition": "prevents switching places",
           "cantTackle": "prevents tackling", "cantBeTackled": "prevents being tackled"},
    "es": {"preventsFight": "impide usar el arma", "preventsSpellCast": "impide lanzar hechizos",
           "cantDealDamage": "impide infligir daños", "invulnerable": "vuelve invulnerable",
           "invulnerableMelee": "vuelve invulnerable cuerpo a cuerpo", "invulnerableRange": "vuelve invulnerable a distancia",
           "incurable": "impide ser curado", "cantBeMoved": "impide ser desplazado",
           "cantBePushed": "impide ser empujado", "cantSwitchPosition": "impide intercambiar posiciones",
           "cantTackle": "impide placar", "cantBeTackled": "impide ser placado"},
}
STATE_NOTE = {
    "fr": {"same": "Nouveau nom, même effet : {d}", "one": "{n} : {d}"},
    "en": {"same": "New name, same effect: {d}", "one": "{n}: {d}"},
    "es": {"same": "Nuevo nombre, mismo efecto: {d}", "one": "{n}: {d}"},
}

L10N = {
    "fr": {
        "size": "{shape} de taille {n}", "zone": "[zone : {z}]", "turn": "tour", "turns": "tours",
        "infinite": "infini", "colon": " : ", "state": "état", "spell": "sort", "effect": "Effet",
        "shapes": {"P": "case", "C": "cercle", "X": "croix", "L": "ligne", "T": "ligne perpendiculaire",
                   "D": "damier", "O": "anneau", "Q": "croix vide", "+": "étoile", "V": "cône",
                   "U": "demi-cercle", "A": "toute la carte", "a": "toute la carte", "G": "carré",
                   "W": "carré vide", "R": "rectangle", "#": "croix diagonale", "/": "diagonale",
                   "-": "ligne", "F": "fourche"},
    },
    "en": {
        "size": "{shape} of size {n}", "zone": "[area: {z}]", "turn": "turn", "turns": "turns",
        "infinite": "infinite", "colon": ": ", "state": "state", "spell": "spell", "effect": "Effect",
        "shapes": {"P": "cell", "C": "circle", "X": "cross", "L": "line", "T": "perpendicular line",
                   "D": "checkerboard", "O": "ring", "Q": "hollow cross", "+": "star", "V": "cone",
                   "U": "half-circle", "A": "whole map", "a": "whole map", "G": "square",
                   "W": "hollow square", "R": "rectangle", "#": "diagonal cross", "/": "diagonal",
                   "-": "line", "F": "fork"},
    },
    "es": {
        "size": "{shape} de tamaño {n}", "zone": "[zona: {z}]", "turn": "turno", "turns": "turnos",
        "infinite": "infinito", "colon": ": ", "state": "estado", "spell": "hechizo", "effect": "Efecto",
        "shapes": {"P": "casilla", "C": "círculo", "X": "cruz", "L": "línea", "T": "línea perpendicular",
                   "D": "damero", "O": "anillo", "Q": "cruz vacía", "+": "estrella", "V": "cono",
                   "U": "semicírculo", "A": "todo el mapa", "a": "todo el mapa", "G": "cuadrado",
                   "W": "cuadrado vacío", "R": "rectángulo", "#": "cruz diagonal", "/": "diagonal",
                   "-": "línea", "F": "horquilla"},
    },
}


def clean_markup(txt):
    """Retire le balisage du client : {{spell,123,1::Texte}} -> Texte, <color=..>x</color> -> x."""
    txt = re.sub(r"\{\{[a-z]+,[^:}]*::([^}]*)\}\}", r"\1", txt)
    txt = re.sub(r"</?(color|b|i|u|size)[^>]*>", "", txt)
    txt = re.sub(r"<sprite[^>]*>", "", txt)
    return txt


# ---------------------------------------------------------------- chargement

def ensure_version(version, langs=LANGS):
    vdir = os.path.join(DATA_DIR, version)
    os.makedirs(vdir, exist_ok=True)
    for f in TABLES + list(langs):
        path = os.path.join(vdir, f + ".json")
        if not os.path.exists(path):
            print(f"  téléchargement {version}/{f}.json ...", file=sys.stderr)
            tmp = path + ".part"
            urllib.request.urlretrieve(RELEASE_URL.format(v=version, f=f), tmp)
            os.replace(tmp, path)
    return vdir


def load_table(vdir, name):
    with open(os.path.join(vdir, name + ".json"), encoding="utf-8") as fh:
        raw = json.load(fh)
    out = {}
    for ref in raw["references"]["RefIds"]:
        data = ref.get("data")
        if isinstance(data, dict) and "id" in data:
            out[data["id"]] = data
    return out


class GameData:
    """Données d'une version. `lang` choisit la langue des textes (modifiable à la volée)."""

    def __init__(self, version, langs=LANGS):
        self.version = version
        vdir = ensure_version(version, langs)
        print(f"Chargement {version} ...", file=sys.stderr)
        self.breeds = load_table(vdir, "breeds")
        self.spells = load_table(vdir, "spells")
        self.levels = load_table(vdir, "spell_levels")
        # Le format a changé entre versions : "effectId" (ancien) est devenu "actionId".
        for lv in self.levels.values():
            for key in ("effects", "criticalEffect"):
                for e in lv.get(key, {}).get("Array", []):
                    if "actionId" not in e:
                        e["actionId"] = e.get("effectId")
        self.variants = load_table(vdir, "spell_variants")
        self.effects = load_table(vdir, "effects")
        self.states = load_table(vdir, "spell_states")
        self.texts = {}
        for lang in langs:
            with open(os.path.join(vdir, lang + ".json"), encoding="utf-8") as fh:
                self.texts[lang] = json.load(fh)["entries"]
        self.lang = langs[0]

    def t(self, text_id):
        if text_id in (None, 0, "0"):
            return ""
        return clean_markup(self.texts[self.lang].get(str(text_id), ""))

    def t_fr(self, text_id):
        """Texte français, utilisé pour les décisions qui ne doivent pas dépendre de la langue."""
        lang, self.lang = self.lang, "fr" if "fr" in self.texts else self.lang
        try:
            return self.t(text_id)
        finally:
            self.lang = lang

    def breed_name(self, breed):
        return self.t(breed.get("shortNameId")) or f"#{breed['id']}"

    def breed_spell_ids(self, breed):
        ids = list(breed.get("breedSpellsId", {}).get("Array", []))
        for var in self.variants.values():  # les variantes complètent la liste
            if var.get("breedId") == breed["id"]:
                for sid in var.get("spellIds", {}).get("Array", []):
                    if sid not in ids:
                        ids.append(sid)
        return ids

    def spell_name(self, sid):
        sp = self.spells.get(sid)
        return self.t(sp["nameId"]) if sp else f"#{sid}"

    def max_grade(self, sid):
        sp = self.spells.get(sid)
        if not sp:
            return None
        lvls = [self.levels[l] for l in sp.get("spellLevels", {}).get("Array", []) if l in self.levels]
        return max(lvls, key=lambda l: l.get("grade", 0)) if lvls else None


# ---------------------------------------------------------------- rendu des effets

def zone_text(gd, z):
    if not z:
        return ""
    loc = L10N[gd.lang]
    shape = chr(z["shape"]) if z.get("shape") else "P"
    size = z.get("param1", 0)
    if shape == "P" or (shape in "CX" and size == 0):
        return ""
    label = loc["shapes"].get(shape, shape)
    return loc["size"].format(shape=label, n=size)


def effect_text(gd, e):
    loc = L10N[gd.lang]
    meta = gd.effects.get(e["actionId"])
    pattern = gd.t(meta["descriptionId"]) if meta else f"{loc['effect']} #{e['actionId']}"
    lo, hi, val = e.get("diceNum", 0), e.get("diceSide", 0), e.get("value", 0)

    # {{~1~2 à }} : affiché seulement s'il y a une fourchette
    txt = re.sub(r"\{\{~1~2([^}]*)\}\}", lambda m: m.group(1) if (hi and hi != lo) else "", pattern)
    txt = txt.replace("{{~ps}}", "s" if max(lo, hi) > 1 else "")
    txt = re.sub(r"\{\{[^}]*\}\}", "", txt)
    txt = txt.replace("#1", str(lo)).replace("#2", str(hi) if (hi and hi != lo) else "")
    if "#3" in txt:
        # #3 est en général un nombre ; c'est un état ou un sort seulement si le libellé le dit
        name, low = "", pattern.lower()
        if loc["state"] in low and val in gd.states:
            name = gd.t(gd.states[val].get("nameId"))
        elif loc["spell"] in low and val in gd.spells:
            name = gd.spell_name(val)
        txt = txt.replace("#3", name or str(val))
    txt = re.sub(r"\s+", " ", txt).strip()
    # certains effets commencent par l'identifiant d'un sort : on le remplace par son nom
    m = re.match(r"^(\d+) ?: ", txt)
    if m and int(m.group(1)) in gd.spells:
        txt = gd.spell_name(int(m.group(1))) + loc["colon"] + txt[m.end():]
    d = e.get("duration")
    if d:
        txt += f" ({loc['infinite']})" if d < 0 else f" ({d} {loc['turns'] if d > 1 else loc['turn']})"
    z = zone_text(gd, e.get("zoneDescr"))
    if z:
        txt += " " + loc["zone"].format(z=z)
    return txt


def state_of(gd, e):
    """Identifiant de l'état posé par un effet (None si l'effet ne pose pas d'état)."""
    if e is None:
        return None
    meta = gd.effects.get(e["actionId"])
    pattern = gd.t_fr(meta["descriptionId"]).lower() if meta else ""
    val = e.get("value")
    return val if ("#3" in pattern and "état" in pattern and val in gd.states) else None


def state_meaning(gds, sid):
    """Ce que fait l'état : sa description officielle (3.7+), sinon ses propriétés de jeu."""
    for gd in gds:  # la version la plus récente d'abord
        st = gd.states.get(sid)
        if st and gd.t(st.get("descriptionId")).strip():
            return gd.t(st.get("descriptionId")).strip().rstrip(".")
    for gd in gds:
        st = gd.states.get(sid)
        if st:
            flags = [txt for k, txt in STATE_FLAGS[gd.lang].items() if st.get(k)]
            if flags:
                return ", ".join(flags)
    return None


def state_note(old_gd, new_gd, oe, ne):
    """Explique un état ajouté, retiré ou remplacé (« Affaibli » -> « Précipité » : même effet ?)."""
    so, sn = state_of(old_gd, oe), state_of(new_gd, ne)
    if so is None and sn is None:
        return None
    gds = [new_gd, old_gd]
    lang = new_gd.lang
    tpl = STATE_NOTE[lang]
    mo = state_meaning(gds, so) if so is not None else None
    mn = state_meaning(gds, sn) if sn is not None else None
    if so is not None and sn is not None and so != sn:
        if mo and mn and mo == mn:
            return tpl["same"].format(d=mn[:1].lower() + mn[1:])
        parts = []
        if mo:
            parts.append(tpl["one"].format(n=old_gd.t(old_gd.states[so].get("nameId")), d=mo))
        if mn:
            parts.append(tpl["one"].format(n=new_gd.t(new_gd.states[sn].get("nameId")), d=mn))
        return " · ".join(parts) or None
    sid, m, gd = (sn, mn, new_gd) if sn is not None else (so, mo, old_gd)
    return tpl["one"].format(n=gd.t(gd.states[sid].get("nameId")), d=m) if m else None


def effect_signature(e):
    z = e.get("zoneDescr", {})
    return (e.get("actionId"), e.get("diceNum"), e.get("diceSide"), e.get("value"), e.get("duration"),
            z.get("shape"), z.get("param1"), e.get("targetMask"), e.get("triggers"))


def effect_element(gd, e):
    meta = gd.effects.get(e["actionId"])
    el = meta.get("elementId", -1) if meta else -1
    if meta and meta.get("category") == 2 and el in ELEMENTS:
        return ELEMENTS[el]
    return None


def effect_verdict(gd, oe, ne):
    """up / nerf quand seule la valeur d'un même effet a changé et que le sens est clair."""
    if oe["actionId"] != ne["actionId"]:
        return None
    zo, zn = oe.get("zoneDescr", {}), ne.get("zoneDescr", {})
    if (oe.get("duration"), zo.get("shape"), zo.get("param1"), oe.get("targetMask")) != \
       (ne.get("duration"), zn.get("shape"), zn.get("param1"), ne.get("targetMask")):
        return None
    aid = ne["actionId"]
    if aid in SPELL_MODIFIER_HIGHER_IS_BETTER:
        a, b = abs(oe.get("value", 0)), abs(ne.get("value", 0))
        if a == b:
            return None
        return "up" if (b > a) == SPELL_MODIFIER_HIGHER_IS_BETTER[aid] else "nerf"
    meta = gd.effects.get(aid)
    if not meta or meta.get("category") != 2:  # dommages, vols de vie, soins
        return None

    def avg(e):
        lo, hi = e.get("diceNum", 0), e.get("diceSide", 0)
        return abs((lo + (hi or lo)) / 2)
    a, b = avg(oe), avg(ne)
    if a == b:
        return None
    return "up" if b > a else "nerf"


def is_visible(txt):
    """Masque les effets techniques sans libellé (qui ne s'affichent que comme un numéro)."""
    if txt is None:
        return True
    core = re.sub(r"\[[^\]]*\]", "", txt)
    return not re.fullmatch(r"[\d\s()a-z:#]*", core)


def diff_effects(old_gd, new_gd, old_list, new_list):
    pairs = []  # (oe, ne) ; None pour ajout ou suppression
    old_by_uid = {e["effectUid"]: e for e in old_list}
    matched = set()
    rest_new = []
    for ne in new_list:  # 1) même identifiant d'effet
        oe = old_by_uid.get(ne["effectUid"])
        if oe is not None:
            matched.add(ne["effectUid"])
            pairs.append((oe, ne))
        else:
            rest_new.append(ne)
    rest_old = [e for e in old_list if e["effectUid"] not in matched]
    for ne in rest_new:  # 2) même type d'effet parmi les restants
        oe = next((o for o in rest_old if o["actionId"] == ne["actionId"]), None)
        if oe is not None:
            rest_old.remove(oe)
        pairs.append((oe, ne))
    pairs += [(oe, None) for oe in rest_old]

    out = []
    for oe, ne in pairs:
        if oe is not None and ne is not None and effect_signature(oe) == effect_signature(ne):
            continue
        before = effect_text(old_gd, oe) if oe is not None else None
        after = effect_text(new_gd, ne) if ne is not None else None
        if before == after or not (is_visible(before) and is_visible(after)):
            continue
        note = state_note(old_gd, new_gd, oe, ne)
        out.append({
            **({"note": note} if note else {}),
            "cle": "effect",
            "type": "modified" if (oe is not None and ne is not None) else ("added" if oe is None else "removed"),
            "avant": before, "apres": after,
            "verdict": effect_verdict(new_gd, oe, ne) if (oe is not None and ne is not None) else None,
            "element": effect_element(new_gd, ne if ne is not None else oe),
        })
    return out


def level_verdict(field, a, b):
    better_up = LEVEL_FIELDS.get(field)
    if better_up is None:
        return None

    def num(v):
        if field in UNLIMITED_ZERO and v in (0, -1):
            return float("inf")
        if field in NONE_ZERO and v in (0, -1):
            return 0
        return v
    x, y = num(a), num(b)
    if x == y:
        return None
    return "up" if (y > x) == better_up else "nerf"


# ---------------------------------------------------------------- diff

def diff_spell(old_gd, new_gd, sid, old_sid=None):
    """Compare un sort. old_sid sert quand Ankama a recréé le sort sous un nouvel identifiant."""
    old_sid = old_sid or sid
    o_sp, n_sp = old_gd.spells.get(old_sid), new_gd.spells.get(sid)
    o_lv, n_lv = old_gd.max_grade(old_sid), new_gd.max_grade(sid)
    out = {"spellId": sid, "nom": new_gd.spell_name(sid) if n_sp else old_gd.spell_name(old_sid), "changements": []}
    if old_sid != sid:
        out["ancienSpellId"] = old_sid
    ch = out["changements"]

    if o_sp and n_sp:
        if old_gd.spell_name(old_sid) != new_gd.spell_name(sid):
            ch.append({"cle": "name", "avant": old_gd.spell_name(old_sid), "apres": new_gd.spell_name(sid)})
        od, nd = old_gd.t(o_sp.get("descriptionId")), new_gd.t(n_sp.get("descriptionId"))
        if " ".join(od.split()) != " ".join(nd.split()):
            ch.append({"cle": "description", "avant": od, "apres": nd})
    if not (o_lv and n_lv):
        return out

    for field in LEVEL_FIELDS:
        a, b = o_lv.get(field), n_lv.get(field)
        if field in UNLIMITED_ZERO | NONE_ZERO and a in (0, -1) and b in (0, -1):
            continue
        if a != b:
            ch.append({"cle": field, "avant": a, "apres": b, "verdict": level_verdict(field, a, b)})
    if o_lv.get("m_flags") != n_lv.get("m_flags"):
        ch.append({"cle": "castFlags", "avant": None, "apres": None})

    normal = diff_effects(old_gd, new_gd, o_lv.get("effects", {}).get("Array", []),
                          n_lv.get("effects", {}).get("Array", []))
    crit = diff_effects(old_gd, new_gd, o_lv.get("criticalEffect", {}).get("Array", []),
                        n_lv.get("criticalEffect", {}).get("Array", []))
    # Les critiques suivent presque toujours les effets normaux : on ne garde que ceux qui
    # apportent une information (texte différent d'un changement normal).
    seen = {(c["avant"], c["apres"]) for c in normal}
    ch += normal
    ch += [dict(c, critique=True) for c in crit if (c["avant"], c["apres"]) not in seen]
    return out


def diff_class(old_gd, new_gd, breed_id):
    o_b, n_b = old_gd.breeds.get(breed_id), new_gd.breeds.get(breed_id)
    breed = n_b or o_b
    gd = new_gd if n_b else old_gd
    o_ids = old_gd.breed_spell_ids(o_b) if o_b else []
    n_ids = new_gd.breed_spell_ids(n_b) if n_b else []
    res = {"classeId": breed_id, "classe": gd.breed_name(breed),
           "sorts_ajoutes": [], "sorts_retires": [], "sorts_modifies": []}

    # Sorts recréés sous un nouvel identifiant (refonte) : appariés par nom français,
    # pour que le résultat soit identique dans toutes les langues.
    def fr_name(g, sid):
        sp = g.spells.get(sid)
        return g.t_fr(sp["nameId"]).strip().lower() if sp else ""
    added = [s for s in n_ids if s not in o_ids]
    removed = [s for s in o_ids if s not in n_ids]
    removed_by_name = {fr_name(old_gd, s): s for s in removed}
    renamed = {}
    for s in added:
        old = removed_by_name.pop(fr_name(new_gd, s), None)
        if old is not None:
            renamed[s] = old

    for sid in n_ids:
        if sid in o_ids or sid in renamed:
            d = diff_spell(old_gd, new_gd, sid, old_sid=renamed.get(sid))
            if d["changements"]:
                res["sorts_modifies"].append(d)
        else:
            sp = new_gd.spells.get(sid)
            res["sorts_ajoutes"].append({"spellId": sid, "nom": new_gd.spell_name(sid),
                                          "description": new_gd.t(sp.get("descriptionId")) if sp else ""})
    for sid in removed_by_name.values():
        res["sorts_retires"].append({"spellId": sid, "nom": old_gd.spell_name(sid)})
    return res


# ---------------------------------------------------------------- rapport

REPORT = {
    "fr": {"title": "Changements des sorts de classe", "summary": "{m} sorts modifiés, {a} ajoutés, {r} retirés.",
           "new": "Nouveau sort", "removed": "Sort retiré", "crit": "critique", "castFlags": "Conditions de lancer modifiées",
           "added": "ajouté", "deleted": "retiré",
           "fields": {"name": "Nom", "description": "Description", "apCost": "Coût en PA", "minRange": "Portée min",
                      "range": "Portée max", "criticalHitProbability": "Critique (%)", "maxCastPerTurn": "Lancers par tour",
                      "maxCastPerTarget": "Lancers par cible", "minCastInterval": "Relance", "initialCooldown": "Relance initiale",
                      "globalCooldown": "Relance globale", "maxStack": "Cumul max", "minPlayerLevel": "Niveau requis",
                      "effect": "Effet"}},
    "en": {"title": "Class spell changes", "summary": "{m} spells changed, {a} added, {r} removed.",
           "new": "New spell", "removed": "Removed spell", "crit": "critical", "castFlags": "Casting conditions changed",
           "added": "added", "deleted": "removed",
           "fields": {"name": "Name", "description": "Description", "apCost": "AP cost", "minRange": "Min range",
                      "range": "Max range", "criticalHitProbability": "Critical (%)", "maxCastPerTurn": "Casts per turn",
                      "maxCastPerTarget": "Casts per target", "minCastInterval": "Cooldown", "initialCooldown": "Initial cooldown",
                      "globalCooldown": "Global cooldown", "maxStack": "Max stacks", "minPlayerLevel": "Required level",
                      "effect": "Effect"}},
    "es": {"title": "Cambios de hechizos de clase", "summary": "{m} hechizos modificados, {a} añadidos, {r} eliminados.",
           "new": "Hechizo nuevo", "removed": "Hechizo eliminado", "crit": "crítico", "castFlags": "Condiciones de lanzamiento modificadas",
           "added": "añadido", "deleted": "eliminado",
           "fields": {"name": "Nombre", "description": "Descripción", "apCost": "Coste en PA", "minRange": "Alcance mín.",
                      "range": "Alcance máx.", "criticalHitProbability": "Crítico (%)", "maxCastPerTurn": "Lanzamientos por turno",
                      "maxCastPerTarget": "Lanzamientos por objetivo", "minCastInterval": "Reutilización",
                      "initialCooldown": "Reutilización inicial", "globalCooldown": "Reutilización global",
                      "maxStack": "Acumulación máx.", "minPlayerLevel": "Nivel requerido", "effect": "Efecto"}},
}


def render_markdown(result, old_v, new_v, lang):
    R = REPORT[lang]
    one = lambda s: " ".join(str(s).split())
    lines = [f"# {R['title']} : {old_v} → {new_v}", ""]
    for c in result:
        if not (c["sorts_modifies"] or c["sorts_ajoutes"] or c["sorts_retires"]):
            continue
        lines += [f"## {c['classe']}", "", R["summary"].format(
            m=len(c["sorts_modifies"]), a=len(c["sorts_ajoutes"]), r=len(c["sorts_retires"])), ""]
        lines += [f"- **{R['new']} : {s['nom']}** — {one(s['description'])}" for s in c["sorts_ajoutes"]]
        lines += [f"- **{R['removed']} : {s['nom']}**" for s in c["sorts_retires"]]
        for s in c["sorts_modifies"]:
            lines += ["", f"### {s['nom']}"]
            for x in s["changements"]:
                if x["cle"] == "castFlags":
                    lines.append(f"- {R['castFlags']}")
                    continue
                label = R["fields"].get(x["cle"], x["cle"])
                if x.get("critique"):
                    label += f" ({R['crit']})"
                if x.get("type") == "added":
                    label += f" {R['added']}"
                elif x.get("type") == "removed":
                    label += f" {R['deleted']}"
                tag = f" `{x['verdict']}`" if x.get("verdict") else ""
                if x["avant"] is None:
                    lines.append(f"- {label} : {one(x['apres'])}{tag}")
                elif x["apres"] is None:
                    lines.append(f"- {label} : ~~{one(x['avant'])}~~{tag}")
                else:
                    lines.append(f"- {label} : {one(x['avant'])} → **{one(x['apres'])}**{tag}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--classe", help="Filtrer sur une classe, nom dans la langue choisie (ex. Iop)")
    ap.add_argument("--lang", choices=LANGS, default="fr")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out"))
    args = ap.parse_args()

    langs = [args.lang] if args.lang == "fr" else ["fr", args.lang]
    old_gd, new_gd = GameData(args.old, langs), GameData(args.new, langs)
    old_gd.lang = new_gd.lang = args.lang
    result = [diff_class(old_gd, new_gd, b) for b in sorted(set(old_gd.breeds) | set(new_gd.breeds))]
    if args.classe:
        result = [c for c in result if c["classe"].lower() == args.classe.lower()]
        if not result:
            sys.exit(f"Classe inconnue : {args.classe}")

    os.makedirs(args.out, exist_ok=True)
    suffix = f"{args.old}_{args.new}" + (f"_{args.classe.lower()}" if args.classe else "") + f"_{args.lang}"
    with open(os.path.join(args.out, f"changes_{suffix}.json"), "w", encoding="utf-8") as fh:
        json.dump({"ancienne_version": args.old, "nouvelle_version": args.new, "langue": args.lang,
                   "classes": result}, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(args.out, f"report_{suffix}.md"), "w", encoding="utf-8") as fh:
        fh.write(render_markdown(result, args.old, args.new, args.lang))
    for c in result:
        print(f"{c['classe']:<12} {len(c['sorts_modifies']):>3} / {len(c['sorts_ajoutes']):>2} / {len(c['sorts_retires']):>2}")


if __name__ == "__main__":
    main()
