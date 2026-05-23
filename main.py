import asyncio, html, json, math, os, random, time, httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

TON_WALLET    = "UQAfazCyjGjugOf73_LrxUuLvxSmExM_8loArhgATwKXU6yA"
TONCENTER_KEY = "062f53efeb759f033896aab86a1f423f4102443694799e2dd34e8c14e7f4e9f0"
BOT_TOKEN     = os.getenv("BOT_TOKEN", "8736629642:AAHe9ZvyuHRGJV4C2t-zv6STyYXbeOxu4Io")
ADMIN_IDS     = {1256452126, 6479535975}
ADMIN_ID      = 1256452126
STARS_TO_TON  = 0.0084
NFT_WITHDRAW_TON_FEE = 0.2

NFT_CATALOG = [
    {"id":"icecream","name":"Ice Cream","floor":1.29,"price":1.35,"rarity":"Common","color":"#0d2e1a"},
    {"id":"santahat","name":"Santa Hat","floor":1.63,"price":1.71,"rarity":"Common","color":"#0d2e1a"},
    {"id":"moussecake","name":"Mousse Cake","floor":1.80,"price":1.89,"rarity":"Common","color":"#0d2e1a"},
    {"id":"lolpop2","name":"Lol Pop","floor":1.90,"price":1.99,"rarity":"Common","color":"#0d2e1a"},
    {"id":"instantramen","name":"Instant Ramen","floor":2.00,"price":2.10,"rarity":"Common","color":"#0d2e1a"},
    {"id":"springbasket","name":"Spring Basket","floor":2.13,"price":2.24,"rarity":"Common","color":"#0d2e1a"},
    {"id":"homemadecake","name":"Homemade Cake","floor":2.19,"price":2.30,"rarity":"Common","color":"#0d2e1a"},
    {"id":"restlessjar","name":"Restless Jar","floor":2.25,"price":2.36,"rarity":"Common","color":"#0d2e1a"},
    {"id":"witchhat","name":"Witch Hat","floor":2.49,"price":2.61,"rarity":"Common","color":"#0d2e1a"},
    {"id":"chillflame","name":"Chill Flame","floor":2.59,"price":2.72,"rarity":"Common","color":"#0d2e1a"},
    {"id":"xmasstocking","name":"Xmas Stocking","floor":2.60,"price":2.73,"rarity":"Common","color":"#0d2e1a"},
    {"id":"vicecream","name":"Vice Cream","floor":2.60,"price":2.73,"rarity":"Common","color":"#0d2e1a"},
    {"id":"snakebox","name":"Snake Box","floor":2.64,"price":2.77,"rarity":"Common","color":"#0d2e1a"},
    {"id":"candycane","name":"Candy Cane","floor":2.65,"price":2.78,"rarity":"Common","color":"#0d2e1a"},
    {"id":"lunarsnak","name":"Lunar Snake","floor":2.74,"price":2.88,"rarity":"Common","color":"#0d2e1a"},
    {"id":"holidaydrink","name":"Holiday Drink","floor":2.82,"price":2.96,"rarity":"Common","color":"#0d2e1a"},
    {"id":"whipcupcake","name":"Whip Cupcake","floor":2.85,"price":2.99,"rarity":"Common","color":"#0d2e1a"},
    {"id":"winterwreath","name":"Winter Wreath","floor":2.85,"price":2.99,"rarity":"Common","color":"#0d2e1a"},
    {"id":"bigyear","name":"Big Year","floor":2.87,"price":3.01,"rarity":"Common","color":"#0d2e1a"},
    {"id":"poolfloat","name":"Pool Float","floor":2.96,"price":3.11,"rarity":"Common","color":"#0d2e1a"},
    {"id":"joyfulbundle2","name":"Joyful Bundle","floor":3.09,"price":3.24,"rarity":"Common","color":"#0d2e1a"},
    {"id":"jesterhat","name":"Jester Hat","floor":3.09,"price":3.24,"rarity":"Common","color":"#0d2e1a"},
    {"id":"petsnake","name":"Pet Snake","floor":3.11,"price":3.27,"rarity":"Common","color":"#0d2e1a"},
    {"id":"partysparker","name":"Party Sparkler","floor":3.16,"price":3.32,"rarity":"Common","color":"#0d2e1a"},
    {"id":"hypnolollipop","name":"Hypno Lollipop","floor":3.18,"price":3.34,"rarity":"Common","color":"#0d2e1a"},
    {"id":"tamagadget","name":"Tama Gadget","floor":3.23,"price":3.39,"rarity":"Common","color":"#0d2e1a"},
    {"id":"freshsocks","name":"Fresh Socks","floor":3.26,"price":3.42,"rarity":"Common","color":"#0d2e1a"},
    {"id":"jackinthebox","name":"Jack-in-the-Box","floor":3.36,"price":3.53,"rarity":"Common","color":"#0d2e1a"},
    {"id":"easteregg","name":"Easter Egg","floor":3.41,"price":3.58,"rarity":"Common","color":"#0d2e1a"},
    {"id":"spicedwine","name":"Spiced Wine","floor":3.47,"price":3.64,"rarity":"Common","color":"#0d2e1a"},
    {"id":"happybroom","name":"Happy Brownie","floor":3.49,"price":3.66,"rarity":"Common","color":"#0d2e1a"},
    {"id":"lolpop","name":"Lol Pop","floor":3.61,"price":3.79,"rarity":"Common","color":"#0d2e1a"},
    {"id":"stellarrocket","name":"Stellar Rocket","floor":3.63,"price":3.81,"rarity":"Common","color":"#0d2e1a"},
    {"id":"jellybunny","name":"Jelly Bunny","floor":3.50,"price":3.68,"rarity":"Common","color":"#0d2e1a"},
    {"id":"moodpack","name":"Mood Pack","floor":3.67,"price":3.85,"rarity":"Common","color":"#0d2e1a"},
    {"id":"starnotepad","name":"Star Notepad","floor":3.71,"price":3.90,"rarity":"Common","color":"#0d2e1a"},
    {"id":"gingercookie","name":"Ginger Cookie","floor":3.73,"price":3.92,"rarity":"Common","color":"#0d2e1a"},
    {"id":"bunnymuffin","name":"Bunny Muffin","floor":3.64,"price":3.82,"rarity":"Common","color":"#0d2e1a"},
    {"id":"cookieheart","name":"Cookie Heart","floor":3.84,"price":4.03,"rarity":"Common","color":"#0d2e1a"},
    {"id":"snowglobe","name":"Snow Globe","floor":3.83,"price":4.02,"rarity":"Common","color":"#0d2e1a"},
    {"id":"hexpot","name":"Hex Pot","floor":3.87,"price":4.06,"rarity":"Common","color":"#0d2e1a"},
    {"id":"bdaycandle","name":"B-Day Candle","floor":4.08,"price":4.28,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"bowtie","name":"Bow Tie","floor":4.27,"price":4.48,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"cloverpin","name":"Clover Pin","floor":4.07,"price":4.27,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"faithamulet","name":"Faith Amulet","floor":4.23,"price":4.44,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"snowmittens","name":"Snow Mittens","floor":4.29,"price":4.50,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"moonpencil","name":"Moon Pendant","floor":4.36,"price":4.58,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"lushbouquet","name":"Lush Bouquet","floor":4.47,"price":4.69,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"inputkey","name":"Input Key","floor":4.75,"price":4.99,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"timelessbook","name":"Timeless Book","floor":4.03,"price":4.23,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"spyagaric","name":"Spy Agaric","floor":4.56,"price":4.79,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"snoopdog","name":"Snoop Dogg","floor":4.71,"price":4.95,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"joyfullbundle","name":"Joyful Bundle","floor":5.61,"price":5.89,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"lightsword","name":"Light Sword","floor":5.04,"price":5.29,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"eternalcandle","name":"Eternal Candle","floor":5.39,"price":5.66,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"deskcalendar","name":"Desk Calendar","floor":5.48,"price":5.75,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"jollychimp","name":"Jolly Chimp","floor":5.88,"price":6.17,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"swagbag","name":"Swag Bag","floor":5.86,"price":6.15,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"evileye","name":"Evil Eye","floor":5.97,"price":6.27,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"sleighbell","name":"Sleigh Bell","floor":6.70,"price":7.04,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"berrybox","name":"Berry Box","floor":6.80,"price":7.14,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"hangingstar","name":"Hanging Star","floor":7.14,"price":7.50,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"jinglebells","name":"Jingle Bells","floor":7.40,"price":7.77,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"valentinebox","name":"Valentine Box","floor":8.22,"price":8.63,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"lovecandle","name":"Love Candle","floor":8.42,"price":8.84,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"crystalball","name":"Crystal Ball","floor":9.74,"price":10.23,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"skullflower","name":"Skull Flower","floor":9.75,"price":10.24,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"flyingbroom","name":"Flying Broom","floor":10.16,"price":10.67,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"tophat","name":"Top Hat","floor":10.59,"price":11.12,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"sakuraflower","name":"Sakura Flower","floor":10.81,"price":11.35,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"madpumpkin","name":"Mad Pumpkin","floor":10.89,"price":11.43,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"lovepotion","name":"Love Potion","floor":11.85,"price":12.44,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"snoopcigar","name":"Snoop Cigar","floor":12.08,"price":12.68,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"trappedheart","name":"Trapped Heart","floor":12.91,"price":13.56,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"skystillettos","name":"Sky Stilettos","floor":13.28,"price":13.94,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"ionicdryer","name":"Ionic Dryer","floor":13.53,"price":14.21,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"recordplayer","name":"Record Player","floor":14.24,"price":14.95,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"signetring","name":"Signet Ring","floor":16.50,"price":17.32,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"cupidcharm","name":"Cupid Charm","floor":17.41,"price":18.28,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"vintagecigar","name":"Vintage Cigar","floor":18.20,"price":19.11,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"bondedring","name":"Bonded Ring","floor":21.00,"price":22.05,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"sharptongue","name":"Sharp Tongue","floor":21.69,"price":22.77,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"eternalrose","name":"Eternal Rose","floor":21.86,"price":22.95,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"electricskull","name":"Electric Skull","floor":24.69,"price":25.92,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"diamondring","name":"Diamond Ring","floor":25.28,"price":26.54,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"voodoodoll","name":"Voodoo Doll","floor":29.27,"price":30.73,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"toybear","name":"Toy Bear","floor":30.10,"price":31.61,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"nekohelmet","name":"Neko Helmet","floor":31.59,"price":33.17,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"lowrider","name":"Low Rider","floor":39.89,"price":41.88,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"genielamp","name":"Genie Lamp","floor":40.70,"price":42.74,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"swisswatch","name":"Swiss Watch","floor":43.13,"price":45.29,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"kissedfrog","name":"Kissed Frog","floor":48.89,"price":51.33,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"nailbracelet","name":"Nail Bracelet","floor":54.70,"price":57.44,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"gemsignet","name":"Gem Signet","floor":55.87,"price":58.66,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"magicpotion","name":"Magic Potion","floor":61.44,"price":64.51,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"artisanbread","name":"Artisan Brick","floor":68.34,"price":71.76,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"iongem","name":"Ion Gem","floor":69.82,"price":73.31,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"perfumebottle","name":"Perfume Bottle","floor":70.86,"price":74.40,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"westsideside","name":"Westside Sign","floor":70.94,"price":74.49,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"minioscal","name":"Mini Oscar","floor":72.22,"price":75.83,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"lootbag","name":"Loot Bag","floor":72.99,"price":76.64,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"mightyarm","name":"Mighty Arm","floor":79.00,"price":82.95,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"scaredcat","name":"Scared Cat","floor":87.99,"price":92.39,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"heroichelmet","name":"Heroic Helmet","floor":200.58,"price":210.61,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"astralshard","name":"Astral Shard","floor":151.69,"price":159.27,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"preciouspeach","name":"Precious Peach","floor":188.80,"price":198.24,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"durovscap","name":"Durov Cap","floor":576.88,"price":605.72,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"heartlocket","name":"Heart Locket","floor":1050.00,"price":1102.50,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"plushpepe","name":"Plush Pepe","floor":4500.00,"price":4725.00,"rarity":"Legendary","color":"#2e1e00"},
]

NFT_PRICE_ALIASES = {
    "lunarsnak": "lunarsnake",
    "partysparker": "partysparkler",
    "happybroom": "happybrownie",
    "hexpot": "hexhot",
    "moonpencil": "moonpendant",
    "minioscal": "minioscars",
    "artisanbread": "artisanbrick",
    "skystillettos": "skystiletto",
}

