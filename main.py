import asyncio, json, math, os, random, time, httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse

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
RAILWAY_DOMAIN = "https://casino-bot-production-5113.up.railway.app"

# Full NFT Catalog (sorted by price)
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
    {"id":"easteregg","name":"Easter Egg","floor":3.41,"price":3.58,"rarity":"Common","color":"#0d2e1a"},
    {"id":"hexpot","name":"Hex Pot","floor":3.87,"price":4.06,"rarity":"Common","color":"#0d2e1a"},
    {"id":"bdaycandle","name":"B-Day Candle","floor":4.08,"price":4.28,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"faithamulet","name":"Faith Amulet","floor":4.23,"price":4.44,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"snowmittens","name":"Snow Mittens","floor":4.29,"price":4.50,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"lushbouquet","name":"Lush Bouquet","floor":4.47,"price":4.69,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"inputkey","name":"Input Key","floor":4.75,"price":4.99,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"lightsword","name":"Light Sword","floor":5.04,"price":5.29,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"eternalcandle","name":"Eternal Candle","floor":5.39,"price":5.66,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"evileye","name":"Evil Eye","floor":5.97,"price":6.27,"rarity":"Rare","color":"#0d1e3a"},
    {"id":"crystalball","name":"Crystal Ball","floor":9.74,"price":10.23,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"tophat","name":"Top Hat","floor":10.59,"price":11.12,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"lovepotion","name":"Love Potion","floor":11.85,"price":12.44,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"recordplayer","name":"Record Player","floor":14.24,"price":14.95,"rarity":"Epic","color":"#1e0d3a"},
    {"id":"toybear","name":"Toy Bear","floor":30.10,"price":31.61,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"lowrider","name":"Low Rider","floor":39.89,"price":41.88,"rarity":"Legendary","color":"#2e1e00"},
    {"id":"swisswatch","name":"Swiss Watch","floor":43.13,"price":45.29,"rarity":"Legendary","color":"#2e1e00"},
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
    except Exception as e:
        print(f"❌ Error saving players: {e}")

def load_players():
    global players
    try:
        if os.path.exists(PLAYERS_FILE):
            with open(PLAYERS_FILE, "r") as f:
                players = json.load(f)
            print(f"📂 Loaded {len(players)} players")
        else:
            print("📂 No saved file, fresh start")
    except Exception as e:
        print(f"❌ Load error: {e}")
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
                print(f"❌ Telegram API error: {data.get('description', 'Unknown')}")
    except Exception as e:
        print(f"❌ TG error to {uid}: {e}")

async def credit_balance(uid: int, amount: float, source: str = "deposit"):
    if uid not in players:
        players[uid] = {"name": "Player", "nick": "", "photo": "", "balance": 0, "nfts": []}
    players[uid]["balance"] = round(players[uid]["balance"] + amount, 4)
    
    # Referral bonus
    if uid in referrals:
        ref_uid = referrals[uid]
        bonus = round(amount * 0.10, 4)
        if ref_uid not in players:
            players[ref_uid] = {"name": "?", "nick": "", "photo": "", "balance": 0, "nfts": []}
        players[ref_uid]["balance"] = round(players[ref_uid]["balance"] + bonus, 4)
        ref_earnings[ref_uid] = round(ref_earnings.get(ref_uid, 0) + bonus, 4)
        add_log("deposits", {"uid": ref_uid, "name": players[ref_uid].get("name", "?"), "amount": bonus, "note": f"ref bonus from {uid}"})
        if ref_uid in clients:
            try:
                await clients[ref_uid].send_text(json.dumps({"t": "ref_bonus", "bonus": bonus, "bal": players[ref_uid]["balance"]}))
            except: pass
        await send_tg(ref_uid, f"👥 <b>Referral bonus!</b>\nYour referral topped up {amount} TON\nYour bonus: <b>+{bonus} TON</b> (10%)")
    
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
                await send_tg(ADMIN_ID, f"💰 <b>TON Deposit</b>\nUser: {players[uid].get('name','?')} (uid: {uid})\nAmount: {amt} TON\nBalance: {bal} TON")

NFT_WITHDRAW_STARS = 1  # TESTING: normally 25 Stars

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
        return JSONResponse({"ok": False, "error": "Stars 1-10000"})
    ton_amount = round(stars * STARS_TO_TON, 4)
    payload = json.dumps({"uid": uid, "stars": stars, "ton": ton_amount, "type": "balance_topup"})
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoiceLink",
                json={"title": "Top Up ⭐", "description": f"{stars} Stars → {ton_amount} TON", "payload": payload, "currency": "XTR", "prices": [{"label": f"{stars} Stars", "amount": stars}]}
            )
            data = r.json()
        if not data.get("ok"):
            return JSONResponse({"ok": False, "error": data.get("description", "Error")})
        return JSONResponse({"ok": True, "invoice_link": data["result"], "ton": ton_amount})
    except Exception as e:
        return JSONResponse({"ok": False, "error": "Server error"})

