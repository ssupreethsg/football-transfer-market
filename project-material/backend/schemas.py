from pydantic import BaseModel
from typing import Optional, List

class PlayerCompetitionStatBase(BaseModel):
    competition_name: str
    competition_type: str
    season: Optional[str] = "2025/2026"
    appearances: int = 0
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    shots: int = 0
    shots_on_target: int = 0
    chances_created: int = 0
    tackles_won: int = 0
    interceptions: int = 0
    clearances: int = 0
    blocks: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    stage_reached: Optional[str] = "Completed"

class PlayerCompetitionStat(PlayerCompetitionStatBase):
    id: int
    player_id: int

    class Config:
        from_attributes = True

class PlayerBase(BaseModel):
    name: str
    nation: Optional[str] = None
    age: int
    position: Optional[str] = "MID"
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    league: str
    team: str
    
    appearances: int = 0
    minutes_played: int = 0
    goals: int = 0
    assists: int = 0
    
    shots: int = 0
    shots_on_target: int = 0
    dribbles_completed: int = 0
    dribbles_attempted: int = 0
    
    chances_created: int = 0
    passes_completed: int = 0
    passes_attempted: int = 0
    progressive_passes: int = 0
    
    tackles_won: int = 0
    defense_interceptions: int = 0
    clearances: int = 0
    blocks: int = 0
    aerials_won: int = 0
    
    clean_sheets: int = 0
    saves: int = 0
    goals_conceded: int = 0
    
    touches: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    
    # Financial & Contract Clauses
    contract_expires_year: Optional[int] = 2028
    release_clause_eur: Optional[float] = None
    wage_eur_weekly: Optional[float] = 35000.0
    buyback_clause_eur: Optional[float] = None
    sell_on_pct: Optional[float] = None
    rating_score: Optional[float] = 75.0

class PlayerCreate(PlayerBase):

    pass

class Player(PlayerBase):
    id: int
    predicted_market_value_eur: float
    competition_stats: Optional[List[PlayerCompetitionStat]] = []

    class Config:
        from_attributes = True
