from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import random
import time
from typing import Dict, List, Set
import httpx
from datetime import datetime

app = FastAPI()

# Конфігурація
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замініть на ваш токен
CHANNEL_USERNAME = "@pepe_GiftsNFT"

# Зберігання активних підключень
active_connections: Dict[str, WebSocket] = {}
players: Dict[str, dict] = {}

# Стан гри
game_state = {
    "phase": "waiting",
    "round": 1,
    "start_time": 0,
    "crash_point": 0,
    "mult": 1.0,
    "bets": {}
}

# Таймер для раундів
round_task = None

# Функція генерації crash point
def generate_crash_point():
    """Генерує випадкову точку краху з реалістичним розподілом"""
    r = random.random()
    if r < 0.5:
        return round(1.0 + random.random() * 0.5, 2)  # 1.0-1.5x (50%)
    elif r < 0.8:
        return round(1.5 + random.random() * 1.5, 2)  # 1.5-3.0x (30%)
    elif r < 0.95:
        return round(3.0 + random.random() * 7.0, 2)  # 3.0-10.0x (15%)
    else:
        return round(10.0 + random.random() * 40.0, 2)  # 10.0-50.0x (5%)

# Перевірка підписки на канал
async def check_subscription(user_id: int, channel: str) -> bool:
    """Перевіряє чи користувач підписаний на канал через Telegram Bot API"""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        # В режимі розробки завжди повертаємо True
        return True
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember"
            params = {
                "chat_id": channel,
                "user_id": user_id
            }
            response = await client.get(url, params=params)
            data = response.json()
            
            if data.get("ok"):
                status = data.get("result", {}).get("status")
                return status in ["member", "administrator", "creator"]
            return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

# Broadcast повідомлення всім
async def broadcast(message: dict, exclude: str = None):
    """Відправляє повідомлення всім підключеним клієнтам"""
    disconnected = []
    for user_id, ws in active_connections.items():
        if user_id != exclude:
            try:
                await ws.send_json(message)
            except:
                disconnected.append(user_id)
    
    # Видалити відключених
    for user_id in disconnected:
        if user_id in active_connections:
            del active_connections[user_id]
        if user_id in players:
            del players[user_id]

# Ігровий цикл
async def game_loop():
    """Основний ігровий цикл"""
    global game_state
    
    while True:
        try:
            # Фаза очікування (10 секунд)
            game_state["phase"] = "waiting"
            game_state["round"] += 1
            game_state["bets"] = {}
            
            # Countdown
            for sec in range(10, 0, -1):
                await broadcast({
                    "t": "cd",
                    "rid": game_state["round"],
                    "sec": sec
                })
                await asyncio.sleep(1)
            
            # Генерація crash point
            game_state["crash_point"] = generate_crash_point()
            game_state["phase"] = "flying"
            game_state["start_time"] = time.time()
            game_state["mult"] = 1.0
            
            # Start повідомлення
            await broadcast({
                "t": "st",
                "rid": game_state["round"],
                "ts": game_state["start_time"]
            })
            
            # Фаза польоту
            start = time.time()
            while game_state["mult"] < game_state["crash_point"]:
                elapsed = time.time() - start
                game_state["mult"] = round(1.0 + (elapsed * 0.1), 2)
                
                # Оновлення гравців
                await broadcast({
                    "t": "tick",
                    "pl": list(game_state["bets"].values())
                })
                
                await asyncio.sleep(0.1)
            
            # Crash!
            game_state["phase"] = "crashed"
            game_state["mult"] = game_state["crash_point"]
            
            # Обробка програшів
            lost_players = []
            for user_id, bet in game_state["bets"].items():
                if not bet.get("cashed_out"):
                    lost_players.append({
                        "user_id": user_id,
                        "name": bet["name"],
                        "lost": True
                    })
            
            await broadcast({
                "t": "cr",
                "ca": game_state["crash_point"],
                "pl": lost_players
            })
            
            # Пауза перед новим раундом
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"Game loop error: {e}")
            await asyncio.sleep(5)

