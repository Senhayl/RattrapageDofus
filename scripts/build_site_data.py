#!/usr/bin/env python3
"""
Génère les données du site dans src/data/ à partir de scripts/versions.json, en FR, EN et ES.

Pour chaque langue :
    src/data/<langue>/classes.json              liste des classes
    src/data/<langue>/diffs/<départ>.json        sorts : version de départ -> version actuelle
    src/data/<langue>/content/<départ>.json      objets, panoplies, métiers, donjons : départ -> actuelle
    src/data/<langue>/patches/<version>.json     tout ce qu'une mise à jour a changé (version précédente -> celle-ci)
Et src/data/versions.json.

Usage :
    python3 scripts/build_site_data.py
"""
import gc
import json
import os
import re
import resource
import shutil
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diff_spells as D  # noqa: E402
import diff_content as C  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "src", "data")


def slugify(txt):
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")


def write(path, data, indent=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def vkey(v):
    return tuple(int(x) for x in v.split("."))


class Loaded:
    """Une version chargée : sorts (GameData) et contenu (ContentData)."""

    def __init__(self, info):
        self.info = info
        self.gd = D.GameData(info["build"])
        self.cd = C.ContentData(self.gd)

    def set_lang(self, lang):
        self.gd.lang = lang


def class_diffs(old, new, classes):
    out = []
    for c in classes:
        r = D.diff_class(old.gd, new.gd, c["id"])
        r["slug"] = c["slug"]
        out.append(r)
    return out


def main():
    with open(os.path.join(HERE, "versions.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    current_info = cfg["actuelle"]
    starts = sorted(cfg["depart"], key=lambda v: vkey(v["build"]))

    # on repart de zéro pour ne pas garder de fichiers d'une ancienne configuration
    for lang in D.LANGS:
        shutil.rmtree(os.path.join(OUT, lang), ignore_errors=True)
    for old in ("classes.json", "diffs"):  # ancien format, sans langue
        p = os.path.join(OUT, old)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)

    current = Loaded(current_info)
    classes, jobs = {}, {}
    for lang in D.LANGS:
        current.set_lang(lang)
        classes[lang] = [{"id": bid, "nom": current.gd.breed_name(current.gd.breeds[bid]),
                          "slug": slugify(current.gd.breed_name(current.gd.breeds[bid]))}
                         for bid in sorted(current.gd.breeds)]
        jobs[lang] = C.job_names_for(current.gd)

    def emit(old, new, lang):
        old.set_lang(lang)
        new.set_lang(lang)
        return class_diffs(old, new, classes[lang]), C.diff_content(old.cd, new.cd, jobs[lang])

    prev = None
    patches = []
    for info in starts + [current_info]:
        is_current = info is current_info
        loaded = current if is_current else Loaded(info)
        for lang in D.LANGS:
            if prev is not None:  # notes de patch : version précédente -> celle-ci
                cls, content = emit(prev, loaded, lang)
                write(os.path.join(OUT, lang, "patches", f"{info['version']}.json"),
                      {"depuis": prev.info, "jusqua": info, "classes": cls, "contenu": content})
            if not is_current:  # « je n'ai pas joué depuis » : cette version -> actuelle
                cls, content = emit(loaded, current, lang)
                write(os.path.join(OUT, lang, "diffs", f"{info['version']}.json"),
                      {"depuis": info, "jusqua": current_info, "classes": cls})
                write(os.path.join(OUT, lang, "content", f"{info['version']}.json"),
                      {"depuis": info, "jusqua": current_info, **content})
                if lang == "fr":
                    s = C.summary(content)
                    n = sum(len(c["sorts_modifies"]) + len(c["sorts_ajoutes"]) + len(c["sorts_retires"]) for c in cls)
                    print(f"{info['version']} → {current_info['version']} : {n} sorts, {s}", file=sys.stderr)
        if prev is not None:
            patches.append({"version": info["version"], "depuis": prev.info["version"], "date": info["date"]})
        if prev is not None and prev is not current:
            del prev
            gc.collect()
        prev = loaded

    for lang in D.LANGS:
        write(os.path.join(OUT, lang, "classes.json"), classes[lang], indent=2)
    write(os.path.join(OUT, "versions.json"),
          {"actuelle": current_info, "depart": cfg["depart"], "patches": patches[::-1]}, indent=2)
    mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    print(f"Données écrites dans src/data/ (mémoire max : {mb:.0f} Mo)", file=sys.stderr)


if __name__ == "__main__":
    main()
