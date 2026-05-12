"""
update_prices.py — підтягування floor-цін NFT з tgmrkt.io у prices.json.

Запуск:
  python update_prices.py            # одноразово
  python update_prices.py --loop     # кожну годину (60 хв)
  python update_prices.py --loop 30  # кожні 30 хв

Оптимізації:
  • Паралельні запити (ThreadPoolExecutor) — замість 1.5с * N послідовно, ~10–15с разом
  • Запитуємо лише УНІКАЛЬНІ назви колекцій, потім розкладаємо результат на всі id
  • Експоненційна затримка при 429 Rate Limited
  • Атомарний запис prices.json (через temp + os.replace) — HTML не зловить пів-файлу
  • Зберігаємо попередні ціни як fallback, якщо API падає
"""

import requests
import json
import time
import os
import tempfile
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

PRICES_FILE    = "prices.json"
MARKET_API_URL = "https://api.tgmrkt.io/api/v1"

# Скільки одночасних запитів. tgmrkt — невеликий API, тримай помірно.
MAX_WORKERS    = 6
# Невелика пауза при відправці запитів у пул — щоб не б'ємо всі одночасно
REQ_DELAY      = 0.25
# Таймаут одного запиту
HTTP_TIMEOUT   = 10

HEADERS = {
    "Authorization": "6719edf2-b2a9-49ca-bdac-add1fd7ba128",
    "Referer": "https://cdn.tgmrkt.io/",
    "Content-Type": "application/json",
}

# id з бота → назва колекції на tgmrkt
NFT_COLLECTION_MAP = {
    # CASES (PINK)
    "snakebox":              "Snake Box",
    "candycane":             "Candy Cane",
    "jesterhat":             "Jester Hat",
    "lolpop":                "Lol Pop",
    "spicedwine":            "Spiced Wine",
    "cookieheart":           "Cookie Heart",
    "lolpopsweetheart":      None,
    "deskcalendar":          "Desk Calendar",
    "joyfullbundle":         "Joyful Bundle",
    "bunnymuffin":           "Bunny Muffin",
    "berrybox":              "Berry Box",
    "valentinebox":          "Valentine Box",
    "joyfullbundleteddybears": None,
    "lovecandle":            "Love Candle",
    "sakuraflower":          "Sakura Flower",
    "lovepotion":            "Love Potion",
    "starnotepad":           "Star Notepad",
    "eternalrose":           "Eternal Rose",
    "toybear":               "Toy Bear",
    "sharptongue":           "Sharp Tongue",
    "nekohelmet":            "Neko Helmet",
    "nailbracelet":          "Nail Bracelet",
    "astralshard":           "Astral Shard",
    # NFT_CATALOG (Rocket)
    "artisanbrick":          "Artisan Brick",
    "astralshards":          "Astral Shard",
    "bdaycandle":            "B-Day Candle",
    "bigyear":               "Big Year",
    "bowtie":                "Bow Tie",
    "chillflame":            "Chill Flame",
    "clovelpin":             "Clover Pin",
    "crystalball":           "Crystal Ball",
    "cupidcharm":            "Cupid Charm",
    "diamondring":           "Diamond Ring",
    "durovcap":              None,
    "easteregg":             "Easter Egg",
    "electricskull":         "Electric Skull",
    "eternalcandle":         "Eternal Candle",
    "evileye":               "Evil Eye",
    "flyingbroom":           "Flying Broom",
    "gemsignet":             "Gem Signet",
    "genielamp":             "Genie Lamp",
    "gingercookie":          "Ginger Cookie",
    "hangingstar":           "Hanging Star",
    "happybrownie":          "Happy Brownie",
    "heartlocket":           "Heart Locket",
    "heroichelmet":          "Heroic Helmet",
    "hexhot":                "Hex Pot",
    "holidaydrink":          "Holiday Drink",
    "homemadecake":          "Homemade Cake",
    "hypnolollipop":         "Hypno Lollipop",
    "icecream":              "Ice Cream",
    "inputkey":              "Input Key",
    "instantramen":          "Instant Ramen",
    "ionicdrier":            "Ionic Dryer",
    "iongem":                "Ion Gem",
    "jackinthebox":          "Jack-in-the-Box",
    "jellybunny":            "Jelly Bunny",
    "jinglebells":           "Jingle Bells",
    "jollychimp":            "Jolly Chimp",
    "joyfulbundle":          "Joyful Bundle",
    "joyfulbundle2":         "Joyful Bundle",
    "kissedfrog":            "Kissed Frog",
    "lightsword":            "Light Sword",
    "lolpop2":               "Lol Pop",
    "lootbag":               "Loot Bag",
    "lowrider":              "Low Rider",
    "lunarsnake":            "Lunar Snake",
    "lunarsnak":             "Lunar Snake",
    "lushbouquet":           "Lush Bouquet",
    "madpumpkin":            "Mad Pumpkin",
    "magicpotion":           "Magic Potion",
    "mightyarm":             "Mighty Arm",
    "minioscars":            "Mini Oscar",
    "minioscal":             "Mini Oscar",
    "moodpack":              "Mood Pack",
    "moonpendant":           "Moon Pendant",
    "moonpencil":            "Moon Pendant",
    "moussecake":            "Mousse Cake",
    "oillamp":               "Oil Lamp",
    "partysparkler":         "Party Sparkler",
    "partysparker":          "Party Sparkler",
    "perfumebottle":         "Perfume Bottle",
    "petsnake":              "Pet Snake",
    "plushpepe":             "Plush Pepe",
    "poolfloat":             "Pool Float",
    "preciouspeach":         "Precious Peach",
    "recordplayer":          "Record Player",
    "restlessjar":           "Restless Jar",
    "santahat":              "Santa Hat",
    "scaredcat":             "Scared Cat",
    "signetring":            "Signet Ring",
    "skullflower":           "Skull Flower",
    "skystiletto":           "Sky Stilettos",
    "skystillettos":         "Sky Stilettos",
    "sleighbell":            "Sleigh Bell",
    "snoopcigar":            "Snoop Cigar",
    "snoopdog":              "Snoop Dogg",
    "snowglobe":             "Snow Globe",
    "snowmittens":           "Snow Mittens",
    "springbasket":          "Spring Basket",
    "spyagaric":             "Spy Agaric",
    "stellarrocket":         "Stellar Rocket",
    "swagbag":               "Swag Bag",
    "swisswatch":            "Swiss Watch",
    "tamagadget":            "Tama Gadget",
    "timelessbook":          "Timeless Book",
    "tophat":                "Top Hat",
    "trappedheart":          "Trapped Heart",
    "vicecream":             "Vice Cream",
    "vintagecigar":          "Vintage Cigar",
    "voodoodoll":            "Voodoo Doll",
    "westsideside":          "Westside Sign",
    "whipcupcake":           "Whip Cupcake",
    "winterwreath":          "Winter Wreath",
    "witchhat":              "Witch Hat",
    "xmasstocking":          "Xmas Stocking",
    "bondedring":            "Bonded Ring",
    "freshsocks":            "Fresh Socks",
    "faithamulet":           "Faith Amulet",
    "cloverpin":             "Clover Pin",
    "artisanbread":          "Artisan Brick",
    "happybroom":            "Happy Brownie",
}


