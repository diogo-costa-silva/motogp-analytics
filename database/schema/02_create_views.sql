-- =============================================================================
-- MotoGP Analytics Database - Materialized Views
-- =============================================================================
-- Purpose: Pre-calculated views for performance and BI tools integration
-- Author: Claude Code Assistant
-- Target: PostgreSQL 13+
-- =============================================================================

-- =============================================================================
-- RIDER PERFORMANCE VIEWS
-- =============================================================================

-- Comprehensive rider performance summary
CREATE MATERIALIZED VIEW mv_rider_performance_summary AS
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
    
    -- Race statistics
    r.total_races,
    r.total_wins,
    r.total_podiums,
    r.total_poles,
    r.total_fastest_laps,
    r.total_championships,
    
    -- Calculated percentages
    r.win_percentage,
    r.podium_percentage,
    CASE 
        WHEN r.total_races > 0 
        THEN ROUND((r.total_poles::NUMERIC / r.total_races) * 100, 2)
        ELSE 0 
    END AS pole_percentage,
    
    CASE 
        WHEN r.total_races > 0 
        THEN ROUND((r.total_fastest_laps::NUMERIC / r.total_races) * 100, 2)
        ELSE 0 
    END AS fastest_lap_percentage,
    
    -- Performance rankings
    RANK() OVER (ORDER BY r.total_wins DESC) as wins_rank,
    RANK() OVER (ORDER BY r.total_podiums DESC) as podiums_rank,
    RANK() OVER (ORDER BY r.win_percentage DESC) as win_rate_rank,
    
    -- Career span
    COALESCE(r.career_end_year, EXTRACT(YEAR FROM CURRENT_DATE)) - r.career_start_year + 1 as career_span_years,
    
    -- Activity status
    CASE 
        WHEN r.career_end_year IS NULL THEN 'Active'
        WHEN r.career_end_year >= EXTRACT(YEAR FROM CURRENT_DATE) - 5 THEN 'Recently Retired'
        ELSE 'Retired'
    END as career_status,
    
    CURRENT_TIMESTAMP as last_updated
    
FROM riders r
JOIN countries c ON r.country_id = c.country_id
JOIN continents cont ON c.continent_id = cont.continent_id
WHERE r.total_races > 0; -- Only include riders with actual race data

CREATE UNIQUE INDEX idx_mv_rider_performance_rider_id ON mv_rider_performance_summary(rider_id);
CREATE INDEX idx_mv_rider_performance_country ON mv_rider_performance_summary(country_name);
CREATE INDEX idx_mv_rider_performance_wins ON mv_rider_performance_summary(total_wins DESC);

-- =============================================================================
-- CIRCUIT ANALYSIS VIEWS
-- =============================================================================

-- Circuit performance and hosting analysis
CREATE MATERIALIZED VIEW mv_circuit_analysis AS
SELECT 
    circ.circuit_id,
    circ.circuit_name,
    circ.circuit_name_clean,
    c.country_name,
    c.country_code,
    cont.continent_name,
    circ.is_active,
    
    -- Event hosting statistics
    COUNT(DISTINCT re.event_id) as total_events_hosted,
    COUNT(DISTINCT s.year) as seasons_hosted,
    MIN(s.year) as first_year_hosted,
    MAX(s.year) as last_year_hosted,
    MAX(s.year) - MIN(s.year) + 1 as hosting_span_years,
    
    -- Winner diversity
    COUNT(DISTINCT rr.rider_id) as unique_winners,
    COUNT(DISTINCT rr.constructor_id) as unique_winning_constructors,
    COUNT(DISTINCT co.country_id) as unique_winning_countries,
    
    -- Most successful rider at this circuit
    (SELECT rider_name_clean FROM riders 
     WHERE rider_id = (
         SELECT rider_id FROM race_results rr2
         JOIN race_events re2 ON rr2.event_id = re2.event_id
         WHERE re2.circuit_id = circ.circuit_id AND rr2.is_winner = true
         GROUP BY rider_id
         ORDER BY COUNT(*) DESC
         LIMIT 1
     )
    ) as most_successful_rider,
    
    (SELECT COUNT(*) FROM race_results rr2
     JOIN race_events re2 ON rr2.event_id = re2.event_id
     WHERE re2.circuit_id = circ.circuit_id AND rr2.is_winner = true
     GROUP BY rider_id
     ORDER BY COUNT(*) DESC
     LIMIT 1
    ) as most_wins_by_single_rider,
    
    -- Home advantage analysis
    COUNT(CASE WHEN co.country_id = c.country_id AND rr.is_winner = true THEN 1 END) as home_wins,
    COUNT(CASE WHEN rr.is_winner = true THEN 1 END) as total_wins,
    CASE 
        WHEN COUNT(CASE WHEN rr.is_winner = true THEN 1 END) > 0
        THEN ROUND(
            (COUNT(CASE WHEN co.country_id = c.country_id AND rr.is_winner = true THEN 1 END)::NUMERIC / 
             COUNT(CASE WHEN rr.is_winner = true THEN 1 END)) * 100, 2
        )
        ELSE 0 
    END as home_win_percentage,
    
    CURRENT_TIMESTAMP as last_updated
    
