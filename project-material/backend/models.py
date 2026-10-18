from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class PlayerCompetitionStat(Base):
    __tablename__ = "player_competition_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), index=True, nullable=False)
    competition_name = Column(String, index=True, nullable=False)
    competition_type = Column(String, index=True, nullable=False)  # 'league', 'domestic_cup', 'continental', 'international'
    season = Column(String, default="2025/2026")
    
    appearances = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    
    shots = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    chances_created = Column(Integer, default=0)
    
    tackles_won = Column(Integer, default=0)
    interceptions = Column(Integer, default=0)
    clearances = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    stage_reached = Column(String, default="Completed")
    
    player = relationship("Player", back_populates="competition_stats")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    nation = Column(String, index=True, nullable=True)
    age = Column(Integer)
    position = Column(String, index=True, default="MID")
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    league = Column(String, index=True)
    team = Column(String, index=True)
    
    # Core
    appearances = Column(Integer, default=0)
    minutes_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    
    # Attacking
    shots = Column(Integer, default=0)
    shots_on_target = Column(Integer, default=0)
    dribbles_completed = Column(Integer, default=0)
    dribbles_attempted = Column(Integer, default=0)
    
    # Passing
    chances_created = Column(Integer, default=0)
    passes_completed = Column(Integer, default=0)
    passes_attempted = Column(Integer, default=0)
    progressive_passes = Column(Integer, default=0)
    
    # Defending
    tackles_won = Column(Integer, default=0)
    defense_interceptions = Column(Integer, default=0)
    clearances = Column(Integer, default=0)
    blocks = Column(Integer, default=0)
    aerials_won = Column(Integer, default=0)
    
    # Goalkeeping
    clean_sheets = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    goals_conceded = Column(Integer, default=0)
    
    # Miscellaneous
    touches = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    
    # Financial & Contract Clauses
    contract_expires_year = Column(Integer, default=2028)
    release_clause_eur = Column(Float, nullable=True)
    wage_eur_weekly = Column(Float, default=35000.0)
    buyback_clause_eur = Column(Float, nullable=True)
    sell_on_pct = Column(Float, nullable=True)
    
    predicted_market_value_eur = Column(Float)
    rating_score = Column(Float, default=75.0)
    
    competition_stats = relationship("PlayerCompetitionStat", back_populates="player", cascade="all, delete-orphan")

