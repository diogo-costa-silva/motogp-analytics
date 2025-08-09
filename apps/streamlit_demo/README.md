# MotoGP Analytics - Streamlit Demo Application

## 🏁 Overview

Interactive demonstration of MotoGP analytical insights built with Streamlit, showcasing comprehensive analysis from decades of motorsport data.

## 🚀 Features

### 📊 Executive Dashboard
- High-level KPIs and strategic metrics
- Performance leaders and champions
- Geographic distribution insights
- Real-time database statistics

### 🏇 Rider Analytics
- Individual rider performance analysis
- Career trajectory visualization
- Head-to-head comparisons
- Championship prediction models

### 🏁 Circuit Intelligence
- Track performance analysis
- Home circuit advantage metrics
- Hosting sustainability insights
- Circuit dominance patterns

### 🏭 Constructor Insights
- Technology cycle analysis
- Market dominance patterns
- Constructor championship history
- Investment timing optimization

### 🌍 Geographic Analysis
- National performance rankings
- Regional trend analysis
- Market expansion opportunities
- Cultural impact assessment

### ❓ Business Intelligence Q&A
- Interactive answers to 20+ strategic questions
- Statistical analysis with confidence intervals
- Business implications and recommendations
- Historical context and patterns

## 🛠️ Technical Architecture

```
apps/streamlit_demo/
├── main.py                 # Main application entry point
├── run_app.py             # Application launcher script
├── components/            # Reusable UI components
│   ├── sidebar.py         # Navigation and filters
│   └── metrics.py         # KPI displays and charts
├── utils/                 # Utility modules
│   ├── api_client.py      # MotoGP API client
│   └── config.py          # App configuration
└── README.md             # This file
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- UV package manager
- MotoGP Analytics API (optional - app works in demo mode)

### Quick Start

1. **Install Dependencies** (from project root):
   ```bash
   uv sync
   ```

2. **Launch Application**:
   ```bash
   # Option 1: Using launcher script
   uv run python apps/streamlit_demo/run_app.py
   
   # Option 2: Direct Streamlit command
   uv run streamlit run apps/streamlit_demo/main.py
   ```

3. **Access Application**:
   Open browser to `http://localhost:8501`

## 🔌 API Integration

The application automatically connects to the MotoGP Analytics API for real-time data:

- **API Endpoint**: `http://localhost:8000` (default)
- **Fallback Mode**: Demo data when API unavailable
- **Caching**: 5-minute cache for performance optimization

### API Configuration

Set environment variables for custom API configuration:
```bash
export MOTOGP_API_URL=http://your-api-server:8000
export DEBUG=true  # Enable debug mode
```

## 📊 Data Sources

The application visualizes insights from 6 core datasets:
- **Race Winners**: Historical race results and champions
- **Rider Information**: Career statistics and demographics
- **Circuit Events**: Track hosting and performance data
- **Constructor Championships**: Technology and market data
- **Finishing Positions**: Detailed race placement analysis
- **Podium Lockouts**: National dominance patterns

## 🎯 Use Cases

### For Executives
- Strategic decision making with executive dashboard
- ROI analysis and investment planning
- Market expansion opportunity assessment

### For Analysts
- Deep-dive performance analysis
- Statistical validation of hypotheses
- Interactive exploration of business questions

### For Stakeholders
- Visual presentation of complex data insights
- Real-time access to key performance indicators
- Geographic and competitive intelligence

## 🔧 Development

### Adding New Sections

1. **Create page module** in `pages/` directory
2. **Update navigation** in `components/sidebar.py`
3. **Add route handler** in `main.py`
4. **Update configuration** in `utils/config.py`

### Custom Components

```python
from apps.streamlit_demo.components.metrics import display_kpi_metrics
from apps.streamlit_demo.utils.api_client import MotoGPAPIClient

# Use in your pages
api_client = MotoGPAPIClient()
data = api_client.get_executive_dashboard()
display_kpi_metrics(data)
```

## 📈 Performance Optimization

- **Caching**: Streamlit `@st.cache_data` decorators
- **API Optimization**: Request batching and intelligent caching
- **Chart Performance**: Plotly with optimized rendering
- **Memory Management**: Efficient data structure usage

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check dependencies
uv run python -c "import streamlit; print('OK')"

# Check API connection
curl http://localhost:8000/health
```

**Import errors:**
```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH=/path/to/motogp-analytics
```

**API connection issues:**
- Verify MotoGP API is running on port 8000
- Check firewall/network configuration
- Application will use demo data as fallback

## 📝 License

Part of the MotoGP Analytics project. Built for educational and analytical purposes.

## 🤝 Contributing

1. Follow existing code structure and patterns
2. Add appropriate error handling and logging
3. Update documentation for new features
4. Test with both live API and demo data modes

## 🔗 Related

- **MotoGP API**: `database/api/` - REST API backend
- **Analytics Notebooks**: `notebooks/` - CRISP-DM analysis
- **Business Intelligence**: Business questions and recommendations

---

**Status**: ✅ Core application complete  
**Demo Mode**: Fully functional without API  
**Next Steps**: Enhanced analytics sections and BI integration