FROM circuits circ
JOIN countries c ON circ.country_id = c.country_id
JOIN continents cont ON c.continent_id = cont.continent_id
LEFT JOIN race_events re ON circ.circuit_id = re.circuit_id
LEFT JOIN seasons s ON re.season_id = s.season_id
LEFT JOIN race_results rr ON re.event_id = rr.event_id AND rr.is_winner = true
LEFT JOIN riders r ON rr.rider_id = r.rider_id
LEFT JOIN countries co ON r.country_id = co.country_id
GROUP BY circ.circuit_id, circ.circuit_name, circ.circuit_name_clean, 
         c.country_name, c.country_code, cont.continent_name, circ.is_active;

CREATE UNIQUE INDEX idx_mv_circuit_analysis_circuit_id ON mv_circuit_analysis(circuit_id);
CREATE INDEX idx_mv_circuit_analysis_country ON mv_circuit_analysis(country_name);
CREATE INDEX idx_mv_circuit_analysis_events ON mv_circuit_analysis(total_events_hosted DESC);

-- =============================================================================
-- CONSTRUCTOR DOMINANCE VIEWS
-- =============================================================================

-- Constructor performance across all classes and seasons
CREATE MATERIALIZED VIEW mv_constructor_dominance AS
SELECT 
    con.constructor_id,
    con.constructor_name,
    con.constructor_name_clean,
    c.country_name as constructor_country,
    con.is_active,
    
    -- Championship statistics
    COUNT(DISTINCT cc.championship_id) as total_championships,
    COUNT(DISTINCT cc.class_id) as classes_won,
    COUNT(DISTINCT cc.season_id) as championship_seasons,
    MIN(s.year) as first_championship_year,
    MAX(s.year) as last_championship_year,
    
    -- Race statistics
    COUNT(CASE WHEN rr.is_winner = true THEN 1 END) as total_race_wins,
    COUNT(CASE WHEN rr.is_podium = true THEN 1 END) as total_podiums,
    COUNT(CASE WHEN rr.is_fastest_lap = true THEN 1 END) as total_fastest_laps,
    COUNT(DISTINCT rr.rider_id) as unique_riders,
    
    -- Performance metrics
    CASE 
        WHEN COUNT(rr.result_id) > 0
        THEN ROUND((COUNT(CASE WHEN rr.is_winner = true THEN 1 END)::NUMERIC / COUNT(rr.result_id)) * 100, 2)
        ELSE 0 
    END as win_percentage,
    
    CASE 
        WHEN COUNT(rr.result_id) > 0
        THEN ROUND((COUNT(CASE WHEN rr.is_podium = true THEN 1 END)::NUMERIC / COUNT(rr.result_id)) * 100, 2)
        ELSE 0 
    END as podium_percentage,
    
    -- Dominance periods
    MAX(s.year) - MIN(s.year) + 1 as active_span_years,
    
    -- Rankings
    RANK() OVER (ORDER BY COUNT(DISTINCT cc.championship_id) DESC) as championship_rank,
    RANK() OVER (ORDER BY COUNT(CASE WHEN rr.is_winner = true THEN 1 END) DESC) as wins_rank,
    
    CURRENT_TIMESTAMP as last_updated
    
FROM constructors con
JOIN countries c ON con.country_id = c.country_id
LEFT JOIN constructor_championships cc ON con.constructor_id = cc.constructor_id
LEFT JOIN seasons s ON cc.season_id = s.season_id
LEFT JOIN race_results rr ON con.constructor_id = rr.constructor_id
GROUP BY con.constructor_id, con.constructor_name, con.constructor_name_clean, 
         c.country_name, con.is_active;

CREATE UNIQUE INDEX idx_mv_constructor_dominance_constructor_id ON mv_constructor_dominance(constructor_id);
CREATE INDEX idx_mv_constructor_dominance_championships ON mv_constructor_dominance(total_championships DESC);
CREATE INDEX idx_mv_constructor_dominance_wins ON mv_constructor_dominance(total_race_wins DESC);