@app.on_event("startup")
async def startup_event():
    """Запуск ігрового циклу при старті сервера"""
    global round_task
    round_task = asyncio.create_task(game_loop())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = None
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("a")
            
            # Ініціалізація
            if action == "init":
                user_id = str(message.get("uid", 0))
                active_connections[user_id] = websocket
                
                # Створити гравця
                if user_id not in players:
                    players[user_id] = {
                        "id": user_id,
                        "name": message.get("name", "Player"),
                        "balance": 10.0,  # Стартовий баланс
                        "nfts": []
                    }
                
                # Відправити початковий стан
                await websocket.send_json({
                    "t": "init",
                    "bal": players[user_id]["balance"],
                    "phase": game_state["phase"],
                    "mult": game_state["mult"],
                    "ts": game_state["start_time"],
                    "pl": list(game_state["bets"].values()),
                    "h": []  # Історія
                })
            
            # Ставка
            elif action == "bet":
                if user_id and game_state["phase"] == "waiting":
                    amt = float(message.get("amt", 0))
                    nft_bet = message.get("nft_bet")
                    
                    if players[user_id]["balance"] >= amt:
                        players[user_id]["balance"] -= amt
                        
                        game_state["bets"][user_id] = {
                            "user_id": user_id,
                            "name": players[user_id]["name"],
                            "amt": amt,
                            "cashed_out": False,
                            "nft_bet": nft_bet
                        }
                        
                        await websocket.send_json({
                            "t": "bet_ok",
                            "amt": amt,
                            "bal": players[user_id]["balance"]
                        })
                        
                        await broadcast({
                            "t": "newbet",
                            "pl": list(game_state["bets"].values())
                        })
            
            # Cashout
            elif action == "cashout":
                if user_id and user_id in game_state["bets"]:
                    bet = game_state["bets"][user_id]
                    if not bet["cashed_out"] and game_state["phase"] == "flying":
                        bet["cashed_out"] = True
                        bet["co_mult"] = game_state["mult"]
                        
                        win = round(bet["amt"] * game_state["mult"], 2)
                        players[user_id]["balance"] += win
                        
                        # Визначити NFT якщо потрібно
                        nft = None
                        if game_state["mult"] >= 1.1 and win >= 2.8:
                            nft = {
                                "id": "random_nft",
                                "name": "Telegram Gift",
                                "price": win,
                                "floor": win,
                                "rarity": "Common"
                            }
                        
                        await websocket.send_json({
                            "t": "your_co",
                            "mx": game_state["mult"],
                            "win": win,
                            "bal": players[user_id]["balance"],
                            "nft": nft
                        })
                        
                        await broadcast({
                            "t": "co",
                            "pl": list(game_state["bets"].values())
                        }, exclude=user_id)
            
            # Перевірка підписки
            elif action == "check_subscription":
                channel = message.get("channel", CHANNEL_USERNAME)
                uid = int(message.get("user_id", 0))
                
                is_subscribed = await check_subscription(uid, channel)
                
                await websocket.send_json({
                    "t": "subscription_checked",
                    "subscribed": is_subscribed
                })
            
            # Пошук користувача (адмін)
            elif action == "admin_find_user":
                query = message.get("query", "")
                # Тут має бути логіка пошуку в базі даних
                # Поки що повертаємо фейкового користувача
                await websocket.send_json({
                    "t": "admin_user_found",
                    "user": {
                        "id": 123456,
                        "username": query,
                        "first_name": "Test User",
                        "balance": 10.0,
                        "banned": False
                    }
                })
    
    except WebSocketDisconnect:
        if user_id:
            if user_id in active_connections:
                del active_connections[user_id]
            if user_id in game_state["bets"]:
                del game_state["bets"][user_id]
    except Exception as e:
        print(f"WebSocket error: {e}")

# Статичні файли
@app.get("/")
async def read_root():
    return FileResponse("index.html")

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "players": len(active_connections)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
