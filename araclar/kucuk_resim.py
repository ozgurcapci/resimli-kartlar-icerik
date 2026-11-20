"""Her görselli kart için listede kullanılan küçük kopyayı üretir ve kartın `thumb` alanını yazar.

cards/<kategori>/<ad>.jpg  →  cards/thumbs/<kategori>/<ad>.jpg  (480 px en, 9:16)
Eksik küçük kopyaları üretir, artık hiçbir kartın kullanmadığı küçük kopyaları siler; tekrar çalıştırmak güvenli.
Görsel değişince yeni ad (_v2) aldığı için küçük kopyası da yeni adla üretilir.
Kullanım: python araclar/kucuk_resim.py   (kart_ekle_ornek.py ve stil_ve_yer.py'den sonra)
"""
import io, json, re
from pathlib import Path
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
CARDS = REPO / "cards"
THUMBS = CARDS / "thumbs"
W = 480


def make(src, dst):
    img = Image.open(src).convert("RGB")
    img = img.resize((W, round(img.height * W / img.width)), Image.LANCZOS)
    b = io.BytesIO(); img.save(b, "JPEG", quality=80, optimize=True, progressive=True)
    dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(b.getvalue())
    return b.tell()


def main():
    path = REPO / "templates.json"
    out, used, made, total = [], set(), 0, 0
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r'^(\s*)(\{.*\})(,?)\s*$', line)
        if m:
            card = json.loads(m.group(2))
            img = card.get("image")
            if img and not img.startswith("assets/") and "://" not in img:
                rel = f"thumbs/{img}"; used.add(rel)
                dst = CARDS / rel
                if not dst.exists():
                    total += make(CARDS / img, dst); made += 1
                # `thumb` alanı `image`'ın hemen ardından
                card.pop("thumb", None)
                card = {k2: v2 for k, v in card.items() for k2, v2 in ([(k, v), ("thumb", rel)] if k == "image" else [(k, v)])}
                line = m.group(1) + json.dumps(card, ensure_ascii=False) + m.group(3)
        out.append(line)
    txt = "\n".join(out); json.loads(txt)
    path.write_text(txt, encoding="utf-8", newline="\n")
    removed = 0
    for f in THUMBS.rglob("*.jpg"):
        if f.relative_to(CARDS).as_posix() not in used: f.unlink(); removed += 1
    print(f"küçük kopya: {made} yeni ({total // 1024} KB), {removed} silindi, toplam {len(used)}")


main()
