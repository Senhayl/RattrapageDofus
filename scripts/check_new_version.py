#!/usr/bin/env python3
"""
Regarde si une nouvelle version de Dofus 3 est publiée sur dofusdude/dofus3-main
et met à jour scripts/versions.json en conséquence.

- Nouveau build de la même mise à jour (ex. 3.7.10.10 -> 3.7.11.12) : on remplace le build actuel.
- Nouvelle mise à jour (ex. 3.7 -> 3.8) : l'actuelle devient une version de départ
  et la nouvelle devient l'actuelle, datée du mois en cours.

Usage :
    python3 scripts/check_new_version.py            # modifie versions.json si besoin
    python3 scripts/check_new_version.py --dry-run  # affiche seulement
Dans GitHub Actions, écrit `changed`, `build` et `kind` dans $GITHUB_OUTPUT.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERSIONS = os.path.join(HERE, "versions.json")
REPO = "https://github.com/dofusdude/dofus3-main"

NAMES = {"default": "Mise à jour {v}"}


def remote_builds():
    out = subprocess.run(["git", "ls-remote", "--tags", REPO], check=True, capture_output=True, text=True).stdout
    tags = {line.split("refs/tags/")[1].removesuffix("^{}") for line in out.splitlines() if "refs/tags/" in line}
    builds = [t for t in tags if re.fullmatch(r"\d+(\.\d+){3}", t)]
    return sorted(builds, key=lambda t: tuple(int(x) for x in t.split(".")))


def major(build):
    return ".".join(build.split(".")[:2])


def set_output(**kw):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            for k, v in kw.items():
                fh.write(f"{k}={v}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--latest", help="forcer le build le plus récent (tests)")
    args = ap.parse_args()

    with open(VERSIONS, encoding="utf-8") as fh:
        cfg = json.load(fh)
    current = cfg["actuelle"]
    latest = args.latest or remote_builds()[-1]
    key = lambda b: tuple(int(x) for x in b.split("."))

    if key(latest) <= key(current["build"]):
        print(f"Rien de nouveau (actuelle : {current['build']}, dernière publiée : {latest}).")
        set_output(changed="false", build=current["build"], kind="none")
        return

    if major(latest) == current["version"]:
        kind = "build"
        print(f"Nouveau build de la {current['version']} : {current['build']} -> {latest}")
        current["build"] = latest
    else:
        kind = "major"
        print(f"Nouvelle mise à jour : {current['version']} -> {major(latest)} ({latest})")
        cfg["depart"].insert(0, dict(current))
        cfg["actuelle"] = {
            "version": major(latest),
            "build": latest,
            "nom": NAMES["default"].format(v=major(latest)),
            "date": datetime.date.today().strftime("%Y-%m"),
        }

    if not args.dry_run:
        with open(VERSIONS, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    set_output(changed="true", build=latest, kind=kind)


if __name__ == "__main__":
    sys.exit(main())
