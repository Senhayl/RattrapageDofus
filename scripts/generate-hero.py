#!/usr/bin/env python3
"""
Génère l'illustration du hero (public/hero.webp) : ciel nocturne du Krosmoz, nébuleuse,
voie lactée, étoiles et îles flottantes en silhouette. Image 100 % originale (aucun droit tiers).

    pip install numpy scipy pillow
    python3 scripts/generate-hero.py            # graine par défaut
    python3 scripts/generate-hero.py --seed 7   # autre tirage

Le centre de l'image reste plus calme pour la lisibilité du texte posé par-dessus.
"""
import argparse
import os

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

W, H = 2880, 1800


def fbm(rng, octaves=7, base=4, persistence=0.55):
    """Bruit fractal (somme d'octaves de bruit lissé), normalisé entre 0 et 1."""
    out = np.zeros((H, W), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        n = base * 2**o
        g = rng.random((max(2, int(n * H / W)) + 1, n + 1)).astype(np.float32)
        layer = zoom(g, (H / g.shape[0], W / g.shape[1]), order=3)[:H, :W]
        out += amp * layer
        total += amp
        amp *= persistence
    out /= total
    return (out - out.min()) / (out.max() - out.min())


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=12)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "public", "hero.webp"))
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u, v = xx / W, yy / H

    # --- fond : nuit profonde, un peu plus claire vers l'horizon
    top, mid, low = hexc("#05060d"), hexc("#0c1028"), hexc("#141a3a")
    t = v[..., None]
    sky = np.where(t < 0.7, top + (mid - top) * (t / 0.7), mid + (low - mid) * ((t - 0.7) / 0.3))

    # --- voie lactée : bande diagonale, modulée par du bruit
    ang = np.deg2rad(-24)
    d = (u - 0.5) * np.sin(ang) + (v - 0.48) * np.cos(ang)  # distance signée à l'axe
    along = (u - 0.5) * np.cos(ang) - (v - 0.48) * np.sin(ang)
    n1, n2, n3 = fbm(rng, 8, 3), fbm(rng, 8, 5), fbm(rng, 6, 2)
    width = 0.16 + 0.07 * (n3 - 0.5)
    band = np.exp(-((d + 0.05 * (n1 - 0.5)) / width) ** 2)
    band *= 0.55 + 0.45 * np.cos(along * 2.2)  # plus dense au centre de la diagonale

    # nébuleuse : couleurs sourdes accordées au site (sarcelle, violet, rose cuivré)
    teal, violet, rose, gold = hexc("#2f7f8f"), hexc("#5b3f8f"), hexc("#a8586e"), hexc("#e9d9b0")
    neb = np.clip((n2 - 0.38) * 1.9, 0, 1) * band
    hue = n1[..., None]
    col = teal * (1 - hue) + violet * hue
    col = col * (1 - np.clip(n3 - 0.55, 0, 1)[..., None] * 2.5) + rose * np.clip(n3 - 0.55, 0, 1)[..., None] * 2.5
    glow = gaussian_filter(neb, 30)[..., None]
    img = sky + col * (neb[..., None] ** 1.3) * 0.75 + col * glow * 0.35

    # bandes de poussière sombres le long de la voie lactée
    dust = np.clip((fbm(rng, 8, 6) - 0.52) * 3.5, 0, 1) * np.exp(-(d / 0.07) ** 2)
    img *= (1 - 0.65 * dust)[..., None]

    # cœur lumineux doré, discret
    core = np.exp(-(((u - 0.68) / 0.12) ** 2 + ((v - 0.34) / 0.1) ** 2)) * band
    img += gold * core[..., None] * 0.22

    # --- étoiles
    stars = np.zeros((H, W), np.float32)
    n_stars = 26000
    sx = rng.integers(0, W, n_stars)
    sy = rng.integers(0, int(H * 0.86), n_stars)
    # plus d'étoiles dans la voie lactée
    keep = rng.random(n_stars) < 0.35 + 0.65 * band[sy, sx]
    sx, sy = sx[keep], sy[keep]
    mag = rng.pareto(2.6, sx.size).astype(np.float32)
    stars[sy, sx] = np.clip(0.18 + mag * 0.35, 0, 3)
    st = gaussian_filter(stars, 0.7) * 2.2 + gaussian_filter(stars, 2.2) * 0.9
    tint = np.stack([0.9 + 0.1 * n1, 0.93 + 0.0 * n1, 1.0 - 0.08 * n1], -1)
    img += st[..., None] * tint

    # quelques étoiles brillantes avec halo et aigrettes
    for k in range(9):
        x, y = rng.integers(80, W - 80), rng.integers(60, int(H * 0.7))
        s = np.zeros((H, W), np.float32)
        s[y, x] = 1
        power = rng.uniform(0.35, 1.0)
        halo = (gaussian_filter(s, 9) * 900 * 0.6 + gaussian_filter(s, 1.6) * 40) * power
        spike = np.zeros((H, W), np.float32)
        spike[y, max(0, x - 40):x + 40] = 1
        spike[max(0, y - 40):y + 40, x] = 1
        spike = gaussian_filter(spike, 0.8) * np.exp(-(((xx - x) ** 2 + (yy - y) ** 2) / 900))
        img += (halo + spike * 0.35 * power)[..., None] * np.array([0.92, 0.95, 1.0], np.float32)

    # --- zone centrale plus calme pour le texte
    calm = np.exp(-(((u - 0.5) / 0.32) ** 2 + ((v - 0.42) / 0.26) ** 2))
    img *= (1 - 0.38 * calm)[..., None]

    # --- silhouettes : collines lointaines, puis îles flottantes
    sil = hexc("#05060b")
    x1 = np.linspace(0, 1, W)
    ridge = fbm(rng, 6, 4)[int(H * 0.5)]  # une ligne de bruit
    hills = H * (0.86 - 0.06 * ridge - 0.03 * np.sin(x1 * 5.0))
    far = hexc("#0a0c1a")
    img = np.where((yy > hills[None, :] - 40)[..., None], far * 0.6 + img * 0.4, img)
    ridge2 = fbm(rng, 6, 6)[int(H * 0.3)]
    near = H * (0.9 - 0.05 * ridge2 + 0.02 * np.cos(x1 * 3.3))
    img = np.where((yy > near[None, :])[..., None], sil, img)

    def island(cx, cy, w, h, seed_shift):
        r = np.random.default_rng(args.seed + seed_shift)
        cols = np.arange(W, dtype=np.float32)
        dx = (cols - cx) / w
        inside = np.abs(dx) < 1
        # dessus : légèrement bombé, irrégulier (végétation)
        bumps = gaussian_filter(r.random(W).astype(np.float32), 2.5) - 0.5
        trees = np.clip(gaussian_filter(r.random(W).astype(np.float32), 1.2) - 0.62, 0, 1) * 160
        top_edge = cy - h * 0.12 * np.sqrt(np.clip(1 - dx**2, 0, 1)) - 14 * bumps - trees * (np.abs(dx) < 0.85)
        # dessous : roche qui pend, en pointes irrégulières
        rough = gaussian_filter(r.random(W).astype(np.float32), 4)
        spikes = gaussian_filter(r.random(W).astype(np.float32), 1.5)
        depth = h * np.clip(1 - np.abs(dx) ** 1.6, 0, 1) ** 0.8 * (0.55 + 0.6 * rough + 0.5 * np.clip(spikes - 0.5, 0, 1))
        bottom = cy + depth
        m = inside[None, :] & (yy > top_edge[None, :]) & (yy < bottom[None, :])
        return gaussian_filter(m.astype(np.float32), 1.2) > 0.5

    for cx, cy, w, h, k in [(W * 0.13, H * 0.66, 210, 150, 1), (W * 0.88, H * 0.58, 150, 110, 2), (W * 0.79, H * 0.72, 70, 50, 3)]:
        m = island(cx, cy, w, h, k)
        img = np.where(m[..., None], sil, img)

    # touche « peinte » : léger flou, puis grain
    img = np.stack([gaussian_filter(img[..., c], 0.6) for c in range(3)], -1)
    img += (rng.random((H, W, 1)).astype(np.float32) - 0.5) * 0.018
    img = np.clip(img, 0, 1) ** 0.95

    full = Image.fromarray((img * 255).astype(np.uint8))
    full.save(args.out, "WEBP", quality=84, method=6)
    # tailles réduites pour le srcset (mobile, portable, grand écran)
    base, ext = os.path.splitext(args.out)
    for w in (960, 1600, 2880):
        im = full if w == W else full.resize((w, round(H * w / W)), Image.LANCZOS)
        im.save(f"{base}-{w}{ext}", "WEBP", quality=82 if w < W else 84, method=6)
    print(f"Écrit : {args.out} (+ 960, 1600, 2880)")


if __name__ == "__main__":
    main()