@app.post("/tg/webhook")
async def tg_webhook(request: Request):
    try:
        update = await request.json()
    except:
        return JSONResponse({"ok": True})
    
    # 1. PRE-CHECKOUT QUERY - КРИТИЧНО ПЕРШИМ!
    if "pre_checkout_query" in update:
        pcq_id = update["pre_checkout_query"]["id"]
        print(f"✅ Pre-checkout: {pcq_id}")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerPreCheckoutQuery",
                    json={"pre_checkout_query_id": pcq_id, "ok": True}
                )
                print(f"✅ Approved!")
        except Exception as e:
            print(f"❌ Error: {e}")
        return JSONResponse({"ok": True})
    
    msg = update.get("message", {})
    
    # 2. SUCCESSFUL PAYMENT
    payment = msg.get("successful_payment")
    if payment and payment.get("currency") == "XTR":
        print(f"💳 Payment: {payment}")
        try:
            payload = json.loads(payment["invoice_payload"])
            uid = int(payload["uid"])
            
            # Balance topup
            if payload.get("type") == "balance_topup" or "stars" in payload:
                stars = int(payload["stars"])
                ton_amount = float(payload["ton"])
                
                bal = await credit_balance(uid, ton_amount, source="stars")
                save_players()
                add_log("stars", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "stars": stars, "ton": ton_amount})
                add_log("deposits", {"uid": uid, "name": players.get(uid, {}).get("name", "?"), "amount": ton_amount, "note": f"Stars x{stars}"})
                
                await send_tg(uid, f"⭐ <b>Credited!</b>\n{stars} Stars → <b>{ton_amount} TON</b>\nBalance: {bal} TON")
                await send_tg(ADMIN_ID, f"⭐ Stars deposit: {stars} Stars from UID {uid}")
                
                if uid in clients:
                    try:
                        await clients[uid].send_text(json.dumps({"t": "bal", "bal": bal}))
                    except: pass
                    
            # NFT withdrawal
            elif payload.get("type") == "nft_withdraw":
                nft_id = payload.get("nft_id")
                await send_tg(uid, f"✅ <b>Fee paid!</b>\nYour NFT withdrawal request accepted.")
                await send_tg(ADMIN_ID, f"📦 NFT withdrawal request!\nUID {uid}, NFT: {nft_id}")
                
        except Exception as e:
            print(f"❌ Payment error: {e}")
        return JSONResponse({"ok": True})
    
    # 3. COMMANDS
    if msg:
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        if text == "/start":
            user_name = msg.get("from", {}).get("first_name", "User")
            await send_tg(chat_id, f"👋 Welcome to Rocket Casino, {user_name}!\n\n🎮 {RAILWAY_DOMAIN}\n\nGood luck! 🚀")
            
    return JSONResponse({"ok": True})

class G:
    phase = "waiting"
    mult = 1.0
    crash_at = 1.0
    start_ts = 0.0
    round_id = 0
    next_hook = random.randint(8, 25)

async def game_loop():
    while True:
        G.round_id += 1
        G.crash_at = round(max(1.01, random.betavariate(2, 5) * 20), 2)
        
        # Waiting
        G.phase = "waiting"
        G.mult = 1.0
        bets.clear()
        await broadcast({"t": "waiting", "id": G.round_id})
        await asyncio.sleep(5)
        
        # Flying
        G.phase = "flying"
        G.start_ts = time.time()
        await broadcast({"t": "flying", "id": G.round_id})
        
        while G.mult < G.crash_at:
            elapsed = time.time() - G.start_ts
            G.mult = round(1 + elapsed * 0.1, 2)
            await broadcast({"t": "tick", "mult": G.mult})
            
            # NFT Hook
            if G.round_id == G.next_hook:
                hook_uid = random.choice(list(clients.keys())) if clients else None
                if hook_uid and hook_uid in bets:
                    bet_amt = bets[hook_uid]["amount"]
                    target = round(bet_amt * random.uniform(2.8, 4.5), 2)
                    if G.mult >= target - 0.2:
                        G.crash_at = target
            
            await asyncio.sleep(0.1)
        
        # Crashed
        G.phase = "crashed"
        G.mult = G.crash_at
        await broadcast({"t": "crash", "mult": G.crash_at})
        
        # Process losing bets
        for uid, b in list(bets.items()):
            if b.get("cashed_out"):
                continue
            add_log("bets", {"uid": uid, "amount": b["amount"], "mult": 0, "win": 0})
        
        G.next_hook = G.round_id + random.randint(8, 25)
        await asyncio.sleep(3)

async def broadcast(msg):
    dead = []
    for uid, ws in clients.items():
        try:
            await ws.send_text(json.dumps(msg))
        except:
            dead.append(uid)
    for uid in dead:
        clients.pop(uid, None)

player_ips: dict = {}

