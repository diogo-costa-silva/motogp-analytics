"""
MotoGP API Client
=================
Purpose: Client for connecting to MotoGP Analytics API
"""

import requests
import json
from typing import Dict, List, Optional, Any
import streamlit as st
from datetime import datetime

class MotoGPAPIClient:
    """Client for MotoGP Analytics API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize API client"""
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise ConnectionError("Cannot connect to MotoGP API. Is the server running?")
        except requests.exceptions.Timeout:
            raise TimeoutError("API request timed out")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"API request failed: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")
    
    def health_check(self) -> bool:
        """Check API health"""
        try:
            response = self._make_request("/health")
            return response.get('status') == 'healthy'
        except:
            return False
    
    def get_executive_dashboard(self) -> Dict[str, Any]:
        """Get executive dashboard data"""
        return self._make_request("/dashboard")
    
    def get_riders(self, limit: int = 50, country: Optional[str] = None, 
                   active: Optional[bool] = None) -> Dict[str, Any]:
        """Get rider data"""
        params = {'limit': limit}
        if country:
            params['country'] = country
        if active is not None:
            params['active'] = active
        return self._make_request("/riders", params)
    
    def get_circuits(self, limit: int = 50, country: Optional[str] = None,
                     active: Optional[bool] = None) -> Dict[str, Any]:
        """Get circuit data"""
        params = {'limit': limit}
        if country:
            params['country'] = country
        if active is not None:
            params['active'] = active
        return self._make_request("/circuits", params)
    
    def get_constructors(self, limit: int = 50, country: Optional[str] = None,
                         active: Optional[bool] = None) -> Dict[str, Any]:
        """Get constructor data"""
        params = {'limit': limit}
        if country:
            params['country'] = country
        if active is not None:
            params['active'] = active
        return self._make_request("/constructors", params)
    
    def get_country_performance(self, limit: int = 50, 
                                continent: Optional[str] = None) -> Dict[str, Any]:
        """Get country performance data"""
        params = {'limit': limit}
        if continent:
            params['continent'] = continent
        return self._make_request("/countries/performance", params)
    
    def get_seasons(self, limit: int = 20, start_year: Optional[int] = None,
                    end_year: Optional[int] = None) -> Dict[str, Any]:
        """Get season data"""
        params = {'limit': limit}
        if start_year:
            params['start_year'] = start_year
        if end_year:
            params['end_year'] = end_year
        return self._make_request("/seasons", params)
    
    def get_race_results(self, limit: int = 100, season: Optional[int] = None,
                         winners_only: bool = False) -> Dict[str, Any]:
        """Get race results"""
        params = {'limit': limit, 'winners_only': winners_only}
        if season:
            params['season'] = season
        return self._make_request("/race-results", params)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self._make_request("/stats/summary")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_dashboard_data():
    """Cached version of dashboard data for better performance"""
    try:
        client = MotoGPAPIClient()
        return client.get_executive_dashboard()
    except:
        return None

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_cached_riders_data(limit: int = 50, country: str = None):
    """Cached version of riders data"""
    try:
        client = MotoGPAPIClient()
        return client.get_riders(limit=limit, country=country)
    except:
        return None