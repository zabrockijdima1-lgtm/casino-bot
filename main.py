import asyncio, json, math, os, random, time, httpx
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

# Константа для вашого домену на Railway (без слеша в кінці)
RAILWAY_DOMAIN = "https://casino-bot-production-5113.up.railway.app"

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

def get_nft_for_win(win: float):
    if win < 0.1: return None
    ok = [n for n in NFT_CATALOG if n["price"] <= win]
    return max(ok, key=lambda n: n["floor"]) if ok else None

async def check_subscription(user_id: int, channel: str) -> bool:
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

PLAYERS_FILE = "players_data.json"

def save_players():
    try:
        with open(PLAYERS_FILE, "w") as f:
            json.dump(players, f)
        print(f"💾 Players data saved ({len(players)} players)")
    except Exception as e:
        print(f"❌ Error saving players: {e}")

def load_players():
    global players
    try:
        if os.path.exists(PLAYERS_FILE):
            with open(PLAYERS_FILE, "r") as f:
                players = json.load(f)
            print(f"📂 Loaded {len(players)} players from file")
        else:
            print("📂 No saved players file, starting fresh")
    except Exception as e:
        print(f"❌ Error loading players: {e}")
        players = {}

load_players()

def add_log(category, entry):
    entry["ts"] = time.time()
    logs[category].insert(0, entry)
    if len(logs[category]) > MAX_LOGS:
        logs[category].pop()

async def send_tg(uid: int, text: str):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": uid, "text": text, "parse_mode": "HTML"}
            )
            data = r.json()
            if not data.get("ok"):
                print(f"❌ Telegram API error: {data.get('description', 'Unknown error')}")
    except Exception as e:
        print(f"❌ TG send error to {uid}: {e}")

async def credit_balance(uid: int, amount: float, source: str = "deposit"):
    if uid not in players:
        players[uid] = {"name": "Player", "nick": "", "photo": "", "balance": 0, "nfts": []}
    players[uid]["balance"] = round(players[uid]["balance"] + amount, 4)
    if uid in referrals:
        ref_uid = referrals[uid]
        bonus = round(amount * 0.10, 4)
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

async def auto_check_topups():
    """Фонова таска ТІЛЬКИ для перевірки блокчейну TON"""
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

NFT_WITHDRAW_STARS = 1

@app.get("/stars/withdraw-invoice/{uid}/{nft_id}/{nft_name}")
async def create_withdraw_invoice(uid: int, nft_id: str, nft_name: str):
    payload = json.dumps({"uid": uid, "nft_id": nft_id, "type": "nft_withdraw"})
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink",
                json={"title": f"NFT Withdrawal: {nft_name}", "description": f"Fee for withdrawing NFT «{nft_name}» to your Telegram wallet", "payload": payload, "currency": "XTR", "prices": [{"label": "Withdrawal fee", "amount": NFT_WITHDRAW_STARS}]}
            )
            data = r.json()
        if not data.get("ok"):
            return JSONResponse({"ok": False, "error": data.get("description", "Telegram error")})
        return JSONResponse({"ok": True, "invoice_link": data["result"]})
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"Server error: {str(e)}"})

@app.get("/stars/invoice/{uid}/{stars}")
async def create_stars_invoice(uid: int, stars: int):
    if stars < 1 or stars > 10000:
        return JSONResponse({"ok": False, "error": "Stars від 1 до 10 000"})
    ton_amount = round(stars * STARS_TO_TON, 4)
    payload = json.dumps({"uid": uid, "stars": stars, "ton": ton_amount, "type": "balance_topup"})
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink",
                json={"title": "Поповнення балансу ⭐", "description": f"{stars} Telegram Stars → {ton_amount} TON на ігровий баланс", "payload": payload, "currency": "XTR", "prices": [{"label": f"{stars} Stars", "amount": stars}]}
            )
            data = r.json()
        if not data.get("ok"):
            return JSONResponse({"ok": False, "error": data.get("description", "Помилка Telegram")})
        return JSONResponse({"ok": True, "invoice_link": data["result"], "ton": ton_amount})
    except Exception as e:
        return JSONResponse({"ok": False, "error": "Помилка сервера"})

