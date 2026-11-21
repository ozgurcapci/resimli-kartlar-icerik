"""İndirilenler'deki görseller (mtime sırası) → 9:16 → CARDS'taki kategorilere; her kategorinin son kartının ardına eklenir.

Son kullanım: Ramazan için 57 görsel (ramazan_ayi_08–64); eski degrade ramazan_ayi_01–04 silindi."""
import io, json
from pathlib import Path
from PIL import Image, ImageStat

DL = Path.home() / "Downloads"
REPO = Path("E:/yedek/Vibe Coding/Claude/apps/resimli-kartlar-icerik")
FILES = sorted(DL.glob("*_2K.jpg"), key=lambda f: (f.stat().st_mtime, f.name))
assert len(FILES) == 64, len(FILES)
HR, RS, HG = "Hayırlı Ramazanlar", "Ramazan-ı Şerifiniz Mübarek Olsun", "Hoş Geldin Ramazan"
HI, HS = "Hayırlı İftarlar", "Hayırlı Sahurlar"
START = {}  # yoksa kategorinin en büyük numarası + 1
PREFIX = {"ramazan": "ramazan_ayi"}  # kimlik öneki kategori anahtarından farklıysa
DROP = {"ramazan_ayi_01", "ramazan_ayi_02", "ramazan_ayi_03", "ramazan_ayi_04"}  # silinecek eski kartlar (degrade)
SKIP = {18, 38, 39, 40, 42, 44, 46}  # kullanılmayan görseller (benzer kopya / zayıf)
TOTAL = 380
# kategori → [(görsel sırası, mesaj, selam)]
CARDS = {
    "ramazan": [
        (0, "Secdeleriniz huzur, oruçlarınız makbul olsun", HR),
        (1, "Akşam serinliğinde bereketli bir iftar dilerim", HI),
        (2, "Fırından yeni çıkmış pide gibi sıcak bir Ramazan", HG),
        (3, "Akşam ezanı gönüllere huzur getirsin", HI),
        (4, "Sahurunuz bereketli, gününüz kolay geçsin", HS),
        (5, "İlk lokma hurma, ilk dua şükür olsun", HI),
        (6, "Teravihlerde gönüller bir olsun", RS),
        (7, "Sıcak bir çorba, sıcak bir dua; afiyet olsun", HI),
        (8, "Güllaç tatlılığında bir Ramazan dilerim", HR),
        (9, "Mukabelelerle gönüller nurlansın", RS),
        (10, "Rahmet suyu gibi serinleten bir ay olsun", HG),
        (11, "Sofranıza bereket, evinize huzur dolsun", HI),
        (12, "Pidesi sıcak, sofrası bereketli bir Ramazan", HR),
        (13, "Tatlı sofralar, tatlı sohbetler dilerim", HI),
        (14, "Tesbih taneleri gibi dualarınız çoğalsın", RS),
        (15, "Davul sesiyle uyanılan sahurlar bereketli olsun", HS),
        (16, "Kur’an ayının nuru evinizi aydınlatsın", HG),
        (17, "Ramazan gecelerinin ışığı yolunuzu aydınlatsın", HR),
        (19, "Sahur sofranız bereketli, niyetiniz halis olsun", HS),
        (20, "Sofradaki dualarımız kabul olsun", HI),
        (21, "Teravih yolunda adımlarınız bereketli olsun", RS),
        (22, "Şerbet gibi serin, hoşaf gibi tatlı bir iftar", HI),
        (23, "Paylaşılan sofralar gönülleri birleştirsin", HR),
        (24, "Emekle kurulan sofralar bereketlensin", HI),
        (25, "Ellerinize sağlık, oruçlarınız kabul olsun", RS),
        (26, "Sahurda kurulan sofralar sevgiyle dolsun", HS),
        (27, "Kalabalık sofralar, bereketli iftarlar dilerim", HI),
        (28, "Ailecek açılan oruçlar şifa olsun", HR),
        (29, "Bereketli bir sahur, kolay bir oruç dilerim", HS),
        (30, "Ezanı bekleyen sofralar huzurla dolsun", HI),
        (31, "Küçük ellerin hazırladığı sofralar bereketli olsun", HR),
        (32, "Emeği büyük, bereketi bol bir Ramazan", HG),
        (33, "Pide kokulu akşamlar mübarek olsun", RS),
        (34, "Saat sahuru gösterdi; bereketli olsun", HS),
        (35, "Şehrin üstünde huzurlu bir iftar dilerim", HI),
        (36, "Köy sofrası gibi sade ve bereketli bir Ramazan", HR),
        (37, "Her lokması bereket olsun", HG),
        (41, "Işıklar altında kurulan sofralar bereketlensin", HI),
        (43, "Gün batarken açılan oruçlar kabul olsun", RS),
        (45, "Mahallemizin sofrasına bereket dolsun", HR),
        (47, "Sahurunuz bal gibi tatlı olsun", HS),
        (48, "İftardan sonra tatlı bir sohbet dilerim", HR),
        (49, "Hoşaf tasında serinlik, gönülde huzur olsun", HI),
        (50, "Verdiğiniz sadakalar kabul olsun", RS),
        (51, "Lale gibi zarif, hurma gibi tatlı bir ay olsun", HG),
        (52, "İftar vakti gönüllere huzur dolsun", HI),
        (53, "Sahur sofranızdan bereket eksik olmasın", HS),
        (54, "Gül kokulu, bereketli bir Ramazan dilerim", HG),
        (55, "Misafirli sofralar rahmete vesile olsun", HI),
        (56, "Sininin etrafında buluşan gönüller bir olsun", HR),
        (57, "Sahura kalkan her göze huzur dolsun", HS),
        (58, "Gül şerbeti gibi ferah bir iftar dilerim", HI),
        (59, "Çayınız demli, sohbetiniz bereketli olsun", HR),
        (60, "İftarın ilk kaşığı şifa olsun", HI),
        (61, "Oruçla gelen sabrın tatlı bir mükâfatı olsun", RS),
        (62, "Bu mübarek ayda rızkınız bol olsun", HG),
        (63, "Kandil ışığı gibi kalbiniz aydınlansın", HR),
    ],
}
assert sorted(i for v in CARDS.values() for i, _, _ in v) == sorted(set(range(64)) - SKIP)
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
