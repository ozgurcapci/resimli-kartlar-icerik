"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: Hicri Yılbaşı için 24 görsel (hicri_yilbasi_01–24); eski degrade kartlar (DROP) silindi."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 24, len(FILES)
HHY, HYMO, MHY = "Hayırlı Hicri Yıllar", "Hicri Yılbaşınız Mübarek Olsun", "Mübarek Hicri Yılbaşı"
START = {"hicri_yilbasi": 1}  # yoksa kategorinin en büyük numarası + 1
DROP = {"hicri_01", "hicri_02"}  # silinecek eski kartlar
TOTAL = 288
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "hicri_yilbasi": [
        (0, "Hicretin ruhu yeni yılınıza yol göstersin", HHY),
        (1, "Medine’nin nuru yeni yılınızı aydınlatsın", HYMO),
        (2, "Hayra giden her yolculuk mübarek olsun", MHY),
        (3, "Güvercin yuvası gibi huzurlu bir yıl dilerim", HHY),
        (4, "Allah’ın koruması yeni yılda da üzerinizde olsun", HYMO),
        (5, "Her adımı hayra açılan bir yıl olsun", MHY),
        (6, "Yeni yılda adımlarınız bereketli olsun", HHY),
        (7, "Yeni yıl hayır kapılarını size açsın", HYMO),
        (8, "Rahmet kapıları ardına kadar açık olsun", MHY),
        (9, "Yeni yılın ilk duası kabul olsun", HHY),
        (10, "Yeni hilalle gelen yıl hayırlar getirsin", HYMO),
        (11, "İlk ışıkla gelen yıl umut dolsun", MHY),
        (12, "Yolunuzu aydınlatan bir yıl dilerim", HHY),
        (13, "Vahada su gibi ferahlatan bir yıl olsun", HYMO),
        (14, "Hicret yolunun bereketi üzerinize olsun", MHY),
        (15, "Sabırla yürünen yollar hayırla biter", HHY),
        (16, "Muharrem hilaliyle yeni yıl mübarek olsun", HYMO),
        (17, "Yeni yıl, yeni niyet, yeni umut", MHY),
        (18, "Sulh ve huzur dolu bir yıl dilerim", HHY),
        (19, "İlk mescidin huzuru evinize dolsun", HYMO),
        (20, "Secdeleriniz huzur, yılınız bereket olsun", MHY),
        (21, "Yeni yılda yolunuz nurla aydınlansın", HHY),
        (22, "Rabbim yolunuzu kolaylaştırsın", HYMO),
        (23, "Sofranız bereketli, yılınız hayırlı olsun", MHY),
    ],
}
assert sorted(i for v in CARDS.values() for i, _, _ in v) == list(range(24))
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


data = json.loads((REPO / "templates.json").read_text(encoding="utf-8"))
new = {}  # kategorinin son kimliği → eklenecek satırlar
for cat, items in CARDS.items():
    ids = [t["id"] for t in data if t["category"] == cat]
    start = START.get(cat) or max(int(i.rsplit("_", 1)[1]) for i in ids) + 1
    rows = []; (REPO / "cards" / cat).mkdir(exist_ok=True)
    for n, (i, msg, greet) in enumerate(items, start):
        img = to_9x16(Image.open(FILES[i]).convert("RGB")); cid = f"{cat}_{n:02d}"
        size = save_small(img, REPO / "cards" / cat / f"{cid}.jpg"); c = color(img)
        rows.append({"id": cid, "category": cat, "message": msg, "greeting": greet, "image": f"{cat}/{cid}.jpg",
                     "textColor": c, "accent": "#C9A45C"})
        print(cid, size // 1024, "KB", c, FILES[i].name)
    new[ids[-1]] = rows

lines = (REPO / "templates.json").read_text(encoding="utf-8").split("\n"); out = []
for l in lines:
    if not any(f'"id": "{d}"' in l for d in DROP): out.append(l)
    for last, rows in new.items():
        if f'"id": "{last}"' in l:
            assert l.rstrip().endswith(","), last
            out += ["  " + json.dumps(r, ensure_ascii=False) + "," for r in rows]
txt = "\n".join(out); data = json.loads(txt); assert len({t["id"] for t in data}) == len(data) == TOTAL
(REPO / "templates.json").write_text(txt, encoding="utf-8", newline="\n")
