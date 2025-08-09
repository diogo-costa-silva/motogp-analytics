"""
Application Configuration
=========================
Purpose: Configuration settings for Streamlit app
"""

import os
from typing import Dict, Any

APP_CONFIG = {
    # API Configuration
    'api_base_url': os.getenv('MOTOGP_API_URL', 'http://localhost:8000'),
    'api_timeout': 10,
    'cache_ttl': 300,  # 5 minutes
    
    # App Settings
    'app_name': 'MotoGP Analytics',
    'app_version': '1.0.0',
    'debug_mode': os.getenv('DEBUG', 'false').lower() == 'true',
    
    # UI Configuration
    'theme': {
        'primary_color': '#1f77b4',
        'background_color': '#ffffff',
        'secondary_background_color': '#f8f9fa',
        'text_color': '#262730'
    },
    
    # Data Settings
    'default_limits': {
        'riders': 50,
        'circuits': 30,
        'constructors': 25,
        'seasons': 20,
        'race_results': 100
    },
    
    # Business Questions
    'business_questions': [
        {
            'id': 'q1',
            'question': 'Qual o piloto com mais títulos em 125cc?',
            'category': 'Performance',
            'complexity': 'Medium',
            'data_sources': ['constructors', 'riders']
        },
        {
            'id': 'q2', 
            'question': 'O país com mais pódios lockout?',
            'category': 'Geographic',
            'complexity': 'High',
            'data_sources': ['lockouts', 'countries']
        },
        {
            'id': 'q3',
            'question': 'Qual o país que tem maior número de vitórias?',
            'category': 'Geographic', 
            'complexity': 'Low',
            'data_sources': ['race_results', 'countries']
        },
        {
            'id': 'q4',
            'question': 'Qual o piloto com maior número de vitórias no seu País?',
            'category': 'Performance',
            'complexity': 'Medium',
            'data_sources': ['race_results', 'riders', 'circuits']
        },
        {
            'id': 'q5',
            'question': 'Nos anos 80 e 90, qual a equipa de construtores que mais teve sucesso?',
            'category': 'Historical',
            'complexity': 'Medium',
            'data_sources': ['constructors', 'seasons']
        }
    ],
    
    # Chart Settings
    'chart_config': {
        'default_height': 400,
        'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
        'font_family': 'Arial, sans-serif',
        'animation_duration': 500
    }
}

# Navigation Configuration
NAVIGATION_CONFIG = {
    'sections': [
        {
            'name': 'Executive Dashboard',
            'icon': '📊',
            'description': 'High-level KPIs and strategic insights'
        },
        {
            'name': 'Rider Analytics', 
            'icon': '🏇',
            'description': 'Individual performance and career analysis'
        },
        {
            'name': 'Circuit Intelligence',
            'icon': '🏁', 
            'description': 'Track performance and hosting insights'
        },
        {
            'name': 'Constructor Insights',
            'icon': '🏭',
            'description': 'Technology cycles and market dominance'
        },
        {
            'name': 'Geographic Analysis',
            'icon': '🌍',
            'description': 'Country and regional performance trends'
        },
        {
            'name': 'Business Q&A',
            'icon': '❓',
            'description': 'Interactive strategic question answering'
        }
    ]
}

# Demo Data for offline mode
DEMO_DATA = {
    'executive_dashboard': {
        'total_active_riders': 180,
        'total_active_circuits': 23,
        'total_active_constructors': 12,
        'countries_represented': 35,
        'current_season': 2024,
        'total_race_results': 12500,
        'most_wins_rider': 'Valentino Rossi',
        'most_wins_count': 89,
        'most_successful_constructor': 'Honda',
        'most_championships_count': 25,
        'most_successful_country': 'Spain',
        'most_country_wins': 180
    },
    'top_riders': [
        {'name': 'Valentino Rossi', 'wins': 89, 'championships': 7, 'country': 'Italy'},
        {'name': 'Marc Márquez', 'wins': 82, 'championships': 6, 'country': 'Spain'},
        {'name': 'Jorge Lorenzo', 'wins': 68, 'championships': 5, 'country': 'Spain'},
        {'name': 'Dani Pedrosa', 'wins': 31, 'championships': 0, 'country': 'Spain'},
        {'name': 'Casey Stoner', 'wins': 38, 'championships': 2, 'country': 'Australia'}
    ],
    'country_performance': [
        {'country': 'Spain', 'riders': 35, 'wins': 180, 'championships': 15},
        {'country': 'Italy', 'riders': 28, 'wins': 156, 'championships': 12},
        {'country': 'UK', 'riders': 18, 'wins': 98, 'championships': 8},
        {'country': 'Australia', 'riders': 12, 'wins': 67, 'championships': 5},
        {'country': 'USA', 'riders': 15, 'wins': 45, 'championships': 3},
        {'country': 'Japan', 'riders': 8, 'wins': 34, 'championships': 2}
    ]
}

def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return APP_CONFIG.get(key, default)

def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return APP_CONFIG.get('debug_mode', False)