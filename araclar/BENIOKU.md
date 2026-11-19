# Araçlar

Kart eklerken sırayla:

1. `kart_ekle_ornek.py`: İndirilenler'deki `*_2K.jpg` görselleri 9:16 1080×1920'ye alta hizalı kırpar, 350 KB'ı aşmayacak JPEG olarak `cards/<kategori>/` içine yazar, yazı rengini üst banda göre seçer ve kartları `templates.json`'a ekler. `CARDS` listesi (görsel sırası, mesaj, selam) ve eklenecek yer her seferinde düzenlenir.
2. `stil_ve_yer.py --write`: her karta `style` (klasik / kitabe / selamOnde, kategori içinde sırayla) ve görselin boş üst alanına göre `textTop` yazar. Uygulamadaki `CardStyle` / `CardTypography` değerlerini taklit eder; uygulamada değişirse burada da değiştirin. `onizleme/` içine kontrol sayfaları çizer. Elle düzeltme: `OVERRIDE` (stil) ve `TOP_OVERRIDE` (yer).

Yazı tipleri uygulama deposundaki `assets/fonts` klasöründen okunur (`FONTS` yolu).
