from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import Optional, List
import models
import schemas
from database import engine, get_db

# Create DB tables if needed
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Football Transfer Analytics API",
    description="API for fetching predictions, contract clauses, and multi-competition statistics (2026 Season)",
    version="2.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Football Transfer Analytics API",
        "season": "2026",
        "reference_date": "August 30, 2026",
        "features": [
            "Contract Expiry & Buyout Clauses",
            "Capology Wage Estimates",
            "Multi-Competition Statistics (League, Cups, UCL, International)"
        ],
        "status": "online"
    }

@app.get("/players", response_model=List[schemas.Player])
def read_players(
    skip: int = Query(0, ge=0, description="Skip N records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records returned"),
    league: Optional[str] = Query(None, description="Filter by league (e.g. Premier League, La Liga)"),
    team: Optional[str] = Query(None, description="Filter by team"),
    position: Optional[str] = Query(None, description="Filter by position (FWD, MID, DEF, GK)"),
    search: Optional[str] = Query(None, description="Search by player name"),
    min_value: Optional[float] = Query(None, description="Minimum market value in EUR"),
    max_value: Optional[float] = Query(None, description="Maximum market value in EUR"),
    has_release_clause: Optional[bool] = Query(None, description="Filter players with active release clauses"),
    sort_by_value: bool = Query(True, description="Sort by market value descending"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Player).options(joinedload(models.Player.competition_stats))
    
    if league:
        query = query.filter(models.Player.league.ilike(f"%{league}%"))
        
    if team:
        query = query.filter(models.Player.team.ilike(f"%{team}%"))
        
    if position:
        query = query.filter(models.Player.position == position.upper())
        
    if search:
        query = query.filter(models.Player.name.ilike(f"%{search}%"))
        
    if min_value is not None:
        query = query.filter(models.Player.predicted_market_value_eur >= min_value)
        
    if max_value is not None:
        query = query.filter(models.Player.predicted_market_value_eur <= max_value)
        
    if has_release_clause is True:
        query = query.filter(models.Player.release_clause_eur.isnot(None), models.Player.release_clause_eur > 0)
    elif has_release_clause is False:
        query = query.filter(models.Player.release_clause_eur.is_(None))
        
    if sort_by_value:
        query = query.order_by(desc(models.Player.predicted_market_value_eur))
    else:
        query = query.order_by(models.Player.name)
        
    players = query.offset(skip).limit(limit).all()
    return players

@app.get("/players/{player_id}", response_model=schemas.Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(models.Player).options(joinedload(models.Player.competition_stats)).filter(models.Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.get("/players/{player_id}/competitions", response_model=List[schemas.PlayerCompetitionStat])
def get_player_competitions(player_id: int, db: Session = Depends(get_db)):
    stats = db.query(models.PlayerCompetitionStat).filter(models.PlayerCompetitionStat.player_id == player_id).all()
    return stats

@app.get("/stats/summary")
def get_summary_stats(db: Session = Depends(get_db)):
    total_players = db.query(models.Player).count()
    top_player = db.query(models.Player).order_by(desc(models.Player.predicted_market_value_eur)).first()
    clause_count = db.query(models.Player).filter(models.Player.release_clause_eur.isnot(None)).count()
    comp_count = db.query(models.PlayerCompetitionStat).count()
    
    return {
        "total_players": total_players,
        "players_with_release_clause": clause_count,
        "total_competition_records": comp_count,
        "most_valuable_player": {
            "name": top_player.name if top_player else None,
            "team": top_player.team if top_player else None,
            "value_eur": top_player.predicted_market_value_eur if top_player else 0,
            "release_clause_eur": top_player.release_clause_eur if top_player else None
        }
    }

@app.post("/api/sync")
def trigger_sync():
    import live_updater
    return live_updater.run_live_sync()

@app.get("/api/sync/status")
def get_sync_status():
    import live_updater
    return live_updater.LAST_SYNC_METADATA

@app.post("/api/players/update")
def update_player_endpoint(payload: dict):
    import live_updater
    player_id_or_name = payload.get("id") or payload.get("name")
    if not player_id_or_name:
        raise HTTPException(status_code=400, detail="Missing player id or name")
    
    fields = {k: v for k, v in payload.items() if k not in ("id", "name")}
    affected = live_updater.update_player(player_id_or_name, **fields)
    return {"success": affected > 0, "affected_rows": affected}