@app.websocket("/ws/{uid}")
async def websocket_endpoint(ws: WebSocket, uid: int):
    await ws.accept()
    
    # IP check
    client_host = ws.client.host if ws.client else None
    if client_host:
        if client_host in player_ips and player_ips[client_host] != uid:
            await ws.send_text(json.dumps({"t": "banned"}))
            await ws.close()
            return
        player_ips[client_host] = uid
    
    clients[uid] = ws
    
    if uid not in players:
        players[uid] = {"name": "Player", "nick": "", "photo": "", "balance": 0, "nfts": []}
    
    try:
        await ws.send_text(json.dumps({
            "t": "init",
            "bal": players[uid]["balance"],
            "phase": G.phase,
            "mult": G.mult,
            "id": G.round_id
        }))
        
        async for message in ws.iter_text():
            d = json.loads(message)
            a = d.get("a")
            
            if a == "profile":
                name = d.get("name", "Player")[:50]
                nick = d.get("nick", "")[:50]
                photo = d.get("photo", "")
                players[uid]["name"] = name
                players[uid]["nick"] = nick
                players[uid]["photo"] = photo
                
            elif a == "bet":
                if G.phase != "waiting":
                    continue
                amount = float(d.get("amount", 0))
                if amount < 0.01 or amount > players[uid]["balance"]:
                    continue
                players[uid]["balance"] = round(players[uid]["balance"] - amount, 4)
                bets[uid] = {"amount": amount, "cashed_out": False}
                await ws.send_text(json.dumps({"t": "bet_ok", "bal": players[uid]["balance"]}))
                
            elif a == "cashout":
                if G.phase != "flying" or uid not in bets or bets[uid].get("cashed_out"):
                    continue
                bets[uid]["cashed_out"] = True
                win = round(bets[uid]["amount"] * G.mult, 4)
                players[uid]["balance"] = round(players[uid]["balance"] + win, 4)
                
                # NFT check - падає вже з 1.1x!
                nft = get_nft_for_win(win)
                if nft and G.mult >= 1.1:
                    nft_entry = {
                        "id": nft["id"],
                        "name": nft["name"],
                        "emoji": "🎁",
                        "rarity": nft["rarity"],
                        "price": nft["price"],
                        "floor": nft["floor"],
                        "ts": time.time()
                    }
                    players[uid]["nfts"].append(nft_entry)
                    save_players()
                    await ws.send_text(json.dumps({"t": "nft_won", "nft": nft_entry}))
                
                await ws.send_text(json.dumps({"t": "cashout_ok", "win": win, "bal": players[uid]["balance"], "mult": G.mult}))
                add_log("cashouts", {"uid": uid, "amount": bets[uid]["amount"], "mult": G.mult, "win": win})
                
            elif a == "topup_start":
                amount = float(d.get("amount", 0))
                if amount >= 0.1:
                    pending_topups[uid] = {"amount": amount, "ts": time.time(), "done": False}
                    
            elif a == "case_win_keep":
                case_name = d.get("case_name", "Unknown")
                nft_id = d.get("nft_id")
                nft_name = d.get("name", "Unknown")
                price = float(d.get("price", 0))
                is_nft = d.get("is_nft", True)
                
                if is_nft and nft_id:
                    nft_entry = {
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
                
                add_log("cases", {"uid": uid, "name": players[uid].get("name", "?"), "case_name": case_name, "won_item": nft_name if is_nft else f"{price} TON", "is_nft": is_nft, "value": price})
                
            elif a == "withdraw_nft":
                nft_id = d.get("nft_id")
                if uid in players and nft_id:
                    nfts = players[uid].get("nfts", [])
                    found_nft = None
                    new_nfts = []
                    removed = False
                    for n in nfts:
                        if n.get("id") == nft_id and not removed:
                            found_nft = n
                            removed = True
                        else:
                            new_nfts.append(n)
                    
                    if found_nft:
                        players[uid]["nfts"] = new_nfts
                        save_players()
                        await ws.send_text(json.dumps({"t": "nft_withdrawn", "nft_id": nft_id, "bal": players[uid]["balance"]}))
                
    except WebSocketDisconnect:
        pass
    finally:
        clients.pop(uid, None)

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/set_webhook")
async def set_webhook(request: Request):
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
async def delete_webhook():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        return r.json()
    except Exception as e:
        return JSONResponse({"error": str(e)})

@app.on_event("startup")
async def startup():
    # Webhook
    FULL_WEBHOOK_URL = f"{RAILWAY_DOMAIN}/tg/webhook"
    print(f"🌐 Webhook: {FULL_WEBHOOK_URL}")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
                json={"url": FULL_WEBHOOK_URL, "allowed_updates": ["message", "pre_checkout_query"]}
            )
            print(f"✅ {r.json()}")
    except Exception as e:
        print(f"❌ {e}")
    
    # Start tasks
    asyncio.create_task(game_loop())
    asyncio.create_task(auto_check_topups())
    print("🎮 Game started!")
