#!/usr/bin/env python3
"""
MotoGP Database Setup Script
============================
Purpose: Complete database initialization and setup
Author: Claude Code Assistant
Usage: python setup_database.py [--reset] [--sample-data]
"""

import argparse
import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    """Database setup and initialization"""
    
    def __init__(self):
        load_dotenv()
        
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
        self.db_name = os.getenv('DB_NAME', 'motogp_analytics')
        self.schema_path = Path(__file__).parent / 'schema'
        
    def check_postgresql_connection(self) -> bool:
        """Check if PostgreSQL is accessible"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.close()
            logger.info("✅ PostgreSQL connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
            
    def create_database(self) -> bool:
        """Create the MotoGP analytics database"""
        try:
            # Connect to default postgres database
            conn = psycopg2.connect(**self.db_config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
            exists = cursor.fetchone()
            
            if exists:
                logger.info(f"📋 Database '{self.db_name}' already exists")
            else:
                # Create database
                cursor.execute(f"CREATE DATABASE {self.db_name}")
                logger.info(f"✅ Database '{self.db_name}' created successfully")
                
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Database creation failed: {e}")
            return False
            
    def drop_database(self) -> bool:
        """Drop the MotoGP analytics database (for reset)"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Terminate active connections
            cursor.execute(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity 
                WHERE datname = '{self.db_name}' AND pid <> pg_backend_pid()
            """)
            
            # Drop database
            cursor.execute(f"DROP DATABASE IF EXISTS {self.db_name}")
            logger.info(f"🗑️  Database '{self.db_name}' dropped")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Database drop failed: {e}")
            return False
            
    def execute_sql_file(self, filepath: Path) -> bool:
        """Execute SQL file against the database"""
        try:
            # Connect to our database
            db_config = self.db_config.copy()
            db_config['database'] = self.db_name
            
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            
            # Read and execute SQL file
            with open(filepath, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                
            cursor.execute(sql_content)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Executed SQL file: {filepath.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ SQL execution failed for {filepath.name}: {e}")
            return False
            
    def setup_schema(self) -> bool:
        """Create database schema"""
        logger.info("🏗️  Setting up database schema...")
        
        # Execute schema files in order
        schema_files = [
            '01_create_tables.sql',
            '02_create_views.sql'
        ]
        
        for filename in schema_files:
            filepath = self.schema_path / filename
            if not filepath.exists():
                logger.error(f"❌ Schema file not found: {filepath}")
                return False
                
            if not self.execute_sql_file(filepath):
                return False
                
        logger.info("✅ Database schema setup completed")
        return True
        
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("📦 Installing Python dependencies...")
        
        try:
            requirements_file = Path(__file__).parent / 'requirements.txt'
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ])
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Dependency installation failed: {e}")
            return False
            
    def create_directories(self) -> bool:
        """Create necessary directories"""
        directories = [
            Path(__file__).parent / 'logs',
            Path(__file__).parent / 'backups',
            Path(__file__).parent / 'exports'
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            logger.info(f"📁 Created directory: {directory}")
            
        return True
        
    def import_sample_data(self) -> bool:
        """Import sample data from CSV files"""
        logger.info("📊 Importing sample data...")
        
        try:
            from etl.import_data import MotoGPETL
            
            data_path = Path(__file__).parent.parent / 'data' / 'raw'
            if not data_path.exists():
                logger.error(f"❌ Data directory not found: {data_path}")
                return False
                
            db_config = self.db_config.copy()
            db_config['database'] = self.db_name
            
            etl = MotoGPETL(data_path, db_config)
            success = etl.run_full_import()
            
            if success:
                logger.info("✅ Sample data imported successfully")
            else:
                logger.error("❌ Sample data import failed")
                
            return success
            
        except ImportError as e:
            logger.error(f"❌ ETL import failed: {e}")
            return False
            
    def run_full_setup(self, reset: bool = False, import_data: bool = False) -> bool:
        """Run complete database setup"""
        logger.info("🚀 Starting MotoGP database setup...")
        
        # Check PostgreSQL connection
        if not self.check_postgresql_connection():
            logger.error("❌ Cannot proceed without PostgreSQL connection")
            return False
            
        # Create directories
        if not self.create_directories():
            return False
            
        # Install dependencies
        if not self.install_dependencies():
            logger.warning("⚠️ Dependency installation failed, continuing anyway...")
            
        # Reset database if requested
        if reset:
            logger.info("🔄 Resetting database...")
            if not self.drop_database():
                return False
                
        # Create database
        if not self.create_database():
            return False
            
        # Setup schema
        if not self.setup_schema():
            return False
            
        # Import sample data if requested
        if import_data:
            if not self.import_sample_data():
                logger.warning("⚠️ Sample data import failed, but setup continues...")
                
        logger.info("🎉 Database setup completed successfully!")
        logger.info(f"📊 Database URL: postgresql://{self.db_config['user']}:***@{self.db_config['host']}:{self.db_config['port']}/{self.db_name}")
        
        return True

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Setup MotoGP Analytics Database')
    parser.add_argument('--reset', action='store_true', help='Reset database (drop and recreate)')
    parser.add_argument('--sample-data', action='store_true', help='Import sample data from CSV files')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency installation')
    
    args = parser.parse_args()
    
    # Create setup instance and run
    setup = DatabaseSetup()
    success = setup.run_full_setup(reset=args.reset, import_data=args.sample_data)
    
    if success:
        print("\n✅ MotoGP Database Setup Complete!")
        print("\n🔧 Next Steps:")
        print("1. Copy .env.example to .env and update your database credentials")
        print("2. Run 'python etl/import_data.py' to import CSV data")
        print("3. Test with 'python api/main.py' to start the API server")
        print("4. Access API docs at: http://localhost:8000/docs")
    else:
        print("\n❌ Database setup failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()