@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    """Головний вхідний вебхук для ВСІХ апдейтів Telegram (включаючи оплату)"""
    try:
        update = await request.json()
    except Exception as e:
        return JSONResponse({"ok": True})
    
    # 1. МИТТЄВА ВІДПОВІДЬ НА PRE-CHECKOUT QUERY (Рятує від нескінченного завантаження)
    if "pre_checkout_query" in update:
        pcq_id = update["pre_checkout_query"]["id"]
        print(f"✅ Pre-checkout query received via webhook: {pcq_id}")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery",
                    json={"pre_checkout_query_id": pcq_id, "ok": True}
                )
                print(f"✅ Pre-checkout query approved!")
        except Exception as e:
            print(f"❌ answerPreCheckoutQuery error: {e}")
        return JSONResponse({"ok": True})
    
    msg = update.get("message", {})
    
    # 2. ОБРОБКА УСПІШНОЇ ОПЛАТИ (Зарахування грошей)
    payment = msg.get("successful_payment")
    if payment and payment.get("currency") == "XTR":
        print(f"💳 Stars payment received via webhook: {payment}")
        try:
            payload = json.loads(payment["invoice_payload"])
            uid = int(payload["uid"])
            
            # Перевіряємо тип платежу
            if payload.get("type") == "balance_topup" or "stars" in payload:
                stars = int(payload["stars"])
                ton_amount = float(payload["ton"])
                
                bal = await credit_balance(uid, ton_amount, source="stars")
                add_log("stars", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "stars": stars, "ton": ton_amount})
                add_log("deposits", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "amount": ton_amount, "note": f"Stars x{stars}"})
                
                await send_tg(uid, f"⭐ <b>Stars зараховано!</b>\n{stars} Stars → <b>{ton_amount} TON</b>\nБаланс: {bal} TON")
                await send_tg(ADMIN_ID, f"⭐ <b>Stars депозит</b>\nКористувач: {players.get(uid,{}).get('name','?')} (uid: {uid})\nStars: {stars} → {ton_amount} TON")
                
                if uid in clients:
                    try: await clients[uid].send_text(json.dumps({"t": "bal", "bal": bal}))
                    except: pass
                    
            elif payload.get("type") == "nft_withdraw":
                nft_id = payload.get("nft_id")
                await send_tg(uid, f"✅ <b>Оплата комісії успішна!</b>\nВаш запит на вивід NFT прийнято в обробку.")
                await send_tg(ADMIN_ID, f"📦 <b>Запит на вивід NFT!</b>\nКористувач {uid} оплатив 1 зірку комісії для виводу NFT ID: {nft_id}")
                
        except Exception as e:
            print(f"❌ Stars payment processing error: {e}")
        return JSONResponse({"ok": True})
    
    # 3. КОМАНДИ БОТА
    if msg:
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        if text == "/start":
            user_name = msg.get("from", {}).get("first_name", "User")
            await send_tg(chat_id, f"👋 Welcome to Rocket Casino, {user_name}!\n\n🎮 Open the game: {RAILWAY_DOMAIN}\n\nGood luck! 🚀")
            
    return JSONResponse({"ok": True})

# Автоматичний запуск при старті додатка на Railway
@app.on_event("startup")
async def startup_event():
    # Запускаємо фонову таску для TON блокчейну
    asyncio.create_task(auto_check_topups())
    
    # Автоматично і ПРАВИЛЬНО реєструємо вебхук на адресу з /tg/webhook
    FULL_WEBHOOK_URL = f"{RAILWAY_DOMAIN}/tg/webhook"
    print(f"🌐 Setting Telegram Webhook to: {FULL_WEBHOOK_URL}")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
                json={"url": FULL_WEBHOOK_URL, "allowed_updates": ["message", "pre_checkout_query"]}
            )
            print(f"🌐 Telegram response: {r.json()}")
    except Exception as e:
        print(f"❌ Failed to set webhook on startup: {e}")

# (Тут залишаються ваші WebSocket ендпоінти /ws/{uid} та інші роути без змін)
