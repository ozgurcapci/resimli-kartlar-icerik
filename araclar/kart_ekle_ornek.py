"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: Gece için 37 görsel (gece_04–40; eski degrade gece_01–03 silindi)."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 37, len(FILES)
HG, IG, AR = "Hayırlı Geceler", "İyi Geceler", "Allah Rahatlık Versin"
START = {"gece": 4}  # yoksa kategorinin en büyük numarası + 1
PREFIX = {"ramazan": "ramazan_ayi"}  # kimlik öneki kategori anahtarından farklıysa
DROP = {"gece_01", "gece_02", "gece_03"}  # silinecek eski kartlar
SKIP = set()  # kullanılmayan görseller
TOTAL = 486
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "gece": [
        (0, "Battaniye sıcaklığında huzurlu bir uyku dilerim", IG),
        (1, "Ateşböcekleri kadar parlak rüyalar dilerim", HG),
        (2, "Dalgaların sesiyle dinlendiren bir gece dilerim", HG),
        (3, "Fenerler yolunuzu, dualar gönlünüzü aydınlatsın", HG),
        (4, "Karlı gecelerde sıcacık bir yuva dilerim", IG),
        (5, "Ay ışığı gibi sakin bir gece dilerim", AR),
        (6, "Şehrin ışıkları sönerken gönlünüz huzurla dolsun", HG),
        (7, "Yıldızlar kadar umutlu bir yarın dilerim", IG),
        (8, "Bir bardak ıhlamur, deliksiz bir uyku dilerim", IG),
        (9, "Mum ışığı gibi yumuşak bir gece dilerim", HG),
        (10, "Gece sefaları gibi açan güzel rüyalar dilerim", IG),
        (11, "Hilalin altında huzurla uyuyun", HG),
        (12, "Pencerenizden yıldızlar, gönlünüzden dualar eksik olmasın", HG),
        (13, "Mışıl mışıl, tatlı bir uyku dilerim", IG),
        (14, "Durgun göl gibi sakin bir gece dilerim", HG),
        (15, "Yasemin kokulu, huzurlu bir gece dilerim", IG),
        (16, "Ihlamur kokulu sohbetlerle güzel bir gece", HG),
        (17, "Kar beyazı, pamuk gibi bir uyku dilerim", IG),
        (18, "Gece okunan dualar sabaha nur olsun", AR),
        (19, "Kuşlar gibi rahat, tatlı bir uyku dilerim", IG),
        (20, "Şehir uyurken dualarımız sizinle olsun", HG),
        (21, "Semaver başında güzel bir gece dilerim", IG),
        (22, "Deniz feneri gibi yolunuz hep aydınlık olsun", HG),
        (23, "Ateşin sıcaklığı, yıldızların huzuru sizinle olsun", IG),
        (24, "Çamların fısıltısıyla huzurlu bir gece dilerim", HG),
        (25, "Evinizin ışığı hiç sönmesin", AR),
        (26, "Yatsı duasıyla huzur dolu bir gece dilerim", AR),
        (27, "Çöl gecesi kadar dingin bir gönül dilerim", HG),
        (28, "Köprünün ışıkları gibi umutlarınız parlasın", IG),
        (29, "Eski sokakların sessizliği gibi derin bir uyku dilerim", IG),
        (30, "Limanına dönen kayık gibi huzurla dinlenin", HG),
        (31, "Lavanta kokulu, deliksiz bir uyku dilerim", IG),
        (32, "Yıldızların yansıdığı göl gibi berrak rüyalar dilerim", HG),
        (33, "Peri bacalarının sessizliğinde güzel bir gece dilerim", IG),
        (34, "Son çay, son dua; huzurlu bir gece dilerim", HG),
        (35, "Dağ evinin sessizliği gibi rahat bir uyku dilerim", IG),
        (36, "Lamba ışığında tatlı bir gece dilerim", AR),
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
