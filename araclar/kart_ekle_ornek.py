"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: Regaib için 19 gerçekçi gece fotoğrafı (regaib_15–33)."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 19, len(FILES)
HK, KMO, MK = "Hayırlı Kandiller", "Kandiliniz Mübarek Olsun", "Mübarek Kandiller"
START = {}  # yoksa kategorinin en büyük numarası + 1
PREFIX = {"ramazan": "ramazan_ayi"}  # kimlik öneki kategori anahtarından farklıysa
DROP = set()  # silinecek eski kartlar
SKIP = set()  # kullanılmayan görseller
TOTAL = 505
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "regaib": [
        (0, "Bir lokum, bir çay; tatlı sohbetli bir kandil gecesi", HK),
        (1, "Akşam ezanıyla başlayan bu gece rahmetle dolsun", KMO),
        (2, "Camiye giden her yol nur ile dolsun", MK),
        (3, "Her tanesi bir dua, her duası kabul olsun", HK),
        (4, "Sofranız bereketli, sohbetiniz muhabbetli olsun", KMO),
        (5, "Bir gül, bir mum, bir dua; gönlünüz aydınlansın", HK),
        (6, "Gönül fenerleriniz Regaib gecesinde parlasın", MK),
        (7, "Şadırvan suyu gibi gönülleriniz arınsın", KMO),
        (8, "Seccadeniz dualarla, gönlünüz huzurla dolsun", HK),
        (9, "Şehrin ışıkları gibi dualarınız semaya yükselsin", MK),
        (10, "Bu gece okunan dualar kalplere şifa olsun", KMO),
        (11, "Karlı bir gecede sıcacık dualar sizinle olsun", HK),
        (12, "Soğuk gecede ısıtan bir dua, sönmeyen bir kandil", MK),
        (13, "Camilerin ışığı gönüllere yansısın", KMO),
        (14, "Okunan her ayet evinize huzur getirsin", HK),
        (15, "Köy camisinin ışığı kadar sıcak bir kandil dilerim", MK),
        (16, "Açılan eller boş dönmesin, dualarınız kabul olsun", KMO),
        (17, "Üç ayların ilk müjdesi hepimize hayırlar getirsin", HK),
        (18, "Minarelerdeki ışıklar gibi kalbiniz nurlansın", MK),
    ],
}
assert sorted(i for v in CARDS.values() for i, _, _ in v) == sorted(set(range(19)) - SKIP)
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
        img = to_9x16(Image.open(FILES[i]).convert("RGB")); cid = f"{PREFIX.get(cat, cat)}_{n:02d}"
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
            add = ["  " + json.dumps(r, ensure_ascii=False) + "," for r in rows]
            if not l.rstrip().endswith(","):  # dizinin son kartı: yeni sonuncu virgülsüz olur
                if out and out[-1] == l: out[-1] = l.rstrip() + ","
                add[-1] = add[-1].rstrip(",")
            out += add
txt = "\n".join(out); data = json.loads(txt); assert len({t["id"] for t in data}) == len(data) == TOTAL
(REPO / "templates.json").write_text(txt, encoding="utf-8", newline="\n")
