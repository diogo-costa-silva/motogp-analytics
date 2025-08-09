"""
Sidebar Component
=================
Purpose: Navigation and filtering controls for Streamlit app
"""

import streamlit as st
from apps.streamlit_demo.utils.config import NAVIGATION_CONFIG, APP_CONFIG

def create_sidebar() -> str:
    """Create application sidebar with navigation"""
    
    with st.sidebar:
        # App Header
        st.markdown("# 🏁 MotoGP Analytics")
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📍 Navigation")
        
        sections = NAVIGATION_CONFIG['sections']
        section_names = [section['name'] for section in sections]
        
        # Radio button for section selection
        selected_section = st.radio(
            "Choose a section:",
            section_names,
            format_func=lambda x: f"{next(s['icon'] for s in sections if s['name'] == x)} {x}"
        )
        
        # Show description for selected section
        selected_info = next(s for s in sections if s['name'] == selected_section)
        st.markdown(f"*{selected_info['description']}*")
        
        st.markdown("---")
        
        # Filters Section
        if selected_section in ['Rider Analytics', 'Circuit Intelligence', 'Constructor Insights']:
            st.markdown("### 🔍 Filters")
            
            # Country filter
            countries = ['All', 'Spain', 'Italy', 'UK', 'Australia', 'USA', 'Japan', 'France', 'Germany']
            selected_country = st.selectbox("Country:", countries)
            
            # Active status filter
            active_status = st.radio("Status:", ['All', 'Active Only', 'Retired Only'])
            
            # Store filters in session state
            st.session_state['filters'] = {
                'country': None if selected_country == 'All' else selected_country,
                'active': None if active_status == 'All' else active_status == 'Active Only'
            }
        
        # Data Settings
        if selected_section == 'Business Q&A':
            st.markdown("### ⚙️ Analysis Settings")
            
            # Question categories
            categories = ['All', 'Performance', 'Geographic', 'Historical', 'Technical']
            selected_category = st.selectbox("Question Category:", categories)
            
            # Complexity filter
            complexity = ['All', 'Low', 'Medium', 'High']
            selected_complexity = st.selectbox("Complexity Level:", complexity)
            
            st.session_state['qa_filters'] = {
                'category': None if selected_category == 'All' else selected_category,
                'complexity': None if selected_complexity == 'All' else selected_complexity
            }
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### 📊 Quick Stats")
        
        # Demo quick stats (would be real data in production)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Riders", "180", "↑12")
        with col2:
            st.metric("Circuits", "23", "↑3")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Countries", "35", "↑2")
        with col2:
            st.metric("Results", "12.5K", "Historical")
        
        st.markdown("---")
        
        # Data Sources Info
        if st.checkbox("Show Data Sources"):
            st.markdown("### 📚 Data Sources")
            st.markdown("""
            **Core Datasets:**
            - Race winners (historical)
            - Rider information
            - Circuit events
            - Constructor championships
            - Finishing positions
            - Podium lockouts
            
            **Analysis Framework:**
            - CRISP-DM methodology
            - 27 specialized notebooks
            - Statistical validation (85%+ confidence)
            """)
        
        # Footer
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; font-size: 0.8rem; color: #666;'>
            v{APP_CONFIG['app_version']}<br>
            Built with ❤️ using Streamlit
        </div>
        """, unsafe_allow_html=True)
    
    return selected_section

def get_current_filters() -> dict:
    """Get current filter settings from session state"""
    return st.session_state.get('filters', {
        'country': None,
        'active': None
    })

def get_qa_filters() -> dict:
    """Get current Q&A filter settings"""
    return st.session_state.get('qa_filters', {
        'category': None,
        'complexity': None
    })