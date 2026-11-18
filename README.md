# resimli-kartlar-icerik

Resimli Cuma & Bayram Kartları uygulamasının kart listesi ve kart görselleri. Uygulama bu depoyu herkese açık adreslerden okur, bu yüzden depo **public** kalmalı. Buraya kod ya da gizli bilgi konmaz.

## Yapı

```
templates.json        kart listesi
cards/<kategori>/     kart görselleri (kategori anahtarıyla klasör: cuma, berat, ramazan_bayrami …)
```

## Uygulama nereden okuyor

- Liste: `https://raw.githubusercontent.com/ozgurcapci/resimli-kartlar-icerik/main/templates.json`
- Görseller: `https://cdn.jsdelivr.net/gh/ozgurcapci/resimli-kartlar-icerik@main/cards/` + kartın `image` değeri

Uygulama listeyi en fazla 6 saatte bir yeniler. Yeni hali bir sonraki açılışta görünür.

## Kart satırı

```json
{ "id": "cuma_05", "category": "cuma", "message": "Hayırlı Cumalar", "image": "cuma/cuma_05.jpg", "textColor": "#FFFFFF", "accent": "#C9A45C", "premium": false }
```

- `id` benzersiz olmalı ve **hiç değişmemeli**. Kullanıcıların favorileri bu kimlikle tutuluyor.
- `category`: `cuma`, `ramazan_bayrami`, `kurban_bayrami`, `arefe`, `regaib`, `mirac`, `berat`, `kadir`, `mevlid`, `sabah`, `gece`, `uc_aylar`, `ramazan`, `hicri_yilbasi`, `asure`. Uygulamanın tanımadığı kategori atlanır.
- `image`: `cards/` altındaki göreli yol. Görsel 9:16 (1080×1920) JPG olmalı, 250–350 KB civarında; gönderi boyutunda (4:5) ortadan kırpılır. Görselin üstünde yazı olmamalı, mesajı uygulama yazar.
- `textColor` görsele göre seçilir. `gradient` görselli kartlarda gerekmez, görsel yüklenirken görünür.
- `premium: true` olan kart yalnız premium üyelere açık.

## Kurallar

- **Görseli aynı adla değiştirmeyin.** jsDelivr eski görseli 12 saate kadar gösterebilir. Yeni görsele yeni ad verin (`cuma_05b.jpg`) ve `image` değerini güncelleyin.
- Her kategoride en az bir kart kalmalı. Uzak liste gelince uygulamadaki gömülü listenin yerini tamamen alıyor.
- JSON bozuksa uygulama listeyi yok sayar ve eskisiyle devam eder. Yine de push etmeden önce geçerliliğini kontrol edin.
