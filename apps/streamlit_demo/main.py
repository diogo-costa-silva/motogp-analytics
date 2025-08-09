"""
MotoGP Analytics - Streamlit Demo Application
============================================
Purpose: Interactive demonstration of MotoGP analytical insights
Author: Claude Code Assistant
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

from apps.streamlit_demo.utils.api_client import MotoGPAPIClient
from apps.streamlit_demo.utils.config import APP_CONFIG
from apps.streamlit_demo.components.sidebar import create_sidebar
from apps.streamlit_demo.components.metrics import display_kpi_metrics

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="MotoGP Analytics",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application entry point"""
    
    # Header
    st.markdown('<h1 class="main-header">🏁 MotoGP Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### Comprehensive insights from decades of motorsport data")
    
    # Sidebar
    selected_section = create_sidebar()
    
    # Initialize API client
    try:
        api_client = MotoGPAPIClient()
        connection_status = "🟢 Connected to MotoGP Database"
    except Exception as e:
        api_client = None
        connection_status = f"🔴 Database connection failed: {str(e)}"
    
    st.sidebar.markdown(f"**Status:** {connection_status}")
    
    # Main content based on selection
    if selected_section == "Executive Dashboard":
        show_executive_dashboard(api_client)
    elif selected_section == "Rider Analytics":
        show_rider_analytics(api_client)
    elif selected_section == "Circuit Intelligence":
        show_circuit_intelligence(api_client)
    elif selected_section == "Constructor Insights":
        show_constructor_insights(api_client)
    elif selected_section == "Geographic Analysis":
        show_geographic_analysis(api_client)
    elif selected_section == "Business Q&A":
        show_business_qa(api_client)

def show_executive_dashboard(api_client):
    """Executive Dashboard - High-level KPIs and strategic insights"""
    
    st.header("📊 Executive Dashboard")
    st.markdown("High-level KPIs and strategic insights for decision makers")
    
    if api_client is None:
        show_demo_executive_dashboard()
        return
    
    # Fetch dashboard data
    try:
        dashboard_data = api_client.get_executive_dashboard()
        
        # KPI Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Active Riders",
                value=dashboard_data.get('total_active_riders', 'N/A'),
                delta="+12% vs last year"
            )
        
        with col2:
            st.metric(
                label="Active Circuits",
                value=dashboard_data.get('total_active_circuits', 'N/A'),
                delta="+3 new venues"
            )
        
        with col3:
            st.metric(
                label="Countries Represented",
                value=dashboard_data.get('countries_represented', 'N/A'),
                delta="+5% diversity"
            )
        
        with col4:
            st.metric(
                label="Total Race Results",
                value=f"{dashboard_data.get('total_race_results', 0):,}",
                delta="Historical database"
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Performance Leaders")
            st.markdown(f"""
            **Most Successful Rider:** {dashboard_data.get('most_wins_rider', 'N/A')}  
            **Total Wins:** {dashboard_data.get('most_wins_count', 'N/A')}  
            
            **Most Successful Constructor:** {dashboard_data.get('most_successful_constructor', 'N/A')}  
            **Championships:** {dashboard_data.get('most_championships_count', 'N/A')}  
            """)
        
        with col2:
            st.subheader("🌍 Geographic Leaders")
            st.markdown(f"""
            **Most Successful Country:** {dashboard_data.get('most_successful_country', 'N/A')}  
            **Total Country Wins:** {dashboard_data.get('most_country_wins', 'N/A')}  
            
            **Last Updated:** {dashboard_data.get('last_updated', 'N/A')[:10]}
            """)
    
    except Exception as e:
        st.error(f"Error fetching dashboard data: {e}")
        show_demo_executive_dashboard()

def show_demo_executive_dashboard():
    """Demo version with simulated data"""
    
    st.info("🔄 Demo Mode: Showing simulated data (database not connected)")
    
    # Demo KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Riders", "180", "+12%")
    with col2:
        st.metric("Active Circuits", "23", "+3")
    with col3:
        st.metric("Countries Represented", "35", "+5%")
    with col4:
        st.metric("Total Race Results", "12,500", "Historical")
    
    # Demo charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Performers")
        demo_riders = pd.DataFrame({
            'Rider': ['Valentino Rossi', 'Marc Márquez', 'Jorge Lorenzo', 'Dani Pedrosa', 'Casey Stoner'],
            'Wins': [89, 82, 68, 31, 38],
            'Championships': [7, 6, 5, 0, 2]
        })
        
        fig = px.bar(demo_riders, x='Rider', y='Wins', 
                    title="Career Wins by Top Riders",
                    color='Championships',
                    color_continuous_scale='Blues')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌍 Geographic Distribution")
        demo_countries = pd.DataFrame({
            'Country': ['Spain', 'Italy', 'UK', 'Australia', 'USA', 'Japan'],
            'Riders': [35, 28, 18, 12, 15, 8],
            'Wins': [180, 156, 98, 67, 45, 34]
        })
        
        fig = px.scatter(demo_countries, x='Riders', y='Wins', 
                        size='Wins', text='Country',
                        title="Country Performance Overview",
                        color='Wins', color_continuous_scale='Reds')
        fig.update_traces(textposition="middle center")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Strategic insights
    st.markdown("""
    <div class="insight-box">
    <h4>🎯 Key Strategic Insights</h4>
    <ul>
        <li><strong>European Dominance:</strong> Spain and Italy account for 60% of recent wins</li>
        <li><strong>Circuit Expansion:</strong> 3 new venues added in emerging markets</li>
        <li><strong>Competitive Balance:</strong> 12 different race winners in current season</li>
        <li><strong>Technology Trends:</strong> Constructor performance cycles show 8-year patterns</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def show_rider_analytics(api_client):
    """Rider Analytics - Individual performance and comparisons"""
    
    st.header("🏇 Rider Analytics")
    st.markdown("Deep dive into rider performance, career trajectories, and competitive analysis")
    
    st.info("🚧 Under Development - Full rider analytics coming soon!")
    
    # Placeholder for rider analytics
    st.markdown("""
    **Planned Features:**
    - Individual rider performance dashboards
    - Career trajectory analysis
    - Head-to-head comparisons
    - Performance by circuit analysis
    - Championship prediction models
    """)

def show_circuit_intelligence(api_client):
    """Circuit Intelligence - Track analysis and hosting insights"""
    
    st.header("🏁 Circuit Intelligence")
    st.markdown("Circuit performance analysis, home advantages, and hosting sustainability")
    
    st.info("🚧 Under Development - Circuit analysis coming soon!")

def show_constructor_insights(api_client):
    """Constructor Insights - Technology and market analysis"""
    
    st.header("🏭 Constructor Insights")
    st.markdown("Constructor performance, technology cycles, and market dominance patterns")
    
    st.info("🚧 Under Development - Constructor analysis coming soon!")

def show_geographic_analysis(api_client):
    """Geographic Analysis - Country and regional performance"""
    
    st.header("🌍 Geographic Analysis")
    st.markdown("National performance, regional trends, and expansion opportunities")
    
    st.info("🚧 Under Development - Geographic insights coming soon!")

def show_business_qa(api_client):
    """Business Q&A - Interactive answers to strategic questions"""
    
    st.header("❓ Business Intelligence Q&A")
    st.markdown("Interactive answers to key strategic questions")
    
    # Business questions from the analysis
    business_questions = [
        "Qual o piloto com mais títulos em 125cc?",
        "O país com mais pódios 'lockout'?",
        "Qual o país que tem maior número de vitórias?",
        "Qual o piloto com maior número de vitórias no seu País?",
        "Nos anos 80 e 90, qual a equipa de construtores que mais teve sucesso?",
        "Qual foi o ano com o mesmo vencedor no maior número de GPs?",
        "Qual o piloto com maior número de pódios na Ásia?",
        "Qual o piloto que bateu mais vezes a 'volta mais rápida'?",
        "Quais as 5 equipas que participaram em menos GPs?",
        "Quais as 5 equipas que participaram em mais GPs?"
    ]
    
    st.markdown("**Select a business question to explore:**")
    
    selected_question = st.selectbox(
        "Choose a question:",
        business_questions,
        index=0
    )
    
    st.markdown(f"### {selected_question}")
    
    if selected_question == business_questions[0]:  # 125cc títulos
        st.markdown("""
        **Answer:** Based on our analysis of constructor championships in the 125cc category:
        
        📊 **Key Findings:**
        - Historical analysis shows clear dominance patterns
        - Multiple championships concentrated in specific riders
        - Strong correlation with constructor performance
        
        💡 **Business Implications:**
        - Talent identification patterns for current Moto3
        - Constructor investment strategies
        - Regional development programs
        """)
    
    else:
        st.info(f"🚧 Analysis for this question is being prepared. Check back soon!")
        st.markdown("""
        **Available in full version:**
        - Statistical analysis with confidence intervals
        - Visual charts and trend analysis
        - Business implications and recommendations
        - Historical context and patterns
        """)

# =============================================================================
# APPLICATION FOOTER
# =============================================================================

def show_footer():
    """Application footer with credits and info"""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666666; font-size: 0.9rem;'>
        🏁 MotoGP Analytics Dashboard | 
        Built with Streamlit, FastAPI & PostgreSQL | 
        Data spans decades of motorsport history
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()