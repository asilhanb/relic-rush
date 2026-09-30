Relic Rush
Üstten bakışlı bir roguelike. Kahraman, slime ve yarasa ızgara üzerinde birer
hücre ilerler. Hücreler arası hareket akıcı ve animasyonludur. Her karakterin
yürüme döngüsü ve bekleme döngüsü vardır.

Kullanılan kütüphaneler
- Pygame Zero (pgzero)
- math
- random
- pygame içinden yalnızca Rect sınıfı (from pygame import Rect)

Oyunun kendisi başka bir kütüphane kullanmaz.

Nasıl çalıştırılır
1. Python 3 kurulu olmalı.
2. Pygame Zero yükleyin:
   pip install pgzero
3. Bu klasörde şu komutlardan birini çalıştırın:
   python game.py
   pgzrun game.py

Nasıl oynanır
- Ana menüde üç tıklanabilir düğme vardır:
  Oyunu Başlat, Müziği ve Sesleri Aç/Kapat, Çıkış.
- Ses düğmesi hem müziği hem de efektleri açar veya kapatır.
- Ok tuşları veya WASD, kahramanı bir kare ilerletir.
- Yeşil koridor slime'a aittir. Mor oda yarasaya aittir.
  Her düşman yalnızca kendi alanında devriye gezer.
- Altınlar isteğe bağlı ödüldür. Çıkış kapısı yadigâr alınmadan açılmaz.
- Kazanma: yadigârı alın ve çıkış karesine basın.
- Kaybetme: slime veya yarasaya dokunun.
- Kazanınca veya kaybedince Tekrar Oyna ve Ana Menü düğmeleri çıkar.

Klasörler
- game.py oyunun tamamıdır.
- images/ kare kare sprite ve zemin görsellerini tutar.
- sounds/ efektleri tutar (wav).
- music/theme.mp3 döngü halinde çalan arka plan müziğidir.