# Fallback from the latest tgmrkt update log. prices.json overrides these when present.
NFT_PRICE_OVERRIDES = {
    "snakebox": 1.81, "candycane": 1.81, "jesterhat": 1.94, "lolpop": 2.50,
    "spicedwine": 2.18, "bunnymuffin": 4.27, "berrybox": 5.24,
    "valentinebox": 5.63, "lovecandle": 5.74, "sakuraflower": 6.24,
    "lovepotion": 8.59, "toybear": 22.48, "sharptongue": 28.25,
    "nekohelmet": 24.95, "nailbracelet": 81.98, "astralshard": 102.50,
    "artisanbrick": 50.55, "astralshards": 102.50, "bowtie": 2.60,
    "chillflame": 1.81, "clovelpin": 2.60, "cloverpin": 2.60,
    "crystalball": 6.76, "cupidcharm": 12.62, "diamondring": 17.47,
    "eternalcandle": 3.31, "evileye": 4.12, "flyingbroom": 6.75,
    "gemsignet": 45.50, "genielamp": 29.79, "gingercookie": 2.25,
    "heartlocket": 1346.98, "heroichelmet": 144.89, "hexhot": 2.23,
    "holidaydrink": 1.88, "homemadecake": 2.74, "hypnolollipop": 2.12,
    "instantramen": 1.82, "ionicdrier": 8.74, "iongem": 55.28,
    "jackinthebox": 2.11, "jellybunny": 4.18, "jinglebells": 5.73,
    "lightsword": 3.21, "lolpop2": 2.50, "lootbag": 83.75,
    "lowrider": 32.33, "lunarsnake": 1.80, "lunarsnak": 1.80,
    "lushbouquet": 2.74, "madpumpkin": 6.99, "minioscars": 53.94,
    "minioscal": 53.94, "moodpack": 2.55, "moonpendant": 3.11,
    "moonpencil": 3.11, "moussecake": 2.63, "partysparkler": 2.01,
    "partysparker": 2.01, "perfumebottle": 57.86, "poolfloat": 2.07,
    "preciouspeach": 246.70, "recordplayer": 6.99, "restlessjar": 2.93,
    "santahat": 2.22, "scaredcat": 117.64, "skystiletto": 9.70,
    "skystillettos": 9.70, "sleighbell": 5.06, "snoopcigar": 7.44,
    "snoopdog": 3.08, "snowglobe": 2.70, "snowmittens": 2.82,
    "stellarrocket": 2.05, "swagbag": 3.13, "swisswatch": 33.59,
    "tamagadget": 2.24, "timelessbook": 2.69, "tophat": 6.13,
    "vintagecigar": 22.80, "voodoodoll": 19.59, "westsideside": 48.07,
    "whipcupcake": 1.83, "winterwreath": 1.83, "witchhat": 3.17,
    "freshsocks": 2.13, "faithamulet": 3.05,
}

_PRICE_FILE_MTIME = None
_PRICE_FILE_PATH = None

def _nft_key(value):
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())

def _price_file_candidates():
    here = os.path.dirname(os.path.abspath(__file__))
    return [
        os.path.join(here, "prices.json"),
        os.path.join(os.getcwd(), "prices.json"),
        os.path.join(os.path.expanduser("~"), "Downloads", "prices.json"),
    ]

def _read_prices_json():
    global _PRICE_FILE_MTIME, _PRICE_FILE_PATH
    for path in _price_file_candidates():
        if not os.path.exists(path):
            continue
        mtime = os.path.getmtime(path)
        if _PRICE_FILE_PATH == path and _PRICE_FILE_MTIME == mtime:
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _PRICE_FILE_PATH = path
            _PRICE_FILE_MTIME = mtime
            return data
        except Exception as e:
            print(f"prices.json read error: {e}")
    return None

def _flatten_price_data(data):
    out = {}
    if isinstance(data, dict):
        for container in ("prices", "items", "nfts", "data"):
            if isinstance(data.get(container), (dict, list)):
                out.update(_flatten_price_data(data[container]))
    if isinstance(data, dict):
        items = data.items()
    elif isinstance(data, list):
        items = [(None, item) for item in data]
    else:
        return out
    for key, value in items:
        nft_id = key
        price = None
        if isinstance(value, (int, float)):
            price = float(value)
        elif isinstance(value, dict):
            nft_id = value.get("id") or value.get("slug") or value.get("name") or key
            for field in ("price", "floor", "floor_price", "ton", "value"):
                if value.get(field) is not None:
                    try:
                        price = float(value[field])
                        break
                    except (TypeError, ValueError):
                        pass
        if nft_id and price and price > 0:
            out[_nft_key(nft_id)] = round(price, 4)
    return out

def sync_nft_prices(force=False):
    prices = dict(NFT_PRICE_OVERRIDES)
    data = _read_prices_json()
    if data is not None:
        prices.update(_flatten_price_data(data))
    elif not force and _PRICE_FILE_MTIME is not None:
        return

    normalized = {_nft_key(k): v for k, v in prices.items()}
    for alias, canonical in NFT_PRICE_ALIASES.items():
        alias_key = _nft_key(alias)
        canonical_key = _nft_key(canonical)
        if canonical_key in normalized:
            normalized[alias_key] = normalized[canonical_key]
        elif alias_key in normalized:
            normalized[canonical_key] = normalized[alias_key]

    for nft in NFT_CATALOG:
        keys = {_nft_key(nft.get("id")), _nft_key(nft.get("name"))}
        keys.update(_nft_key(NFT_PRICE_ALIASES.get(k, "")) for k in list(keys))
        for key in keys:
            if key in normalized:
                nft["floor"] = normalized[key]
                nft["price"] = normalized[key]
                nft["price_source"] = "prices"
                break

def get_nft_for_win(win: float):
    if win < 0.1: return None  # NFT падають при виграші від 0.1 TON
    sync_nft_prices()
    if not NFT_CATALOG: return None
    
    # Фільтруємо тільки ті NFT що вміщуються у виграш
    ok = [n for n in NFT_CATALOG if n["price"] <= win]
    if not ok: return None
    
    # Зважений випадковий вибір: дешеві NFT падають частіше
    # Вага = 1 / ціна (чим дешевше, тим більша вага)
    weights = [1.0 / n["price"] for n in ok]
    total_weight = sum(weights)
    rand = random.random() * total_weight
    
    for i, w in enumerate(weights):
        rand -= w
        if rand <= 0:
            return ok[i]
    
    return ok[-1]  # Fallback

def get_nft_for_rocket_win(win: float):
    """Повертає NFT тільки якщо win >= ціни найдешевшого NFT в каталозі.
    Інакше повертає None (падає TON замість NFT)."""
    if win < 0.1:
        return None
    sync_nft_prices()
    
    # Знаходимо NFT з ціною <= win
    available = [n for n in NFT_CATALOG if float(n.get("price") or n.get("floor") or 0) <= win]
    
    if available:
        # Вибираємо NFT з НАЙБЛИЖЧОЮ ціною до win (найдорожчий з доступних)
        available_sorted = sorted(
            available, 
            key=lambda n: float(n.get("price") or n.get("floor") or 0),
            reverse=True
        )
        return available_sorted[0]
    
    # Якщо win менше найдешевшого NFT — повертаємо None (падає TON)
    return None

sync_nft_prices(force=True)

