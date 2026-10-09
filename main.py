"""
main.py - FastAPI application serving the LoL Balance Web App and API.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Load .env file if present
load_dotenv()

import balancer
from riot_service import RiotService

app = FastAPI(title="LoL Stream Custom Matchmaker")

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Global Riot Service instance
riot_service = RiotService()


# --- Pydantic Models ---
class RiotSearchRequest(BaseModel):
    riot_id: str


class RiotKeyRequest(BaseModel):
    api_key: str


class PlayerModel(BaseModel):
    id: str
    name: str
    tier: str = "GOLD"
    rank: str = "II"
    lp: int = 0
    mmr: int = 1500
    roles: List[str] = Field(default_factory=lambda: ["TOP", "MID"])
    is_pinned: bool = False
    pin_team: Optional[str] = None  # 'blue' | 'red' | None  (이전엔 누락되어 서버에서 버려졌음)
    is_active: bool = True
    riot_id: Optional[str] = None
    icon_id: Optional[int] = 29
    manual_adjust: int = 0


class BalanceRequest(BaseModel):
    players: List[PlayerModel]
    weight_team: float = 1.0
    weight_lane: float = 0.6


# --- Sample Data for Instant Demo (25 realistic players) ---
DEFAULT_SAMPLE_PLAYERS = [
    # Top laners & flex
    {"id": "p1", "name": "기인열전", "tier": "CHALLENGER", "rank": "I", "lp": 650, "roles": ["TOP"], "is_pinned": True, "icon_id": 1},
    {"id": "p2", "name": "너구리짱", "tier": "GRANDMASTER", "rank": "I", "lp": 420, "roles": ["TOP", "MID"], "is_pinned": False, "icon_id": 2},
    {"id": "p3", "name": "골목대장탑", "tier": "DIAMOND", "rank": "II", "lp": 45, "roles": ["TOP", "JUG"], "is_pinned": False, "icon_id": 3},
    {"id": "p4", "name": "탑신병자", "tier": "EMERALD", "rank": "I", "lp": 70, "roles": ["TOP", "MID", "BOT"], "is_pinned": False, "icon_id": 4},
    {"id": "p5", "name": "칼챔장인", "tier": "PLATINUM", "rank": "III", "lp": 20, "roles": ["TOP"], "is_pinned": False, "icon_id": 5},

    # Junglers & flex
    {"id": "p6", "name": "캐니언워너비", "tier": "CHALLENGER", "rank": "I", "lp": 710, "roles": ["JUG"], "is_pinned": True, "icon_id": 6},
    {"id": "p7", "name": "정글차이외침", "tier": "MASTER", "rank": "I", "lp": 180, "roles": ["JUG", "SUP"], "is_pinned": False, "icon_id": 7},
    {"id": "p8", "name": "강타의신", "tier": "DIAMOND", "rank": "III", "lp": 15, "roles": ["JUG", "TOP"], "is_pinned": False, "icon_id": 8},
    {"id": "p9", "name": "와드지우개", "tier": "EMERALD", "rank": "II", "lp": 80, "roles": ["JUG", "SUP", "MID"], "is_pinned": False, "icon_id": 9},
    {"id": "p10", "name": "동선연구가", "tier": "GOLD", "rank": "I", "lp": 50, "roles": ["JUG", "TOP"], "is_pinned": False, "icon_id": 10},

    # Mid laners & flex
    {"id": "p11", "name": "대상혁후계자", "tier": "CHALLENGER", "rank": "I", "lp": 890, "roles": ["MID"], "is_pinned": True, "icon_id": 11},
    {"id": "p12", "name": "황족미드", "tier": "MASTER", "rank": "I", "lp": 110, "roles": ["MID", "TOP"], "is_pinned": False, "icon_id": 12},
    {"id": "p13", "name": "로밍마스터", "tier": "DIAMOND", "rank": "I", "lp": 90, "roles": ["MID", "BOT"], "is_pinned": False, "icon_id": 13},
    {"id": "p14", "name": "아지르원챔", "tier": "EMERALD", "rank": "III", "lp": 35, "roles": ["MID"], "is_pinned": False, "icon_id": 14},
    {"id": "p15", "name": "야스오과학", "tier": "GOLD", "rank": "II", "lp": 40, "roles": ["MID", "TOP", "BOT"], "is_pinned": False, "icon_id": 15},

    # Bot / ADCs & flex
    {"id": "p16", "name": "룰러엔딩", "tier": "GRANDMASTER", "rank": "I", "lp": 530, "roles": ["BOT"], "is_pinned": True, "icon_id": 16},
    {"id": "p17", "name": "숟가락살인마", "tier": "DIAMOND", "rank": "II", "lp": 60, "roles": ["BOT", "MID"], "is_pinned": False, "icon_id": 17},
    {"id": "p18", "name": "카이사장인", "tier": "EMERALD", "rank": "I", "lp": 45, "roles": ["BOT"], "is_pinned": False, "icon_id": 18},
    {"id": "p19", "name": "앞점프의미학", "tier": "PLATINUM", "rank": "II", "lp": 90, "roles": ["BOT", "TOP"], "is_pinned": False, "icon_id": 19},
    {"id": "p20", "name": "원딜서폿다됨", "tier": "GOLD", "rank": "III", "lp": 15, "roles": ["BOT", "SUP"], "is_pinned": False, "icon_id": 20},

    # Supports & flex
    {"id": "p21", "name": "케리아따라잡기", "tier": "CHALLENGER", "rank": "I", "lp": 620, "roles": ["SUP", "MID"], "is_pinned": False, "icon_id": 21},
    {"id": "p22", "name": "그랩의정석", "tier": "DIAMOND", "rank": "IV", "lp": 30, "roles": ["SUP"], "is_pinned": False, "icon_id": 22},
    {"id": "p23", "name": "유미공주님", "tier": "EMERALD", "rank": "IV", "lp": 10, "roles": ["SUP"], "is_pinned": False, "icon_id": 23},
    {"id": "p24", "name": "올라운더형님", "tier": "PLATINUM", "rank": "I", "lp": 85, "roles": ["TOP", "JUG", "MID", "BOT", "SUP"], "is_pinned": False, "icon_id": 24},
    {"id": "p25", "name": "즐겜러방장", "tier": "SILVER", "rank": "I", "lp": 95, "roles": ["MID", "SUP", "BOT"], "is_pinned": False, "icon_id": 25},
]


@app.get("/api/health")
def health_check():
    key = riot_service.api_key
    masked = f"{key[:9]}...{key[-4:]}" if len(key) > 13 else ("설정됨" if key else "미설정")
    return {
        "status": "ok",
        "has_riot_api_key": bool(key),
        "is_env_configured": bool(os.getenv("RIOT_API_KEY")),
        "is_server_managed": bool(os.getenv("RIOT_API_KEY")),
        "key_preview": masked,
    }


@app.post("/api/riot/search")
def search_summoner(req: RiotSearchRequest):
    try:
        data = riot_service.fetch_summoner_profile(req.riot_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"조회 중 오류 발생: {str(e)}")


@app.post("/api/riot/key")
def update_riot_key(req: RiotKeyRequest):
    riot_service.set_api_key(req.api_key)
    return {"message": "API 키가 성공적으로 설정 및 저장되었습니다.", "has_key": bool(req.api_key)}


@app.post("/api/riot/clear-cache")
def clear_cache():
    import riot_service as rs
    rs._CACHE.clear()
    return {"message": "전적 캐시가 초기화되었습니다."}


@app.get("/api/sample-pool")
def get_sample_pool():
    # Calculate MMR for all sample players
    result = []
    for p in DEFAULT_SAMPLE_PLAYERS:
        player_dict = dict(p)
        player_dict["mmr"] = balancer.calculate_player_mmr(
            tier=p["tier"], rank=p.get("rank", "IV"), lp=p.get("lp", 0)
        )
        player_dict["is_active"] = True
        result.append(player_dict)
    return result


@app.post("/api/balance")
def calculate_balance(req: BalanceRequest):
    try:
        raw_players = [p.model_dump() for p in req.players]
        res = balancer.optimize_match(
            players=raw_players,
            weight_team=req.weight_team,
            weight_lane=req.weight_lane,
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"밸런싱 계산 중 오류: {str(e)}")


# Serve Frontend
@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "LoL Balancer Backend running. Place index.html in static/"}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print(" LoL 내전 황금 밸런스 매치메이커 서버가 시작됩니다!")
    print(" 브라우저에서 아래 주소로 접속하세요:")
    print(" -> http://localhost:8000")
    print("=" * 60)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
