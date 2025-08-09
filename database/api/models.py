"""
MotoGP API Data Models
======================
Purpose: Pydantic models for API request/response serialization
Author: Claude Code Assistant
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Generic, TypeVar, Any, Dict
from datetime import datetime
from enum import Enum

# Generic type for API responses
T = TypeVar('T')

# =============================================================================
# BASE MODELS
# =============================================================================

class BaseAPIModel(BaseModel):
    """Base model with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_assignment=True
    )

class APIResponse(BaseAPIModel, Generic[T]):
    """Generic API response wrapper"""
    data: T
    total: int = Field(description="Total number of records available")
    limit: int = Field(description="Number of records returned")
    offset: int = Field(description="Number of records skipped")
    message: str = Field(description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# =============================================================================
# ENUMS
# =============================================================================

class CareerStatus(str, Enum):
    """Rider career status"""
    ACTIVE = "Active"
    RECENTLY_RETIRED = "Recently Retired"
    RETIRED = "Retired"

class PerformanceTier(str, Enum):
    """Performance tier classification"""
    CHAMPION = "Champion"
    CONTENDER = "Contender"
    REGULAR = "Regular"
    OCCASIONAL = "Occasional"

# =============================================================================
# RIDER MODELS
# =============================================================================

class RiderBasic(BaseAPIModel):
    """Basic rider information"""
    rider_id: int = Field(description="Unique rider identifier")
    rider_name: str = Field(description="Full rider name")
    rider_name_clean: str = Field(description="Standardized rider name")
    country_name: str = Field(description="Rider's country")
    country_code: str = Field(description="ISO country code")
    
class RiderSummary(RiderBasic):
    """Complete rider performance summary"""
    continent_name: str = Field(description="Rider's continent")
    career_start_year: Optional[int] = Field(description="First year of competition")
    career_end_year: Optional[int] = Field(description="Last year of competition")
    is_active: bool = Field(description="Currently active status")
    
    # Career statistics
    total_races: int = Field(description="Total races participated")
    total_wins: int = Field(description="Total race wins")
    total_podiums: int = Field(description="Total podium finishes")
    total_poles: int = Field(description="Total pole positions")
    total_fastest_laps: int = Field(description="Total fastest laps")
    total_championships: int = Field(description="Total world championships")
    
    # Performance metrics
    win_percentage: float = Field(description="Win rate as percentage")
    podium_percentage: float = Field(description="Podium rate as percentage")
    pole_percentage: float = Field(description="Pole position rate as percentage")
    fastest_lap_percentage: float = Field(description="Fastest lap rate as percentage")
    
    # Rankings
    wins_rank: int = Field(description="Ranking by total wins")
    podiums_rank: int = Field(description="Ranking by total podiums")
    win_rate_rank: int = Field(description="Ranking by win percentage")
    
    # Career metrics
    career_span_years: int = Field(description="Length of career in years")
    career_status: CareerStatus = Field(description="Current career status")

class RiderDetailed(RiderSummary):
    """Detailed rider information with additional statistics"""
    birth_date: Optional[datetime] = Field(description="Date of birth")
    birth_city: Optional[str] = Field(description="City of birth")
    
    # Additional performance metrics
    avg_finish_position: Optional[float] = Field(description="Average finishing position")
    consistency_score: Optional[float] = Field(description="Performance consistency metric")
    performance_tier: Optional[PerformanceTier] = Field(description="Performance tier classification")
    
    # Season-by-season breakdown
    best_season_year: Optional[int] = Field(description="Best performing season")
    best_season_wins: Optional[int] = Field(description="Wins in best season")

# =============================================================================
# CIRCUIT MODELS
# =============================================================================

class CircuitBasic(BaseAPIModel):
    """Basic circuit information"""
    circuit_id: int = Field(description="Unique circuit identifier")
    circuit_name: str = Field(description="Official circuit name")
    circuit_name_clean: str = Field(description="Standardized circuit name")
    country_name: str = Field(description="Host country")
    country_code: str = Field(description="ISO country code")

class CircuitSummary(CircuitBasic):
    """Circuit hosting and performance summary"""
    continent_name: str = Field(description="Circuit's continent")
    is_active: bool = Field(description="Currently active status")
    
    # Hosting statistics
    total_events_hosted: int = Field(description="Total events hosted")
    seasons_hosted: int = Field(description="Number of seasons hosted")
    first_year_hosted: Optional[int] = Field(description="First year of hosting")
    last_year_hosted: Optional[int] = Field(description="Most recent year hosted")
    hosting_span_years: int = Field(description="Span of hosting years")
    
    # Winner diversity
    unique_winners: int = Field(description="Number of different race winners")
    unique_winning_constructors: int = Field(description="Number of different winning constructors")
    unique_winning_countries: int = Field(description="Number of different winning countries")
    
    # Dominance analysis
    most_successful_rider: Optional[str] = Field(description="Most successful rider at this circuit")
    most_wins_by_single_rider: Optional[int] = Field(description="Most wins by any single rider")
    
    # Home advantage
    home_wins: int = Field(description="Wins by home country riders")
    total_wins: int = Field(description="Total wins recorded")
    home_win_percentage: float = Field(description="Percentage of home country wins")

# =============================================================================
# CONSTRUCTOR MODELS
# =============================================================================

class ConstructorBasic(BaseAPIModel):
    """Basic constructor information"""
    constructor_id: int = Field(description="Unique constructor identifier")
    constructor_name: str = Field(description="Official constructor name")
    constructor_name_clean: str = Field(description="Standardized constructor name")
    constructor_country: str = Field(description="Constructor's country")

class ConstructorSummary(ConstructorBasic):
    """Constructor performance and championship summary"""
    is_active: bool = Field(description="Currently active status")
    
    # Championship statistics
    total_championships: int = Field(description="Total constructor championships")
    classes_won: int = Field(description="Number of different classes won")
    championship_seasons: int = Field(description="Number of championship seasons")
    first_championship_year: Optional[int] = Field(description="First championship year")
    last_championship_year: Optional[int] = Field(description="Most recent championship year")
    
    # Race statistics
    total_race_wins: int = Field(description="Total race wins")
    total_podiums: int = Field(description="Total podium finishes")
    total_fastest_laps: int = Field(description="Total fastest laps")
    unique_riders: int = Field(description="Number of different riders")
    
    # Performance metrics
    win_percentage: float = Field(description="Race win percentage")
    podium_percentage: float = Field(description="Podium finish percentage")
    
    # Dominance periods
    active_span_years: int = Field(description="Years of active participation")
    
    # Rankings
    championship_rank: int = Field(description="Ranking by total championships")
    wins_rank: int = Field(description="Ranking by total wins")

# =============================================================================
# SEASON MODELS
# =============================================================================

class SeasonSummary(BaseAPIModel):
    """Season performance and participation summary"""
    season_id: int = Field(description="Unique season identifier")
    year: int = Field(description="Season year")
    era_name: str = Field(description="Historical era name")
    
    # Event statistics
    total_events: int = Field(description="Total events in season")
    unique_circuits: int = Field(description="Number of different circuits")
    classes_active: int = Field(description="Number of active racing classes")
    
    # Participation statistics
    unique_riders: int = Field(description="Number of different riders")
    unique_constructors: int = Field(description="Number of different constructors")
    countries_represented: int = Field(description="Number of countries represented")
    
    # Competition metrics
    unique_race_winners: int = Field(description="Number of different race winners")
    unique_podium_finishers: int = Field(description="Number of different podium finishers")
    competitive_balance_index: Optional[float] = Field(description="Competitive balance measure")

# =============================================================================
# COUNTRY PERFORMANCE MODELS
# =============================================================================

class CountryPerformance(BaseAPIModel):
    """Country-level performance statistics"""
    country_id: int = Field(description="Unique country identifier")
    country_code: str = Field(description="ISO country code")
    country_name: str = Field(description="Country name")
    continent_name: str = Field(description="Continent name")
    
    # Rider representation
    total_riders: int = Field(description="Total riders from this country")
    active_riders: int = Field(description="Currently active riders")
    
    # Performance statistics
    total_wins: int = Field(description="Total race wins")
    total_podiums: int = Field(description="Total podium finishes")
    total_championships: int = Field(description="Total world championships")
    home_circuits: int = Field(description="Number of home circuits")
    
    # Constructor presence
    total_constructors: int = Field(description="Total constructors from this country")
    active_constructors: int = Field(description="Currently active constructors")
    
    # Success rates
    avg_rider_win_rate: float = Field(description="Average rider win percentage")
    avg_rider_podium_rate: float = Field(description="Average rider podium percentage")
    
    # National dominance
    podium_lockouts: int = Field(description="Number of podium lockouts")
    
    # Rankings
    wins_rank: int = Field(description="Ranking by total wins")
    riders_count_rank: int = Field(description="Ranking by number of riders")

# =============================================================================
# RACE RESULT MODELS
# =============================================================================

class RaceResult(BaseAPIModel):
    """Individual race result"""
    result_id: int = Field(description="Unique result identifier")
    event_id: int = Field(description="Race event identifier")
    
    # Race information
    season_year: int = Field(description="Season year")
    circuit_name: str = Field(description="Circuit name")
    class_name: str = Field(description="Racing class")
    
    # Rider and constructor
    rider_name: str = Field(description="Rider name")
    constructor_name: str = Field(description="Constructor name")
    rider_country: str = Field(description="Rider's country")
    
    # Result details
    grid_position: Optional[int] = Field(description="Starting grid position")
    finish_position: Optional[int] = Field(description="Final finishing position")
    points_awarded: int = Field(description="Championship points awarded")
    
    # Performance flags
    is_winner: bool = Field(description="Race winner flag")
    is_podium: bool = Field(description="Podium finish flag")
    is_points: bool = Field(description="Points-scoring position flag")
    is_pole_position: bool = Field(description="Pole position flag")
    is_fastest_lap: bool = Field(description="Fastest lap flag")
    is_dnf: bool = Field(description="Did not finish flag")

# =============================================================================
# BUSINESS INTELLIGENCE MODELS
# =============================================================================

class ExecutiveDashboard(BaseAPIModel):
    """Executive dashboard KPIs"""
    # Overall statistics
    total_active_riders: int = Field(description="Currently active riders")
    total_active_circuits: int = Field(description="Currently active circuits")
    total_active_constructors: int = Field(description="Currently active constructors")
    countries_represented: int = Field(description="Countries with riders")
    
    # Current season
    current_season: int = Field(description="Current season year")
    current_season_events: int = Field(description="Events in current season")
    
    # Historical totals
    total_race_results: int = Field(description="Total race results recorded")
    total_race_wins: int = Field(description="Total race wins recorded")
    total_podiums: int = Field(description="Total podium finishes recorded")
    
    # Performance leaders
    most_wins_rider: str = Field(description="Rider with most wins")
    most_wins_count: int = Field(description="Highest win count")
    most_successful_constructor: str = Field(description="Most successful constructor")
    most_championships_count: int = Field(description="Highest championship count")
    
    # Geographic leaders
    most_successful_country: str = Field(description="Most successful country")
    most_country_wins: int = Field(description="Highest country win count")
    
    # Metadata
    last_updated: datetime = Field(description="Last data update timestamp")

# =============================================================================
# ANALYTICS MODELS
# =============================================================================

class TrendAnalysis(BaseAPIModel):
    """Trend analysis data point"""
    period: str = Field(description="Time period (year, decade, era)")
    metric_value: float = Field(description="Metric value for the period")
    metric_name: str = Field(description="Name of the metric")
    change_percentage: Optional[float] = Field(description="Percentage change from previous period")

class CompetitiveBalance(BaseAPIModel):
    """Competitive balance metrics"""
    season_year: int = Field(description="Season year")
    herfindahl_index: float = Field(description="Herfindahl-Hirschman concentration index")
    unique_winners: int = Field(description="Number of different winners")
    winner_share_top3: float = Field(description="Win share of top 3 performers")
    balance_rating: str = Field(description="Balance rating (High/Medium/Low)")

# =============================================================================
# ERROR MODELS
# =============================================================================

class ErrorResponse(BaseAPIModel):
    """API error response"""
    message: str = Field(description="Error message")
    status: str = Field(description="Error status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[Dict[str, Any]] = Field(description="Additional error details")