def _fetch_floor(collection_name, session, attempt=0):
    """Один запит на одну колекцію. Повертає float або None.
    На 429 робить експоненційну затримку (макс 2 retry).
    """
    try:
        resp = session.post(
            f"{MARKET_API_URL}/gifts/saling",
            headers=HEADERS,
            json={
                "collectionNames": [collection_name],
                "modelNames": [], "backdropNames": [], "symbolNames": [],
                "ordering": "Price", "lowToHigh": True,
                "maxPrice": None, "minPrice": None, "mintable": None,
                "number": None, "count": 1, "cursor": "", "query": None,
                "promotedFirst": False,
            },
            timeout=HTTP_TIMEOUT,
        )
        if resp.status_code == 429:
            if attempt < 2:
                time.sleep(2 ** attempt + 1)  # 2с, 3с
                return _fetch_floor(collection_name, session, attempt + 1)
            return None
        if resp.status_code != 200:
            return None
        gifts = resp.json().get("gifts", [])
        if not gifts:
            return None
        price = gifts[0].get("salePrice")
        if price is None:
            return None
        return round(price / 1_000_000_000, 2)
    except Exception:
        return None


def _save_atomic(path, payload):
    """Атомарний запис: пишемо в temp у тій же папці, потім os.replace.
    Це гарантує, що HTML ніколи не прочитає недописаний/порожній файл."""
    dir_ = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".prices_", suffix=".tmp", dir=dir_)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except: pass
        raise


def update_prices():
    started = time.time()
    print(f"\n{'='*60}")
    print(f"  Оновлення цін NFT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Джерело: tgmrkt.io API (паралельно, workers={MAX_WORKERS})")
    print(f"{'='*60}\n")

    # Завантажуємо існуючі ціни як fallback
    try:
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            existing = json.load(f).get("prices", {})
    except Exception:
        existing = {}

    prices = dict(existing)

    # Беремо тільки УНІКАЛЬНІ назви колекцій (None → пропуск)
    unique_collections = sorted({c for c in NFT_COLLECTION_MAP.values() if c})
    print(f"  Унікальних колекцій до запиту: {len(unique_collections)}\n")

    # Паралельні запити
    collection_floors = {}
    with requests.Session() as sess, ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {}
        for coll in unique_collections:
            futures[pool.submit(_fetch_floor, coll, sess)] = coll
            time.sleep(REQ_DELAY)  # ramping — не б'ємо всі одразу

        for fut in as_completed(futures):
            coll = futures[fut]
            try:
                floor = fut.result()
            except Exception:
                floor = None
            collection_floors[coll] = floor
            tag = "OK" if floor else "--"
            val = f"{floor:.2f} TON" if floor else "немає"
            print(f"  [{tag}] {coll:<24} {val}")

    # Розкладаємо результати на всі NFT-id
    success = 0
    fallback = 0
    none_count = 0
    for nft_id, coll in NFT_COLLECTION_MAP.items():
        if coll is None:
            none_count += 1
            continue
        floor = collection_floors.get(coll)
        if floor is not None:
            prices[nft_id] = floor
            success += 1
        else:
            # лишаємо попереднє значення з prices.json як fallback
            fallback += 1

    payload = {
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "prices": prices,
    }
    _save_atomic(PRICES_FILE, payload)

    elapsed = time.time() - started
    print(f"\n{'='*60}")
    print(f"  SUCCESS      : {success}")
    print(f"  FALLBACK     : {fallback}")
    print(f"  NO MAPPING   : {none_count}")
    print(f"  TIME         : {elapsed:.1f}s")
    print(f"  SAVED TO     : {PRICES_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if "--loop" in sys.argv:
        idx = sys.argv.index("--loop")
        # дефолт — 60 хв (одна година)
        try:
            interval = int(sys.argv[idx + 1]) if len(sys.argv) > idx + 1 else 60
        except ValueError:
            interval = 60
        print(f"Авто-оновлення кожні {interval} хв.")
        while True:
            try:
                update_prices()
            except Exception as e:
                print(f"Помилка: {e}")
            time.sleep(interval * 60)
    else:
        update_prices()
