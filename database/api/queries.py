"""
MotoGP Database Query Handlers
==============================
Purpose: SQL query implementations for all API endpoints
Author: Claude Code Assistant
"""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from .database import QueryBuilder
from .models import (
    RiderSummary, RiderBasic, CircuitSummary, ConstructorSummary,
    SeasonSummary, CountryPerformance, ExecutiveDashboard, RaceResult,
    CareerStatus, PerformanceTier
)

logger = logging.getLogger(__name__)

class MotoGPQueries:
    """SQL query handlers for MotoGP analytics database"""
    
    def __init__(self):
        self.query_builder = QueryBuilder()
        
    def test_connection(self, db) -> bool:
        """Test database connection"""
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT 1")
                return bool(cursor.fetchone())
        except Exception:
            return False
    
    # ==========================================================================
    # RIDER QUERIES
    # ==========================================================================
    
    def get_riders(self, db, limit: int = 50, offset: int = 0, 
                   country: Optional[str] = None, active: Optional[bool] = None,
                   min_wins: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get rider performance summaries with filtering"""
        
        conditions = {}
        if country:
            conditions['c.country_code'] = country.upper()
        if active is not None:
            conditions['r.is_active'] = active
        if min_wins is not None:
            conditions['r.total_wins >='] = min_wins
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        limit_clause = self.query_builder.build_limit_offset(limit, offset)
        
        query = f"""
        SELECT 
            r.rider_id,
            r.rider_name,
            r.rider_name_clean,
            c.country_name,
            c.country_code,
            cont.continent_name,
            r.career_start_year,
            r.career_end_year,
            r.is_active,
            r.total_races,
            r.total_wins,
            r.total_podiums,
            r.total_poles,
            r.total_fastest_laps,
            r.total_championships,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_wins::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as win_percentage,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_podiums::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as podium_percentage,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_poles::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as pole_percentage,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_fastest_laps::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as fastest_lap_percentage,
            RANK() OVER (ORDER BY r.total_wins DESC) as wins_rank,
            RANK() OVER (ORDER BY r.total_podiums DESC) as podiums_rank,
            RANK() OVER (ORDER BY 
                CASE 
                    WHEN r.total_races > 0 THEN r.total_wins::FLOAT / r.total_races::FLOAT
                    ELSE 0
                END DESC
            ) as win_rate_rank,
            COALESCE(r.career_end_year, EXTRACT(YEAR FROM CURRENT_DATE)) - r.career_start_year as career_span_years,
            CASE 
                WHEN r.is_active THEN 'Active'
                WHEN COALESCE(r.career_end_year, 2024) >= 2020 THEN 'Recently Retired'
                ELSE 'Retired'
            END as career_status
        FROM riders r
        JOIN countries c ON r.country_id = c.country_id
        JOIN continents cont ON c.continent_id = cont.continent_id
        {where_clause}
        ORDER BY r.total_wins DESC, r.total_podiums DESC
        {limit_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error executing get_riders: {e}")
            raise
            
    def count_riders(self, db, country: Optional[str] = None, 
                     active: Optional[bool] = None, min_wins: Optional[int] = None) -> int:
        """Count riders matching filters"""
        
        conditions = {}
        if country:
            conditions['c.country_code'] = country.upper()
        if active is not None:
            conditions['r.is_active'] = active
        if min_wins is not None:
            conditions['r.total_wins >='] = min_wins
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        
        query = f"""
        SELECT COUNT(*) 
        FROM riders r
        JOIN countries c ON r.country_id = c.country_id
        {where_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error counting riders: {e}")
            return 0
            
    def get_rider_by_id(self, db, rider_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed rider information by ID"""
        
        query = """
        SELECT 
            r.rider_id,
            r.rider_name,
            r.rider_name_clean,
            c.country_name,
            c.country_code,
            cont.continent_name,
            r.career_start_year,
            r.career_end_year,
            r.is_active,
            r.total_races,
            r.total_wins,
            r.total_podiums,
            r.total_poles,
            r.total_fastest_laps,
            r.total_championships,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_wins::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as win_percentage,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_podiums::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as podium_percentage,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_poles::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as pole_percentage,
            CASE 
                WHEN r.total_races > 0 THEN ROUND((r.total_fastest_laps::FLOAT / r.total_races::FLOAT) * 100, 2)
                ELSE 0.0
            END as fastest_lap_percentage,
            RANK() OVER (ORDER BY r.total_wins DESC) as wins_rank,
            RANK() OVER (ORDER BY r.total_podiums DESC) as podiums_rank,
            RANK() OVER (ORDER BY 
                CASE 
                    WHEN r.total_races > 0 THEN r.total_wins::FLOAT / r.total_races::FLOAT
                    ELSE 0
                END DESC
            ) as win_rate_rank,
            COALESCE(r.career_end_year, EXTRACT(YEAR FROM CURRENT_DATE)) - r.career_start_year as career_span_years,
            CASE 
                WHEN r.is_active THEN 'Active'
                WHEN COALESCE(r.career_end_year, 2024) >= 2020 THEN 'Recently Retired'
                ELSE 'Retired'
            END as career_status
        FROM riders r
        JOIN countries c ON r.country_id = c.country_id
        JOIN continents cont ON c.continent_id = cont.continent_id
        WHERE r.rider_id = %s
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, (rider_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting rider by ID: {e}")
            return None
            
    def search_riders_by_name(self, db, name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search riders by name with partial matching"""
        
        query = """
        SELECT 
            r.rider_id,
            r.rider_name,
            r.rider_name_clean,
            c.country_name,
            c.country_code,
            r.total_wins,
            r.total_podiums,
            r.is_active
        FROM riders r
        JOIN countries c ON r.country_id = c.country_id
        WHERE r.rider_name ILIKE %s OR r.rider_name_clean ILIKE %s
        ORDER BY 
            CASE WHEN r.rider_name ILIKE %s THEN 1 ELSE 2 END,
            r.total_wins DESC
        LIMIT %s
        """
        
        search_pattern = f"%{name}%"
        exact_pattern = f"{name}%"
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, (search_pattern, search_pattern, exact_pattern, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error searching riders: {e}")
            return []
    
    # ==========================================================================
    # CIRCUIT QUERIES
    # ==========================================================================
    
    def get_circuits(self, db, limit: int = 50, offset: int = 0,
                     country: Optional[str] = None, active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get circuit information with hosting statistics"""
        
        conditions = {}
        if country:
            conditions['c.country_code'] = country.upper()
        if active is not None:
            conditions['circ.is_active'] = active
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        limit_clause = self.query_builder.build_limit_offset(limit, offset)
        
        query = f"""
        SELECT 
            circ.circuit_id,
            circ.circuit_name,
            circ.circuit_name_clean,
            c.country_name,
            c.country_code,
            cont.continent_name,
            circ.is_active,
            circ.total_events_hosted,
            circ.seasons_hosted,
            circ.first_year_hosted,
            circ.last_year_hosted,
            circ.last_year_hosted - circ.first_year_hosted as hosting_span_years,
            circ.unique_winners,
            circ.unique_winning_constructors,
            circ.unique_winning_countries,
            circ.most_successful_rider,
            circ.most_wins_by_single_rider,
            circ.home_wins,
            circ.total_wins,
            CASE 
                WHEN circ.total_wins > 0 THEN ROUND((circ.home_wins::FLOAT / circ.total_wins::FLOAT) * 100, 2)
                ELSE 0.0
            END as home_win_percentage
        FROM circuits circ
        JOIN countries c ON circ.country_id = c.country_id
        JOIN continents cont ON c.continent_id = cont.continent_id
        {where_clause}
        ORDER BY circ.total_events_hosted DESC, circ.circuit_name
        {limit_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error executing get_circuits: {e}")
            raise
            
    def count_circuits(self, db, country: Optional[str] = None, active: Optional[bool] = None) -> int:
        """Count circuits matching filters"""
        
        conditions = {}
        if country:
            conditions['c.country_code'] = country.upper()
        if active is not None:
            conditions['circ.is_active'] = active
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        
        query = f"""
        SELECT COUNT(*) 
        FROM circuits circ
        JOIN countries c ON circ.country_id = c.country_id
        {where_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error counting circuits: {e}")
            return 0
            
    def get_circuit_by_id(self, db, circuit_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed circuit information by ID"""
        
        query = """
        SELECT 
            circ.circuit_id,
            circ.circuit_name,
            circ.circuit_name_clean,
            c.country_name,
            c.country_code,
            cont.continent_name,
            circ.is_active,
            circ.total_events_hosted,
            circ.seasons_hosted,
            circ.first_year_hosted,
            circ.last_year_hosted,
            circ.last_year_hosted - circ.first_year_hosted as hosting_span_years,
            circ.unique_winners,
            circ.unique_winning_constructors,
            circ.unique_winning_countries,
            circ.most_successful_rider,
            circ.most_wins_by_single_rider,
            circ.home_wins,
            circ.total_wins,
            CASE 
                WHEN circ.total_wins > 0 THEN ROUND((circ.home_wins::FLOAT / circ.total_wins::FLOAT) * 100, 2)
                ELSE 0.0
            END as home_win_percentage
        FROM circuits circ
        JOIN countries c ON circ.country_id = c.country_id
        JOIN continents cont ON c.continent_id = cont.continent_id
        WHERE circ.circuit_id = %s
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, (circuit_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error getting circuit by ID: {e}")
            return None
    
    # ==========================================================================
    # CONSTRUCTOR QUERIES
    # ==========================================================================
    
    def get_constructors(self, db, limit: int = 50, offset: int = 0,
                         country: Optional[str] = None, active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Get constructor performance and championship data"""
        
        conditions = {}
        if country:
            conditions['cons.constructor_country'] = country.upper()
        if active is not None:
            conditions['cons.is_active'] = active
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        limit_clause = self.query_builder.build_limit_offset(limit, offset)
        
        query = f"""
        SELECT 
            cons.constructor_id,
            cons.constructor_name,
            cons.constructor_name_clean,
            cons.constructor_country,
            cons.is_active,
            cons.total_championships,
            cons.classes_won,
            cons.championship_seasons,
            cons.first_championship_year,
            cons.last_championship_year,
            cons.total_race_wins,
            cons.total_podiums,
            cons.total_fastest_laps,
            cons.unique_riders,
            CASE 
                WHEN cons.championship_seasons > 0 THEN ROUND((cons.total_race_wins::FLOAT / cons.championship_seasons::FLOAT) * 100, 2)
                ELSE 0.0
            END as win_percentage,
            CASE 
                WHEN cons.championship_seasons > 0 THEN ROUND((cons.total_podiums::FLOAT / cons.championship_seasons::FLOAT) * 100, 2)
                ELSE 0.0
            END as podium_percentage,
            COALESCE(cons.last_championship_year, cons.first_championship_year) - cons.first_championship_year as active_span_years,
            RANK() OVER (ORDER BY cons.total_championships DESC) as championship_rank,
            RANK() OVER (ORDER BY cons.total_race_wins DESC) as wins_rank
        FROM constructors cons
        {where_clause}
        ORDER BY cons.total_championships DESC, cons.total_race_wins DESC
        {limit_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error executing get_constructors: {e}")
            raise
            
    def count_constructors(self, db, country: Optional[str] = None, active: Optional[bool] = None) -> int:
        """Count constructors matching filters"""
        
        conditions = {}
        if country:
            conditions['cons.constructor_country'] = country.upper()
        if active is not None:
            conditions['cons.is_active'] = active
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        
        query = f"""
        SELECT COUNT(*) 
        FROM constructors cons
        {where_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()['count']
        except Exception as e:
            logger.error(f"Error counting constructors: {e}")
            return 0
    
    # ==========================================================================
    # BUSINESS INTELLIGENCE QUERIES
    # ==========================================================================
    
    def get_executive_dashboard(self, db) -> Dict[str, Any]:
        """Get executive dashboard with key performance indicators"""
        
        query = """
        SELECT 
            -- Current active counts
            (SELECT COUNT(*) FROM riders WHERE is_active = true) as total_active_riders,
            (SELECT COUNT(*) FROM circuits WHERE is_active = true) as total_active_circuits,
            (SELECT COUNT(*) FROM constructors WHERE is_active = true) as total_active_constructors,
            (SELECT COUNT(DISTINCT country_id) FROM riders) as countries_represented,
            
            -- Current season (assuming we have seasons table)
            (SELECT MAX(year) FROM seasons) as current_season,
            (SELECT total_events FROM seasons WHERE year = (SELECT MAX(year) FROM seasons)) as current_season_events,
            
            -- Historical totals
            (SELECT COUNT(*) FROM race_results) as total_race_results,
            (SELECT COUNT(*) FROM race_results WHERE is_winner = true) as total_race_wins,
            (SELECT COUNT(*) FROM race_results WHERE is_podium = true) as total_podiums,
            
            -- Performance leaders
            (SELECT r.rider_name FROM riders r ORDER BY r.total_wins DESC LIMIT 1) as most_wins_rider,
            (SELECT MAX(total_wins) FROM riders) as most_wins_count,
            (SELECT c.constructor_name FROM constructors c ORDER BY c.total_championships DESC LIMIT 1) as most_successful_constructor,
            (SELECT MAX(total_championships) FROM constructors) as most_championships_count,
            
            -- Geographic leaders
            (SELECT co.country_name FROM countries co 
             JOIN riders r ON co.country_id = r.country_id 
             GROUP BY co.country_name 
             ORDER BY SUM(r.total_wins) DESC LIMIT 1) as most_successful_country,
            (SELECT MAX(country_wins) FROM (
                SELECT SUM(r.total_wins) as country_wins
                FROM countries co 
                JOIN riders r ON co.country_id = r.country_id 
                GROUP BY co.country_name
            ) cw) as most_country_wins,
            
            -- Metadata
            CURRENT_TIMESTAMP as last_updated
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return dict(result) if result else {}
        except Exception as e:
            logger.error(f"Error getting executive dashboard: {e}")
            return {}
    
    def get_country_performance(self, db, limit: int = 50, offset: int = 0,
                                continent: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get country-level performance statistics"""
        
        conditions = {}
        if continent:
            conditions['cont.continent_name'] = continent
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        limit_clause = self.query_builder.build_limit_offset(limit, offset)
        
        query = f"""
        SELECT 
            c.country_id,
            c.country_code,
            c.country_name,
            cont.continent_name,
            COUNT(DISTINCT r.rider_id) as total_riders,
            COUNT(DISTINCT CASE WHEN r.is_active THEN r.rider_id END) as active_riders,
            SUM(r.total_wins) as total_wins,
            SUM(r.total_podiums) as total_podiums,
            SUM(r.total_championships) as total_championships,
            COUNT(DISTINCT circ.circuit_id) as home_circuits,
            COUNT(DISTINCT cons.constructor_id) as total_constructors,
            COUNT(DISTINCT CASE WHEN cons.is_active THEN cons.constructor_id END) as active_constructors,
            CASE 
                WHEN COUNT(r.rider_id) > 0 THEN ROUND(AVG(
                    CASE WHEN r.total_races > 0 THEN r.total_wins::FLOAT / r.total_races::FLOAT * 100 ELSE 0 END
                ), 2)
                ELSE 0.0
            END as avg_rider_win_rate,
            CASE 
                WHEN COUNT(r.rider_id) > 0 THEN ROUND(AVG(
                    CASE WHEN r.total_races > 0 THEN r.total_podiums::FLOAT / r.total_races::FLOAT * 100 ELSE 0 END
                ), 2)
                ELSE 0.0
            END as avg_rider_podium_rate,
            0 as podium_lockouts, -- This would require more complex analysis
            RANK() OVER (ORDER BY SUM(r.total_wins) DESC) as wins_rank,
            RANK() OVER (ORDER BY COUNT(DISTINCT r.rider_id) DESC) as riders_count_rank
        FROM countries c
        JOIN continents cont ON c.continent_id = cont.continent_id
        LEFT JOIN riders r ON c.country_id = r.country_id
        LEFT JOIN circuits circ ON c.country_id = circ.country_id
        LEFT JOIN constructors cons ON c.country_name = cons.constructor_country
        {where_clause}
        GROUP BY c.country_id, c.country_code, c.country_name, cont.continent_name
        HAVING COUNT(DISTINCT r.rider_id) > 0  -- Only countries with riders
        ORDER BY SUM(r.total_wins) DESC, COUNT(DISTINCT r.rider_id) DESC
        {limit_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting country performance: {e}")
            raise
    
    # ==========================================================================
    # SEASON QUERIES
    # ==========================================================================
    
    def get_seasons(self, db, limit: int = 20, offset: int = 0,
                    start_year: Optional[int] = None, end_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get seasonal performance summaries"""
        
        conditions = {}
        if start_year:
            conditions['s.year >='] = start_year
        if end_year:
            conditions['s.year <='] = end_year
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        limit_clause = self.query_builder.build_limit_offset(limit, offset)
        
        query = f"""
        SELECT 
            s.season_id,
            s.year,
            s.era_name,
            s.total_events,
            s.unique_circuits,
            s.classes_active,
            s.unique_riders,
            s.unique_constructors,
            s.countries_represented,
            s.unique_race_winners,
            s.unique_podium_finishers,
            s.competitive_balance_index
        FROM seasons s
        {where_clause}
        ORDER BY s.year DESC
        {limit_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting seasons: {e}")
            raise
    
    # ==========================================================================
    # RACE RESULT QUERIES
    # ==========================================================================
    
    def get_race_results(self, db, limit: int = 100, offset: int = 0,
                         season: Optional[int] = None, circuit_id: Optional[int] = None,
                         rider_id: Optional[int] = None, winners_only: bool = False) -> List[Dict[str, Any]]:
        """Get detailed race results with filtering options"""
        
        conditions = {}
        if season:
            conditions['rr.season_year'] = season
        if circuit_id:
            conditions['rr.circuit_id'] = circuit_id
        if rider_id:
            conditions['rr.rider_id'] = rider_id
        if winners_only:
            conditions['rr.is_winner'] = True
            
        where_clause, params = self.query_builder.build_where_clause(conditions)
        limit_clause = self.query_builder.build_limit_offset(limit, offset)
        
        query = f"""
        SELECT 
            rr.result_id,
            rr.event_id,
            rr.season_year,
            circ.circuit_name,
            cl.class_name,
            r.rider_name,
            cons.constructor_name,
            c.country_name as rider_country,
            rr.grid_position,
            rr.finish_position,
            rr.points_awarded,
            rr.is_winner,
            rr.is_podium,
            rr.is_points,
            rr.is_pole_position,
            rr.is_fastest_lap,
            rr.is_dnf
        FROM race_results rr
        JOIN riders r ON rr.rider_id = r.rider_id
        JOIN circuits circ ON rr.circuit_id = circ.circuit_id
        JOIN constructors cons ON rr.constructor_id = cons.constructor_id
        JOIN countries c ON r.country_id = c.country_id
        JOIN classes cl ON rr.class_id = cl.class_id
        {where_clause}
        ORDER BY rr.season_year DESC, rr.event_id DESC, rr.finish_position ASC
        {limit_clause}
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting race results: {e}")
            raise
    
    # ==========================================================================
    # UTILITY QUERIES
    # ==========================================================================
    
    def get_database_stats(self, db) -> Dict[str, Any]:
        """Get database statistics and record counts"""
        
        query = """
        SELECT 
            'riders' as table_name, COUNT(*) as record_count FROM riders
        UNION ALL
        SELECT 'circuits', COUNT(*) FROM circuits
        UNION ALL
        SELECT 'constructors', COUNT(*) FROM constructors
        UNION ALL
        SELECT 'race_results', COUNT(*) FROM race_results
        UNION ALL
        SELECT 'countries', COUNT(*) FROM countries
        UNION ALL
        SELECT 'seasons', COUNT(*) FROM seasons
        UNION ALL
        SELECT 'classes', COUNT(*) FROM classes
        """
        
        try:
            with db.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
                stats = {}
                for row in results:
                    stats[row['table_name']] = row['record_count']
                    
                # Add summary statistics
                stats['total_records'] = sum(stats.values())
                stats['last_updated'] = datetime.now().isoformat()
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def refresh_materialized_views(self, db):
        """Refresh all materialized views"""
        
        views_to_refresh = [
            'mv_rider_performance_summary',
            'mv_circuit_hosting_analysis',
            'mv_constructor_dominance',
            'mv_country_performance_analysis',
            'mv_seasonal_competitive_balance',
            'mv_executive_dashboard'
        ]
        
        try:
            with db.cursor() as cursor:
                for view in views_to_refresh:
                    cursor.execute(f"REFRESH MATERIALIZED VIEW {view}")
                    logger.info(f"Refreshed materialized view: {view}")
                    
                # Commit the transaction
                db.commit()
                
        except Exception as e:
            logger.error(f"Error refreshing materialized views: {e}")
            db.rollback()
            raise