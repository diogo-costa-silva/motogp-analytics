"""
MotoGP Analytics API
====================
Purpose: FastAPI REST API for MotoGP database access
Author: Claude Code Assistant
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uvicorn
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

from database.api.database import get_database, DatabaseManager
from database.api.models import (
    RiderSummary, CircuitSummary, ConstructorSummary, 
    SeasonSummary, CountryPerformance, ExecutiveDashboard,
    RaceResult, APIResponse
)
from database.api.queries import MotoGPQueries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🚀 Starting MotoGP Analytics API...")
    
    # Initialize database connection
    try:
        db = DatabaseManager()
        db.connect()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise
        
    yield
    
    # Cleanup
    try:
        db.disconnect()
        logger.info("🔌 Database connection closed")
    except:
        pass

# Create FastAPI application
app = FastAPI(
    title="MotoGP Analytics API",
    description="""
    ## 🏁 MotoGP Analytics REST API
    
    Comprehensive API for accessing MotoGP historical data, performance statistics, and business intelligence.
    
    ### Features:
    * **Rider Performance**: Complete career statistics and rankings
    * **Circuit Analysis**: Track performance and hosting statistics  
    * **Constructor Data**: Championship history and market dominance
    * **Seasonal Trends**: Year-over-year competition analysis
    * **Geographic Intelligence**: Country and regional performance
    * **Business Intelligence**: Executive dashboards and KPIs
    
    ### Data Sources:
    Based on comprehensive analysis of 6 core MotoGP datasets covering historical race results,
    rider profiles, circuit information, constructor championships, and competitive dynamics.
    
    ### Usage:
    All endpoints support filtering, pagination, and sorting. Use the interactive docs below
    to explore available endpoints and test queries.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize queries handler
queries = MotoGPQueries()

# =============================================================================
# HEALTH CHECK ENDPOINTS
# =============================================================================

@app.get("/", response_model=Dict[str, Any])
async def root():
    """API root endpoint with basic information"""
    return {
        "message": "🏁 MotoGP Analytics API",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "riders": "/riders",
            "circuits": "/circuits", 
            "constructors": "/constructors",
            "seasons": "/seasons",
            "countries": "/countries",
            "dashboard": "/dashboard",
            "race_results": "/race-results"
        }
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check(db = Depends(get_database)):
    """Health check endpoint"""
    try:
        # Test database connection
        result = queries.test_connection(db)
        if result:
            return {"status": "healthy", "database": "connected"}
        else:
            raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

# =============================================================================
# RIDER ENDPOINTS
# =============================================================================