# НОВА ФУНКЦІЯ: Перевірка підписки на канал
async def check_subscription(user_id: int, channel: str) -> bool:
    """Перевіряє чи користувач підписаний на канал через Telegram Bot API"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
            params = {"chat_id": channel, "user_id": user_id}
            response = await client.get(url, params=params)
            data = response.json()
            
            if data.get("ok"):
                status = data.get("result", {}).get("status")
                return status in ["member", "administrator", "creator"]
            return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

clients: dict = {}
players: dict = {}
bets:    dict = {}
referrals: dict = {}
ref_earnings: dict = {}
pending_topups: dict = {}

logs = {"bets": [], "cashouts": [], "deposits": [], "withdrawals": [], "referrals": [], "stars": [], "cases": []}
MAX_LOGS = 500

# Збереження даних у файл
PLAYERS_FILE = "players_data.json"

def save_players():
    try:
        tmp_file = PLAYERS_FILE + ".tmp"
        with open(tmp_file, "w") as f:
            json.dump(players, f)
        os.replace(tmp_file, PLAYERS_FILE)
        print(f"💾 Players data saved ({len(players)} players)")
    except Exception as e:
        print(f"❌ Error saving players: {e}")

def load_players():
    global players
    try:
        if os.path.exists(PLAYERS_FILE):
            with open(PLAYERS_FILE, "r") as f:
                raw_players = json.load(f)
            players = {}
            for raw_uid, data in raw_players.items():
                try:
                    fixed_uid = int(raw_uid)
                except Exception:
                    fixed_uid = raw_uid
                if isinstance(data, dict):
                    data.setdefault("balance", 0)
                    data.setdefault("nfts", [])
                    data.setdefault("name", "Player")
                    data.setdefault("nick", "")
                    data.setdefault("photo", "")
                    players[fixed_uid] = data
            print(f"📂 Loaded {len(players)} players from file")
        else:
            print("📂 No saved players file, starting fresh")
    except Exception as e:
        print(f"❌ Error loading players: {e}")
        players = {}

# Завантажуємо при старті
load_players()

def add_log(category, entry):
    entry["ts"] = time.time()
    logs[category].insert(0, entry)
    if len(logs[category]) > MAX_LOGS:
        logs[category].pop()

async def send_tg(uid: int, text: str, reply_markup=None):
    try:
        print(f"📤 Sending message to {uid}: {text[:50]}...")
        payload = {"chat_id": uid, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json=payload
            )
            data = r.json()
            if data.get("ok"):
                print(f"✅ Message sent successfully to {uid}")
            else:
                print(f"❌ Telegram API error: {data.get('description', 'Unknown error')}")
    except Exception as e:
        print(f"❌ TG send error to {uid}: {e}")

async def send_admins(text: str):
    await asyncio.gather(*(send_tg(admin_id, text) for admin_id in ADMIN_IDS), return_exceptions=True)

async def credit_balance(uid: int, amount: float, source: str = "deposit"):
    if uid not in players:
        players[uid] = {"name": "Player", "nick": "", "photo": "", "balance": 0, "nfts": []}
    players[uid]["balance"] = round(players[uid]["balance"] + amount, 4)
    if uid in referrals:
        ref_uid = referrals[uid]
        bonus = round(amount * 0.10, 4)  # 10% реферальний бонус
        if ref_uid not in players:
            players[ref_uid] = {"name": "?", "nick": "", "photo": "", "balance": 0, "nfts": []}
        players[ref_uid]["balance"] = round(players[ref_uid]["balance"] + bonus, 4)
        ref_earnings[ref_uid] = round(ref_earnings.get(ref_uid, 0) + bonus, 4)
        add_log("deposits", {"uid": ref_uid, "name": players[ref_uid].get("name", "?"), "amount": bonus, "note": f"ref bonus від {uid}"})
        if ref_uid in clients:
            try:
                await clients[ref_uid].send_text(json.dumps({"t": "ref_bonus", "bonus": bonus, "bal": players[ref_uid]["balance"]}))
            except: pass
        await send_tg(ref_uid, f"👥 <b>Реферальний бонус!</b>\nВаш реферал поповнив баланс на {amount} TON\nВаш бонус: <b>+{bonus} TON</b> (10%)")
    if uid in clients:
        try:
            await clients[uid].send_text(json.dumps({"t": "topup_ok", "credited": amount, "bal": players[uid]["balance"], "source": source}))
        except: pass
    return players[uid]["balance"]

async def check_ton_tx(uid: int, amount: float, since_ts: float) -> bool:
    if not TON_WALLET: return False
    try:
        params = {"address": TON_WALLET, "limit": 20}
        if TONCENTER_KEY: params["api_key"] = TONCENTER_KEY
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get("https://toncenter.com/api/v2/getTransactions", params=params)
            data = r.json()
            if not data.get("ok"): return False
            nanos = int(amount * 1e9)
            for tx in data.get("result", []):
                if tx.get("utime", 0) < since_ts - 180: break
                val = int(tx.get("in_msg", {}).get("value", 0))
                if abs(val - nanos) < 50_000_000: return True
    except Exception as e:
        print(f"check_ton_tx error: {e}")
    return False

pending_stars_payments = {}  # {uid: {"stars": 10, "ton": 0.084, "ts": timestamp}}

async def auto_check_topups():
    while True:
        await asyncio.sleep(10)
        for uid, info in list(pending_topups.items()):
            if info.get("done"):
                pending_topups.pop(uid, None); continue
            if time.time() - info["ts"] > 900:
                pending_topups.pop(uid, None); continue
            found = await check_ton_tx(uid, info["amount"], info["ts"])
            if found:
                info["done"] = True
                amt = info["amount"]
                bal = await credit_balance(uid, amt, source="ton")
                add_log("deposits", {"uid": uid, "name": players[uid].get("name", "?"), "amount": amt})
                await send_tg(ADMIN_ID, f"💰 <b>Депозит TON</b>\nКористувач: {players[uid].get('name','?')} (uid: {uid})\nСума: {amt} TON\nБаланс: {bal} TON")

async def check_stars_payments():
    """Перевіряє pending Stars payments через getUpdates як fallback"""
    while True:
        await asyncio.sleep(5)
        
        if pending_stars_payments:
            print(f"🔍 Checking {len(pending_stars_payments)} pending Stars payment(s)")
        
        if not pending_stars_payments:
            continue
        
        # Видаляємо старі (більше 10 хвилин)
        for uid in list(pending_stars_payments.keys()):
            if time.time() - pending_stars_payments[uid]["ts"] > 600:
                print(f"⏱️ Removing expired Stars payment for {uid}")
                pending_stars_payments.pop(uid, None)
        
        if not pending_stars_payments:
            continue
        
        try:
            # Робимо один запит getUpdates для перевірки
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                    params={"offset": -1, "limit": 10}  # Тільки останні 10 updates
                )
                data = r.json()
                
                if not data.get("ok"):
                    continue
                
                for update in data.get("result", []):
                    msg = update.get("message", {})
                    payment = msg.get("successful_payment")
                    
                    if payment and payment.get("currency") == "XTR":
                        try:
                            payload = json.loads(payment["invoice_payload"])
                            uid = int(payload["uid"])
                            
                            if uid in pending_stars_payments:
                                stars = int(payload["stars"])
                                ton_amount = float(payload["ton"])
                                
                                print(f"✅ Found Stars payment via fallback check: {stars} Stars for {uid}")
                                
                                # Зараховуємо
                                bal = await credit_balance(uid, ton_amount, source="stars")
                                add_log("stars", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "stars": stars, "ton": ton_amount})
                                add_log("deposits", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "amount": ton_amount, "note": f"Stars x{stars} (fallback)"})
                                
                                await send_tg(uid, f"⭐ <b>Stars зараховано!</b>\n{stars} Stars → <b>{ton_amount} TON</b>\nБаланс: {bal} TON")
                                await send_tg(ADMIN_ID, f"⭐ <b>Stars депозит (fallback)</b>\nКористувач: {players.get(uid,{}).get('name','?')} (uid: {uid})\nStars: {stars} → {ton_amount} TON")
                                
                                # Оновлюємо баланс через WebSocket
                                if uid in clients:
                                    try:
                                        await clients[uid].send_text(json.dumps({"t": "bal", "bal": bal}))
                                    except:
                                        pass
                                
                                # Видаляємо з pending
                                pending_stars_payments.pop(uid, None)
                                print(f"✅ Stars credited via fallback: {stars} → {ton_amount} TON, balance: {bal}")
                        except Exception as e:
                            print(f"❌ Error processing fallback payment: {e}")
        except Exception as e:
            print(f"❌ check_stars_payments error: {e}")

# Long polling для отримання Stars payments
last_update_id = 0
async def poll_telegram_updates():
    global last_update_id
    print("🔄 Starting Telegram polling for Stars payments...")
    while True:
        try:
            await asyncio.sleep(2)
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                    params={"offset": last_update_id + 1, "timeout": 5, "allowed_updates": ["message", "pre_checkout_query"]}
                )
                data = r.json()
                
                if not data.get("ok"):
                    print(f"❌ getUpdates error: {data}")
                    await asyncio.sleep(5)
                    continue
                
                updates = data.get("result", [])
                if updates:
                    print(f"📨 Received {len(updates)} update(s)")
                
                for update in updates:
                    last_update_id = max(last_update_id, update.get("update_id", 0))
                    
                    # Pre-checkout query
                    if "pre_checkout_query" in update:
                        pcq_id = update["pre_checkout_query"]["id"]
                        print(f"✅ Pre-checkout query: {pcq_id}")
                        try:
                            async with httpx.AsyncClient(timeout=10) as client2:
                                await client2.post(
                                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery",
                                    json={"pre_checkout_query_id": pcq_id, "ok": True}
                                )
                                print(f"✅ Answered pre-checkout query")
                        except Exception as e:
                            print(f"❌ answerPreCheckoutQuery error: {e}")
                    
                    # Successful payment
                    msg = update.get("message", {})
                    payment = msg.get("successful_payment")
                    if payment and payment.get("currency") == "XTR":
                        print(f"💳 Stars payment received via polling: {payment}")
                        try:
                            payload = json.loads(payment["invoice_payload"])
                            uid = int(payload["uid"])
                            stars = int(payload["stars"])
                            ton_amount = float(payload["ton"])
                            
                            print(f"💰 Processing: {stars} Stars → {ton_amount} TON for user {uid}")
                            
                            bal = await credit_balance(uid, ton_amount, source="stars")
                            add_log("stars", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "stars": stars, "ton": ton_amount})
                            add_log("deposits", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "amount": ton_amount, "note": f"Stars x{stars}"})
                            
                            await send_tg(uid, f"⭐ <b>Stars зараховано!</b>\n{stars} Stars → <b>{ton_amount} TON</b>\nБаланс: {bal} TON")
                            await send_tg(ADMIN_ID, f"⭐ <b>Stars депозит</b>\nКористувач: {players.get(uid,{}).get('name','?')} (uid: {uid})\nStars: {stars} → {ton_amount} TON")
                            print(f"✅ Stars credited: {stars} → {ton_amount} TON for user {uid}, new balance: {bal}")
                            
                            # Оновлюємо баланс через WebSocket
                            if uid in clients:
                                try:
                                    await clients[uid].send_text(json.dumps({"t": "bal", "bal": bal}))
                                    print(f"✅ Balance updated via WebSocket")
                                except Exception as e:
                                    print(f"❌ WebSocket update error: {e}")
                        except Exception as e:
                            print(f"❌ Stars payment processing error: {e}")
                            import traceback
                            traceback.print_exc()
        except Exception as e:
            print(f"❌ Polling error: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(5)

NFT_WITHDRAW_STARS = 1

@app.get("/stars/withdraw-invoice/{uid}/{nft_id}/{nft_name}")
async def create_withdraw_invoice(uid: int, nft_id: str, nft_name: str):
    payload = json.dumps({"uid": uid, "nft_id": nft_id, "type": "nft_withdraw"})
    print(f"🎫 Creating withdraw invoice for UID:{uid}, NFT:{nft_name}, Fee:{NFT_WITHDRAW_STARS}⭐")
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink",
                json={"title": f"NFT Withdrawal: {nft_name}", "description": f"Fee for withdrawing NFT «{nft_name}» to your Telegram wallet", "payload": payload, "currency": "XTR", "prices": [{"label": "Withdrawal fee", "amount": NFT_WITHDRAW_STARS}]}
            )
            data = r.json()
            print(f"📋 Telegram API response: {data}")
        if not data.get("ok"):
            error_msg = data.get("description", "Telegram error")
            print(f"❌ Invoice creation failed: {error_msg}")
            return JSONResponse({"ok": False, "error": error_msg})
        print(f"✅ Invoice created successfully")
        return JSONResponse({"ok": True, "invoice_link": data["result"]})
    except Exception as e:
        print(f"❌ Server error creating invoice: {str(e)}")
        return JSONResponse({"ok": False, "error": f"Server error: {str(e)}"})

@app.get("/stars/invoice/{uid}/{stars}")
async def create_stars_invoice(uid: int, stars: int):
    if stars < 10 or stars > 10000:
        return JSONResponse({"ok": False, "error": "Stars від 10 до 10 000"})
    ton_amount = round(stars * STARS_TO_TON, 4)
    payload = json.dumps({"uid": uid, "stars": stars, "ton": ton_amount})
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink",
                json={"title": "Поповнення балансу ⭐", "description": f"{stars} Telegram Stars → {ton_amount} TON на ігровий баланс", "payload": payload, "currency": "XTR", "prices": [{"label": f"{stars} Stars", "amount": stars}]}
            )
            data = r.json()
        if not data.get("ok"):
            return JSONResponse({"ok": False, "error": data.get("description", "Помилка Telegram")})
        
        # Додаємо в pending для fallback перевірки
        pending_stars_payments[uid] = {"stars": stars, "ton": ton_amount, "ts": time.time()}
        print(f"📝 Added pending Stars payment: {uid} → {stars} Stars")
        
        return JSONResponse({"ok": True, "invoice_link": data["result"], "ton": ton_amount})
    except Exception as e:
        return JSONResponse({"ok": False, "error": "Помилка сервера"})

@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    try:
        update = await request.json()
        print(f"📨 Webhook received: {json.dumps(update, ensure_ascii=False)[:500]}")
    except Exception as e:
        print(f"❌ Failed to parse webhook: {e}")
        return JSONResponse({"ok": True})

    # 1. PRE-CHECKOUT QUERY — КРИТИЧНО ПЕРШИМ! Telegram вимагає відповіді протягом 10 сек
    if "pre_checkout_query" in update:
        pcq_id = update["pre_checkout_query"]["id"]
        print(f"✅ Pre-checkout query received via webhook: {pcq_id}")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery", json={"pre_checkout_query_id": pcq_id, "ok": True})
                result = r.json()
                print(f"✅ Pre-checkout answered: {result}")
        except Exception as e:
            print(f"❌ answerPreCheckoutQuery error: {e}")
        return JSONResponse({"ok": True})

    msg = update.get("message", {})

    # 2. SUCCESSFUL PAYMENT — Stars оплата
    payment = msg.get("successful_payment")
    if payment and payment.get("currency") == "XTR":
        print(f"💳 Stars payment received: {payment}")
        try:
            payload = json.loads(payment["invoice_payload"])
            print(f"📦 Payload: {payload}")
        except Exception as e:
            print(f"❌ Payload parse error: {e}")
            return JSONResponse({"ok": True})
        pay_type = payload.get("type", "deposit")
        print(f"🔍 Payment type: {pay_type}")
        if pay_type == "nft_withdraw":
            uid = int(payload["uid"])
            nft_id = payload["nft_id"]
            print(f"👤 UID: {uid}, NFT ID: {nft_id}")
            p = players.get(uid)
            if p:
                nfts = p.get("nfts", [])
                print(f"🎁 Player has {len(nfts)} NFTs: {[n.get('id') for n in nfts]}")
                found_nft = None; new_nfts = []; removed = False
                for n in nfts:
                    if n.get("id") == nft_id and not removed:
                        found_nft = n; removed = True
                        print(f"✅ Found NFT: {n.get('name')}")
                    else:
                        new_nfts.append(n)
                if found_nft:
                    p["nfts"] = new_nfts
                    add_log("withdrawals", {"uid": uid, "name": p.get("name","?"), "nft_name": found_nft.get("name"), "nft_floor": found_nft.get("floor"), "sell_price": 0, "type": "withdraw_stars"})
                    if uid in clients:
                        try:
                            await clients[uid].send_text(json.dumps({"t": "nft_withdrawn", "nft_id": nft_id, "nft_name": found_nft.get('name'), "msg": f"✅ {found_nft.get('name')} успішно виведено!"}))
                        except: pass
                    
                    # Повідомлення користувачу з кнопкою
                    keyboard = {
                        "inline_keyboard": [[
                            {"text": "📨 Send 'HI' to @Pepe_sender", "url": "https://t.me/Pepe_sender"}
                        ]]
                    }
                    await send_tg(uid, 
                        f"✅ <b>NFT Withdrawal Request Submitted!</b>\n\n"
                        f"NFT: <b>{found_nft.get('name')}</b>\n"
                        f"Floor: {found_nft.get('floor')} TON\n"
                        f"Fee paid: {NFT_WITHDRAW_STARS} ⭐\n\n"
                        f"⚠️ <b>IMPORTANT:</b> To complete the withdrawal, you must:\n"
                        f"1️⃣ Click the button below\n"
                        f"2️⃣ Send the word <b>'HI'</b> to @Pepe_sender\n\n"
                        f"Your NFT will be sent after verification.",
                        reply_markup=keyboard
                    )
                    
                    # Повідомлення адміну (правильний формат)
                    name = p.get("name", "?")
                    nick = p.get("nick", "")
                    nick_str = f"(@{nick})" if nick else ""
                    await send_tg(ADMIN_ID, f"🎁 <b>NFT Withdrawal Request</b>\n\nUser: {name} {nick_str}\nUID: <code>{uid}</code>\nNFT: <b>{found_nft.get('name')}</b>\nFloor: {found_nft.get('floor')} TON\nFee paid: {NFT_WITHDRAW_STARS} ⭐\n\n⚠️ User must send 'HI' to @Pepe_sender for verification")
                    
                    print(f"✅ NFT withdrawal completed for {uid}")
                else:
                    print(f"❌ NFT {nft_id} not found in player inventory")
            else:
                print(f"❌ Player {uid} not found")
        else:
            try:
                uid = int(payload["uid"]); stars = int(payload["stars"]); ton_amount = float(payload["ton"])
            except:
                return JSONResponse({"ok": True})
            bal = await credit_balance(uid, ton_amount, source="stars")
            add_log("stars", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "stars": stars, "ton": ton_amount})
            add_log("deposits", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "amount": ton_amount, "note": f"Stars x{stars}"})
            await send_tg(uid, f"⭐ <b>Stars зараховано!</b>\n{stars} Stars → <b>{ton_amount} TON</b>\nБаланс: {bal} TON")
            await send_tg(ADMIN_ID, f"⭐ <b>Stars депозит</b>\nКористувач: {players.get(uid,{}).get('name','?')} (uid: {uid})\nStars: {stars} → {ton_amount} TON")
        return JSONResponse({"ok": True})

    # 3. КОМАНДИ
    if msg:
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        if text == "/start":
            user_name = msg.get("from", {}).get("first_name", "User")
            await send_tg(chat_id, f"👋 Welcome to Rocket Casino, {user_name}!\n\n🎮 Open the game: https://casino-bot-production-5113.up.railway.app\n\nGood luck! 🚀")

    return JSONResponse({"ok": True})

@app.get("/admin/give_nft/{uid}/{nft_id}/{nft_name}/{floor}")
async def admin_give_nft(uid: int, nft_id: str, nft_name: str, floor: float, request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red'>⛔ Access Denied</h2>", status_code=403)
    
    if uid not in players:
        players[uid] = {"balance": 0, "nfts": [], "name": f"User{uid}", "nick": ""}
    
    # Додаємо NFT
    nft_entry = {
        "id": nft_id,
        "name": nft_name,
        "emoji": "🎁",
        "rarity": "Common",
        "price": floor,
        "floor": floor,
        "ts": time.time()
    }
    players[uid]["nfts"].append(nft_entry)
    save_players()
    
    print(f"✅ Admin {admin_uid} gave NFT {nft_name} to {uid}")
    
    # Якщо гравець онлайн - повідомляємо
    if uid in clients:
        try:
            await clients[uid].send_text(json.dumps({"t": "admin_nft_added", "nft": nft_entry}))
        except: pass
    
    return HTMLResponse(f'<script>alert("NFT {nft_name} added to player {uid}"); window.location="/admin/player/{uid}?uid={admin_uid}"</script>')

@app.get("/test/send_message/{chat_id}")
async def test_send_message(chat_id: int):
    """Test endpoint to verify bot can send messages"""
    try:
        await send_tg(chat_id, "🧪 <b>Test message from Railway</b>\n\nIf you see this, bot is working! ✅")
        return {"ok": True, "message": f"Message sent to {chat_id}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/set_webhook")
async def set_webhook(request: Request):
    admin_uid = int(request.query_params.get("uid", 0) or 0)
    if admin_uid not in ADMIN_IDS:
        return JSONResponse({"error": "forbidden"}, status_code=403)
    webhook_url = request.query_params.get("url")
    if not webhook_url:
        return JSONResponse({"error": "передай ?url=https://твій-сервер.com"})
    full_url = webhook_url.rstrip("/") + "/tg/webhook"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", json={"url": full_url})
        return r.json()
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.get("/delete_webhook")
async def delete_webhook(request: Request):
    admin_uid = int(request.query_params.get("uid", 0) or 0)
    if admin_uid not in ADMIN_IDS:
        return JSONResponse({"error": "forbidden"}, status_code=403)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        return r.json()
    except Exception as e:
        return JSONResponse({"error": str(e)})

class G:
    phase    = "waiting"
    mult     = 1.0
    crash_at = 1.0
    start_ts = 0.0
    round_id = 0
    next_hook = random.randint(8, 25)
    history: list = []
    def calc_mult(self, t): return round(math.exp(t * 0.06), 2)  # Трохи повільніше для реалізму

g = G()

def gen_crash():
    r = random.random()
    # Новий розподіл - низький RTP (~85%), казино заробляє
    if r < 0.15: return 1.00  # 15% - instant crash
    if r < 0.50: return round(random.uniform(1.01, 1.5), 2)  # 35% - малий виграш
    if r < 0.75: return round(random.uniform(1.5,  2.5), 2)  # 25% - середній
    if r < 0.90: return round(random.uniform(2.5,  5.0), 2)  # 15% - добрий
    if r < 0.97: return round(random.uniform(5.0,  20.0), 2) # 7% - великий
    if r < 0.99: return round(random.uniform(20.0, 50.0), 2) # 2% - дуже великий
    return round(random.uniform(50.0, 100.0), 2)  # 1% - джекпот

def gen_crash_no_bets():
    return round(random.uniform(30.0, 100.0), 2)

async def broadcast(msg):
    data = json.dumps(msg)
    dead = []
    for uid, ws in list(clients.items()):
        try: await ws.send_text(data)
        except: dead.append(uid)
    for uid in dead: clients.pop(uid, None)

def players_list():
    return [
        {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "nick": players.get(uid, {}).get("nick", ""),
         "photo": players.get(uid, {}).get("photo", ""), "bet": b["amount"],
         "cashed": b.get("cashed", False), "win": b.get("win"), "mult": b.get("mult"),
         "lost": b.get("lost", False),
         # NFT показуємо тільки після кешауту (не під час польоту)
         "nft": b.get("nft") if b.get("cashed") else None}
        for uid, b in bets.items()
    ]

async def do_cashout(uid, mult):
    bet = bets.get(uid)
    if not bet or bet.get("cashed"): return
    bet["cashed"] = True
    bet["mult"] = mult
    p = players.get(uid, {})

    # Звичайна TON ставка
    win = round(bet["amount"] * mult, 4)
    bet["win"] = win
    
    # NFT падає якщо виграш >= ціни найдешевшого NFT і множник >= 1.1
    min_nft_price = min((float(n.get("price") or n.get("floor") or 999) for n in NFT_CATALOG), default=999)
    nft = get_nft_for_rocket_win(win) if (win >= min_nft_price and mult >= 1.1) else None
    
    bet["nft"] = nft
    if nft:
        nft_entry = {**nft, "uid": f"rocket_{uid}_{int(time.time()*1000)}_{random.randint(1000,9999)}", "won_at": mult, "win_ton": win, "ts": time.time()}
        p.setdefault("nfts", []).append(nft_entry)
        nft = nft_entry
        add_log("cashouts", {"uid": uid, "name": p.get("name","?"), "bet": bet["amount"], "win": win, "mult": mult, "nft": nft.get("name"), "nft_floor": nft.get("floor")})
    else:
        p["balance"] = round(p.get("balance", 0) + win, 4)
        add_log("cashouts", {"uid": uid, "name": p.get("name","?"), "bet": bet["amount"], "win": win, "mult": mult, "nft": None})
    await broadcast({"t": "co", "uid": uid, "win": win, "mx": mult, "pl": players_list(), "now": time.time()})
    if uid in clients:
        try:
            await clients[uid].send_text(json.dumps({"t": "your_co", "win": win, "mx": mult, "bal": p.get("balance", 0), "nft": nft}))
        except: pass
    save_players()

async def game_loop():
    while True:
        g.phase = "waiting"; g.mult = 1.0; g.round_id += 1
        bets.clear()
        if g.round_id % g.next_hook == 0 and len(bets) == 0:
            g.crash_at = gen_crash_no_bets()
            g.next_hook = random.randint(8, 25)
        else:
            g.crash_at = gen_crash()
            if g.round_id % g.next_hook == 0:
                g.next_hook = random.randint(8, 25)
        for cd in range(5, 0, -1):
            await broadcast({"t": "cd", "sec": cd, "rid": g.round_id, "ca": g.crash_at, "now": time.time()})
            await asyncio.sleep(1)
        g.phase = "flying"; g.start_ts = time.time()
        await broadcast({"t": "st", "ts": g.start_ts, "ca": g.crash_at, "rid": g.round_id, "now": time.time()})
        max_fly_time = 120  # Максимум 120 секунд (достатньо для 100x)
        while True:
            el = time.time() - g.start_ts
            if el > max_fly_time: break  # Захист від нескінченного польоту
            g.mult = g.calc_mult(el)
            if g.mult >= g.crash_at: g.mult = g.crash_at; break
            for uid, bet in list(bets.items()):
                if bet.get("cashed") or bet.get("lost"): continue
                ac = bet.get("auto_cashout")
                if ac and g.mult >= ac: await do_cashout(uid, g.mult)
            # ДОДАНО: elapsed для синхронізації графіка між клієнтами
            await broadcast({"t": "tick", "m": g.mult, "el": el, "pl": players_list(), "now": time.time()})
            await asyncio.sleep(0.1)  # 100ms для максимальної синхронізації
        g.phase = "crashed"; g.history.insert(0, g.crash_at); g.history = g.history[:20]
        for uid, bet in bets.items():
            if not bet.get("cashed"):
                bet["lost"] = True
        save_players()
        await broadcast({"t": "cr", "ca": g.crash_at, "rid": g.round_id, "h": g.history, "pl": players_list(), "now": time.time()})
        await asyncio.sleep(3)

@app.on_event("startup")
async def startup():
    # Встановлюємо webhook назад (він надійніший для production)
    try:
        webhook_url = "https://casino-bot-production-5113.up.railway.app/tg/webhook"
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", json={"url": webhook_url})
            result = r.json()
            if result.get("ok"):
                print(f"✅ Webhook set to {webhook_url}")
            else:
                print(f"⚠️ setWebhook response: {result}")
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")
    
    asyncio.create_task(game_loop())
    asyncio.create_task(auto_check_topups())
    asyncio.create_task(check_stars_payments())
    print("🔄 Started Stars payment fallback checker")

player_ips: dict = {}

@app.websocket("/ws/{uid}")
async def ws_ep(ws: WebSocket, uid: int):
    await ws.accept()
    
    # Перевірка ban
    if players.get(uid, {}).get("banned"):
        await ws.send_text(json.dumps({"t": "banned"}))
        await ws.close()
        return
    
    clients[uid] = ws
    ip = ws.headers.get("x-forwarded-for", ws.client.host if ws.client else "unknown")
    ip = ip.split(",")[0].strip()
    if uid not in player_ips:
        player_ips[uid] = []
    if ip not in player_ips[uid]:
        player_ips[uid].insert(0, ip)
        player_ips[uid] = player_ips[uid][:5]
    await ws.send_text(json.dumps({
        "t": "init", "phase": g.phase, "mult": g.mult, "ts": g.start_ts,
        "ca": g.crash_at, "rid": g.round_id, "h": g.history,
        "pl": players_list(), "bal": players.get(uid, {}).get("balance", 1.0),
        "nfts": players.get(uid, {}).get("nfts", []), "now": time.time()
    }))
    try:
        while True:
            d = json.loads(await ws.receive_text())
            a = d.get("a")

            if a == "auth":
                ref_by = d.get("ref_by")
                if uid not in players:
                    players[uid] = {"name": d.get("name", "Player"), "nick": d.get("nick", ""), "photo": d.get("photo", ""), "balance": 1.0, "nfts": []}
                    if ref_by and int(ref_by) != uid:
                        referrals[uid] = int(ref_by)
                        ref_name = players.get(int(ref_by), {}).get("name", "?")
                        add_log("referrals", {"uid": uid, "name": d.get("name", "Player"), "invited_by": int(ref_by), "invited_name": ref_name})
                else:
                    players[uid]["name"] = d.get("name", players[uid]["name"])
                    players[uid]["nick"] = d.get("nick", players[uid]["nick"])
                    players[uid]["photo"] = d.get("photo", players[uid]["photo"])
                save_players()

            elif a == "bet":
                if g.phase != "waiting": continue
                amt = float(d.get("amt", 0))
                bal = players.get(uid, {}).get("balance", 0)

                # Звичайна TON ставка
                if amt < 0.1 or amt > bal:
                    await ws.send_text(json.dumps({"t": "err", "msg": "Недостатньо TON"}))
                    continue
                players[uid]["balance"] = round(bal - amt, 4)
                bets[uid] = {"amount": amt, "auto_cashout": d.get("ac"), "cashed": False, "lost": False}
                add_log("bets", {"uid": uid, "name": players[uid].get("name", "?"), "amount": amt, "round_id": g.round_id})
                save_players()
                await ws.send_text(json.dumps({"t": "bet_ok", "amt": amt, "bal": players[uid]["balance"]}))
                await broadcast({"t": "newbet", "pl": players_list(), "now": time.time()})

            elif a == "cashout":
                if g.phase == "flying" and uid in bets:
                    await do_cashout(uid, g.mult)

            # НОВА ОБРОБКА: Перевірка підписки на канал
            elif a == "check_subscription":
                channel = "@pepe_GiftsNFT"
                user_id = int(d.get("user_id", uid))
                
                # РЕАЛЬНА перевірка підписки
                is_subscribed = await check_subscription(user_id, channel)
                
                await ws.send_text(json.dumps({
                    "t": "subscription_checked",
                    "subscribed": is_subscribed
                }))
            elif a == "topup_start":
                amt = float(d.get("amount", 0))
                if amt >= 0.1:
                    pending_topups[uid] = {"amount": amt, "ts": time.time(), "done": False}
                    await ws.send_text(json.dumps({"t": "topup_pending", "amount": amt}))

            elif a == "admin_find_user":
                if uid not in ADMIN_IDS: continue
                query = str(d.get("query", "")).strip().lstrip("@")
                found_user = None
                for pid, p in players.items():
                    if str(pid) == query or p.get("nick", "").lstrip("@") == query or p.get("name", "") == query:
                        found_user = {**p, "id": pid, "balance": p.get("balance", 0), "banned": p.get("banned", False)}
                        break
                if found_user:
                    await ws.send_text(json.dumps({"t": "admin_user_found", "user": found_user}))
                else:
                    await ws.send_text(json.dumps({"t": "admin_user_not_found"}))

            elif a == "admin_balance":
                if uid not in ADMIN_IDS: continue
                target = int(d.get("uid", 0))
                delta = float(d.get("delta", 0))
                if target in players:
                    players[target]["balance"] = round(max(0, players[target].get("balance", 0) + delta), 4)
                    save_players()
                    if target in clients:
                        try:
                            await clients[target].send_text(json.dumps({"t": "topup_ok", "credited": delta, "bal": players[target]["balance"]}))
                        except: pass

            elif a == "admin_set_balance":
                if uid not in ADMIN_IDS: continue
                target = int(d.get("uid", 0))
                new_bal = float(d.get("balance", 0))
                if target not in players:
                    players[target] = {"name": "?", "nick": "", "photo": "", "balance": 0, "nfts": []}
                players[target]["balance"] = round(max(0, new_bal), 4)
                save_players()
                if target in clients:
                    try:
                        await clients[target].send_text(json.dumps({"t": "topup_ok", "credited": 0, "bal": players[target]["balance"]}))
                    except: pass

            elif a == "admin_ban":
                if uid not in ADMIN_IDS: continue
                target = int(d.get("uid", 0))
                ban = bool(d.get("ban", True))
                if target in players:
                    players[target]["banned"] = ban
                    save_players()
                    if ban and target in clients:
                        try:
                            await clients[target].send_text(json.dumps({"t": "banned"}))
                        except: pass

            elif a == "admin_clear_nfts":
                if uid not in ADMIN_IDS: continue
                target = int(d.get("uid", 0))
                if target in players:
                    players[target]["nfts"] = []
                    save_players()

            elif a in ("withdraw_nft", "nft_sell_local"):
                nft_id = d.get("nft_id")
                try:
                    sell_price = float(d.get("price", 0) or 0)
                except Exception:
                    sell_price = 0
                nft_uid = d.get("nft_uid")
                action_type = d.get("type", "sell")
                print(f"💎 withdraw_nft request: nft_id={nft_id}, price={sell_price}, type={action_type}, uid={uid}")
                if uid in players and nft_id:
                    nfts = players[uid].get("nfts", [])
                    print(f"🔍 Player has {len(nfts)} NFTs: {[n.get('id') for n in nfts]}")
                    found_nft = None; new_nfts = []; removed = False
                    # Спочатку шукаємо точний збіг по uid
                    for n in nfts:
                        same_id = n.get("id") == nft_id
                        same_uid = not nft_uid or n.get("uid") == nft_uid
                        if same_id and same_uid and not removed:
                            found_nft = n; removed = True
                            print(f"✅ Found NFT (uid match): {n.get('name')} (id: {n.get('id')})")
                        else:
                            new_nfts.append(n)
                    # Якщо не знайдено по uid — шукаємо тільки по id (клієнт міг генерувати локальний uid)
                    if not found_nft:
                        new_nfts = []; removed = False
                        print(f"🔄 uid mismatch, searching by id only: nft_id={nft_id}")
                        for n in nfts:
                            if n.get("id") == nft_id and not removed:
                                found_nft = n; removed = True
                                print(f"✅ Found NFT (id only): {n.get('name')} (id: {n.get('id')})")
                            else:
                                new_nfts.append(n)
                    if found_nft:
                        name = players[uid].get("name", "?")
                        nick = players[uid].get("nick", "")
                        nick_str = f"@{nick}" if nick else f"uid:{uid}"
                        
                        if action_type == "withdraw_ton_fee":
                            fee = NFT_WITHDRAW_TON_FEE
                            balance = float(players[uid].get("balance", 0) or 0)
                            if balance < fee:
                                await ws.send_text(json.dumps({
                                    "t": "err",
                                    "msg": f"Недостатньо TON для виводу NFT. Потрібно {fee:.2f} TON, баланс {balance:.4f} TON"
                                }))
                                continue

                            print(f"🎁 NFT withdrawal: {found_nft.get('name')} by {name} (uid:{uid})")
                            players[uid]["nfts"] = new_nfts
                            players[uid]["balance"] = round(balance - fee, 4)
                            save_players()
                            add_log("withdrawals", {"uid": uid, "name": name, "nft_name": found_nft.get("name"), "nft_floor": found_nft.get("floor"), "sell_price": fee, "type": "withdraw_ton_fee"})
                            await ws.send_text(json.dumps({"t": "nft_withdrawn", "nft_id": nft_id, "nft_name": found_nft.get('name'), "bal": players[uid]["balance"], "msg": f"✅ {found_nft.get('name')} withdrawal requested. Fee: {fee:.2f} TON"}))
                            print(f"📨 Sending admin withdrawal notification to {sorted(ADMIN_IDS)}")
                            asyncio.create_task(send_admins(f"🎁 <b>NFT Withdrawal Request</b>\n\nUser: {name} ({nick_str})\nUID: <code>{uid}</code>\nNFT: <b>{found_nft.get('name')}</b>\nFloor: {found_nft.get('floor')} TON\nFee paid: {fee:.2f} TON\nBalance after fee: {players[uid]['balance']:.4f} TON\n\n⚠️ User must send 'HI' to @Pepe_sender for verification"))
                        elif action_type == "sell":
                            sell_price = float(found_nft.get("price") or found_nft.get("floor") or sell_price or 0)
                            players[uid]["nfts"] = new_nfts
                            players[uid]["balance"] = round(players[uid].get("balance", 0) + sell_price, 4)
                            save_players()
                            add_log("withdrawals", {"uid": uid, "name": name, "nft_name": found_nft.get("name"), "nft_floor": found_nft.get("floor"), "sell_price": sell_price, "type": "sell"})
                            await ws.send_text(json.dumps({"t": "nft_sold", "nft_id": nft_id, "amount": sell_price, "bal": players[uid]["balance"], "msg": f"✅ {found_nft.get('name')} продано за {sell_price} TON!"}))
                            asyncio.create_task(send_admins(f"💰 <b>Продаж NFT</b>\nКористувач: {name} ({nick_str})\nNFT: {found_nft.get('name')} (floor {found_nft.get('floor')} TON)\nПродано за: {sell_price} TON"))
                        else:
                            # Вивід через WebSocket (не Stars, не TON fee)
                            players[uid]["nfts"] = new_nfts
                            save_players()
                            add_log("withdrawals", {"uid": uid, "name": name, "nft_name": found_nft.get("name"), "nft_floor": found_nft.get("floor"), "sell_price": 0, "type": "withdraw"})
                            await ws.send_text(json.dumps({"t": "nft_withdrawn", "nft_id": nft_id, "nft_name": found_nft.get('name'), "msg": f"✅ {found_nft.get('name')} успішно виведено!"}))
                            
                            # Повідомлення адміну (правильний формат)
                            asyncio.create_task(send_admins(f"🎁 <b>NFT Withdrawal Request</b>\n\nUser: {name} ({nick_str})\nUID: <code>{uid}</code>\nNFT: <b>{found_nft.get('name')}</b>\nFloor: {found_nft.get('floor')} TON\nFee: FREE (no fee)\n\n⚠️ User must send 'HI' to @Pepe_sender for verification"))
                            
                            # Повідомлення користувачу з кнопкою
                            keyboard = {
                                "inline_keyboard": [[
                                    {"text": "📨 Send 'HI' to @Pepe_sender", "url": "https://t.me/Pepe_sender"}
                                ]]
                            }
                            asyncio.create_task(send_tg(uid, 
                                f"✅ <b>NFT Withdrawal Request Submitted!</b>\n\n"
                                f"NFT: <b>{found_nft.get('name')}</b>\n"
                                f"Floor: {found_nft.get('floor')} TON\n\n"
                                f"⚠️ <b>IMPORTANT:</b> To complete the withdrawal, you must:\n"
                                f"1️⃣ Click the button below\n"
                                f"2️⃣ Send the word <b>'HI'</b> to @Pepe_sender\n\n"
                                f"Your NFT will be sent after verification.",
                                reply_markup=keyboard
                            ))
                    else:
                        print(f"❌ NFT {nft_id} not found in player inventory")
                        await ws.send_text(json.dumps({"t": "err", "msg": "NFT не знайдено"}))
                else:
                    print(f"❌ Player {uid} not found or nft_id is None")

            elif a == "case_opened":
                # Списуємо баланс на сервері при відкритті кейса
                case_id = d.get("case_id", "")
                try:
                    case_price = float(d.get("price", 0) or 0)
                except Exception:
                    case_price = 0

                if uid not in players:
                    players[uid] = {"balance": 0, "nfts": [], "name": "Player", "nick": ""}

                # ── ЗАХИСТ FREE DAILY від подвійного відкриття з різних пристроїв ──
                if case_id == "free_daily":
                    last_open = players[uid].get("free_daily_last_open", 0)
                    cooldown = 86400  # 24 години
                    elapsed = time.time() - last_open
                    if elapsed < cooldown:
                        hours_left = math.ceil((cooldown - elapsed) / 3600)
                        print(f"[FREE_DAILY] {players[uid].get('name','?')} (uid:{uid}) — cooldown! {hours_left}h left")
                        await ws.send_text(json.dumps({"t": "free_daily_cooldown", "hours_left": hours_left, "msg": f"Wait {hours_left}h before opening again"}))
                        continue
                    # Записуємо час відкриття на сервері — до спіну
                    players[uid]["free_daily_last_open"] = time.time()
                    save_players()
                    print(f"[FREE_DAILY] {players[uid].get('name','?')} (uid:{uid}) — opened, cooldown set")
                    await ws.send_text(json.dumps({"t": "case_opened", "bal": players[uid].get("balance", 0), "case_id": "free_daily"}))
                    continue

                if case_price > 0:
                    server_bal = players[uid].get("balance", 0)
                    if server_bal < case_price:
                        await ws.send_text(json.dumps({"t": "err", "msg": "Недостатньо коштів"}))
                        continue
                    players[uid]["balance"] = round(server_bal - case_price, 4)
                    save_players()
                    print(f"[CASE] {players[uid].get('name','?')} (uid:{uid}) відкрив кейс '{d.get('case_name','')}' за {case_price} TON | Баланс: {server_bal} -> {players[uid]['balance']}")
                    await ws.send_text(json.dumps({"t": "case_opened", "bal": players[uid]["balance"]}))

            elif a == "case_win_keep":
                # Логування відкриття кейсу та виграшу
                case_name = d.get("case_name", "Unknown")
                nft_id = d.get("nft_id")
                nft_name = d.get("name", "Unknown")
                price = float(d.get("price", 0))
                is_nft = d.get("is_nft", True)
                name = players.get(uid, {}).get("name", "?")
                
                # Додаємо NFT в інвентар якщо це NFT
                if is_nft and nft_id:
                    if uid not in players:
                        players[uid] = {"balance": 0, "nfts": [], "name": name, "nick": ""}
                    
                    nft_entry = {
                        "uid": f"case_{uid}_{int(time.time()*1000)}_{random.randint(1000,9999)}",
                        "id": nft_id,
                        "name": nft_name,
                        "emoji": "🎁",
                        "rarity": "Common",
                        "price": price,
                        "floor": price,
                        "ts": time.time()
                    }
                    players[uid]["nfts"].append(nft_entry)
                    save_players()
                    print(f"🎁 NFT added from case: {nft_name} for {name} (uid:{uid})")
                    await ws.send_text(json.dumps({"t": "case_win_ok", "nft": nft_entry, "bal": players[uid].get("balance", 0)}))
                
                # Логуємо
                elif not is_nft and price > 0:
                    if uid not in players:
                        players[uid] = {"balance": 0, "nfts": [], "name": name, "nick": ""}
                    players[uid]["balance"] = round(players[uid].get("balance", 0) + price, 4)
                    save_players()
                    await ws.send_text(json.dumps({"t": "case_win_ok", "bal": players[uid]["balance"], "amount": price}))
                add_log("cases", {
                    "uid": uid,
                    "name": name,
                    "case_name": case_name,
                    "won_item": nft_name if is_nft else f"{price} TON",
                    "is_nft": is_nft,
                    "value": price,
                    "ts": time.time()
                })

            elif a == "case_win_sell_client":
                try:
                    price = float(d.get("price", 0) or 0)
                except Exception:
                    price = 0
                nft_name = d.get("name", "Unknown")
                if price <= 0:
                    await ws.send_text(json.dumps({"t": "err", "msg": "Невірна ціна NFT"}))
                    continue
                if uid not in players:
                    players[uid] = {"balance": 0, "nfts": [], "name": "Player", "nick": ""}
                players[uid]["balance"] = round(players[uid].get("balance", 0) + price, 4)
                save_players()
                add_log("cases", {"uid": uid, "name": players[uid].get("name", "?"), "case_name": d.get("case_name", "Unknown"), "won_item": nft_name, "is_nft": True, "value": price, "sold": True, "ts": time.time()})
                await ws.send_text(json.dumps({"t": "case_win_ok", "bal": players[uid]["balance"], "amount": price, "sold": True}))

            elif a == "case_ton_win":
                try:
                    amount = float(d.get("amount", 0) or 0)
                except Exception:
                    amount = 0
                if amount <= 0:
                    await ws.send_text(json.dumps({"t": "err", "msg": "Невірна сума виграшу"}))
                    continue
                if uid not in players:
                    players[uid] = {"balance": 0, "nfts": [], "name": "Player", "nick": ""}
                players[uid]["balance"] = round(players[uid].get("balance", 0) + amount, 4)
                save_players()
                add_log("cases", {"uid": uid, "name": players[uid].get("name", "?"), "case_name": d.get("case_name", "Unknown"), "won_item": f"{amount} TON", "is_nft": False, "value": amount, "ts": time.time()})
                await ws.send_text(json.dumps({"t": "case_win_ok", "bal": players[uid]["balance"], "amount": amount}))


    except WebSocketDisconnect:
        clients.pop(uid, None)
    except Exception as e:
        print(f"WS Error for {uid}: {e}")
        clients.pop(uid, None)

@app.get("/topup/{uid}/{amount}")
async def get_topup(uid: int, amount: float):
    if uid not in players:
        players[uid] = {"name": "Player", "nick": "", "photo": "", "balance": 0, "nfts": []}
    players[uid]["balance"] = round(players[uid]["balance"] + amount, 4)
    add_log("deposits", {"uid": uid, "name": players[uid].get("name", "?"), "amount": amount})
    if uid in referrals:
        ref_uid = referrals[uid]
        bonus = round(amount * 0.05, 4)
        if ref_uid not in players:
            players[ref_uid] = {"name": "?", "nick": "", "photo": "", "balance": 0, "nfts": []}
        players[ref_uid]["balance"] = round(players[ref_uid]["balance"] + bonus, 4)
        ref_earnings[ref_uid] = round(ref_earnings.get(ref_uid, 0) + bonus, 4)
        if ref_uid in clients:
            try: await clients[ref_uid].send_text(json.dumps({"t": "ref_bonus", "bonus": bonus, "bal": players[ref_uid]["balance"]}))
            except: pass
        await send_tg(ref_uid, f"👥 <b>Реферальний бонус!</b>\nВаш реферал поповнив на {amount} TON\nВаш бонус: <b>+{bonus} TON</b>")
    if uid in clients:
        try: await clients[uid].send_text(json.dumps({"t": "topup", "credited": amount, "bal": players[uid]["balance"]}))
        except: pass
    await send_tg(ADMIN_ID, f"💰 <b>Ручний депозит</b>\nКористувач: {players[uid].get('name','?')} (uid: {uid})\nСума: {amount} TON")
    return {"ok": True, "balance": players[uid]["balance"]}

@app.post("/topup/{uid}/{amount}")
async def post_topup(uid: int, amount: float):
    return await get_topup(uid, amount)

@app.get("/ref/{uid}")
async def get_ref(uid: int):
    my_refs = [r for r, by in referrals.items() if by == uid]
    return {"link": f"https://t.me/Pepe_GiftsBot?start=ref_{uid}", "count": len(my_refs), "earned": ref_earnings.get(uid, 0), "referrals": [{"uid": r, "name": players.get(r, {}).get("name", "?")} for r in my_refs]}

@app.get("/referrals")
async def get_referrals(uid: int):
    """Endpoint для bot.py - отримати інфо про рефералів"""
    my_refs = [r for r, by in referrals.items() if by == uid]
    return {"link": f"https://t.me/Pepe_GiftsBot?start=ref_{uid}", "count": len(my_refs), "earned": ref_earnings.get(uid, 0)}

@app.get("/get_balance")
async def get_balance_endpoint(uid: int):
    """Endpoint для bot.py - отримати баланс"""
    if uid not in players:
        return {"balance": 0}
    return {"balance": players[uid].get("balance", 0)}

@app.post("/set_referral")
async def set_referral_endpoint(request: Request):
    """Endpoint для bot.py - зберегти реферала"""
    try:
        data = await request.json()
        user_id = int(data.get("user_id"))
        referrer_id = int(data.get("referrer_id"))
        username = data.get("username", "")
        first_name = data.get("first_name", "User")
        
        # Перевірка: не можна бути рефералом самого себе
        if user_id == referrer_id:
            return {"success": False, "error": "Cannot refer yourself"}
        
        # Перевірка: чи вже є реферер
        if user_id in referrals:
            return {"success": False, "error": "Referrer already set"}
        
        # Зберігаємо реферала
        referrals[user_id] = referrer_id
        
        # Створюємо гравця якщо не існує
        if user_id not in players:
            players[user_id] = {
                "name": first_name,
                "nick": username,
                "balance": 0,
                "nfts": []
            }
        
        add_log("referrals", {
            "user": user_id,
            "name": first_name,
            "referred_by": referrer_id,
            "referrer_name": players.get(referrer_id, {}).get("name", "?")
        })
        
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

# DEBUG endpoint - додати реферала вручну
@app.get("/debug_add_ref")
async def debug_add_referral(user_id: int, referrer_id: int, admin_uid: int = 0):
    """Тестовий endpoint - додати реферала вручну"""
    if admin_uid not in ADMIN_IDS:
        return {"error": "Access denied"}
    
    if user_id in referrals:
        return {"error": f"User {user_id} вже має реферера: {referrals[user_id]}"}
    
    referrals[user_id] = referrer_id
    return {"success": True, "user_id": user_id, "referrer_id": referrer_id, "referrals": dict(referrals)}



@app.get("/admin_old", response_class=HTMLResponse)
async def admin_panel(request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red;font-family:monospace;padding:40px'>⛔ Access Denied</h2>", status_code=403)
    total_bets = sum(l.get("amount", 0) for l in logs["bets"])
    total_wins = sum(l.get("win", 0) for l in logs["cashouts"])
    total_deps = sum(l.get("amount", 0) for l in logs["deposits"])
    total_stars_ton = sum(l.get("ton", 0) for l in logs["stars"])
    pnl = total_bets - total_wins
    players_list_html = "".join([
        f'<tr><td><a href="/admin/player/{uid}?uid={admin_uid}" style="color:#4d8fff">{uid}</a></td><td>{p.get("name","?")}</td><td>{"@"+p.get("nick") if p.get("nick") else "-"}</td>'
        f'<td>{p.get("balance",0):.2f}</td><td>{len(p.get("nfts",[]))}</td>'
        f'<td style="font-size:10px;color:#888">{", ".join(player_ips.get(uid,[])[:2]) or "-"}</td>'
        f'<td>{"🚫" if p.get("banned") else "✅"}</td>'
        f'<td><a href="/admin/topup/{uid}/1?uid={admin_uid}" style="background:#0098ea;color:#fff;padding:2px 8px;border-radius:4px;text-decoration:none;font-size:11px;margin-right:2px">+1</a>'
        f'<a href="/admin/topup/{uid}/5?uid={admin_uid}" style="background:#6c4fff;color:#fff;padding:2px 8px;border-radius:4px;text-decoration:none;font-size:11px;margin-right:2px">+5</a>'
        f'<a href="/admin/set_balance/{uid}?amount=0&uid={admin_uid}" style="background:#ff4d4d;color:#fff;padding:2px 8px;border-radius:4px;text-decoration:none;font-size:11px">-ALL</a></td></tr>'
        for uid, p in list(players.items())[:100]
    ])
    bets_html = "".join([f'<tr><td>{l.get("name","?")}</td><td>{l.get("amount",0):.2f}</td><td>{l.get("nft","")}</td><td>{l.get("round_id","")}</td><td>{time.strftime("%H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in logs["bets"][:20]])
    cashouts_html = "".join([f'<tr><td>{l.get("name","?")}</td><td>{l.get("bet",0):.2f}</td><td>{l.get("win",0):.2f}</td><td>{l.get("mult",0):.2f}x</td><td>{"🎁 "+str(l["nft"]) if l.get("nft") else "TON"}</td><td>{time.strftime("%H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in logs["cashouts"][:20]])
    deps_html = "".join([f'<tr><td>{l.get("name","?")}</td><td>{l.get("uid","")}</td><td>{l.get("amount",0):.2f}</td><td>{l.get("note","")}</td><td>{time.strftime("%H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in logs["deposits"][:20]])
    stars_html = "".join([f'<tr><td>{l.get("name","?")}</td><td>{l.get("uid","")}</td><td>{l.get("stars",0)} ⭐</td><td>{l.get("ton",0):.4f} TON</td><td>{time.strftime("%H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in logs["stars"][:20]])
    refs_html = "".join([f'<tr><td>{l.get("name","?")}</td><td>{l.get("invited_name","?")}</td><td>{time.strftime("%H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in logs["referrals"][:20]])
    withdrawals_html = "".join([f'<tr><td>{l.get("name","?")}</td><td>{l.get("nft_name","?")}</td><td>{l.get("nft_floor",0)}</td><td>{l.get("sell_price",0)}</td><td>{l.get("type","")}</td><td>{time.strftime("%H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in logs["withdrawals"][:20]])
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Admin</title>
<style>body{{font-family:monospace;background:#0a0e1a;color:#ccc;padding:20px}}h1{{color:#f5c500;margin-bottom:20px}}h2{{color:#aa77ff;margin:20px 0 10px}}.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:24px}}.stat{{background:#111827;border-radius:12px;padding:16px;text-align:center}}.stat .v{{font-size:22px;font-weight:700;color:#f5c500}}.stat .l{{font-size:11px;color:#556;margin-top:4px}}table{{width:100%;border-collapse:collapse;background:#111827;border-radius:8px;overflow:hidden;margin-bottom:20px}}th{{background:#1a2236;padding:8px 12px;text-align:left;font-size:11px;color:#556;text-transform:uppercase}}td{{padding:7px 12px;border-bottom:1px solid #1a2236;font-size:12px}}</style></head><body>
<h1>🎰 Casino Admin <span style="color:#0098ea;font-size:14px">uid:{admin_uid}</span></h1>
<div class="stats">
  <div class="stat"><div class="v">{len(players)}</div><div class="l">Гравців / онлайн: {len(clients)}</div></div>
  <div class="stat"><div class="v">{total_deps:.1f}</div><div class="l">TON депозитів</div></div>
  <div class="stat"><div class="v" style="color:#aa77ff">{total_stars_ton:.2f}</div><div class="l">TON через Stars ⭐</div></div>
  <div class="stat"><div class="v">{total_wins:.1f}</div><div class="l">TON виплат</div></div>
  <div class="stat"><div class="v" style="color:{"#00e676" if pnl>=0 else "#ff1744"}">{pnl:+.1f}</div><div class="l">TON прибуток</div></div>
</div>
<h2>👥 Всі гравці</h2>
<form action="/admin/player" method="get" style="margin-bottom:12px;display:flex;gap:8px">
<input type="hidden" name="uid" value="{admin_uid}">
<input type="number" name="search_uid" placeholder="Search by UID" style="padding:8px;background:#111827;border:1px solid #333;color:#fff;border-radius:4px;flex:1">
<input type="text" name="search_username" placeholder="Search by @username" style="padding:8px;background:#111827;border:1px solid #333;color:#fff;border-radius:4px;flex:1">
<button type="submit" style="padding:8px 16px;background:#4d8fff;color:#fff;border:none;border-radius:4px;cursor:pointer">🔍 Search</button>
</form>
<table><tr><th>UID</th><th>Ім'я</th><th>@</th><th>Баланс</th><th>NFT</th><th>IP</th><th>Status</th><th>Дія</th></tr>{players_list_html}</table>
<h2>⭐ Stars депозити</h2><table><tr><th>Гравець</th><th>UID</th><th>Stars</th><th>TON</th><th>Час</th></tr>{stars_html}</table>
<h2>💰 Ставки</h2><table><tr><th>Гравець</th><th>Ставка</th><th>NFT</th><th>Раунд</th><th>Час</th></tr>{bets_html}</table>
<h2>🚀 Кешаути</h2><table><tr><th>Гравець</th><th>Ставка</th><th>Виграш</th><th>Множник</th><th>NFT</th><th>Час</th></tr>{cashouts_html}</table>
<h2>💎 Депозити</h2><table><tr><th>Гравець</th><th>UID</th><th>Сума</th><th>Примітка</th><th>Час</th></tr>{deps_html}</table>
<h2>🎁 Виводи NFT</h2><table><tr><th>Гравець</th><th>NFT</th><th>Floor</th><th>Продано за</th><th>Тип</th><th>Час</th></tr>{withdrawals_html}</table>
<h2>👥 Реферали</h2><table><tr><th>Новий гравець</th><th>Запросив</th><th>Час</th></tr>{refs_html}</table>
</body></html>"""

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel_v2(request: Request):
    try:
        admin_uid = int(request.query_params.get("uid", 0))
    except ValueError:
        admin_uid = 0
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red;font-family:monospace;padding:40px'>Access Denied</h2>", status_code=403)

    def esc(value):
        return html.escape(str(value if value is not None else ""))

    def dt(ts):
        return time.strftime("%d.%m %H:%M:%S", time.localtime(float(ts or 0)))

    def ton(value, digits=2):
        try:
            return f"{float(value or 0):.{digits}f}"
        except (TypeError, ValueError):
            return f"{0:.{digits}f}"

    def empty_row(cols, text="No data"):
        return f'<tr><td colspan="{cols}" class="empty">{esc(text)}</td></tr>'

    total_bets = sum(float(l.get("amount", 0) or 0) for l in logs["bets"])
    total_wins = sum(float(l.get("win", 0) or 0) for l in logs["cashouts"])
    total_deps = sum(float(l.get("amount", 0) or 0) for l in logs["deposits"])
    total_stars_ton = sum(float(l.get("ton", 0) or 0) for l in logs["stars"])
    total_balances = sum(float(p.get("balance", 0) or 0) for p in players.values())
    total_nfts = sum(len(p.get("nfts", [])) for p in players.values())
    banned_count = sum(1 for p in players.values() if p.get("banned"))
    pnl = total_bets - total_wins

    ordered_players = sorted(players.items(), key=lambda item: float(item[1].get("balance", 0) or 0), reverse=True)
    player_rows = []
    for uid, p in ordered_players[:150]:
        status = '<span class="badge bad">Banned</span>' if p.get("banned") else '<span class="badge good">Active</span>'
        player_rows.append(
            f'<tr><td><a class="link" href="/admin/player/{uid}?uid={admin_uid}">{uid}</a></td>'
            f'<td><strong>{esc(p.get("name","?"))}</strong><span class="muted block">{esc("@"+p.get("nick") if p.get("nick") else "no username")}</span></td>'
            f'<td class="num">{ton(p.get("balance",0), 4)}</td>'
            f'<td class="num">{len(p.get("nfts", []))}</td>'
            f'<td>{esc(", ".join(player_ips.get(uid, [])[:2]) or "-")}</td>'
            f'<td>{status}</td>'
            f'<td class="actions"><a class="btn mini green" href="/admin/topup/{uid}/1?uid={admin_uid}">+1</a>'
            f'<a class="btn mini green" href="/admin/topup/{uid}/5?uid={admin_uid}">+5</a>'
            f'<a class="btn mini blue" href="/admin/player/{uid}?uid={admin_uid}">Open</a>'
            f'<a class="btn mini red" href="/admin/set_balance/{uid}?amount=0&uid={admin_uid}">Zero</a></td></tr>'
        )
    players_list_html = "".join(player_rows) or empty_row(7, "No players yet")

    bets_html = "".join([
        f'<tr><td>{esc(l.get("name","?"))}<span class="muted block">uid {esc(l.get("uid",""))}</span></td><td class="num">{ton(l.get("amount"), 4)}</td><td>{esc(l.get("nft") or "TON")}</td><td>{esc(l.get("round_id",""))}</td><td>{dt(l.get("ts"))}</td></tr>'
        for l in logs["bets"][:80]
    ]) or empty_row(5)
    cashouts_html = "".join([
        f'<tr><td>{esc(l.get("name","?"))}<span class="muted block">uid {esc(l.get("uid",""))}</span></td><td class="num">{ton(l.get("bet"), 4)}</td><td class="num">{ton(l.get("win"), 4)}</td><td>{ton(l.get("mult"), 2)}x</td><td>{esc(l.get("nft") or "TON")}</td><td>{dt(l.get("ts"))}</td></tr>'
        for l in logs["cashouts"][:80]
    ]) or empty_row(6)
    deps_html = "".join([
        f'<tr><td>{esc(l.get("name","?"))}</td><td>{esc(l.get("uid",""))}</td><td class="num">{ton(l.get("amount"), 4)}</td><td>{esc(l.get("note",""))}</td><td>{dt(l.get("ts"))}</td></tr>'
        for l in logs["deposits"][:80]
    ]) or empty_row(5)
    stars_html = "".join([
        f'<tr><td>{esc(l.get("name","?"))}</td><td>{esc(l.get("uid",""))}</td><td class="num">{esc(l.get("stars",0))}</td><td class="num">{ton(l.get("ton"), 4)}</td><td>{dt(l.get("ts"))}</td></tr>'
        for l in logs["stars"][:80]
    ]) or empty_row(5)
    refs_html = "".join([
        f'<tr><td>{esc(l.get("name","?"))}</td><td>{esc(l.get("invited_name","?"))}</td><td>{dt(l.get("ts"))}</td></tr>'
        for l in logs["referrals"][:80]
    ]) or empty_row(3)
    withdrawals_html = "".join([
        f'<tr><td>{esc(l.get("name","?"))}<span class="muted block">uid {esc(l.get("uid",""))}</span></td><td>{esc(l.get("nft_name","?"))}</td><td class="num">{ton(l.get("nft_floor"), 2)}</td><td class="num">{ton(l.get("sell_price"), 2)}</td><td><span class="badge">{esc(l.get("type",""))}</span></td><td>{dt(l.get("ts"))}</td></tr>'
        for l in logs["withdrawals"][:80]
    ]) or empty_row(6)
    cases_html = "".join([
        f'<tr><td>{esc(l.get("name","?"))}<span class="muted block">uid {esc(l.get("uid",""))}</span></td><td>{esc(l.get("case_name","?"))}</td><td>{esc(l.get("won_item","?"))}</td><td class="num">{ton(l.get("value"), 2)}</td><td>{dt(l.get("ts"))}</td></tr>'
        for l in logs["cases"][:80]
    ]) or empty_row(5)

    pnl_color = "#22c55e" if pnl >= 0 else "#ef4444"
    now = time.strftime("%d.%m %H:%M:%S")
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Casino Admin</title>
<style>
:root{{--bg:#070b16;--panel:#101827;--panel2:#0c1220;--line:#22304a;--text:#eef4ff;--muted:#8290aa;--blue:#38bdf8;--green:#22c55e;--red:#ef4444}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif;font-size:14px}}a{{color:inherit}}.wrap{{max-width:1480px;margin:0 auto;padding:22px}}
.top{{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:18px}}h1{{font-size:24px;margin:0}}.sub{{color:var(--muted);font-size:12px;margin-top:5px}}.pill{{display:inline-flex;align-items:center;gap:7px;border:1px solid var(--line);background:var(--panel2);padding:8px 11px;border-radius:999px;color:#cbd5e1;text-decoration:none;font-weight:700;font-size:12px}}
.stats{{display:grid;grid-template-columns:repeat(8,minmax(130px,1fr));gap:10px;margin-bottom:16px}}.stat{{background:linear-gradient(180deg,#121c2e,#0d1424);border:1px solid var(--line);border-radius:12px;padding:14px}}.stat .v{{font-size:22px;font-weight:800;letter-spacing:.2px}}.stat .l{{color:var(--muted);font-size:11px;margin-top:5px;text-transform:uppercase;letter-spacing:.06em}}
.tabs{{display:flex;gap:8px;overflow:auto;padding:6px 0 14px;position:sticky;top:0;background:linear-gradient(var(--bg),rgba(7,11,22,.92));z-index:5}}.tab{{border:1px solid var(--line);background:#0d1424;color:#cbd5e1;border-radius:10px;padding:10px 12px;font-weight:800;cursor:pointer;white-space:nowrap}}.tab.active{{background:#1e3a5f;border-color:#38bdf866;color:white}}
.panel{{display:none;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:18px;box-shadow:0 12px 36px rgba(0,0,0,.22)}}.panel.active{{display:block}}.panel-head{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}}h2{{font-size:17px;margin:0}}.muted{{color:var(--muted);font-size:12px}}.block{{display:block;margin-top:3px}}
.search{{display:grid;grid-template-columns:1fr 1fr auto;gap:10px;margin-bottom:12px}}input{{width:100%;background:#090f1d;border:1px solid var(--line);color:var(--text);border-radius:10px;padding:11px 12px;outline:none}}button,.btn{{border:0;border-radius:10px;background:#1d4ed8;color:white;padding:10px 13px;text-decoration:none;font-weight:800;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;gap:6px}}.btn.mini{{padding:6px 8px;font-size:12px;border-radius:8px}}.green{{background:#15803d}}.red{{background:#b91c1c}}.blue{{background:#2563eb}}
.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px}}table{{width:100%;border-collapse:collapse;min-width:760px}}th{{background:#0b1323;color:#93a4c3;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.06em;padding:10px 12px;position:sticky;top:0}}td{{padding:10px 12px;border-top:1px solid #1b2740;vertical-align:middle}}tr:hover td{{background:#111c30}}.num{{font-variant-numeric:tabular-nums;text-align:right}}.actions{{display:flex;gap:6px;flex-wrap:wrap}}.link{{color:#7dd3fc;font-weight:800;text-decoration:none}}.badge{{display:inline-flex;border:1px solid #334155;background:#111827;color:#cbd5e1;border-radius:999px;padding:3px 8px;font-size:11px;font-weight:800}}.badge.good{{border-color:#166534;color:#86efac}}.badge.bad{{border-color:#7f1d1d;color:#fca5a5}}.empty{{text-align:center;color:var(--muted);padding:28px!important}}
@media(max-width:900px){{.wrap{{padding:14px}}.top{{align-items:flex-start;flex-direction:column}}.stats{{grid-template-columns:repeat(2,1fr)}}.search{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">
<div class="top"><div><h1>Casino Admin</h1><div class="sub">Admin UID: {admin_uid} · online {len(clients)} · updated {now}</div></div><div style="display:flex;gap:8px;flex-wrap:wrap"><a class="pill" href="/admin?uid={admin_uid}">Refresh</a><a class="pill" href="/api/status">API status</a><a class="pill" href="/admin_old?uid={admin_uid}">Old view</a></div></div>
<div class="stats">
  <div class="stat"><div class="v">{len(players)}</div><div class="l">Players</div></div><div class="stat"><div class="v">{len(clients)}</div><div class="l">Online</div></div><div class="stat"><div class="v">{banned_count}</div><div class="l">Banned</div></div><div class="stat"><div class="v">{total_nfts}</div><div class="l">NFT in users</div></div>
  <div class="stat"><div class="v">{ton(total_deps,1)}</div><div class="l">Deposits TON</div></div><div class="stat"><div class="v">{ton(total_stars_ton,2)}</div><div class="l">Stars to TON</div></div><div class="stat"><div class="v">{ton(total_balances,1)}</div><div class="l">User balances</div></div><div class="stat"><div class="v" style="color:{pnl_color}">{pnl:+.1f}</div><div class="l">Game P/L</div></div>
</div>
<div class="tabs"><button class="tab active" data-tab="players">Players</button><button class="tab" data-tab="money">Money</button><button class="tab" data-tab="game">Game</button><button class="tab" data-tab="nft">NFT</button><button class="tab" data-tab="refs">Refs</button></div>
<section class="panel active" id="tab-players"><div class="panel-head"><h2>Players</h2><span class="muted">Top 150 by balance</span></div><form class="search" action="/admin/player" method="get"><input type="hidden" name="uid" value="{admin_uid}"><input type="number" name="search_uid" placeholder="Search UID"><input type="text" name="search_username" placeholder="Search @username"><button type="submit">Search</button></form><div class="table-wrap"><table><tr><th>UID</th><th>User</th><th class="num">Balance</th><th class="num">NFT</th><th>IP</th><th>Status</th><th>Actions</th></tr>{players_list_html}</table></div></section>
<section class="panel" id="tab-money"><div class="panel-head"><h2>Money</h2><span class="muted">Deposits and Stars</span></div><h2 style="margin:4px 0 10px">TON deposits</h2><div class="table-wrap"><table><tr><th>User</th><th>UID</th><th class="num">Amount</th><th>Note</th><th>Time</th></tr>{deps_html}</table></div><h2 style="margin:18px 0 10px">Stars deposits</h2><div class="table-wrap"><table><tr><th>User</th><th>UID</th><th class="num">Stars</th><th class="num">TON</th><th>Time</th></tr>{stars_html}</table></div></section>
<section class="panel" id="tab-game"><div class="panel-head"><h2>Game Logs</h2><span class="muted">Bets, cashouts and cases</span></div><h2 style="margin:4px 0 10px">Bets</h2><div class="table-wrap"><table><tr><th>User</th><th class="num">Bet</th><th>Type</th><th>Round</th><th>Time</th></tr>{bets_html}</table></div><h2 style="margin:18px 0 10px">Cashouts</h2><div class="table-wrap"><table><tr><th>User</th><th class="num">Bet</th><th class="num">Win</th><th>Mult</th><th>Prize</th><th>Time</th></tr>{cashouts_html}</table></div><h2 style="margin:18px 0 10px">Cases</h2><div class="table-wrap"><table><tr><th>User</th><th>Case</th><th>Won</th><th class="num">Value</th><th>Time</th></tr>{cases_html}</table></div></section>
<section class="panel" id="tab-nft"><div class="panel-head"><h2>NFT Withdrawals</h2><span class="muted">Sell and withdraw requests</span></div><div class="table-wrap"><table><tr><th>User</th><th>NFT</th><th class="num">Floor</th><th class="num">Amount/Fee</th><th>Type</th><th>Time</th></tr>{withdrawals_html}</table></div></section>
<section class="panel" id="tab-refs"><div class="panel-head"><h2>Referrals</h2><span class="muted">Invite logs</span></div><div class="table-wrap"><table><tr><th>New player</th><th>Invited by</th><th>Time</th></tr>{refs_html}</table></div></section>
</div><script>document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{{document.querySelectorAll('.tab').forEach(b=>b.classList.remove('active'));document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));btn.classList.add('active');document.getElementById('tab-'+btn.dataset.tab).classList.add('active');}}));</script></body></html>"""

@app.get("/admin/topup/{uid}/{amount}")
async def admin_topup_get(uid: int, amount: float, request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red'>⛔ Access Denied</h2>", status_code=403)
    await get_topup(uid, amount)
    return HTMLResponse(f'<script>window.location="/admin?uid={admin_uid}"</script>')

@app.get("/admin/set_balance/{uid}")
async def admin_set_balance(uid: int, request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    amount = float(request.query_params.get("amount", 0))
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red'>⛔ Access Denied</h2>", status_code=403)
    if uid not in players:
        players[uid] = {"balance": 0, "nfts": [], "name": f"User{uid}"}
    old_balance = players[uid].get("balance", 0)
    players[uid]["balance"] = round(amount, 4)
    save_players()
    logs["deposits"].append({"uid": uid, "name": players[uid].get("name", "?"), "amount": amount - old_balance, "note": f"Admin set to {amount}", "ts": time.time()})
    return HTMLResponse(f'<script>window.location="/admin?uid={admin_uid}"</script>')

@app.get("/admin/ban/{uid}")
async def admin_ban(uid: int, request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red'>⛔ Access Denied</h2>", status_code=403)
    if uid not in players:
        players[uid] = {"balance": 0, "nfts": [], "name": f"User{uid}"}
    players[uid]["banned"] = True
    save_players()
    return HTMLResponse(f'<script>window.location="/admin?uid={admin_uid}"</script>')

@app.get("/admin/unban/{uid}")
async def admin_unban(uid: int, request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red'>⛔ Access Denied</h2>", status_code=403)
    if uid in players:
        players[uid]["banned"] = False
        save_players()
    return HTMLResponse(f'<script>window.location="/admin?uid={admin_uid}"</script>')

@app.get("/admin/player")
async def admin_player_search(request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    search_uid = request.query_params.get("search_uid", "")
    search_username = request.query_params.get("search_username", "")
    
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red'>⛔ Access Denied</h2>", status_code=403)
    
    # Пошук по UID
    if search_uid:
        try:
            uid_to_find = int(search_uid)
            return RedirectResponse(url=f"/admin/player/{uid_to_find}?uid={admin_uid}")
        except:
            pass
    
    # Пошук по username
    if search_username:
        search_username = search_username.strip().lower().replace("@", "")
        for uid, p in players.items():
            nick = p.get("nick", "").lower()
            if nick == search_username:
                return RedirectResponse(url=f"/admin/player/{uid}?uid={admin_uid}")
        return HTMLResponse(f"<h2>User @{search_username} not found</h2><p><a href='/admin?uid={admin_uid}'>Back</a></p>", status_code=404)
    
    return RedirectResponse(url=f"/admin?uid={admin_uid}")

@app.get("/admin/player/{uid}", response_class=HTMLResponse)
async def admin_player_detail(uid: int, request: Request):
    admin_uid = int(request.query_params.get("uid", 0))
    if admin_uid not in ADMIN_IDS:
        return HTMLResponse("<h2 style='color:red'>⛔ Access Denied</h2>", status_code=403)
    
    player = players.get(uid, {})
    if not player:
        return HTMLResponse(f"<h2 style='color:red'>Player {uid} not found</h2><p><a href='/admin?uid={admin_uid}'>Back</a></p>", status_code=404)
    
    player_bets = [l for l in logs["bets"] if l.get("uid") == uid]
    player_cashouts = [l for l in logs["cashouts"] if l.get("uid") == uid]
    player_deposits = [l for l in logs["deposits"] if l.get("uid") == uid]
    player_cases = [l for l in logs["cases"] if l.get("uid") == uid]
    player_nft_actions = [l for l in logs["withdrawals"] if l.get("uid") == uid]
    
    total_bets = sum(b.get("amount", 0) for b in player_bets)
    total_wins = sum(c.get("win", 0) for c in player_cashouts)
    total_deposits = sum(d.get("amount", 0) for d in player_deposits)
    
    bets_html = "".join([f'<tr><td>{l.get("amount",0):.2f}</td><td>{l.get("round_id","")}</td><td>{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in player_bets[-100:]])
    cashouts_html = "".join([f'<tr><td>{l.get("bet",0):.2f}</td><td>{l.get("win",0):.2f}</td><td>{l.get("mult",0):.2f}x</td><td>{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in player_cashouts[-100:]])
    deposits_html = "".join([f'<tr><td>{l.get("amount",0):.2f}</td><td>{l.get("note","")}</td><td>{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in player_deposits[-100:]])
    cases_html = "".join([f'<tr><td>{l.get("case_name","?")}</td><td>{"🎁 " + l.get("won_item","?") if l.get("is_nft") else "💰 " + l.get("won_item","?")}</td><td>{l.get("value",0):.2f} TON</td><td>{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in player_cases[-100:]])
    nft_actions_html = "".join([f'<tr><td>{l.get("nft_name","?")}</td><td>{l.get("nft_floor",0):.2f}</td><td>{"💰 Sold" if l.get("type")=="sell" else "📤 Withdrawn"}</td><td>{l.get("sell_price",0):.2f if l.get("type")=="sell" else "-"}</td><td>{time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(l.get("ts",0)))}</td></tr>' for l in player_nft_actions[-100:]])
    
    current_nfts_html = "".join([f'<tr><td>{n.get("name","?")}</td><td>{n.get("rarity","?")}</td><td>{n.get("price",0):.2f}</td></tr>' for n in player.get("nfts", [])])
    
    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Player {uid}</title>
    <style>body{{font-family:monospace;background:#0a0e27;color:#fff;padding:20px;font-size:13px}}h1{{font-size:24px}}h2{{font-size:18px;margin-top:30px}}h3{{font-size:16px}}table{{border-collapse:collapse;width:100%;margin:20px 0;font-size:12px}}td,th{{border:1px solid #333;padding:6px;text-align:left}}th{{background:#1a1a2e;font-weight:600}}a{{color:#4d8fff;text-decoration:none}}.btn{{background:#4d8fff;color:#fff;padding:8px 16px;border-radius:8px;display:inline-block;margin:4px;text-decoration:none;font-size:13px}}.danger{{background:#ff4d4d}}input,button{{padding:8px;margin:4px}}</style>
    </head><body>
    <h1>👤 Player: {uid}</h1>
    <p><a href="/admin?uid={admin_uid}">← Back to Admin</a></p>
    
    <h2>📊 Stats</h2>
    <p>Name: <b>{player.get("name", "Unknown")}</b></p>
    <p>Username: <b>@{player.get("nick", "none")}</b></p>
    <p>Balance: <b>{player.get("balance", 0):.4f} TON</b></p>
    <p>Current NFTs: <b>{len(player.get("nfts", []))}</b></p>
    <p>Banned: <b>{"❌ Yes" if player.get("banned") else "✅ No"}</b></p>
    <p>Total Bets: <b>{total_bets:.2f} TON</b> ({len(player_bets)} bets)</p>
    <p>Total Wins: <b>{total_wins:.2f} TON</b> ({len(player_cashouts)} cashouts)</p>
    <p>Total Deposits: <b>{total_deposits:.2f} TON</b></p>
    <p>Cases Opened: <b>{len(player_cases)}</b></p>
    <p>NFT Actions: <b>{len(player_nft_actions)}</b> (sold/withdrawn)</p>
    <p>P/L: <b style="color:{'#0f0' if (total_wins - total_bets) > 0 else '#f00'}">{(total_wins - total_bets):.2f} TON</b></p>
    
    <h3>⚙️ Actions</h3>
    <a class="btn danger" href="/admin/set_balance/{uid}?amount=0&uid={admin_uid}">Set Balance to 0</a>
    <a class="btn danger" href="/admin/ban/{uid}?uid={admin_uid}">🚫 Ban</a>
    <a class="btn" href="/admin/unban/{uid}?uid={admin_uid}">✅ Unban</a>
    
    <h4>💰 Set Custom Balance</h4>
    <form action="/admin/set_balance/{uid}" method="get">
    <input type="hidden" name="uid" value="{admin_uid}">
    <input type="number" name="amount" step="0.01" placeholder="Amount TON" style="background:#1a1a2e;border:1px solid #333;color:#fff;border-radius:4px">
    <button type="submit" style="background:#4d8fff;color:#fff;border:none;border-radius:4px;cursor:pointer">Set</button>
    </form>
    
    <h2>🎁 Current NFTs ({len(player.get("nfts", []))})</h2>
    <table><tr><th>Name</th><th>Rarity</th><th>Value</th></tr>{current_nfts_html or '<tr><td colspan="3">No NFTs</td></tr>'}</table>
    
    <h2>🎰 Cases Opened ({len(player_cases)})</h2>
    <table><tr><th>Case</th><th>Won</th><th>Value</th><th>Time</th></tr>{cases_html or '<tr><td colspan="4">No cases opened</td></tr>'}</table>
    
    <h2>💎 NFT Actions ({len(player_nft_actions)})</h2>
    <table><tr><th>NFT</th><th>Floor</th><th>Action</th><th>Amount</th><th>Time</th></tr>{nft_actions_html or '<tr><td colspan="5">No NFT actions</td></tr>'}</table>
    
    <h2>🎲 Bets ({len(player_bets)})</h2>
    <table><tr><th>Amount</th><th>Round</th><th>Time</th></tr>{bets_html or '<tr><td colspan="3">No bets</td></tr>'}</table>
    
    <h2>💰 Cashouts ({len(player_cashouts)})</h2>
    <table><tr><th>Bet</th><th>Win</th><th>Mult</th><th>Time</th></tr>{cashouts_html or '<tr><td colspan="4">No cashouts</td></tr>'}</table>
    
    <h2>💳 Deposits ({len(player_deposits)})</h2>
    <table><tr><th>Amount</th><th>Note</th><th>Time</th></tr>{deposits_html or '<tr><td colspan="3">No deposits</td></tr>'}</table>
    
    </body></html>"""



# ============================================================================
# NFT PRICE API PROXY - для обходу CORS помилок
# ============================================================================
@app.post("/api/nft-price")
async def nft_price_proxy(request: Request):
    """Проксі для запитів до tgmrkt.io API (обхід CORS)"""
    try:
        data = await request.json()
        collection_name = data.get('collectionName')
        
        if not collection_name:
            return JSONResponse({"success": False, "error": "collectionName required"}, status_code=400)
        
        # Робимо запит до tgmrkt.io з серверу (немає CORS проблеми)
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                'https://api.tgmrkt.io/api/v1/gifts/saling',
                headers={
                    'Authorization': f'Bot {BOT_TOKEN}',
                    'Content-Type': 'application/json',
                },
                json={
                    'collectionNames': [collection_name],
                    'modelNames': [],
                    'backdropNames': [],
                    'symbolNames': [],
                    'ordering': 'Price',
                    'lowToHigh': True,
                    'maxPrice': None,
                    'minPrice': None,
                    'mintable': None,
                    'number': None,
                    'count': 1,
                    'cursor': '',
                    'query': None,
                    'promotedFirst': False,
                },
                timeout=10.0
            )
            
            if resp.status_code != 200:
                return JSONResponse({"success": False, "error": f"API returned {resp.status_code}"})
            
            api_data = resp.json()
            gifts = api_data.get('gifts', [])
            
            if not gifts:
                return JSONResponse({"success": False, "error": "No gifts found"})
            
            sale_price = gifts[0].get('salePrice')
            if sale_price is None:
                return JSONResponse({"success": False, "error": "No price found"})
            
            # Конвертуємо з nanoTON в TON
            price_ton = round(sale_price / 1_000_000_000, 2)
            
            return JSONResponse({
                "success": True,
                "price": price_ton,
                "collectionName": collection_name
            })
            
    except httpx.TimeoutException:
        return JSONResponse({"success": False, "error": "Timeout"}, status_code=504)
    except Exception as e:
        print(f"[NFT Price API] Error: {e}")
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@app.get("/", response_class=HTMLResponse)
async def root():
    for filename in ("index (8).html", "index (7).html", "index.html"):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            continue
    return HTMLResponse("<h1>Game loading...</h1><p>index file not found. Please check deployment.</p>", status_code=500)

@app.get("/tonconnect-manifest.json")
async def tonconnect_manifest():
    return JSONResponse({
        "url": "https://casino-bot-production-5113.up.railway.app",
        "name": "Rocket Casino",
        "iconUrl": "https://raw.githubusercontent.com/zabrockijdima1-lgtm/casino-bot/main/pepe-flower.png"
    }, headers={"Access-Control-Allow-Origin": "*"})

# Кеш для TonConnect JS бібліотеки
_tonconnect_js_cache: bytes = None

@app.get("/static/tonconnect-ui.min.js")
async def serve_tonconnect_js():
    global _tonconnect_js_cache
    # Спробуємо прочитати з файлу (якщо є в репозиторії)
    for fname in ["tonconnect-ui.min.js", "tonconnnnect-ui.min.js", "static/tonconnect-ui.min.js"]:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                content = f.read()
            return Response(content=content, media_type="application/javascript",
                          headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=86400"})
    # Якщо файлу немає — беремо з CDN і кешуємо в пам'яті
    if _tonconnect_js_cache:
        return Response(content=_tonconnect_js_cache, media_type="application/javascript",
                      headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=3600"})
    import httpx
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get("https://unpkg.com/@tonconnect/ui@2.0.10/dist/tonconnect-ui.min.js")
            if r.status_code == 200:
                _tonconnect_js_cache = r.content
                return Response(content=_tonconnect_js_cache, media_type="application/javascript",
                              headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "public, max-age=3600"})
    except Exception as e:
        print(f"Failed to fetch TonConnect from CDN: {e}")
    return Response(content=b"// TonConnect not available", media_type="application/javascript", status_code=503)

@app.get("/api/status")
async def api_status():
    return {"status": "ok", "round": g.round_id, "phase": g.phase, "players": len(clients), "version": "v3_fix_cashout_nft_admin", "nft_withdraw_fee": NFT_WITHDRAW_TON_FEE}

@app.get("/api/nft_catalog")
async def api_nft_catalog():
    sync_nft_prices()
    return {
        "ok": True,
        "price_file": _PRICE_FILE_PATH,
        "count": len(NFT_CATALOG),
        "items": NFT_CATALOG,
    }

@app.get("/debug/check_payment_handler")
async def debug_payment_handler():
    """Check if new payment handler code is deployed"""
    import inspect
    source = inspect.getsource(tg_webhook)
    has_logging = "💳 Stars payment received" in source
    return {
        "payment_handler_updated": has_logging,
        "nft_withdraw_stars": NFT_WITHDRAW_STARS,
        "first_100_chars": source[:100]
    }
