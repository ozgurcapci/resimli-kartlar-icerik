"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: 34 ayrık elli dua fotoğrafı Kandiller ve Hayırlı Günler kategorilerine dağıtıldı."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 34, len(FILES)
HK, KMO, MK = "Hayırlı Kandiller", "Kandiliniz Mübarek Olsun", "Mübarek Kandiller"
START = {}  # yoksa kategorinin en büyük numarası + 1
PREFIX = {"ramazan": "ramazan_ayi"}  # kimlik öneki kategori anahtarından farklıysa
DROP = set()  # silinecek eski kartlar
SKIP = set()  # kullanılmayan görseller
TOTAL = 539
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "regaib": [
        (15, "Seccade başında geçen bir Regaib gecesi dilerim", HK),
        (32, "Sessizce edilen dualar Rabbime ulaşsın", KMO),
    ],
    "mirac": [
        (0, "Minareler gibi göğe uzanan dualar kabul olsun", MK),
        (23, "Gün batarken başlayan Miraç gecesi mübarek olsun", HK),
        (11, "Denizler kadar geniş bir rahmet dilerim", KMO),
        (31, "Yaşlı ellerin duası semalara ulaşsın", HK),
    ],
    "berat": [
        (19, "Berat gecesinde her tesbih bir tövbe olsun", HK),
        (24, "Annelerimizin duası Berat gecesinde kabul olsun", KMO),
        (27, "Kar gibi temiz, arınmış gönüller dilerim", MK),
        (6, "Dededen toruna dualarla bir Berat gecesi", HK),
    ],
    "kadir": [
        (1, "Kur’an’ın gölgesinde açılan eller rahmetle dolsun", "Kadir Geceniz Mübarek Olsun"),
        (3, "Mushaf başında edilen dualar arşa ulaşsın", "Hayırlı Kadir Geceleri"),
        (18, "Camide, secdede, duada geçen bir Kadir Gecesi dilerim", "Kadir Geceniz Mübarek Olsun"),
        (12, "Sabaha kadar süren dualarınız kabul olsun", "Hayırlı Kadir Geceleri"),
    ],
    "mevlid": [
        (2, "Salavatlarla açılan eller rahmetle dolsun", "Mevlid Kandiliniz Mübarek Olsun"),
        (7, "Efendimizin doğumu gönüllere sevinç getirsin", HK),
        (9, "Mevlid okunan camilerden gönüllere nur dolsun", MK),
        (21, "Çocuklarımızın dilinde salavat, gönlünde sevgi olsun", HK),
    ],
    "sabah": [
        (4, "Güne duayla başlayan gönüllere aydınlık bir gün", "Güne Bismillah"),
        (5, "Sisin ardından doğan güneş gibi umutlu bir gün dilerim", "Hayırlı Sabahlar"),
        (17, "Sabah duasıyla açılan pencerelere bereket dolsun", "Günaydın"),
    ],
    "gece": [
        (10, "Mumların ışığında edilen dualar yüreğinizi ısıtsın", "Hayırlı Geceler"),
        (30, "Günü şükürle kapatan gönüllere huzurlu bir gece", "İyi Geceler"),
        (25, "Annelerimizin duası gecemizi aydınlatsın", "Allah Rahatlık Versin"),
    ],
    "uc_aylar": [
        (13, "Bahar dallarında açan dualar gibi gönlünüz yeşersin", "Hayırlı Üç Aylar"),
        (14, "Tesbih taneleri gibi sayısız hayır dilerim", "Mübarek Üç Aylar"),
        (26, "Kışın ortasında rahmet baharı başlasın", "Üç Aylarınız Mübarek Olsun"),
    ],
    "ramazan": [
        (20, "Küçük ellerin duası Ramazan’a bereket katsın", "Hayırlı Ramazanlar"),
        (28, "Birlikte edilen dualar evinize bereket getirsin", "Ramazan-ı Şerifiniz Mübarek Olsun"),
    ],
    "hicri_yilbasi": [
        (22, "Batan güneşle eski yıl, duayla yeni yıl", "Hayırlı Hicri Yıllar"),
        (8, "Ufuk kadar geniş, deniz kadar dingin bir yıl dilerim", "Mübarek Hicri Yılbaşı"),
        (16, "Yeni yılınız olgun başaklar gibi bereketli olsun", "Hicri Yılbaşınız Mübarek Olsun"),
    ],
    "asure": [
        (29, "Evlatlarımızla edilen dualar kabul olsun", "Hayırlı Aşureler"),
        (33, "Tarladaki başaklar gibi şükrümüz çoğalsın", "Mübarek Aşure Günü"),
    ],
}
assert sorted(i for v in CARDS.values() for i, _, _ in v) == sorted(set(range(34)) - SKIP)
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
