import requests
import json
import time
import os
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
MARKET_API_URL = "https://api.tgmrkt.io/api/v1"
PRICES_FILE    = "prices.json"   # куди зберігати результат
TOKEN_FILE     = "mrkt_token.txt"

# ─── NFT маппінг: id з CASES → точна назва колекції на tgmrkt ────────────────
# Якщо назва колекції відрізняється — просто виправ праву частину
NFT_COLLECTION_MAP = {
    "snakebox":              "Snake Box",
    "candycane":             "Candy Cane",
    "jesterhat":             "Jester Hat",
    "lolpop":                "Lol Pop",
    "spicedwine":            "Spiced Wine",
    "cookieheart":           "Cookie Heart",
    "lolpopsweetheart":      "Lol Pop Sweetheart",
    "deskcalendar":          "Desk Calendar",
    "joyfullbundle":         "Joyful Bundle",
    "bunnymuffin":           "Bunny Muffin",
    "berrybox":              "Berry Box",
    "valentinebox":          "Valentine Box",
    "joyfullbundleteddybears": "Joyful Bundle Teddy Bears",
    "lovecandle":            "Love Candle",
    "sakuraflower":          "Sakura Flower",
    "lovepotion":            "Love Potion",
    "starnotepad":           "Star Notepad True Love",
    "eternalrose":           "Eternal Rose",
    "toybear":               "Toy Bear",
    "sharptongue":           "Sharp Tongue Glamour",
    "nekohelmet":            "Neko Helmet Princess",
    "nailbracelet":          "Nail Bracelet Neon Tube",
    "astralshard":           "Astral Shard Lovestone",
}

# Fallback ціни (якщо API не повернув результат) — твої поточні ціни
FALLBACK_PRICES = {
    "snakebox":              2.60,
    "candycane":             2.85,
    "jesterhat":             3.28,
    "lolpop":                3.35,
    "spicedwine":            3.69,
    "cookieheart":           4.11,
    "lolpopsweetheart":      5.24,
    "deskcalendar":          5.74,
    "joyfullbundle":         5.83,
    "bunnymuffin":           5.94,
    "berrybox":              7.41,
    "valentinebox":          8.64,
    "joyfullbundleteddybears": 8.93,
    "lovecandle":            9.08,
    "sakuraflower":          11.50,
    "lovepotion":            12.46,
    "starnotepad":           12.60,
    "eternalrose":           23.81,
    "toybear":               32.75,
    "sharptongue":           40.84,
    "nekohelmet":            89.36,
    "nailbracelet":          107.10,
    "astralshard":           249.10,
}

# ─── ЗАВАНТАЖЕННЯ ТОКЕНА ──────────────────────────────────────────────────────
def load_token():
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(f"Файл {TOKEN_FILE} не знайдено!")
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()

# ─── ОТРИМАННЯ FLOOR PRICE ДЛЯ ОДНІЄЇ КОЛЕКЦІЇ ───────────────────────────────
def get_floor_price(collection_name: str, headers: dict) -> float | None:
    """
    Бере найдешевший лот у колекції — це і є floor price.
    """
    try:
        resp = requests.post(
            f"{MARKET_API_URL}/gifts/saling",
            headers=headers,
            json={
                "collectionNames": [collection_name],
                "modelNames":    [],
                "backdropNames": [],
                "symbolNames":   [],
                "ordering":      "Price",
                "lowToHigh":     True,
                "maxPrice":      None,
                "minPrice":      None,
                "mintable":      None,
                "number":        None,
                "count":         1,
                "cursor":        "",
                "query":         None,
                "promotedFirst": False,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        gifts = data.get("gifts", [])
        if not gifts:
            return None

        gift = gifts[0]
        # Ціна може бути в полях: price, floorPrice, priceNano (наноTON → ділити на 1e9)
        price = gift.get("price") or gift.get("floorPrice")
        if price is None and "priceNano" in gift:
            price = gift["priceNano"] / 1_000_000_000
        return round(float(price), 2) if price else None

    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Мережева помилка для '{collection_name}': {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        print(f"  ⚠️  Помилка парсингу для '{collection_name}': {e}")
        return None

# ─── ГОЛОВНА ФУНКЦІЯ ──────────────────────────────────────────────────────────
def update_prices():
    print(f"\n{'='*55}")
    print(f"  🔄  Оновлення цін NFT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    token = load_token()
    headers = {
        "Authorization": token,
        "Referer":       "https://cdn.tgmrkt.io/",
        "Content-Type":  "application/json",
    }

    prices = {}
    success = 0
    failed  = 0

    for nft_id, collection_name in NFT_COLLECTION_MAP.items():
        print(f"  📦  {collection_name:<35}", end="", flush=True)
        floor = get_floor_price(collection_name, headers)

        if floor is not None:
            prices[nft_id] = floor
            print(f"✅  {floor:.2f} TON")
            success += 1
        else:
            # Використовуємо fallback
            fallback = FALLBACK_PRICES.get(nft_id)
            prices[nft_id] = fallback
            print(f"❌  не знайдено → fallback {fallback} TON")
            failed += 1

        time.sleep(0.3)  # Щоб не флудити API

    # ─── ЗБЕРЕЖЕННЯ В JSON ────────────────────────────────────────────────────
    output = {
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "prices":    prices,
    }
    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'─'*55}")
    print(f"  ✅  Успішно: {success} | ❌ Не знайдено: {failed}")
    print(f"  💾  Збережено → {PRICES_FILE}")
    print(f"{'='*55}\n")

    return prices

# ─── ЗАПУСК ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    # Режим "loop" — запускати кожні N хвилин
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        print(f"🔁  Авто-оновлення кожні {interval} хв. Ctrl+C для зупинки.")
        while True:
            try:
                update_prices()
            except Exception as e:
                print(f"❌ Критична помилка: {e}")
            time.sleep(interval * 60)
    else:
        update_prices()
