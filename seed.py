"""
Скрипт для разового заполнения таблицы nft_catalog всеми подарками.

ПОМЕТКА ДЕНИСУ: запускать из корня backend-deploy командой:
    python seed.py

Скрипт безопасно перезапускать несколько раз — перед вставкой проверяет,
есть ли уже подарок с таким названием, и не создаёт дубликат, а просто
обновляет ему картинку/цену, если ты их поменял.
"""

from app.db.session import SessionLocal
from app.models.nft import NftCatalog

# (название, имя файла картинки, цена в монетах)
GIFTS = [
    ("Chill Flame", "Chill-Flame-400.png", 400),
    ("Lunar Snake", "Lunar-Snake-400.png", 400),
    ("Xmas Stocking", "Xmas-Stocking-400.png", 400),
    ("Big Year", "Big-Year-425.png", 425),
    ("Snake Box", "Snake-Box-425.png", 425),
    ("Candy Cane", "Candy-Cane-445.png", 445),
    ("Santa Hat", "Santa-Hat-450.png", 450),
    ("Vice Cream", "Vice-Cream-450.png", 450),
    ("Whip Cupcake", "Whip-Cupcake-450.png", 450),
    ("Winter Wreath", "Winter-Wreath-450.png", 450),
    ("Lol Pop", "Lol-Pop-480.png", 480),
    ("Jack in the Box", "Jack-in-the-Box-525.png", 525),
    ("Hypno Lollipop", "Hypno-Lollipop-545.png", 545),
    ("Fresh Socks", "Fresh-Socks-550.png", 550),
    ("Ginger Cookie", "Ginger-Cookie-550.png", 550),
    ("Happy Brownie", "Happy-Brownie-550.png", 550),
    ("Hex Pot", "Hex-Pot-550.png", 550),
    ("Money Pot", "Money-Pot-550.png", 550),
    ("Mood Pack", "Mood-Pack-550.png", 550),
    ("Party Sparkler", "Party-Sparkler-550.png", 550),
    ("Snow Mittens", "Snow-Mittens-550.png", 550),
    ("Holiday Drink", "Holiday-Drink-575.png", 575),
    ("Star Notepad", "Star-Notepad-575.png", 575),
    ("Victory Medal", "Victory-Medal-575.png", 575),
    ("Cookie Heart", "Cookie-Heart-600.png", 600),
    ("Liberty Figure", "Liberty-Figure-600.png", 600),
    ("Mousse Cake", "Mousse-Cake-600.png", 600),
    ("Pretty Posy", "Pretty-Posy-600.png", 600),
    ("Snow Globe", "Snow-Globe-600.png", 600),
    ("Spiced Wine", "Spiced-Wine-600.png", 600),
    ("Stellar Rocket", "Stellar-Rocket-600.png", 600),
    ("Timeless Book", "Timeless-Book-600.png", 600),
    ("Clover Pin", "Clover-Pin-650.png", 650),
    ("Faith Amulet", "Faith-Amulet-650.png", 650),
    ("Spring Basket", "Spring-Basket-650.png", 650),
    ("Witch Hat", "Witch-Hat-650.png", 650),
    ("B-day Candle", "B-day-Candle-675.png", 675),
    ("Bow Tie", "Bow-Tie-675.png", 675),
    ("Desk Calendar", "Desk-Calendar-700.png", 700),
    ("Homemade Cake", "Homemade-Cake-700.png", 700),
    ("Restless Jar", "Restless-Jar-700.png", 700),
    ("Spy Agaric", "Spy-Agaric-700.png", 700),
    ("Swag Bag", "Swag-Bag-700.png", 700),
    ("Eternal Candle", "Eternal-Candle-710.png", 710),
    ("Moon Pendant", "Moon-Pendant-767.png", 767),
    ("Lush Bouquet", "Lush-Bouquet-775.png", 775),
    ("Bunny Muffin", "Bunny-Muffin-800.png", 800),
    ("Evil Eye", "Evil-Eye-800.png", 800),
    ("Input Key", "Input-Key-800.png", 800),
    ("Jelly Bunny", "Jelly-Bunny-800.png", 800),
    ("Jingle Bells", "Jingle-Bells-800.png", 800),
    ("Jolly Chimp", "Jolly-Chimp-800.png", 800),
    ("Joyful Bundle", "Joyful-Bundle-800.png", 800),
    ("Light Sword", "Light-Sword-800.png", 800),
    ("Sleigh Bell", "Sleigh-Bell-800.png", 800),
    ("Surge Board", "Surge-Board-800.png", 800),
    ("Hanging Star", "Hanging-Star-900.png", 900),
    ("Berry Box", "Berry-Box-900.png", 900),
    ("Sakura Flower", "Sakura-Flower-900.png", 900),
    ("Love Candle", "Love-Candle-1000.png", 1000),
    ("Top Hat", "Top-Hat-1000.png", 1000),
    ("Valentine Box", "Valentine-Box-1100.png", 1100),
    ("Crystal Ball", "Crystal-Ball-1250.png", 1250),
    ("Flying Broom", "Flying-Broom-1200.png", 1200),
    ("Mad Pumpkin", "Mad-Pumpkin-1200.png", 1200),
    ("Skull Flower", "Skull-Flower-1200.png", 1200),
    ("Snoop Cigar", "Snoop-Cigar-1325.png", 1325),
    ("Trapped Heart", "Trapped-Heart-1350.png", 1350),
    ("Record Player", "Record-Player-1400.png", 1400),
    ("UFC Strike", "UFC-Strike-1450.png", 1450),
    ("Love Potion", "Love-Potion-1500.png", 1500),
    ("Ionic Dryer", "Ionic-Dryer-1500.png", 1500),
    ("Sky Stilettos", "Sky-Stilettos-2052.png", 2052),
    ("Bling Binky", "Bling-Binky-2500.png", 2500),
    ("Eternal Rose", "Eternal-Rose-2500.png", 2500),
    ("Khabib's Papakha", "Khabib`s-Papakha-2550.png", 2550),
    ("Rare Bird", "Rare-Bird-2600.png", 2600),
    ("Electric Skull", "Electric-Skull-2700.png", 2700),
    ("Diamond Ring", "Diamond-Ring-3350.png", 3350),
    ("Signet Ring", "Signet-Ring-3450.png", 3450),
    ("Genie Lamp", "Genie-Lamp-3800.png", 3800),
    ("Neko Helmet", "Neko-Helmet-3700.png", 3700),
    ("Vintage Cigar", "Vintage-Cigar-3650.png", 3650),
    ("Voodoo Doll", "Voodoo-Doll-3600.png", 3600),
    ("Toy Bear", "Toy-Bear-4000.png", 4000),
    ("Bonded Ring", "Bonded-Ring-4500.png", 4500),
    ("Kissed Frog", "Kissed-Frog-4500.png", 4500),
    ("Sharp Tongue", "Sharp-Tongue-4600.png", 4600),
    ("Low Rider", "Low-Rider-5200.png", 5200),
    ("Swiss Watch", "Swiss-Watch-5150.png", 5150),
    ("Artisan Brick", "Artisan-Brick-6300.png", 6300),
    ("Magic Potion", "Magic-Potion-6000.png", 6000),
    ("Gem Signet", "Gem-Signet-7100.png", 7100),
    ("Ion Gem", "Ion-Gem-7600.png", 7600),
    ("Mini Oscar", "Mini-Oscar-8000.png", 8000),
    ("Nail Bracelet", "Nail-Bracelet-10500.png", 10500),
    ("Westside Sign", "Westside-Sign-11000.png", 11000),
    ("Loot Bag", "Loot-Bag-13500.png", 13500),
    ("Mighty Arm", "Mighty-Arm-14600.png", 14600),
    ("Astral Shard", "Astral-Shard-15200.png", 15200),
    ("Scared Cat", "Scared-Cat-21000.png", 21000),
    ("Heroic Helmet", "Heroic-Helmet-23000.png", 23000),
    ("Precious Peach", "Precious-Peach-33500.png", 33500),
    ("Durov's Cap", "Durov`s-Cap-49000.png", 49000),
    ("Heart Locket", "Heart-Locket-150000.png", 150000),
    ("Plush Pepe", "Plush-Pepe-600000.png", 600000),
    ("Easter Egg", "Easter-Egg-500.png", 500),
    ("Ice Cream", "Ice-Cream-500.png", 500),
    ("Instant Ramen", "Instant-Ramen-500.png", 500),
    ("Jester Hat", "Jester-Hat-500.png", 500),
    ("Pet Snake", "Pet-Snake-500.png", 500),
    ("Pool Float", "Pool-Float-500.png", 500),
    ("Tama Gadget", "Tama-Gadget-500.png", 500),
    ("Cupid Charm", "Cupid-Charm-2200.png", 2200),
    ("Perfume Bottle", "Perfume-Bottle-6800.png", 6800),
    ("Snoop Dogg", "Snoop-Dogg-750.png", 750),
]


def seed():
    db = SessionLocal()
    created = 0
    updated = 0
    try:
        for name, filename, price in GIFTS:
            image_url = f"/assets/{filename}"
            existing = db.query(NftCatalog).filter(NftCatalog.name == name).first()
            if existing:
                existing.image_url = image_url
                existing.value = price
                updated += 1
            else:
                db.add(NftCatalog(name=name, image_url=image_url, value=price))
                created += 1
        db.commit()
        print(f"Готово. Добавлено новых: {created}, обновлено существующих: {updated}")
        print(f"Всего в GIFTS: {len(GIFTS)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
