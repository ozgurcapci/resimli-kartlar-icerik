"""İçerik deposu: her karta tipografi stili (`style`) ve görselin boş alanına göre yazı yeri (`textTop`) yazar,
greetingFont'u kaldırır, kesme işaretini tipografik yapar; uygulamadaki düzeni taklit eden önizleme sayfaları çizer.

Kullanım: python apply_styles.py [--write]   (yazmadan yalnız önizleme için --write vermeyin)
Elle stil düzeltmesi: OVERRIDE sözlüğü."""
import json, sys, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FONTS = Path("E:/yedek/Vibe Coding/Claude/apps/Resimli Cuma Kartlari/assets/fonts")
OUT = Path(__file__).parent / "onizleme"; OUT.mkdir(exist_ok=True)
W, PH = 1080, 1350

# Uygulamadaki CardStyle ile aynı değerler (lib/theme/card_style.dart).
STYLES = {
    "klasik": dict(mf="PlayfairDisplay.ttf", ms=.050, mw=420, tr=.01, lh=1.32, gf="PinyonScript.ttf", gs=.105, measure=.74, gap=.03, first="m"),
    "kitabe": dict(mf="Marcellus.ttf", ms=.044, mw=None, tr=.06, lh=1.38, gf="Corinthia.ttf", gs=.148, measure=.72, gap=.008, first="m"),
    "selamOnde": dict(mf="GildaDisplay.ttf", ms=.047, mw=None, tr=.02, lh=1.32, gf="Allura.ttf", gs=.135, measure=.74, gap=.016, first="g"),
}
ROTATION = ["kitabe", "klasik", "selamOnde"]
OVERRIDE = {"kadir_05": "klasik", "cuma_76": "klasik", "cuma_79": "klasik",  # konu yukarıdan başlıyor, iri selam ele değiyordu
            "cuma_88": "klasik", "cuma_93": "klasik", "cuma_94": "klasik"}  # iri selam ağaca, taşa, ufka biniyordu
G_MAX, G_LH, M_FIT, G_FIT = .86, 1.1, .92, .72
G_LH_MULTI = {"Corinthia.ttf": .85}  # iki satırlı selamda satır yüksekliği (ScriptFont.lineHeight)
TOP_MIN, TOP_MAX = .055, .22
TOP_OVERRIDE = {"cuma_76": .055}  # alttaki parlak bahçe yerine üstteki açık alan


def font(name, size, wght=None):
    f = ImageFont.truetype(str(FONTS / name), max(1, round(size)))
    if wght:
        f.set_variation_by_axes([wght])
    return f


class Face:
    def __init__(self, name, size, wght=None, tr=0.0, lh=1.25):
        self.name, self.size, self.wght, self.tr, self.lh = name, size, wght, tr, lh
        self.f = font(name, size, wght)

    def scaled(self, k):
        return Face(self.name, self.size * k, self.wght, self.tr, self.lh)

    def width(self, t):  # Flutter letterSpacing her harften sonra eklenir
        return self.f.getlength(t) + self.size * self.tr * len(t)


def balance(words, maxw, face):
    def greedy(limit):
        lines, cur = [], ""
        for w in words:
            nxt = w if not cur else cur + " " + w
            if cur and face.width(nxt) > limit:
                lines.append(cur); cur = w
            else:
                cur = nxt
        return lines + [cur]
    n = len(greedy(maxw))
    if n < 2:
        return greedy(maxw)
    lo, hi = max(face.width(w) for w in words), maxw
    for _ in range(14):
        if hi - lo <= .5: break
        mid = (lo + hi) / 2
        if len(greedy(mid)) <= n: hi = mid
        else: lo = mid
    return greedy(hi)


def best_two(words, face):
    best = None
    for i in range(1, len(words)):
        p = [" ".join(words[:i]), " ".join(words[i:])]
        w = max(map(face.width, p))
        if best is None or w < best[0]: best = (w, p)
    return best[1]


def lay(kind, text, st):
    """Uygulamadaki CardTypography.layout: (satırlar, yüz) döndürür."""
    s = STYLES[st]
    if kind == "m":
        face = Face(s["mf"], W * s["ms"], s["mw"], s["tr"], s["lh"]); maxw = W * s["measure"]; fit = M_FIT
    else:
        face = Face(s["gf"], W * s["gs"], None, 0, G_LH); maxw = W * G_MAX; fit = G_FIT
    nat = face.width(text)
    lines = [text]
    if nat > maxw:
        words = text.split()
        if len(words) < 2 or nat * fit <= maxw:
            face = face.scaled(maxw / nat)
        else:
            lines = balance(words, maxw, face)
            if kind == "g" and len(lines) > 2: lines = best_two(words, face)
            widest = max(map(face.width, lines))
            if widest > maxw: face = face.scaled(maxw / widest)
            if kind == "g" and len(lines) > 1: face.lh = G_LH_MULTI.get(s["gf"], G_LH)
    return lines, face


def block(card, st):
    """Öndeki ve arkadaki yazı (tür, satırlar, yüz, yükseklik px)."""
    s = STYLES[st]
    parts = [("m", card["message"]), ("g", card.get("greeting"))]
    if s["first"] == "g": parts.reverse()
    out = []
    for kind, text in parts:
        if not text: continue
        lines, face = lay(kind, text, st)
        out.append((kind, lines, face, len(lines) * face.size * face.lh))
    height = sum(b[3] for b in out) + s["gap"] * W * (len(out) - 1)
    return out, height


