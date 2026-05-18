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

NFT_CATALOG = [
    {"id":"icecream","name":"Ice Cream","floor":1.29,"price":1.35},
    {"id":"easteregg","name":"Easter Egg","floor":3.41,"price":3.58},
    {"id":"faithamulet","name":"Faith Amulet","floor":4.23,"price":4.44},
]

def get_nft_for_win(win: float):
    if win < 0.1: return None
    ok = [n for n in NFT_CATALOG if n["price"] <= win]
    return max(ok, key=lambda n: n["floor"]) if ok else None

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
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": uid, "text": text, "parse_mode": "HTML"}
            )
    except Exception as e:
        print(f"❌ TG error: {e}")

async def credit_balance(uid: int, amount: float, source: str = "deposit"):
    if uid not in players:
        players[uid] = {"name": "Player", "nick": "", "photo": "", "balance": 0, "nfts": []}
    players[uid]["balance"] = round(players[uid]["balance"] + amount, 4)
    if uid in clients:
        try:
            await clients[uid].send_text(json.dumps({"t": "topup_ok", "credited": amount, "bal": players[uid]["balance"], "source": source}))
        except: pass
    return players[uid]["balance"]

async def check_ton_tx(uid: int, amount: float, since_ts: float) -> bool:
    return False  # Simplified

async def auto_check_topups():
    while True:
        await asyncio.sleep(10)

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
    
    # PRE-CHECKOUT
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
    
    # PAYMENT
    payment = msg.get("successful_payment")
    if payment and payment.get("currency") == "XTR":
        print(f"💳 Payment: {payment}")
        try:
            payload = json.loads(payment["invoice_payload"])
            uid = int(payload["uid"])
            stars = int(payload["stars"])
            ton_amount = float(payload["ton"])
            
            bal = await credit_balance(uid, ton_amount, source="stars")
            save_players()
            
            await send_tg(uid, f"⭐ <b>Credited!</b>\n{stars} Stars → <b>{ton_amount} TON</b>\nBalance: {bal} TON")
            await send_tg(ADMIN_ID, f"⭐ Deposit: {stars} Stars from UID {uid}")
            
            if uid in clients:
                try:
                    await clients[uid].send_text(json.dumps({"t": "bal", "bal": bal}))
                except: pass
        except Exception as e:
            print(f"❌ Payment error: {e}")
        return JSONResponse({"ok": True})
    
    # COMMANDS
    if msg:
        chat_id = msg.get("chat", {}).get("id")
        text = msg.get("text", "")
        if text == "/start":
            await send_tg(chat_id, f"👋 Welcome!\n\n🎮 {RAILWAY_DOMAIN}\n\nGood luck!")
            
    return JSONResponse({"ok": True})

class G:
    phase = "waiting"
    mult = 1.0
    crash_at = 1.0
    start_ts = 0.0
    round_id = 0

async def game_loop():
    while True:
        G.round_id += 1
        G.crash_at = round(max(1.01, random.betavariate(2, 5) * 20), 2)
        
        G.phase = "waiting"
        G.mult = 1.0
        bets.clear()
        await broadcast({"t": "waiting", "id": G.round_id})
        await asyncio.sleep(5)
        
        G.phase = "flying"
        G.start_ts = time.time()
        await broadcast({"t": "flying", "id": G.round_id})
        
        while G.mult < G.crash_at:
            elapsed = time.time() - G.start_ts
            G.mult = round(1 + elapsed * 0.1, 2)
            await broadcast({"t": "tick", "mult": G.mult})
            await asyncio.sleep(0.1)
        
        G.phase = "crashed"
        G.mult = G.crash_at
        await broadcast({"t": "crash", "mult": G.crash_at})
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

@app.websocket("/ws/{uid}")
async def websocket_endpoint(ws: WebSocket, uid: int):
    await ws.accept()
    clients[uid] = ws
    
    if uid not in players:
        players[uid] = {"name": "Player", "balance": 0, "nfts": []}
    
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
            
            if a == "bet":
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
                
                nft = get_nft_for_win(win)
                if nft and win >= 2.8:
                    nft_entry = {"id": nft["id"], "name": nft["name"], "price": nft["price"], "floor": nft["floor"], "ts": time.time()}
                    players[uid]["nfts"].append(nft_entry)
                    save_players()
                    await ws.send_text(json.dumps({"t": "nft_won", "nft": nft_entry}))
                
                await ws.send_text(json.dumps({"t": "cashout_ok", "win": win, "bal": players[uid]["balance"], "mult": G.mult}))
                
    except WebSocketDisconnect:
        pass
    finally:
        clients.pop(uid, None)

@app.get("/")
async def root():
    return FileResponse("index.html")

@app.on_event("startup")
async def startup():
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
    
    asyncio.create_task(game_loop())
    asyncio.create_task(auto_check_topups())
    print("🎮 Game started!")
