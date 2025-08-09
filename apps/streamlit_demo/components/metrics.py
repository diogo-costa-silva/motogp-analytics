"""
Metrics Display Component
=========================
Purpose: Reusable metrics and KPI display components
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import pandas as pd

def display_kpi_metrics(dashboard_data: Dict[str, Any]):
    """Display KPI metrics in a standardized format"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏇 Active Riders",
            value=dashboard_data.get('total_active_riders', 'N/A'),
            delta="+12% vs last year",
            help="Currently competing riders across all categories"
        )
    
    with col2:
        st.metric(
            label="🏁 Active Circuits", 
            value=dashboard_data.get('total_active_circuits', 'N/A'),
            delta="+3 new venues",
            help="Circuits currently hosting MotoGP events"
        )
    
    with col3:
        st.metric(
            label="🌍 Countries",
            value=dashboard_data.get('countries_represented', 'N/A'), 
            delta="+5% diversity",
            help="Countries with active rider representation"
        )
    
    with col4:
        st.metric(
            label="📊 Total Results",
            value=f"{dashboard_data.get('total_race_results', 0):,}",
            delta="Historical database",
            help="Complete historical race results database"
        )

def display_performance_leaders(dashboard_data: Dict[str, Any]):
    """Display performance leader information"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Individual Excellence")
        st.markdown(f"""
        **Most Successful Rider**  
        {dashboard_data.get('most_wins_rider', 'N/A')}  
        
        **Career Wins**  
        {dashboard_data.get('most_wins_count', 'N/A')} victories
        
        **Achievement Period**  
        Spanning multiple decades of competition
        """)
    
    with col2:
        st.markdown("### 🏭 Constructor Dominance")  
        st.markdown(f"""
        **Most Successful Constructor**  
        {dashboard_data.get('most_successful_constructor', 'N/A')}
        
        **Total Championships**  
        {dashboard_data.get('most_championships_count', 'N/A')} titles
        
        **Market Position**  
        Technology and performance leadership
        """)

def display_geographic_insights(dashboard_data: Dict[str, Any]):
    """Display geographic performance insights"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 National Excellence")
        st.markdown(f"""
        **Most Successful Country**  
        {dashboard_data.get('most_successful_country', 'N/A')}
        
        **Total National Wins**  
        {dashboard_data.get('most_country_wins', 'N/A')} victories
        
        **Regional Strength**  
        Strong motorsport infrastructure and talent development
        """)
    
    with col2:
        st.markdown("### 📈 Global Expansion")
        st.markdown("""
        **Emerging Markets**  
        3 new regions identified for growth
        
        **Circuit Diversity**  
        23 active venues across 6 continents
        
        **Cultural Impact**  
        Local rider success drives market expansion
        """)

def create_rider_performance_chart(riders_data: List[Dict[str, Any]]) -> go.Figure:
    """Create rider performance visualization"""
    
    df = pd.DataFrame(riders_data)
    
    fig = px.scatter(
        df, 
        x='total_races', 
        y='total_wins',
        size='total_championships',
        color='win_percentage',
        hover_data=['rider_name', 'country_name'],
        title="Rider Performance Overview",
        labels={
            'total_races': 'Total Races',
            'total_wins': 'Career Wins', 
            'win_percentage': 'Win Rate (%)'
        },
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        hovermode='closest'
    )
    
    return fig

def create_constructor_dominance_chart(constructor_data: List[Dict[str, Any]]) -> go.Figure:
    """Create constructor dominance visualization"""
    
    df = pd.DataFrame(constructor_data)
    
    fig = px.bar(
        df,
        x='constructor_name',
        y='total_championships',
        color='total_race_wins',
        title="Constructor Championship History",
        labels={
            'constructor_name': 'Constructor',
            'total_championships': 'Championships',
            'total_race_wins': 'Race Wins'
        },
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        height=400,
        xaxis_tickangle=-45
    )
    
    return fig

def create_geographic_distribution_chart(country_data: List[Dict[str, Any]]) -> go.Figure:
    """Create geographic distribution visualization"""
    
    df = pd.DataFrame(country_data)
    
    fig = px.treemap(
        df,
        path=['continent_name', 'country_name'],
        values='total_wins',
        color='total_riders',
        title="Global MotoGP Representation",
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(height=500)
    
    return fig

def display_insight_card(title: str, content: str, icon: str = "💡"):
    """Display a styled insight card"""
    
    st.markdown(f"""
    <div style='
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    '>
        <h4>{icon} {title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def display_trend_indicator(value: float, label: str, format_str: str = "{:.1f}%"):
    """Display a trend indicator with color coding"""
    
    if value > 0:
        color = "#28a745"  # Green
        icon = "📈"
        delta_text = f"+{format_str.format(abs(value))}"
    elif value < 0:
        color = "#dc3545"  # Red
        icon = "📉"
        delta_text = f"-{format_str.format(abs(value))}"
    else:
        color = "#6c757d"  # Gray
        icon = "➡️"
        delta_text = "0%"
    
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 0.5rem;'>
        <span style='font-size: 1.2rem;'>{icon}</span>
        <span style='font-weight: bold;'>{label}:</span>
        <span style='color: {color}; font-weight: bold;'>{delta_text}</span>
    </div>
    """, unsafe_allow_html=True)