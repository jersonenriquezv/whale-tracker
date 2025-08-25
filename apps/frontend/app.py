"""
Whale Tracker v0 - Frontend Dashboard
Streamlit application for whale transaction tracking and analysis
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from typing import Dict, Any, List

# Page configuration
st.set_page_config(
    page_title="Whale Tracker v0",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-healthy {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Environment variables
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SUPABASE_URL = os.getenv("SUPABASE_URL", "http://localhost:54321")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")

def get_backend_status() -> Dict[str, Any]:
    """Get backend API status"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.json() if response.status_code == 200 else {"status": "error"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_system_status() -> Dict[str, Any]:
    """Get system status from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=5)
        return response.json() if response.status_code == 200 else {"status": "error"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_sample_data() -> pd.DataFrame:
    """Create sample whale transaction data for demonstration"""
    data = {
        'timestamp': pd.date_range(start='2024-01-01', periods=100, freq='H'),
        'from_address': [f'0x{i:040x}' for i in range(100)],
        'to_address': [f'0x{i+1000:040x}' for i in range(100)],
        'value_eth': [100 + i * 10 for i in range(100)],
        'value_usd': [(100 + i * 10) * 2000 for i in range(100)],
        'gas_price': [20 + i * 0.5 for i in range(100)],
        'whale_score': [0.5 + i * 0.005 for i in range(100)]
    }
    return pd.DataFrame(data)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">🐋 Whale Tracker v0</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "Whale Transactions", "Liquidity Zones", "Market Analysis", "Alerts", "Settings"]
    )
    
    # System status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    
    backend_status = get_backend_status()
    system_status = get_system_status()
    
    # Backend status
    if backend_status.get("status") == "healthy":
        st.sidebar.markdown('<p class="status-healthy">✅ Backend API: Healthy</p>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<p class="status-error">❌ Backend API: Error</p>', unsafe_allow_html=True)
    
    # Database status
    if backend_status.get("services", {}).get("database") == "healthy":
        st.sidebar.markdown('<p class="status-healthy">✅ Database: Healthy</p>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<p class="status-warning">⚠️ Database: Not Implemented</p>', unsafe_allow_html=True)
    
    # Redis status
    if backend_status.get("services", {}).get("redis") == "healthy":
        st.sidebar.markdown('<p class="status-healthy">✅ Redis: Healthy</p>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<p class="status-warning">⚠️ Redis: Not Implemented</p>', unsafe_allow_html=True)
    
    # Page routing
    if page == "Dashboard":
        show_dashboard()
    elif page == "Whale Transactions":
        show_whale_transactions()
    elif page == "Liquidity Zones":
        show_liquidity_zones()
    elif page == "Market Analysis":
        show_market_analysis()
    elif page == "Alerts":
        show_alerts()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    """Show main dashboard"""
    st.header("📊 Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Whale Transactions",
            value="1,234",
            delta="+12%"
        )
    
    with col2:
        st.metric(
            label="Active Liquidity Zones",
            value="56",
            delta="+3"
        )
    
    with col3:
        st.metric(
            label="Total Volume (24h)",
            value="$45.2M",
            delta="+8.5%"
        )
    
    with col4:
        st.metric(
            label="Alert Triggers",
            value="23",
            delta="+5"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🐋 Whale Transaction Volume")
        # Sample data for demonstration
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        volumes = [1000000 + i * 50000 + (i % 7) * 200000 for i in range(30)]
        
        fig = px.line(
            x=dates,
            y=volumes,
            title="Daily Whale Transaction Volume (USD)",
            labels={'x': 'Date', 'y': 'Volume (USD)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Transaction Size Distribution")
        # Sample data for demonstration
        sizes = [100, 200, 500, 1000, 2000, 5000, 10000]
        counts = [45, 32, 18, 12, 8, 4, 2]
        
        fig = px.bar(
            x=sizes,
            y=counts,
            title="Whale Transaction Size Distribution",
            labels={'x': 'Transaction Size (ETH)', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    # Sample recent transactions
    sample_data = create_sample_data().tail(10)
    
    st.dataframe(
        sample_data[['timestamp', 'from_address', 'to_address', 'value_eth', 'value_usd']].rename(
            columns={
                'timestamp': 'Time',
                'from_address': 'From',
                'to_address': 'To',
                'value_eth': 'ETH',
                'value_usd': 'USD'
            }
        ),
        use_container_width=True
    )

def show_whale_transactions():
    """Show whale transactions page"""
    st.header("🐋 Whale Transactions")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_amount = st.number_input("Minimum Amount (ETH)", value=100.0)
    
    with col2:
        time_range = st.selectbox("Time Range", ["1 Hour", "24 Hours", "7 Days", "30 Days"])
    
    with col3:
        whale_score = st.slider("Whale Score", 0.0, 1.0, 0.5)
    
    # Sample data
    sample_data = create_sample_data()
    
    # Filter data (simplified for demo)
    filtered_data = sample_data[
        (sample_data['value_eth'] >= min_amount) &
        (sample_data['whale_score'] >= whale_score)
    ]
    
    # Display transactions
    st.dataframe(
        filtered_data[['timestamp', 'from_address', 'to_address', 'value_eth', 'value_usd', 'whale_score']].rename(
            columns={
                'timestamp': 'Time',
                'from_address': 'From',
                'to_address': 'To',
                'value_eth': 'ETH',
                'value_usd': 'USD',
                'whale_score': 'Whale Score'
            }
        ),
        use_container_width=True
    )

def show_liquidity_zones():
    """Show liquidity zones page"""
    st.header("💧 Liquidity Zones")
    
    st.info("Liquidity zone analysis will be implemented in future versions.")
    
    # Placeholder for liquidity zone visualization
    st.subheader("Order Book Liquidity Heatmap")
    
    # Sample heatmap data
    import numpy as np
    
    # Create sample order book data
    prices = np.linspace(1900, 2100, 50)
    bids = np.random.exponential(100, 50)
    asks = np.random.exponential(100, 50)
    
    fig = go.Figure()
    
    # Add bid side
    fig.add_trace(go.Bar(
        x=bids,
        y=prices,
        orientation='h',
        name='Bids',
        marker_color='green',
        opacity=0.7
    ))
    
    # Add ask side
    fig.add_trace(go.Bar(
        x=asks,
        y=prices,
        orientation='h',
        name='Asks',
        marker_color='red',
        opacity=0.7
    ))
    
    fig.update_layout(
        title="ETH/USD Order Book Liquidity",
        xaxis_title="Size",
        yaxis_title="Price (USD)",
        barmode='overlay'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_market_analysis():
    """Show market analysis page"""
    st.header("📈 Market Analysis")
    
    st.info("Market analysis features will be implemented in future versions.")
    
    # Placeholder for market analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Price Action")
        # Sample price data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
        prices = [2000 + 100 * np.sin(i/10) + np.random.normal(0, 20) for i in range(100)]
        
        fig = px.line(
            x=dates,
            y=prices,
            title="ETH Price (USD)",
            labels={'x': 'Time', 'y': 'Price (USD)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Volume Analysis")
        # Sample volume data
        volumes = [1000000 + np.random.normal(0, 200000) for _ in range(100)]
        
        fig = px.bar(
            x=dates,
            y=volumes,
            title="Trading Volume (USD)",
            labels={'x': 'Time', 'y': 'Volume (USD)'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_alerts():
    """Show alerts page"""
    st.header("🔔 Alerts")
    
    st.info("Alert management will be implemented in future versions.")
    
    # Placeholder for alerts
    st.subheader("Active Alerts")
    
    # Sample alerts
    alerts = [
        {"type": "Whale Movement", "condition": ">1000 ETH", "status": "Active"},
        {"type": "Liquidity Zone", "condition": "Price < $1900", "status": "Active"},
        {"type": "SMC Pattern", "condition": "Fair Value Gap", "status": "Triggered"},
    ]
    
    for alert in alerts:
        st.write(f"**{alert['type']}**: {alert['condition']} - {alert['status']}")

def show_settings():
    """Show settings page"""
    st.header("⚙️ Settings")
    
    st.info("Settings and configuration will be implemented in future versions.")
    
    # Placeholder for settings
    st.subheader("API Configuration")
    
    st.text_input("Backend URL", value=BACKEND_URL, disabled=True)
    st.text_input("Supabase URL", value=SUPABASE_URL, disabled=True)
    
    st.subheader("Alert Preferences")
    st.checkbox("Email Notifications", value=False)
    st.checkbox("Telegram Notifications", value=True)
    st.checkbox("Desktop Notifications", value=False)

if __name__ == "__main__":
    main()
