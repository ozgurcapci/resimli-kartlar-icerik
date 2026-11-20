# Araçlar

Kart eklerken sırayla:

1. `kart_ekle_ornek.py`: İndirilenler'deki `*_2K.jpg` görselleri 9:16 1080×1920'ye alta hizalı kırpar, 350 KB'ı aşmayacak JPEG olarak `cards/<kategori>/` içine yazar, yazı rengini üst banda göre seçer ve kartları `templates.json`'a ekler. `CARDS` listesi (görsel sırası, mesaj, selam) ve eklenecek yer her seferinde düzenlenir.
2. `stil_ve_yer.py --write`: her karta `style` (klasik / kitabe / selamOnde, kategori içinde sırayla) ve görselin boş üst alanına göre `textTop` yazar. Uygulamadaki `CardStyle` / `CardTypography` değerlerini taklit eder; uygulamada değişirse burada da değiştirin. `onizleme/` içine kontrol sayfaları çizer. Yazı gönderide konuya biniyorsa görseli aşağı kaydıran `postAlign` (1 = alta hizalı) da yazar. Elle düzeltme: `OVERRIDE` (stil), `TOP_OVERRIDE` (yer), `ALIGN_OVERRIDE` (kaydırma).
3. `kucuk_resim.py`: listede kullanılan küçük kopyaları (`cards/thumbs/`, 480 px en) üretir ve kartlara `thumb` alanını yazar; kullanılmayanları siler. Tekrar çalıştırmak güvenlidir.

Görsel değişince yeni ad verin (`kadir_13_v2.jpg`) ve eskisini silin: görseller telefonlarda bir yıl önbellekte kalır (`_headers`).

Yazı tipleri uygulama deposundaki `assets/fonts` klasöründen okunur (`FONTS` yolu).
