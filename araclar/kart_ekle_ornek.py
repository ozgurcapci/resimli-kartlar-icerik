"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: Cuma için 39 görsel (cuma_99–137): doğa fotoğrafları, suluboya doğa, çiçek ve kuş."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 39, len(FILES)
HC, CM, MC, CH = "Hayırlı Cumalar", "Cumanız Mübarek Olsun", "Mübarek Cumalar", "Cumanız Hayırlı Olsun"
START = {}  # yoksa kategorinin en büyük numarası + 1
PREFIX = {"ramazan": "ramazan_ayi"}  # kimlik öneki kategori anahtarından farklıysa
DROP = set()  # silinecek eski kartlar
SKIP = set()  # kullanılmayan görseller
TOTAL = 418
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "cuma": [
        (0, "Sisli bir sabah, sakin bir gönül dilerim", HC),
        (1, "Bembeyaz bir gönül, berrak bir dua dilerim", CM),
        (2, "Akan dere gibi bereketiniz hiç dinmesin", HC),
        (3, "Doğan güneşle umutlarınız tazelensin", MC),
        (4, "Her damla çiy gibi rahmet üzerinize insin", HC),
        (5, "Çiçek açan dallar gibi gönlünüz ferah olsun", CH),
        (6, "Kökleri sağlam, gölgesi geniş bir iman dilerim", HC),
        (7, "Şelale gibi coşan bereket hanenize dolsun", CM),
        (8, "Dağ suyu gibi tertemiz bir gün dilerim", HC),
        (9, "Su gibi aziz olun, gönlünüz serin kalsın", MC),
        (10, "Yaylaların huzuru gönlünüze dolsun", HC),
        (11, "Durgun su gibi sakin, ağaç gibi sabırlı olalım", CH),
        (12, "Gelincikler gibi neşeli bir Cuma dilerim", HC),
        (13, "Ormana süzülen ışık gibi rahmet kalbinize dolsun", CM),
        (14, "Akşamın huzuru gönlünüze yansısın", HC),
        (15, "Değirmen döner, bereket hiç tükenmesin", MC),
        (16, "Abdestiniz bereket, namazınız nur olsun", HC),
        (17, "Kuş sesleri gibi müjdeli haberleriniz olsun", CH),
        (18, "Yaylanın serinliği, ezanın huzuru sizinle olsun", HC),
        (19, "Rahmet suyu gönüllerimize aksın", CM),
        (20, "Köprüler kuran, gönüller yapan bir gün olsun", HC),
        (21, "Derelerin sesi, duaların sesi olsun", MC),
        (22, "Köyün sabahı gibi sade ve huzurlu bir gün", HC),
        (23, "Karlar gibi ak, ezan gibi temiz bir gönül dilerim", CH),
        (24, "Her mevsimin güzelliği gönlünüze dolsun", HC),
        (25, "Dallardaki çiçekler gibi umutlarınız açsın", CM),
        (26, "Bülbülün güle hasreti gibi dualarımız Rabbe olsun", HC),
        (27, "Küçük bir kuşun sevinci gününüze dolsun", MC),
        (28, "Bahar dalları gibi taze bir gönül dilerim", HC),
        (29, "Akan su gibi duru bir kalp dilerim", CH),
        (30, "Soğuk günlerde sıcak dualar sizinle olsun", HC),
        (31, "Sevdiklerinizle yan yana huzurlu bir Cuma", CM),
        (32, "Şakayıklar gibi zarif ve bereketli bir gün dilerim", HC),
        (33, "Sümbül kokulu, huzur dolu bir Cuma", MC),
        (34, "Karı delen kardelen gibi umudunuz taze kalsın", HC),
        (35, "Ortancalar gibi rengârenk bir gönül dilerim", CH),
        (36, "Yasemin kokulu dualarınız kabul olsun", HC),
        (37, "Nilüfer gibi tertemiz bir kalp dilerim", CM),
        (38, "Mor salkımlar gibi bereketiniz bol olsun", HC),
    ],
}
assert sorted(i for v in CARDS.values() for i, _, _ in v) == sorted(set(range(39)) - SKIP)
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
