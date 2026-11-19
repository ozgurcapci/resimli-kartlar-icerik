"""19 fotoğraf (İndirilenler, mtime sırası) → 9:16 → cuma_80…; cuma_79'un ardına eklenir."""
import io, json, re
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 19, len(FILES)
HC, CM, CH, MC = "Hayırlı Cumalar", "Cumanız Mübarek Olsun", "Cumanız Hayırlı Olsun", "Mübarek Cumalar"
CARDS = [
    (0, "Açılan her el boş dönmesin", HC),
    (1, "Hurma tatlılığında, su berraklığında bir gün dilerim", CH),
    (2, "Kırlangıçlar gibi müjdeli haberleriniz olsun", HC),
    (3, "Bir güvercin kanadında selam gönderdim", MC),
    (4, "Gönlünüz gül gibi açılsın, rahmetle dolsun", CM),
    (5, "Secdeniz nurlu, gönlünüz ak olsun", HC),
    (6, "Kandil ışığı gibi sönmeyen bir iman dilerim", MC),
    (7, "Ayetlerin bereketi hanenizi sarsın", CM),
    (8, "Her mevsim gönlünüz huzurla dolsun", HC),
    (9, "Medine’nin selamı gönlünüze ulaşsın", CH),
    (10, "Her tane bir dua, her dua bir şifa olsun", HC),
    (11, "İstanbul’un akşamından size selam olsun", MC),
    (12, "Gül bahçeleri gibi kokulu bir gün dilerim", CH),
    (13, "Akan su gibi bereketiniz bol olsun", HC),
    (14, "Kâbe’ye dönen gönüller dualarda buluşsun", CM),
    (15, "Avlularda yükselen dualar sizin için olsun", HC),
    (16, "Yüzünüz bahar gibi gülsün", CH),
    (17, "Sarı güller gibi neşeli bir gün dilerim", MC),
    (18, "Yayla serinliğinde, huzur dolu bir Cuma dilerim", HC),
]
W, H = 1080, 1920; PH = W * 5 // 4; TOP = H - PH


def to_9x16(img):
    w, h = img.size; th = round(w * 16 / 9)
    if th <= h: img = img.crop((0, h - th, w, h))
    else:
        tw = round(h * 9 / 16); l = (w - tw) // 2; img = img.crop((l, 0, l + tw, h))
    return img.resize((W, H), Image.LANCZOS)


def save_small(img, path):
    for q in range(86, 60, -3):
        b = io.BytesIO(); img.save(b, "JPEG", quality=q, optimize=True, progressive=True)
        if b.tell() <= 350_000 or q <= 63: path.write_bytes(b.getvalue()); return b.tell()


def color(img):
    r, g, b = ImageStat.Stat(img.crop((100, TOP, 980, TOP + 420))).mean
    if (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 < 0.55: return "#FFF8E7"
    return "#5B4630" if r - b > 25 else "#2F5D50"


rows = []
for n, (i, msg, greet) in enumerate(CARDS, 80):
    img = to_9x16(Image.open(FILES[i]).convert("RGB")); cid = f"cuma_{n:02d}"
    size = save_small(img, REPO / "cards" / "cuma" / f"{cid}.jpg"); c = color(img)
    rows.append({"id": cid, "category": "cuma", "message": msg, "greeting": greet, "image": f"cuma/{cid}.jpg",
                 "textColor": c, "accent": "#C9A45C"})
    print(cid, size // 1024, "KB", c, FILES[i].name)

lines = (REPO / "templates.json").read_text(encoding="utf-8").split("\n"); out = []
for l in lines:
    out.append(l)
    if '"id": "cuma_79"' in l:
        assert l.rstrip().endswith(",")
        out += ["  " + json.dumps(r, ensure_ascii=False) + "," for r in rows]
txt = "\n".join(out); data = json.loads(txt); assert len({t["id"] for t in data}) == len(data) == 205
(REPO / "templates.json").write_text(txt, encoding="utf-8", newline="\n")
