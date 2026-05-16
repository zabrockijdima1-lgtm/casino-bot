import asyncio, json, math, os, random, time, httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

TON_WALLET = "UQAfazCyjGjugOf73_LrxUuLvxSmExM_8loArhgATwKXU6yA"
BOT_TOKEN = "8757352545:AAGlu9yQu97JHfGljZH4ocqOBU_-sJm1KR8"
ADMIN_IDS = {1256452126, 6479535975}

clients = {}
players = {}
bets = {}
referrals = {}
ref_earnings = {}

class G:
    phase = "waiting"
    mult = 1.0
    crash_at = 1.0
    start_ts = 0.0
    round_id = 0
    history = []
    def calc_mult(self, t): 
        return round(math.exp(t * 0.06), 2)

g = G()

def gen_crash():
    r = random.random()
    if r < 0.15: return 1.00
    if r < 0.50: return round(random.uniform(1.01, 1.5), 2)
    if r < 0.75: return round(random.uniform(1.5, 2.5), 2)
    if r < 0.90: return round(random.uniform(2.5, 5.0), 2)
    if r < 0.97: return round(random.uniform(5.0, 20.0), 2)
    if r < 0.99: return round(random.uniform(20.0, 50.0), 2)
    return round(random.uniform(50.0, 100.0), 2)

async def broadcast(msg):
    for ws in list(clients.values()):
        try:
            await ws.send_text(json.dumps(msg))
        except:
            pass

async def game_loop():
    while True:
        g.phase = "waiting"
        g.round_id += 1
        g.crash_at = gen_crash()
        bets.clear()
        
        for sec in range(5, 0, -1):
            await broadcast({"t": "cd", "sec": sec, "rid": g.round_id})
            await asyncio.sleep(1)
        
        g.phase = "flying"
        g.start_ts = time.time()
        g.mult = 1.0
        
        await broadcast({"t": "start", "rid": g.round_id, "ts": g.start_ts})
        
        while g.mult < g.crash_at:
            await asyncio.sleep(0.15)
            elapsed = time.time() - g.start_ts
            g.mult = g.calc_mult(elapsed)
            if g.mult >= g.crash_at:
                break
            await broadcast({"t": "tick", "m": g.mult})
        
        g.mult = g.crash_at
        await broadcast({"t": "crash", "m": g.crash_at})
        g.history.insert(0, g.crash_at)
        g.history = g.history[:50]
        
        await asyncio.sleep(3)

@app.on_event("startup")
async def startup():
    asyncio.create_task(game_loop())

@app.websocket("/ws/{uid}")
async def websocket_endpoint(ws: WebSocket, uid: int):
    await ws.accept()
    clients[uid] = ws
    
    if uid not in players:
        players[uid] = {"name": "Player", "balance": 100.0, "nfts": []}
    
    pl = [{"uid": u, "name": players[u].get("name", "?")} for u in bets.keys()]
    
    await ws.send_text(json.dumps({
        "t": "init",
        "bal": players[uid]["balance"],
        "phase": g.phase,
        "mult": g.mult,
        "ts": g.start_ts,
        "h": g.history,
        "pl": pl
    }))
    
    try:
        async for msg in ws.iter_text():
            d = json.loads(msg)
            a = d.get("a")
            
            if a == "bet":
                amt = float(d.get("amt", 0.1))
                if amt > players[uid]["balance"]:
                    continue
                players[uid]["balance"] -= amt
                bets[uid] = {"amt": amt, "cashed": False}
                await ws.send_text(json.dumps({"t": "bet_ok", "amt": amt, "bal": players[uid]["balance"]}))
            
            elif a == "cashout":
                if uid in bets and not bets[uid]["cashed"] and g.phase == "flying":
                    win = round(bets[uid]["amt"] * g.mult, 2)
                    players[uid]["balance"] += win
                    bets[uid]["cashed"] = True
                    await ws.send_text(json.dumps({"t": "your_co", "mx": g.mult, "win": win, "bal": players[uid]["balance"]}))
            
            elif a == "check_subscription":
                await ws.send_text(json.dumps({"t": "subscription_checked", "subscribed": True}))
    
    except WebSocketDisconnect:
        pass
    finally:
        clients.pop(uid, None)
        bets.pop(uid, None)

@app.get("/")
async def root():
    return {"status": "ok", "round": g.round_id, "phase": g.phase, "players": len(clients)}

@app.get("/admin")
async def admin_page(uid: int):
    if uid not in ADMIN_IDS:
        return HTMLResponse("<h2>Access Denied</h2>", status_code=403)
    
    total_players = len(players)
    total_balance = sum(p.get("balance", 0) for p in players.values())
    
    html = f"""
    <html><head><title>Admin</title></head><body>
    <h1>Admin Panel</h1>
    <p>Players: {total_players}</p>
    <p>Total Balance: {total_balance:.2f} TON</p>
    <p>Round: {g.round_id}</p>
    <p>Phase: {g.phase}</p>
    </body></html>
    """
    return HTMLResponse(html)
