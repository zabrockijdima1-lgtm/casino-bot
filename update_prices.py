import requests
import json
import time
from datetime import datetime

PRICES_FILE    = "prices.json"
MARKET_API_URL = "https://api.tgmrkt.io/api/v1"

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

def get_floor_price(collection_name):
    try:
        resp = requests.post(
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
            timeout=10,
        )
        if resp.status_code == 429:
            return "RATE_LIMITED"
        if resp.status_code != 200:
            return None
        gifts = resp.json().get("gifts", [])
        if not gifts:
            return None
        price = gifts[0].get("salePrice")
        if price is not None:
            return round(price / 1_000_000_000, 2)
        return None
    except:
        return None

def update_prices():
    print(f"\n{'='*60}")
    print(f"  Оновлення цін NFT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Джерело: tgmrkt.io API")
    print(f"{'='*60}\n")

    # Завантажуємо існуючі ціни як fallback
    try:
        with open(PRICES_FILE, "r") as f:
            existing = json.load(f).get("prices", {})
    except:
        existing = {}

    prices = dict(existing)
    success = 0
    fallback = 0
    rate_limited = 0
    seen_collections = {}  # кешуємо вже запитані колекції

    for nft_id, collection_name in NFT_COLLECTION_MAP.items():
        label = nft_id.ljust(22)

        if collection_name is None:
            print(f"  [ ]  {label} → немає на tgmrkt")
            fallback += 1
            continue

        # Якщо вже запитували цю колекцію — беремо з кешу
        if collection_name in seen_collections:
            floor = seen_collections[collection_name]
            if floor is not None:
                prices[nft_id] = floor
                print(f"  [=]  {label} {floor:.2f} TON (кеш)")
                success += 1
            continue

        print(f"  ...  {label}", end="", flush=True)
        floor = get_floor_price(collection_name)

        if floor == "RATE_LIMITED":
            print(f"\r  [429] {label} rate limit — чекаємо 5 сек...")
            time.sleep(5)
            floor = get_floor_price(collection_name)

        seen_collections[collection_name] = floor if floor != "RATE_LIMITED" else None

        if floor and floor != "RATE_LIMITED":
            prices[nft_id] = floor
            print(f"\r  [OK] {label} {floor:.2f} TON")
            success += 1
        else:
            print(f"\r  [!!] {label} fallback {existing.get(nft_id, '?')} TON")
            fallback += 1

        time.sleep(1.5)

    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump({"updatedAt": datetime.utcnow().isoformat()+"Z", "prices": prices}, f, indent=2)

    print(f"\n{'='*60}")
    print(f"  SUCCESS      : {success}")
    print(f"  FALLBACK     : {fallback}")
    print(f"  RATE LIMITED : {rate_limited}")
    print(f"  SAVED TO     : {PRICES_FILE}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    import sys
    if "--loop" in sys.argv:
        idx = sys.argv.index("--loop")
        interval = int(sys.argv[idx+1]) if len(sys.argv) > idx+1 else 60
        print(f"Авто-оновлення кожні {interval} хв.")
        while True:
            try: update_prices()
            except Exception as e: print(f"Помилка: {e}")
            time.sleep(interval * 60)
    else:
        update_prices()
