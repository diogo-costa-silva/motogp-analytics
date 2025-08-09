#!/usr/bin/env python3
"""
MotoGP Data ETL Pipeline
========================
Purpose: Import and transform CSV data into PostgreSQL database
Author: Claude Code Assistant
Dependencies: pandas, psycopg2, python-dotenv
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/etl_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MotoGPETL:
    """Main ETL class for MotoGP data processing"""
    
    def __init__(self, data_path: Path, db_config: Dict[str, str]):
        self.data_path = data_path
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        
        # Data cleaning mappings
        self.country_mappings = {
            'ES': 'ESP', 'IT': 'ITA', 'GB': 'GBR', 'FR': 'FRA', 'DE': 'DEU',
            'AU': 'AUS', 'US': 'USA', 'JP': 'JPN', 'NL': 'NLD', 'PT': 'PRT',
            'CZ': 'CZE', 'BE': 'BEL', 'TH': 'THA', 'MY': 'MYS', 'IN': 'IND'
        }
        
        self.continent_mapping = {
            'ESP': 'EU', 'ITA': 'EU', 'GBR': 'EU', 'FRA': 'EU', 'DEU': 'EU',
            'NLD': 'EU', 'PRT': 'EU', 'CZE': 'EU', 'BEL': 'EU',
            'AUS': 'OC', 'USA': 'AM', 'JPN': 'AS', 'THA': 'AS', 'MYS': 'AS', 'IND': 'AS'
        }
        
    def connect_database(self) -> bool:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("✅ Database connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
            
    def disconnect_database(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("🔌 Database connection closed")
        
    def clean_name(self, name: str) -> str:
        """Standardize rider/constructor/circuit names"""
        if pd.isna(name):
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', str(name).strip())
        
        # Handle special characters and accents
        replacements = {
            'ñ': 'n', 'ç': 'c', 'ü': 'u', 'ö': 'o', 'ä': 'a',
            'é': 'e', 'è': 'e', 'à': 'a', 'ò': 'o', 'ì': 'i'
        }
        
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new).replace(old.upper(), new.upper())
            
        return cleaned
        
    def normalize_country_code(self, country_code: str) -> str:
        """Convert country codes to ISO 3166-1 alpha-3"""
        if pd.isna(country_code):
            return "UNK"
        
        code = str(country_code).upper().strip()
        return self.country_mappings.get(code, code)
        
    def get_or_create_country(self, country_code: str, country_name: str = None) -> int:
        """Get existing country_id or create new country entry"""
        norm_code = self.normalize_country_code(country_code)
        
        # Try to get existing country
        self.cursor.execute("SELECT country_id FROM countries WHERE country_code = %s", (norm_code,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
            
        # Create new country
        if not country_name:
            # Generate country name from code
            country_name_map = {
                'ESP': 'Spain', 'ITA': 'Italy', 'GBR': 'Great Britain', 'FRA': 'France',
                'DEU': 'Germany', 'AUS': 'Australia', 'USA': 'United States', 'JPN': 'Japan',
                'NLD': 'Netherlands', 'PRT': 'Portugal', 'CZE': 'Czech Republic',
                'BEL': 'Belgium', 'THA': 'Thailand', 'MYS': 'Malaysia', 'IND': 'India'
            }
            country_name = country_name_map.get(norm_code, norm_code)
            
        # Get continent_id
        continent_code = self.continent_mapping.get(norm_code, 'EU')  # Default to Europe
        self.cursor.execute("SELECT continent_id FROM continents WHERE continent_code = %s", (continent_code,))
        continent_id = self.cursor.fetchone()[0]
        
        self.cursor.execute(
            "INSERT INTO countries (country_code, country_name, continent_id) VALUES (%s, %s, %s) RETURNING country_id",
            (norm_code, country_name, continent_id)
        )
        country_id = self.cursor.fetchone()[0]
        logger.info(f"Created new country: {country_name} ({norm_code})")
        return country_id
        
    def get_or_create_class(self, class_name: str) -> int:
        """Get existing class_id or create new racing class"""
        if pd.isna(class_name):
            class_name = "Unknown"
            
        clean_class = str(class_name).strip()
        
        # Try to get existing class
        self.cursor.execute("SELECT class_id FROM racing_classes WHERE class_name = %s", (clean_class,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
            
        # Determine class category
        category_map = {
            'MotoGP™': 'Premier', '500cc': 'Premier',
            'Moto2™': 'Intermediate', '250cc': 'Intermediate', '350cc': 'Intermediate',
            'Moto3™': 'Lightweight', '125cc': 'Lightweight',
            'MotoE™': 'Electric'
        }
        category = category_map.get(clean_class, 'Other')
        
        # Determine if active (current classes)
        active_classes = ['MotoGP™', 'Moto2™', 'Moto3™', 'MotoE™']
        is_active = clean_class in active_classes
        
        self.cursor.execute(
            "INSERT INTO racing_classes (class_name, class_category, is_active) VALUES (%s, %s, %s) RETURNING class_id",
            (clean_class, category, is_active)
        )
        class_id = self.cursor.fetchone()[0]
        logger.info(f"Created new racing class: {clean_class} ({category})")
        return class_id
        
    def get_or_create_season(self, year: int) -> int:
        """Get existing season_id or create new season"""
        # Try to get existing season
        self.cursor.execute("SELECT season_id FROM seasons WHERE year = %s", (year,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
            
        # Determine era
        if year <= 1948:
            era_name = 'Pre-World Championship'
        elif year <= 1969:
            era_name = 'Early Championship Era'
        elif year <= 1999:
            era_name = 'Two-stroke Golden Age'
        else:
            era_name = 'Four-stroke Modern Era'
            
        self.cursor.execute("SELECT era_id FROM eras WHERE era_name = %s", (era_name,))
        era_id = self.cursor.fetchone()[0]
        
        self.cursor.execute(
            "INSERT INTO seasons (year, era_id) VALUES (%s, %s) RETURNING season_id",
            (year, era_id)
        )
        season_id = self.cursor.fetchone()[0]
        logger.info(f"Created new season: {year} ({era_name})")
        return season_id
        
    def import_race_winners(self) -> bool:
        """Import race winners data"""
        logger.info("📥 Starting race winners import...")
        
        try:
            # Load CSV
            df = pd.read_csv(self.data_path / "grand_prix_race_winners.csv")
            logger.info(f"Loaded {len(df)} race winner records")
            
            # Clean data
            df['circuit_clean'] = df['Circuit'].apply(self.clean_name)
            df['rider_clean'] = df['Rider'].apply(self.clean_name)
            df['constructor_clean'] = df['Constructor'].apply(self.clean_name)
            df['country_norm'] = df['Country'].apply(self.normalize_country_code)
            
            # Process each record
            for idx, row in df.iterrows():
                try:
                    # Get/create foreign key references
                    country_id = self.get_or_create_country(row['country_norm'])
                    class_id = self.get_or_create_class(row['Class'])
                    season_id = self.get_or_create_season(row['Season'])
                    
                    # Get/create circuit
                    circuit_name_clean = row['circuit_clean']
                    self.cursor.execute("SELECT circuit_id FROM circuits WHERE circuit_name_clean = %s", (circuit_name_clean,))
                    circuit_result = self.cursor.fetchone()
                    
                    if not circuit_result:
                        self.cursor.execute(
                            "INSERT INTO circuits (circuit_name, circuit_name_clean, country_id) VALUES (%s, %s, %s) RETURNING circuit_id",
                            (row['Circuit'], circuit_name_clean, country_id)
                        )
                        circuit_id = self.cursor.fetchone()[0]
                    else:
                        circuit_id = circuit_result[0]
                    
                    # Get/create constructor
                    constructor_name_clean = row['constructor_clean']
                    self.cursor.execute("SELECT constructor_id FROM constructors WHERE constructor_name_clean = %s", (constructor_name_clean,))
                    constructor_result = self.cursor.fetchone()
                    
                    if not constructor_result:
                        self.cursor.execute(
                            "INSERT INTO constructors (constructor_name, constructor_name_clean, country_id) VALUES (%s, %s, %s) RETURNING constructor_id",
                            (row['Constructor'], constructor_name_clean, country_id)
                        )
                        constructor_id = self.cursor.fetchone()[0]
                    else:
                        constructor_id = constructor_result[0]
                    
                    # Get/create rider
                    rider_name_clean = row['rider_clean']
                    self.cursor.execute("SELECT rider_id FROM riders WHERE rider_name_clean = %s", (rider_name_clean,))
                    rider_result = self.cursor.fetchone()
                    
                    if not rider_result:
                        self.cursor.execute(
                            "INSERT INTO riders (rider_name, rider_name_clean, country_id, career_start_year) VALUES (%s, %s, %s, %s) RETURNING rider_id",
                            (row['Rider'], rider_name_clean, country_id, row['Season'])
                        )
                        rider_id = self.cursor.fetchone()[0]
                    else:
                        rider_id = rider_result[0]
                    
                    # Create/get race event
                    self.cursor.execute(
                        "SELECT event_id FROM race_events WHERE season_id = %s AND circuit_id = %s AND class_id = %s",
                        (season_id, circuit_id, class_id)
                    )
                    event_result = self.cursor.fetchone()
                    
                    if not event_result:
                        self.cursor.execute(
                            "INSERT INTO race_events (season_id, circuit_id, class_id, round_number, event_date) VALUES (%s, %s, %s, %s, %s) RETURNING event_id",
                            (season_id, circuit_id, class_id, 1, f"{row['Season']}-01-01")
                        )
                        event_id = self.cursor.fetchone()[0]
                    else:
                        event_id = event_result[0]
                    
                    # Insert race result (winner)
                    self.cursor.execute(
                        """INSERT INTO race_results 
                           (event_id, rider_id, constructor_id, finish_position, is_winner, is_podium, is_points, points_awarded)
                           VALUES (%s, %s, %s, 1, true, true, true, 25)
                           ON CONFLICT (event_id, rider_id) DO NOTHING""",
                        (event_id, rider_id, constructor_id)
                    )
                    
                    if (idx + 1) % 100 == 0:
                        self.conn.commit()
                        logger.info(f"Processed {idx + 1}/{len(df)} race winner records")
                        
                except Exception as e:
                    logger.error(f"Error processing race winner row {idx}: {e}")
                    continue
            
            self.conn.commit()
            logger.info("✅ Race winners import completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Race winners import failed: {e}")
            self.conn.rollback()
            return False
            
    def import_riders_info(self) -> bool:
        """Import riders information data"""
        logger.info("📥 Starting riders info import...")
        
        try:
            # Load CSV
            df = pd.read_csv(self.data_path / "riders_info.csv")
            logger.info(f"Loaded {len(df)} rider info records")
            
            # Clean column names
            df.columns = [col.strip() for col in df.columns]
            
            # Process each rider
            for idx, row in df.iterrows():
                try:
                    rider_name = str(row['Riders All Time in All Classes']).strip()
                    rider_name_clean = self.clean_name(rider_name)
                    
                    # Skip header row or invalid data
                    if 'Riders All Time' in rider_name or pd.isna(rider_name) or rider_name == '':
                        continue
                    
                    # Extract statistics (handle NaN values)
                    victories = int(row.get('Victories', 0)) if pd.notna(row.get('Victories')) else 0
                    second_places = int(row.get('2nd places', 0)) if pd.notna(row.get('2nd places')) else 0
                    third_places = int(row.get('3rd places', 0)) if pd.notna(row.get('3rd places')) else 0
                    pole_positions = int(row.get('Pole positions from \'74 to 2022', 0)) if pd.notna(row.get('Pole positions from \'74 to 2022')) else 0
                    fastest_laps = int(row.get('Race fastest lap to 2022', 0)) if pd.notna(row.get('Race fastest lap to 2022')) else 0
                    championships = int(row.get('World Championships', 0)) if pd.notna(row.get('World Championships')) else 0
                    
                    # Calculate totals
                    total_podiums = victories + second_places + third_places
                    
                    # Update or insert rider with statistics
                    self.cursor.execute(
                        """INSERT INTO riders 
                           (rider_name, rider_name_clean, total_wins, total_podiums, total_poles, 
                            total_fastest_laps, total_championships, country_id)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, 
                            (SELECT country_id FROM countries WHERE country_code = 'UNK' LIMIT 1))
                           ON CONFLICT (rider_name_clean) DO UPDATE SET
                           total_wins = EXCLUDED.total_wins,
                           total_podiums = EXCLUDED.total_podiums,
                           total_poles = EXCLUDED.total_poles,
                           total_fastest_laps = EXCLUDED.total_fastest_laps,
                           total_championships = EXCLUDED.total_championships,
                           updated_at = CURRENT_TIMESTAMP""",
                        (rider_name, rider_name_clean, victories, total_podiums, 
                         pole_positions, fastest_laps, championships)
                    )
                    
                    if (idx + 1) % 50 == 0:
                        self.conn.commit()
                        logger.info(f"Processed {idx + 1}/{len(df)} rider info records")
                        
                except Exception as e:
                    logger.error(f"Error processing rider info row {idx}: {e}")
                    continue
                    
            self.conn.commit()
            logger.info("✅ Riders info import completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Riders info import failed: {e}")
            self.conn.rollback()
            return False
    
    def run_full_import(self) -> bool:
        """Run complete ETL pipeline"""
        logger.info("🚀 Starting full MotoGP data import...")
        
        if not self.connect_database():
            return False
            
        try:
            # Import in logical order
            success = True
            success &= self.import_race_winners()
            success &= self.import_riders_info()
            # Add other import methods here
            
            if success:
                logger.info("🎉 Full import completed successfully!")
                
                # Refresh materialized views
                logger.info("🔄 Refreshing materialized views...")
                self.cursor.execute("SELECT refresh_all_materialized_views();")
                self.conn.commit()
                logger.info("✅ Materialized views refreshed")
                
            return success
            
        except Exception as e:
            logger.error(f"❌ Full import failed: {e}")
            return False
            
        finally:
            self.disconnect_database()

def main():
    """Main execution function"""
    
    # Database configuration from environment variables
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'motogp_analytics'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    # Data path
    data_path = Path("../../data/raw")
    
    # Create ETL instance and run
    etl = MotoGPETL(data_path, db_config)
    success = etl.run_full_import()
    
    if success:
        print("✅ MotoGP data import completed successfully!")
    else:
        print("❌ MotoGP data import failed. Check logs for details.")
        exit(1)

if __name__ == "__main__":
    main()