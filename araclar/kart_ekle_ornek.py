"""40 görsel (İndirilenler, mtime sırası) → 9:16 → beş kandile sekizer; her kategorinin son kartının ardına eklenir."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 40, len(FILES)
HK, KMO, MK = "Hayırlı Kandiller", "Kandiliniz Mübarek Olsun", "Mübarek Kandiller"
MV = "Mevlid Kandiliniz Mübarek Olsun"
KG, HKG = "Kadir Geceniz Mübarek Olsun", "Hayırlı Kadir Geceleri"
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "regaib": [
        (1, "Üç ayların bereketi gönlünüze yol bulsun", HK),
        (7, "Gönlünüz bu göl gibi dingin, duanız kabul olsun", MK),
        (15, "Üç ayların kapısı rahmetle açılsın", KMO),
        (18, "Recep’in ilk kandili gönlünüzü gül bahçesine çevirsin", HK),
        (23, "Uzaktaki sevdiklerime kandil selamı", MK),
        (25, "Rağbet gecesinde dilekleriniz karşılık bulsun", HK),
        (32, "Kanatlanan dualar Rabbime ulaşsın", KMO),
        (33, "Üç ayların baharı gönlünüzde açsın", HK),
    ],
    "mirac": [
        (6, "Bu gece semalar açık, dualar makbul olsun", HK),
        (8, "Boğaz’ın ışıkları gibi gönlünüz nurlansın", MK),
        (13, "Yıldızlı bir gecede yükselen dualar sizin için", KMO),
        (21, "Miraç’ın müjdesi gönlünüze huzur getirsin", HK),
        (28, "Mescid-i Aksa’dan semalara uzanan gece mübarek olsun", MK),
        (34, "Uzattığımız eller rahmetle dolsun", KMO),
        (36, "Gönülleri semaya taşıyan gece mübarek olsun", HK),
        (39, "Pencere önünde bir mum, gönülde bir dua", MK),
    ],
    "berat": [
        (2, "Ekmeğiniz bol, rızkınız helal olsun", HK),
        (3, "Arınmış gönüllerle bir Berat gecesi dilerim", KMO),
        (4, "Yeni yılın takdiri hayırla yazılsın", MK),
        (10, "Ayçiçekleri gibi yüzünüz hep nura dönsün", HK),
        (17, "Bereketiniz artsın, kısmetiniz açılsın", KMO),
        (20, "Tövbelerle arınan gönüllere selam olsun", HK),
        (27, "Rahmet suyuyla günahlarımız yıkansın", MK),
        (30, "Büyüklerin duası küçüklerin üzerinde olsun", HK),
    ],
    "kadir": [
        (14, "Rahmet kapıları ardına kadar açılsın", KG),
        (16, "Her tesbih tanesi bir af vesilesi olsun", HKG),
        (22, "Orucunuz ve duanız kabul olsun", KG),
        (24, "Kur’an’ın sesi evinizden eksik olmasın", HKG),
        (29, "Bu gece edilen dualar bin aya bedel olsun", KG),
        (35, "Kâbe’ye dönen yüzler, Rabbe açılan eller", HKG),
        (37, "Rabbim bu geceyi idrak edenlerden eylesin", KG),
        (38, "Sessiz bir secdede kabul olan dualar dilerim", HKG),
    ],
    "mevlid": [
        (0, "Bir gül açtı, âlem nura gark oldu", MV),
        (5, "Medine’nin nuru gönlünüze dolsun", HK),
        (9, "Yeşil Kubbe’ye selam, Efendimize salavat", MK),
        (11, "Mekke çöllerinden doğan nur yolunuzu aydınlatsın", HK),
        (12, "Efendimizin doğduğu gece mübarek olsun", MV),
        (19, "Salavatlarla dolu, gül kokulu bir gece dilerim", MK),
        (26, "Peygamber gülü gönlünüzde açsın", HK),
        (31, "Avuçlarınız gül, dilleriniz salavat dolsun", MV),
    ],
}
assert sorted(i for v in CARDS.values() for i, _, _ in v) == list(range(40))
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
txt = "\n".join(out); data = json.loads(txt); assert len({t["id"] for t in data}) == len(data) == 245
(REPO / "templates.json").write_text(txt, encoding="utf-8", newline="\n")
