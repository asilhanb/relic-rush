Relic Rush
A top-down roguelike. The hero, the slime, and the bat each move one grid cell
at a time. Movement between cells is smooth and animated. Every character has
a walk cycle and an idle cycle.

Libraries
- Pygame Zero (pgzero)
- math
- random
- Only the Rect class from pygame (from pygame import Rect)

The game itself uses no other libraries.

How to run
1. Python 3 must be installed.
2. Install Pygame Zero:
   pip install pgzero
3. In this folder, run either command:
   python game.py
   pgzrun game.py

How to play
- The main menu has three clickable buttons:
  Oyunu Başlat (Start Game), Müziği ve Sesleri Aç/Kapat (Sound On/Off), Çıkış (Exit).
- The sound button turns both the music and the sound effects on or off.
- Arrow keys or WASD move the hero one tile.
- The green corridor belongs to the slime. The purple room belongs to the bat.
  Each enemy patrols only inside its own area.
- Coins are optional rewards. The exit gate stays locked until the relic is collected.
- Win: pick up the relic, then step on the exit tile.
- Lose: touch the slime or the bat.
- After a win or a loss, Tekrar Oyna (Play Again) and Ana Menü (Main Menu) appear.

Folders
- game.py is the whole game.
- images/ holds the sprite frames and floor tiles.
- sounds/ holds the sound effects (wav).
- music/theme.mp3 is the looping background music.

------------------------------------------------------------

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