def subject_top(post):
    """Konunun başladığı satır (gönderi boyuna oran): üstten itibaren ayrıntı yoğunluğu belirgin artan ilk bant."""
    g = np.asarray(post.convert("L").resize((216, 270), Image.BILINEAR), dtype=np.float32)
    busy = np.abs(np.diff(g, axis=1)).mean(axis=1)[:-1] + np.abs(np.diff(g, axis=0)).mean(axis=1)
    busy = np.convolve(busy, np.ones(5) / 5, mode="same")
    base = np.median(busy[8:40])
    thr = max(base * 2.6, base + 2.2)
    for r in range(30, len(busy) - 4):
        if (busy[r:r + 4] > thr).all():
            return r / 270
    return .55


def place(card, st, post):
    _, hb = block(card, st)
    sub = subject_top(post)
    avail = (sub - .035) * PH - TOP_MIN * PH
    top = TOP_MIN * PH + max(0, avail - hb) * .35
    return round(min(top / PH, TOP_MAX), 3), sub, hb


def render(post, card, st, top):
    im = post.convert("RGBA"); layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    color = card.get("textColor", "#FFFFFF"); parts, _ = block(card, st); y = top * PH
    for kind, lines, face, h in parts:
        lh = face.size * face.lh
        for i, l in enumerate(lines):
            cy = y + lh * (i + .5); x = W / 2 - face.width(l) / 2
            for ch in l:
                d.text((x, cy), ch, font=face.f, fill=color, anchor="lm"); x += face.f.getlength(ch) + face.size * face.tr
        y += h + STYLES[st]["gap"] * W
    r, g_, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    if (0.2126 * r + 0.7152 * g_ + 0.0722 * b) / 255 > .45:  # açık yazıya hafif gölge (uygulamadaki gibi)
        a = layer.split()[3].filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * .4))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(a); im = Image.alpha_composite(im, sh)
    return Image.alpha_composite(im, layer).convert("RGB")


def main():
    write = "--write" in sys.argv
    lines = (REPO / "templates.json").read_text(encoding="utf-8").split("\n")
    out, thumbs, report = [], [], []
    counters = {}
    for line in lines:
        m = re.match(r'^(\s*)(\{.*\})(,?)\s*$', line)
        if not m:
            out.append(line); continue
        card = json.loads(m.group(2))
        cat = card["category"]
        for k in ("message", "greeting"):
            if card.get(k): card[k] = card[k].replace("'", "’")
        i = counters.get(cat, 0); counters[cat] = i + 1
        offset = sorted(STYLES).index(ROTATION[0]) + len(cat)  # kategoriye göre farklı başlangıç
        st = OVERRIDE.get(card["id"], ROTATION[(i + offset) % 3])
        card.pop("greetingFont", None)
        card["style"] = st
        if card.get("image"):
            post = Image.open(REPO / "cards" / card["image"]).convert("RGB")
            post = post.crop((0, post.height - PH, W, post.height)) if post.height * 4 >= post.width * 5 else post
            top, sub, hb = place(card, st, post)
            top = TOP_OVERRIDE.get(card["id"], top)
            card["textTop"] = top
            parts, _ = block(card, st)
            ml = next((len(p[1]) for p in parts if p[0] == "m"), 0)
            gl = next((len(p[1]) for p in parts if p[0] == "g"), 0)
            report.append((card["id"], st, top, round(sub, 2), ml, gl))
            th = render(post, card, st, top).resize((216, 270), Image.LANCZOS)
            dd = ImageDraw.Draw(th); dd.rectangle((0, 258, 216, 270), fill="white")
            dd.text((3, 258), f'{card["id"]} {st[:3]} {top}', fill="red")
            # konu sınırı çizgisi (yalnız önizlemede)
            dd.line((0, sub * 270, 6, sub * 270), fill="red", width=2)
            thumbs.append(th)
        keys = list(card)
        ordered = {k: card[k] for k in keys if k not in ("style", "textTop")}
        ordered["style"] = card["style"]
        if "textTop" in card: ordered["textTop"] = card["textTop"]
        out.append(m.group(1) + json.dumps(ordered, ensure_ascii=False) + m.group(3))
    txt = "\n".join(out); json.loads(txt)
    if write:
        (REPO / "templates.json").write_text(txt, encoding="utf-8", newline="\n")
    per = 40
    for k in range(0, len(thumbs), per):
        s = Image.new("RGB", (216 * 10, 270 * 4), "white")
        for j, t in enumerate(thumbs[k:k + per]): s.paste(t, ((j % 10) * 216, (j // 10) * 270))
        s.save(OUT / f"sheet_{k // per}.jpg", quality=88)
    from collections import Counter
    print("stiller:", Counter(r[1] for r in report))
    print("mesaj satır:", Counter(r[4] for r in report), "selam satır:", Counter(r[5] for r in report))
    print("3+ satır:", [r for r in report if r[4] > 2])
    print("üstte (konu yakın):", [r[0] for r in report if r[2] <= TOP_MIN + .001][:60])
    print("sayfa:", (len(thumbs) + per - 1) // per)


main()
