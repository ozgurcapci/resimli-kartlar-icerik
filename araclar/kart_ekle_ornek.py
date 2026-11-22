"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: Sabah için 37 görsel (sabah_04–40; eski degrade sabah_01–03 silindi)."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 37, len(FILES)
HS, GA, GB = "Hayırlı Sabahlar", "Günaydın", "Güne Bismillah"
START = {"sabah": 4}  # yoksa kategorinin en büyük numarası + 1
PREFIX = {"ramazan": "ramazan_ayi"}  # kimlik öneki kategori anahtarından farklıysa
DROP = {"sabah_01", "sabah_02", "sabah_03"}  # silinecek eski kartlar
SKIP = set()  # kullanılmayan görseller
TOTAL = 452
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "sabah": [
        (0, "Lale gibi zarif, çiy gibi taze bir sabah dilerim", GA),
        (1, "Bir fincan kahve, bir tutam huzur dilerim", HS),
        (2, "Güneşle uyanan gönüllere aydınlık bir gün", GA),
        (3, "Sofranız taze ekmek gibi bereketli olsun", HS),
        (4, "Kuş sesleriyle uyanılan huzurlu bir sabah dilerim", GA),
        (5, "Demli bir çay, güzel bir manzara, huzurlu bir gün", GA),
        (6, "Simit kokulu, çayı demli bir sabah dilerim", HS),
        (7, "Kahvaltınız bereketli, gününüz neşeli olsun", HS),
        (8, "Şehrin üstüne doğan güneş gönlünüze de doğsun", GA),
        (9, "Durgun su gibi sakin bir sabah dilerim", HS),
        (10, "Serçeler kadar neşeli bir güne uyanın", GA),
        (11, "Kahvesi köpüklü, sohbeti tatlı bir sabah dilerim", HS),
        (12, "Sofranız bereketli, sohbetiniz bol olsun", HS),
        (13, "Çay ve simitle güzel bir güne merhaba", GA),
        (14, "Güzel bir günün kapıları size açılsın", HS),
        (15, "Gül kokulu bir sabah, güler yüzlü bir gün dilerim", GA),
        (16, "Sabah ezanıyla başlayan gününüz bereketli olsun", GB),
        (17, "Pencerenizden huzur, kapınızdan bereket girsin", GA),
        (18, "Çiçek dolu yollarda güzel bir gün dilerim", GA),
        (19, "Güvercin kanadında selamımız size gelsin", HS),
        (20, "Semaver kaynasın, sohbet hiç bitmesin", GA),
        (21, "Bahçenin bereketi sofranızdan eksik olmasın", HS),
        (22, "Taze çay yaprağı gibi canlı bir gün dilerim", GA),
        (23, "Dalga sesi, çay buharı ve huzurlu bir sabah", GA),
        (24, "Sulanan çiçekler gibi gönlünüz yeşersin", HS),
        (25, "Ağaçlardan süzülen ışık yolunuzu aydınlatsın", GB),
        (26, "Yayla havası gibi ferah bir gün dilerim", GA),
        (27, "Lavanta kokulu, sakin bir sabah dilerim", HS),
        (28, "Dalında kiraz gibi tatlı bir gün dilerim", GA),
        (29, "Her damla çiy yeni bir umut olsun", HS),
        (30, "Sisli dağlardan size güzel bir sabah selamı", GA),
        (31, "Güneşli bir pencere, tatlı bir uyanış dilerim", GA),
        (32, "Çaydanlık kaynadı, güzel bir gün başlasın", GB),
        (33, "Bal gibi tatlı, kaymak gibi yumuşak bir gün dilerim", GA),
        (34, "Portakal bahçesi gibi ferah ve bereketli bir gün", HS),
        (35, "Köy kahvaltısı tadında güzel bir gün dilerim", HS),
        (36, "Deniz kadar geniş, ufuk kadar aydınlık bir gün dilerim", GA),
    ],
}
assert sorted(i for v in CARDS.values() for i, _, _ in v) == sorted(set(range(37)) - SKIP)
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
