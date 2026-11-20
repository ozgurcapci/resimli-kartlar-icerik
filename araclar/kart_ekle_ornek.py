"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: Üç Aylar için 24 görsel (uc_aylar_04–27)."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 24, len(FILES)
HUA, UAMO, MUA = "Hayırlı Üç Aylar", "Üç Aylarınız Mübarek Olsun", "Mübarek Üç Aylar"
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "uc_aylar": [
        (0, "Üç ayların bereketiyle gönlünüz yeşersin", HUA),
        (1, "Kur’an’la geçen günler, nurla dolan gönüller", MUA),
        (2, "Rahmet yağmuruyla arınan bir üç ay dilerim", UAMO),
        (3, "Tövbeyle yeşeren gönüllere selam olsun", HUA),
        (4, "Recep, Şaban ve Ramazan bereketle gelsin", UAMO),
        (5, "Üç mum, üç ay, bin dua", MUA),
        (6, "Üç ayların ilk ışığı gönlünüze doğsun", HUA),
        (7, "Dualarımız kanatlanıp Rabbimize ulaşsın", UAMO),
        (8, "Her tesbih tanesinde bir dua, her duada bir umut", MUA),
        (9, "Gönüller arınsın, dualar kabul olsun", HUA),
        (10, "Büyüklerimizin duası üzerimizden eksik olmasın", UAMO),
        (11, "Okunan her ayet gönlünüze şifa olsun", MUA),
        (12, "Nesilden nesile dualarla Üç Aylar", HUA),
        (13, "Ramazan’a uzanan yolunuz hayırla dolsun", MUA),
        (14, "Açılan eller boş dönmesin", HUA),
        (15, "Dualarınız kabul, gönlünüz huzurlu olsun", MUA),
        (16, "Üç ay, üç fener; yolunuz hep aydınlık olsun", MUA),
        (17, "Rahmet aylarının ışığı evinizi aydınlatsın", HUA),
        (18, "Lale kokulu bir Üç Aylar dilerim", HUA),
        (19, "Rabbe yaklaştıran her adım mübarek olsun", MUA),
        (20, "Tövbe kapısı açık, rahmet kapısı geniş", HUA),
        (21, "Dualarınız çiçek açsın", MUA),
        (22, "Seccadeniz bereketli, secdeniz makbul olsun", MUA),
        (23, "Rahmet pınarından gönlünüze huzur aksın", HUA),
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
    start = max(int(i.rsplit("_", 1)[1]) for i in ids) + 1
    rows = []
    for n, (i, msg, greet) in enumerate(items, start):
        img = to_9x16(Image.open(FILES[i]).convert("RGB")); cid = f"{cat}_{n:02d}"
        size = save_small(img, REPO / "cards" / cat / f"{cid}.jpg"); c = color(img)
        rows.append({"id": cid, "category": cat, "message": msg, "greeting": greet, "image": f"{cat}/{cid}.jpg",
                     "textColor": c, "accent": "#C9A45C"})
        print(cid, size // 1024, "KB", c, FILES[i].name)
    new[ids[-1]] = rows

lines = (REPO / "templates.json").read_text(encoding="utf-8").split("\n"); out = []
for l in lines:
    out.append(l)
    for last, rows in new.items():
        if f'"id": "{last}"' in l:
            assert l.rstrip().endswith(","), last
            out += ["  " + json.dumps(r, ensure_ascii=False) + "," for r in rows]
txt = "\n".join(out); data = json.loads(txt); assert len({t["id"] for t in data}) == len(data) == 269
(REPO / "templates.json").write_text(txt, encoding="utf-8", newline="\n")
