-- =============================================================================
-- MotoGP Analytics Database Schema
-- =============================================================================
-- Purpose: Relational database optimized for complex queries, BI tools, and web apps
-- Author: Claude Code Assistant
-- Target: PostgreSQL 13+
-- =============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- LOOKUP TABLES (Reference Data)
-- =============================================================================

-- Continents lookup table
CREATE TABLE continents (
    continent_id SERIAL PRIMARY KEY,
    continent_code VARCHAR(2) UNIQUE NOT NULL, -- EU, AS, AM, OC, AF
    continent_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Countries dimension table
CREATE TABLE countries (
    country_id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) UNIQUE NOT NULL, -- ISO 3166-1 alpha-3
    country_name VARCHAR(100) NOT NULL,
    continent_id INTEGER REFERENCES continents(continent_id),
    region VARCHAR(50), -- Western Europe, Southeast Asia, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Eras lookup table for historical context
CREATE TABLE eras (
    era_id SERIAL PRIMARY KEY,
    era_name VARCHAR(50) UNIQUE NOT NULL, -- "Two-stroke era", "Four-stroke era", etc.
    start_year INTEGER NOT NULL,
    end_year INTEGER, -- NULL for current era
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- CORE DIMENSION TABLES
-- =============================================================================

-- Racing classes/categories
CREATE TABLE racing_classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(20) UNIQUE NOT NULL, -- "MotoGP™", "Moto2™", "Moto3™", etc.
    class_category VARCHAR(20) NOT NULL,     -- "Premier", "Intermediate", "Lightweight"
    engine_capacity VARCHAR(10),             -- "1000cc", "765cc", "250cc"
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seasons dimension
CREATE TABLE seasons (
    season_id SERIAL PRIMARY KEY,
    year INTEGER UNIQUE NOT NULL,
    era_id INTEGER REFERENCES eras(era_id),
    total_rounds INTEGER,
    season_start_date DATE,
    season_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Circuits dimension
CREATE TABLE circuits (
    circuit_id SERIAL PRIMARY KEY,
    circuit_name VARCHAR(100) NOT NULL,
    circuit_name_clean VARCHAR(100) NOT NULL, -- Standardized name
    country_id INTEGER REFERENCES countries(country_id),
    city VARCHAR(100),
    circuit_length_km NUMERIC(5,3),
    first_motogp_year INTEGER,
    last_motogp_year INTEGER, -- NULL if still active
    is_active BOOLEAN DEFAULT true,
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Constructors/Manufacturers dimension
CREATE TABLE constructors (
    constructor_id SERIAL PRIMARY KEY,
    constructor_name VARCHAR(50) NOT NULL,
    constructor_name_clean VARCHAR(50) NOT NULL,
    country_id INTEGER REFERENCES countries(country_id),
    founded_year INTEGER,
    first_motogp_year INTEGER,
    last_motogp_year INTEGER, -- NULL if still active
    is_active BOOLEAN DEFAULT true,
    headquarters_city VARCHAR(100),
    website_url VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Riders dimension
CREATE TABLE riders (
    rider_id SERIAL PRIMARY KEY,
    rider_name VARCHAR(100) NOT NULL,
    rider_name_clean VARCHAR(100) NOT NULL, -- Standardized name
    country_id INTEGER REFERENCES countries(country_id),
    birth_date DATE,
    birth_city VARCHAR(100),
    career_start_year INTEGER,
    career_end_year INTEGER, -- NULL if still active
    is_active BOOLEAN DEFAULT true,
    
    -- Career summary statistics (denormalized for performance)
    total_races INTEGER DEFAULT 0,
    total_wins INTEGER DEFAULT 0,
    total_podiums INTEGER DEFAULT 0,
    total_poles INTEGER DEFAULT 0,
    total_fastest_laps INTEGER DEFAULT 0,
    total_championships INTEGER DEFAULT 0,
    
    -- Calculated performance metrics
    win_percentage NUMERIC(5,2) DEFAULT 0.00,
    podium_percentage NUMERIC(5,2) DEFAULT 0.00,
    avg_finish_position NUMERIC(4,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- FACT TABLES (Transactional Data)
-- =============================================================================

-- Race events (races/rounds in a season)
CREATE TABLE race_events (
    event_id SERIAL PRIMARY KEY,
    season_id INTEGER REFERENCES seasons(season_id),
    circuit_id INTEGER REFERENCES circuits(circuit_id),
    class_id INTEGER REFERENCES racing_classes(class_id),
    round_number INTEGER NOT NULL,
    event_name VARCHAR(100), -- "Spanish Grand Prix", "Italian Grand Prix"
    event_date DATE NOT NULL,
    
    -- Weather and conditions (for future enhancement)
    weather_condition VARCHAR(50),
    track_temperature_celsius INTEGER,
    air_temperature_celsius INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(season_id, circuit_id, class_id, round_number)
);

-- Race results (individual rider results)
CREATE TABLE race_results (
    result_id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES race_events(event_id),
    rider_id INTEGER REFERENCES riders(rider_id),
    constructor_id INTEGER REFERENCES constructors(constructor_id),
    
    -- Race result data
    grid_position INTEGER, -- Starting position
    finish_position INTEGER, -- Final position (NULL for DNF)
    points_awarded INTEGER DEFAULT 0,
    
    -- Performance flags
    is_winner BOOLEAN DEFAULT false,
    is_podium BOOLEAN DEFAULT false, -- Positions 1, 2, 3
    is_points BOOLEAN DEFAULT false, -- Points-scoring position
    is_pole_position BOOLEAN DEFAULT false,
    is_fastest_lap BOOLEAN DEFAULT false,
    is_dnf BOOLEAN DEFAULT false, -- Did not finish
    is_dns BOOLEAN DEFAULT false, -- Did not start
    
    -- Time data (for future enhancement)
    race_time_milliseconds BIGINT,
    gap_to_leader_milliseconds BIGINT,
    fastest_lap_time_milliseconds BIGINT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(event_id, rider_id)
);

-- Constructor championships (annual constructor titles)
CREATE TABLE constructor_championships (
    championship_id SERIAL PRIMARY KEY,
    season_id INTEGER REFERENCES seasons(season_id),
    class_id INTEGER REFERENCES racing_classes(class_id),
    constructor_id INTEGER REFERENCES constructors(constructor_id),
    points_total INTEGER DEFAULT 0,
    wins_total INTEGER DEFAULT 0,
    podiums_total INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(season_id, class_id, constructor_id)
);

-- Podium lockouts (same nation podium dominance)
CREATE TABLE podium_lockouts (
    lockout_id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES race_events(event_id),
    country_id INTEGER REFERENCES countries(country_id), -- Dominant nation
    
    -- Podium rider details
    first_place_rider_id INTEGER REFERENCES riders(rider_id),
    second_place_rider_id INTEGER REFERENCES riders(rider_id),
    third_place_rider_id INTEGER REFERENCES riders(rider_id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Core lookup indexes
CREATE INDEX idx_countries_continent ON countries(continent_id);
CREATE INDEX idx_countries_code ON countries(country_code);

-- Dimension table indexes
CREATE INDEX idx_circuits_country ON circuits(country_id);
CREATE INDEX idx_circuits_active ON circuits(is_active);
CREATE INDEX idx_circuits_name_clean ON circuits(circuit_name_clean);

CREATE INDEX idx_constructors_country ON constructors(country_id);
CREATE INDEX idx_constructors_active ON constructors(is_active);
CREATE INDEX idx_constructors_name_clean ON constructors(constructor_name_clean);

CREATE INDEX idx_riders_country ON riders(country_id);
CREATE INDEX idx_riders_active ON riders(is_active);
CREATE INDEX idx_riders_name_clean ON riders(rider_name_clean);
CREATE INDEX idx_riders_career_years ON riders(career_start_year, career_end_year);

CREATE INDEX idx_seasons_year ON seasons(year);
CREATE INDEX idx_seasons_era ON seasons(era_id);

-- Fact table indexes for complex queries
CREATE INDEX idx_race_events_season_circuit ON race_events(season_id, circuit_id);
CREATE INDEX idx_race_events_class ON race_events(class_id);
CREATE INDEX idx_race_events_date ON race_events(event_date);

CREATE INDEX idx_race_results_event_rider ON race_results(event_id, rider_id);
CREATE INDEX idx_race_results_rider_performance ON race_results(rider_id, is_winner, is_podium);
CREATE INDEX idx_race_results_constructor ON race_results(constructor_id);
CREATE INDEX idx_race_results_winners ON race_results(is_winner) WHERE is_winner = true;
CREATE INDEX idx_race_results_podiums ON race_results(is_podium) WHERE is_podium = true;

CREATE INDEX idx_constructor_championships_season_class ON constructor_championships(season_id, class_id);
CREATE INDEX idx_podium_lockouts_country_season ON podium_lockouts(country_id, event_id);

-- =============================================================================
-- CONSTRAINTS AND BUSINESS RULES
-- =============================================================================

-- Ensure finish positions are valid
ALTER TABLE race_results ADD CONSTRAINT check_finish_position 
    CHECK (finish_position IS NULL OR finish_position > 0);

-- Ensure grid positions are valid
ALTER TABLE race_results ADD CONSTRAINT check_grid_position 
    CHECK (grid_position IS NULL OR grid_position > 0);

-- Ensure points are non-negative
ALTER TABLE race_results ADD CONSTRAINT check_points 
    CHECK (points_awarded >= 0);

-- Winner must be in position 1
ALTER TABLE race_results ADD CONSTRAINT check_winner_position 
    CHECK (NOT is_winner OR finish_position = 1);

-- Podium must be in positions 1, 2, or 3
ALTER TABLE race_results ADD CONSTRAINT check_podium_position 
    CHECK (NOT is_podium OR finish_position <= 3);

-- Career years logic
ALTER TABLE riders ADD CONSTRAINT check_career_years 
    CHECK (career_end_year IS NULL OR career_end_year >= career_start_year);

ALTER TABLE constructors ADD CONSTRAINT check_constructor_years 
    CHECK (last_motogp_year IS NULL OR last_motogp_year >= first_motogp_year);

-- Era years logic
ALTER TABLE eras ADD CONSTRAINT check_era_years 
    CHECK (end_year IS NULL OR end_year >= start_year);

-- =============================================================================
-- TRIGGERS FOR DATA INTEGRITY
-- =============================================================================

-- Update rider statistics trigger
CREATE OR REPLACE FUNCTION update_rider_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update rider statistics when race results change
    UPDATE riders SET
        total_races = (
            SELECT COUNT(*) FROM race_results 
            WHERE rider_id = NEW.rider_id AND finish_position IS NOT NULL
        ),
        total_wins = (
            SELECT COUNT(*) FROM race_results 
            WHERE rider_id = NEW.rider_id AND is_winner = true
        ),
        total_podiums = (
            SELECT COUNT(*) FROM race_results 
            WHERE rider_id = NEW.rider_id AND is_podium = true
        ),
        total_poles = (
            SELECT COUNT(*) FROM race_results 
            WHERE rider_id = NEW.rider_id AND is_pole_position = true
        ),
        total_fastest_laps = (
            SELECT COUNT(*) FROM race_results 
            WHERE rider_id = NEW.rider_id AND is_fastest_lap = true
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE rider_id = NEW.rider_id;
    
    -- Calculate percentages
    UPDATE riders SET
        win_percentage = CASE 
            WHEN total_races > 0 THEN ROUND((total_wins::NUMERIC / total_races) * 100, 2)
            ELSE 0 
        END,
        podium_percentage = CASE 
            WHEN total_races > 0 THEN ROUND((total_podiums::NUMERIC / total_races) * 100, 2)
            ELSE 0 
        END,
        avg_finish_position = (
            SELECT ROUND(AVG(finish_position::NUMERIC), 2) 
            FROM race_results 
            WHERE rider_id = NEW.rider_id AND finish_position IS NOT NULL
        )
    WHERE rider_id = NEW.rider_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_rider_stats
    AFTER INSERT OR UPDATE ON race_results
    FOR EACH ROW
    EXECUTE FUNCTION update_rider_stats();

-- =============================================================================
-- INITIAL DATA POPULATION
-- =============================================================================

-- Insert initial reference data
INSERT INTO continents (continent_code, continent_name) VALUES
('EU', 'Europe'),
('AS', 'Asia'),
('AM', 'Americas'),
('OC', 'Oceania'),
('AF', 'Africa');

-- Insert historical eras
INSERT INTO eras (era_name, start_year, end_year, description) VALUES
('Pre-World Championship', 1900, 1948, 'Before official World Championship'),
('Early Championship Era', 1949, 1969, 'Establishment of World Championship'),
('Two-stroke Golden Age', 1970, 1999, 'Dominance of two-stroke engines'),
('Four-stroke Modern Era', 2000, NULL, 'Modern four-stroke MotoGP era');

-- Insert racing classes
INSERT INTO racing_classes (class_name, class_category, engine_capacity, is_active) VALUES
('MotoGP™', 'Premier', '1000cc', true),
('Moto2™', 'Intermediate', '765cc', true),
('Moto3™', 'Lightweight', '250cc', true),
('MotoE™', 'Electric', 'Electric', true),
('500cc', 'Premier', '500cc', false),
('250cc', 'Intermediate', '250cc', false),
('125cc', 'Lightweight', '125cc', false);

-- =============================================================================
-- COMMENTS AND DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE riders IS 'Dimension table containing all MotoGP riders with career statistics';
COMMENT ON TABLE circuits IS 'Dimension table containing all circuits that have hosted MotoGP events';
COMMENT ON TABLE constructors IS 'Dimension table containing motorcycle manufacturers and teams';
COMMENT ON TABLE race_results IS 'Fact table containing individual race results for every rider in every race';
COMMENT ON TABLE race_events IS 'Fact table containing race/event information for each round of each season';

COMMENT ON COLUMN riders.total_wins IS 'Denormalized count of race wins for performance';
COMMENT ON COLUMN riders.win_percentage IS 'Calculated win rate as percentage';
COMMENT ON COLUMN race_results.is_winner IS 'Boolean flag for race winners (finish_position = 1)';
COMMENT ON COLUMN race_results.is_podium IS 'Boolean flag for podium finishers (finish_position <= 3)';

-- =============================================================================
-- SCHEMA VERSION TRACKING
-- =============================================================================

CREATE TABLE schema_version (
    version VARCHAR(10) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES
('1.0.0', 'Initial MotoGP database schema with core tables and indexes');

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================