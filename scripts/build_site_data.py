#!/usr/bin/env python3
"""
Génère les données du site dans src/data/<langue>/ à partir de scripts/versions.json.

Pour chaque version de départ, calcule le diff « cette version → version actuelle »
pour toutes les classes, en français, anglais et espagnol.

Usage :
    python3 scripts/build_site_data.py
"""
import gc
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diff_spells as D  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "src", "data")


def slugify(txt):
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")


def write(path, data, indent=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=indent)


def main():
    with open(os.path.join(HERE, "versions.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    current = cfg["actuelle"]

    new_gd = D.GameData(current["build"])
    breed_ids = sorted(new_gd.breeds)
    classes = {}
    for lang in D.LANGS:
        new_gd.lang = lang
        classes[lang] = []
        for bid in breed_ids:
            b = new_gd.breeds[bid]
            name = new_gd.breed_name(b)
            classes[lang].append({"id": bid, "nom": name, "slug": slugify(name)})

    for start in cfg["depart"]:
        old_gd = D.GameData(start["build"])
        for lang in D.LANGS:
            old_gd.lang = new_gd.lang = lang
            result = []
            for c in classes[lang]:
                r = D.diff_class(old_gd, new_gd, c["id"])
                r["slug"] = c["slug"]
                result.append(r)
            write(os.path.join(OUT, lang, "diffs", f"{start['version']}.json"),
                  {"depuis": start, "jusqua": current, "classes": result})
            if lang == "fr":
                total = sum(len(c["sorts_modifies"]) + len(c["sorts_ajoutes"]) + len(c["sorts_retires"])
                            for c in result)
                print(f"{start['version']} → {current['version']} : {total} sorts concernés", file=sys.stderr)
        del old_gd
        gc.collect()

    for lang in D.LANGS:
        write(os.path.join(OUT, lang, "classes.json"), classes[lang], indent=2)
    write(os.path.join(OUT, "versions.json"), {"actuelle": current, "depart": cfg["depart"]}, indent=2)

    # nettoyage de l'ancien format (un seul dossier, sans langue)
    for old in (os.path.join(OUT, "classes.json"),):
        if os.path.exists(old):
            os.remove(old)
    old_diffs = os.path.join(OUT, "diffs")
    if os.path.isdir(old_diffs):
        for f in os.listdir(old_diffs):
            os.remove(os.path.join(old_diffs, f))
        os.rmdir(old_diffs)
    print("Données écrites dans src/data/", file=sys.stderr)


if __name__ == "__main__":
    main()