-- =============================================================================
-- SEASONAL ANALYSIS VIEWS
-- =============================================================================

-- Season-by-season performance summary
CREATE MATERIALIZED VIEW mv_seasonal_summary AS
SELECT 
    s.season_id,
    s.year,
    e.era_name,
    
    -- Event statistics
    COUNT(DISTINCT re.event_id) as total_events,
    COUNT(DISTINCT re.circuit_id) as unique_circuits,
    COUNT(DISTINCT re.class_id) as classes_active,
    
    -- Participation statistics
    COUNT(DISTINCT rr.rider_id) as unique_riders,
    COUNT(DISTINCT rr.constructor_id) as unique_constructors,
    COUNT(DISTINCT co.country_id) as countries_represented,
    
    -- Competition metrics
    COUNT(DISTINCT rr.rider_id) FILTER (WHERE rr.is_winner = true) as unique_race_winners,
    COUNT(DISTINCT rr.rider_id) FILTER (WHERE rr.is_podium = true) as unique_podium_finishers,
    
    -- Competitive balance (Herfindahl-Hirschman Index approximation)
    1.0 - (SUM(POWER(rider_wins.wins::NUMERIC / total_wins.total, 2))) as competitive_balance_index,
    
    CURRENT_TIMESTAMP as last_updated
    
FROM seasons s
JOIN eras e ON s.era_id = e.era_id
LEFT JOIN race_events re ON s.season_id = re.season_id
LEFT JOIN race_results rr ON re.event_id = rr.event_id
LEFT JOIN riders r ON rr.rider_id = r.rider_id
LEFT JOIN countries co ON r.country_id = co.country_id
LEFT JOIN (
    -- Subquery for rider wins per season
    SELECT 
        s2.season_id,
        rr2.rider_id,
        COUNT(*) as wins
    FROM seasons s2
    JOIN race_events re2 ON s2.season_id = re2.season_id
    JOIN race_results rr2 ON re2.event_id = rr2.event_id
    WHERE rr2.is_winner = true
    GROUP BY s2.season_id, rr2.rider_id
) rider_wins ON s.season_id = rider_wins.season_id
LEFT JOIN (
    -- Subquery for total wins per season
    SELECT 
        s3.season_id,
        COUNT(*) as total
    FROM seasons s3
    JOIN race_events re3 ON s3.season_id = re3.season_id
    JOIN race_results rr3 ON re3.event_id = rr3.event_id
    WHERE rr3.is_winner = true
    GROUP BY s3.season_id
) total_wins ON s.season_id = total_wins.season_id
GROUP BY s.season_id, s.year, e.era_name
ORDER BY s.year DESC;

CREATE UNIQUE INDEX idx_mv_seasonal_summary_season_id ON mv_seasonal_summary(season_id);
CREATE INDEX idx_mv_seasonal_summary_year ON mv_seasonal_summary(year DESC);

-- =============================================================================
-- GEOGRAPHIC ANALYSIS VIEWS
-- =============================================================================

-- Country representation and performance
CREATE MATERIALIZED VIEW mv_country_performance AS
SELECT 
    c.country_id,
    c.country_code,
    c.country_name,
    cont.continent_name,
    
    -- Rider representation
    COUNT(DISTINCT r.rider_id) as total_riders,
    COUNT(DISTINCT r.rider_id) FILTER (WHERE r.is_active = true) as active_riders,
    
    -- Performance statistics
    SUM(r.total_wins) as total_wins,
    SUM(r.total_podiums) as total_podiums,
    SUM(r.total_championships) as total_championships,
    COUNT(DISTINCT re.circuit_id) as home_circuits,
    
    -- Constructor presence
    COUNT(DISTINCT con.constructor_id) as total_constructors,
    COUNT(DISTINCT con.constructor_id) FILTER (WHERE con.is_active = true) as active_constructors,
    
    -- Success rates
    CASE 
        WHEN COUNT(DISTINCT r.rider_id) > 0
        THEN ROUND(AVG(r.win_percentage), 2)
        ELSE 0 
    END as avg_rider_win_rate,
    
    CASE 
        WHEN COUNT(DISTINCT r.rider_id) > 0
        THEN ROUND(AVG(r.podium_percentage), 2)
        ELSE 0 
    END as avg_rider_podium_rate,
    
    -- Podium lockouts
    COUNT(DISTINCT pl.lockout_id) as podium_lockouts,
    
    -- Rankings
    RANK() OVER (ORDER BY SUM(r.total_wins) DESC) as wins_rank,
    RANK() OVER (ORDER BY COUNT(DISTINCT r.rider_id) DESC) as riders_count_rank,
    
    CURRENT_TIMESTAMP as last_updated
    
FROM countries c
JOIN continents cont ON c.continent_id = cont.continent_id
LEFT JOIN riders r ON c.country_id = r.country_id
LEFT JOIN circuits re ON c.country_id = re.country_id
LEFT JOIN constructors con ON c.country_id = con.country_id
LEFT JOIN podium_lockouts pl ON c.country_id = pl.country_id
GROUP BY c.country_id, c.country_code, c.country_name, cont.continent_name;

CREATE UNIQUE INDEX idx_mv_country_performance_country_id ON mv_country_performance(country_id);
CREATE INDEX idx_mv_country_performance_continent ON mv_country_performance(continent_name);
CREATE INDEX idx_mv_country_performance_wins ON mv_country_performance(total_wins DESC);

-- =============================================================================
-- BUSINESS INTELLIGENCE VIEWS
-- =============================================================================

-- Executive dashboard summary
CREATE MATERIALIZED VIEW mv_executive_dashboard AS
SELECT 
    -- Overall statistics
    (SELECT COUNT(*) FROM riders WHERE total_races > 0) as total_active_riders,
    (SELECT COUNT(*) FROM circuits WHERE is_active = true) as total_active_circuits,
    (SELECT COUNT(*) FROM constructors WHERE is_active = true) as total_active_constructors,
    (SELECT COUNT(DISTINCT country_id) FROM riders) as countries_represented,
    
    -- Current season data (latest year)
    (SELECT MAX(year) FROM seasons) as current_season,
    (SELECT COUNT(*) FROM race_events re JOIN seasons s ON re.season_id = s.season_id 
     WHERE s.year = (SELECT MAX(year) FROM seasons)) as current_season_events,
    
    -- Historical totals
    (SELECT COUNT(*) FROM race_results) as total_race_results,
    (SELECT COUNT(*) FROM race_results WHERE is_winner = true) as total_race_wins,
    (SELECT COUNT(*) FROM race_results WHERE is_podium = true) as total_podiums,
    
    -- Performance leaders
    (SELECT rider_name_clean FROM riders ORDER BY total_wins DESC LIMIT 1) as most_wins_rider,
    (SELECT total_wins FROM riders ORDER BY total_wins DESC LIMIT 1) as most_wins_count,
    
    (SELECT constructor_name_clean FROM mv_constructor_dominance ORDER BY total_championships DESC LIMIT 1) as most_successful_constructor,
    (SELECT total_championships FROM mv_constructor_dominance ORDER BY total_championships DESC LIMIT 1) as most_championships_count,
    
    -- Geographic leaders
    (SELECT country_name FROM mv_country_performance ORDER BY total_wins DESC LIMIT 1) as most_successful_country,
    (SELECT total_wins FROM mv_country_performance ORDER BY total_wins DESC LIMIT 1) as most_country_wins,
    
    CURRENT_TIMESTAMP as last_updated;

-- =============================================================================
-- VIEW REFRESH FUNCTIONS
-- =============================================================================

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_rider_performance_summary;
    REFRESH MATERIALIZED VIEW mv_circuit_analysis;
    REFRESH MATERIALIZED VIEW mv_constructor_dominance;
    REFRESH MATERIALIZED VIEW mv_seasonal_summary;
    REFRESH MATERIALIZED VIEW mv_country_performance;
    REFRESH MATERIALIZED VIEW mv_executive_dashboard;
    
    INSERT INTO schema_version (version, description) VALUES
    ('VIEWS_' || to_char(CURRENT_TIMESTAMP, 'YYYY-MM-DD-HH24-MI-SS'), 'Materialized views refreshed');
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- VIEW DOCUMENTATION
-- =============================================================================

COMMENT ON MATERIALIZED VIEW mv_rider_performance_summary IS 'Comprehensive rider statistics with rankings and performance metrics';
COMMENT ON MATERIALIZED VIEW mv_circuit_analysis IS 'Circuit hosting statistics and winner diversity analysis';
COMMENT ON MATERIALIZED VIEW mv_constructor_dominance IS 'Constructor championship and race performance metrics';
COMMENT ON MATERIALIZED VIEW mv_seasonal_summary IS 'Season-by-season participation and competition statistics';
COMMENT ON MATERIALIZED VIEW mv_country_performance IS 'Country-level rider and constructor representation and success';
COMMENT ON MATERIALIZED VIEW mv_executive_dashboard IS 'High-level KPIs for executive reporting';

-- =============================================================================
-- END OF MATERIALIZED VIEWS
-- =============================================================================