@app.get("/riders", response_model=APIResponse[List[RiderSummary]])
async def get_riders(
    limit: int = Query(50, ge=1, le=500, description="Number of riders to return"),
    offset: int = Query(0, ge=0, description="Number of riders to skip"),
    country: Optional[str] = Query(None, description="Filter by country code (e.g., ESP, ITA)"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    min_wins: Optional[int] = Query(None, ge=0, description="Minimum number of wins"),
    db = Depends(get_database)
):
    """Get rider performance summaries with filtering options"""
    try:
        riders = queries.get_riders(
            db, limit=limit, offset=offset, 
            country=country, active=active, min_wins=min_wins
        )
        
        total_count = queries.count_riders(db, country=country, active=active, min_wins=min_wins)
        
        return APIResponse(
            data=riders,
            total=total_count,
            limit=limit,
            offset=offset,
            message=f"Retrieved {len(riders)} riders"
        )
        
    except Exception as e:
        logger.error(f"Error fetching riders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/riders/{rider_id}", response_model=RiderSummary)
async def get_rider(rider_id: int, db = Depends(get_database)):
    """Get detailed information for a specific rider"""
    try:
        rider = queries.get_rider_by_id(db, rider_id)
        if not rider:
            raise HTTPException(status_code=404, detail="Rider not found")
        return rider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching rider {rider_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/riders/search/{name}", response_model=APIResponse[List[RiderSummary]])
async def search_riders(
    name: str, 
    limit: int = Query(20, ge=1, le=100),
    db = Depends(get_database)
):
    """Search riders by name (partial matching)"""
    try:
        riders = queries.search_riders_by_name(db, name, limit=limit)
        return APIResponse(
            data=riders,
            total=len(riders),
            limit=limit,
            offset=0,
            message=f"Found {len(riders)} riders matching '{name}'"
        )
    except Exception as e:
        logger.error(f"Error searching riders: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# CIRCUIT ENDPOINTS  
# =============================================================================

@app.get("/circuits", response_model=APIResponse[List[CircuitSummary]])
async def get_circuits(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    country: Optional[str] = Query(None, description="Filter by country code"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    db = Depends(get_database)
):
    """Get circuit information with hosting statistics"""
    try:
        circuits = queries.get_circuits(
            db, limit=limit, offset=offset, 
            country=country, active=active
        )
        
        total_count = queries.count_circuits(db, country=country, active=active)
        
        return APIResponse(
            data=circuits,
            total=total_count,
            limit=limit,
            offset=offset,
            message=f"Retrieved {len(circuits)} circuits"
        )
        
    except Exception as e:
        logger.error(f"Error fetching circuits: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/circuits/{circuit_id}", response_model=CircuitSummary)
async def get_circuit(circuit_id: int, db = Depends(get_database)):
    """Get detailed information for a specific circuit"""
    try:
        circuit = queries.get_circuit_by_id(db, circuit_id)
        if not circuit:
            raise HTTPException(status_code=404, detail="Circuit not found")
        return circuit
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching circuit {circuit_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# CONSTRUCTOR ENDPOINTS
# =============================================================================

@app.get("/constructors", response_model=APIResponse[List[ConstructorSummary]])
async def get_constructors(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    country: Optional[str] = Query(None, description="Filter by country code"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    db = Depends(get_database)
):
    """Get constructor performance and championship data"""
    try:
        constructors = queries.get_constructors(
            db, limit=limit, offset=offset, 
            country=country, active=active
        )
        
        total_count = queries.count_constructors(db, country=country, active=active)
        
        return APIResponse(
            data=constructors,
            total=total_count,
            limit=limit,
            offset=offset,
            message=f"Retrieved {len(constructors)} constructors"
        )
        
    except Exception as e:
        logger.error(f"Error fetching constructors: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# BUSINESS INTELLIGENCE ENDPOINTS
# =============================================================================

@app.get("/dashboard", response_model=ExecutiveDashboard)
async def get_executive_dashboard(db = Depends(get_database)):
    """Get executive dashboard with key performance indicators"""
    try:
        dashboard = queries.get_executive_dashboard(db)
        return dashboard
    except Exception as e:
        logger.error(f"Error fetching dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/countries/performance", response_model=APIResponse[List[CountryPerformance]])
async def get_country_performance(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    continent: Optional[str] = Query(None, description="Filter by continent"),
    db = Depends(get_database)
):
    """Get country-level performance statistics"""
    try:
        countries = queries.get_country_performance(
            db, limit=limit, offset=offset, continent=continent
        )
        
        return APIResponse(
            data=countries,
            total=len(countries),
            limit=limit,
            offset=offset,
            message=f"Retrieved {len(countries)} countries"
        )
        
    except Exception as e:
        logger.error(f"Error fetching country performance: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# SEASONAL ANALYSIS ENDPOINTS
# =============================================================================

@app.get("/seasons", response_model=APIResponse[List[SeasonSummary]])
async def get_seasons(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    start_year: Optional[int] = Query(None, ge=1900, le=2030),
    end_year: Optional[int] = Query(None, ge=1900, le=2030),
    db = Depends(get_database)
):
    """Get seasonal performance summaries"""
    try:
        seasons = queries.get_seasons(
            db, limit=limit, offset=offset, 
            start_year=start_year, end_year=end_year
        )
        
        return APIResponse(
            data=seasons,
            total=len(seasons),
            limit=limit,
            offset=offset,
            message=f"Retrieved {len(seasons)} seasons"
        )
        
    except Exception as e:
        logger.error(f"Error fetching seasons: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# RACE RESULTS ENDPOINTS
# =============================================================================

@app.get("/race-results", response_model=APIResponse[List[RaceResult]])
async def get_race_results(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    season: Optional[int] = Query(None, ge=1900, le=2030),
    circuit_id: Optional[int] = Query(None, ge=1),
    rider_id: Optional[int] = Query(None, ge=1),
    winners_only: bool = Query(False, description="Only return race winners"),
    db = Depends(get_database)
):
    """Get detailed race results with filtering options"""
    try:
        results = queries.get_race_results(
            db, limit=limit, offset=offset, 
            season=season, circuit_id=circuit_id, 
            rider_id=rider_id, winners_only=winners_only
        )
        
        return APIResponse(
            data=results,
            total=len(results),
            limit=limit,
            offset=offset,
            message=f"Retrieved {len(results)} race results"
        )
        
    except Exception as e:
        logger.error(f"Error fetching race results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.get("/stats/summary", response_model=Dict[str, Any])
async def get_database_stats(db = Depends(get_database)):
    """Get database statistics and record counts"""
    try:
        stats = queries.get_database_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Error fetching database stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/admin/refresh-views")
async def refresh_materialized_views(db = Depends(get_database)):
    """Refresh all materialized views (admin endpoint)"""
    try:
        queries.refresh_materialized_views(db)
        return {"message": "Materialized views refreshed successfully"}
    except Exception as e:
        logger.error(f"Error refreshing views: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh materialized views")

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found", "status": "error"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "status": "error"}
    )

# =============================================================================
# DEVELOPMENT SERVER
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )