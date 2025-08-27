"""
Whale Tracker v0 - Streamlit Dashboard
Basic dashboard to visualize whale transactions and market data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Optional

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
        font-size: 2.5rem;
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
    .whale-table {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"

def get_backend_status() -> Dict:
    """Get backend status"""
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_whale_transactions(limit: int = 50, hours_back: int = 24) -> Optional[Dict]:
    """Get whale transactions from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/whales/recent",
            params={"limit": limit, "hours_back": hours_back},
            timeout=10
        )
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def create_metrics_row(data: List[Dict]) -> None:
    """Create metrics row"""
    if not data:
        return
    
    df = pd.DataFrame(data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_volume = df['value_eth'].sum()
        st.metric(
            label="Total Volume (ETH)",
            value=f"{total_volume:,.1f}",
            delta=None
        )
    
    with col2:
        total_usd = df['value_usd'].sum()
        st.metric(
            label="Total Volume (USD)",
            value=f"${total_usd:,.0f}",
            delta=None
        )
    
    with col3:
        avg_tx_size = df['value_eth'].mean()
        st.metric(
            label="Avg Transaction Size",
            value=f"{avg_tx_size:.1f} ETH",
            delta=None
        )
    
    with col4:
        high_priority_count = len(df[df['priority_level'] == 'high'])
        st.metric(
            label="High Priority Transactions",
            value=high_priority_count,
            delta=None
        )



def create_transaction_table(data: List[Dict]) -> None:
    """Create transaction table"""
    if not data:
        return
    
    df = pd.DataFrame(data)
    
    # Format columns for display
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601').dt.strftime('%Y-%m-%d %H:%M:%S')
    df['value_eth'] = df['value_eth'].round(2)
    df['value_usd'] = df['value_usd'].round(0).astype(int)
    df['tx_hash_short'] = df['tx_hash'].str[:10] + '...'
    df['from_short'] = df['from_address'].str[:10] + '...'
    df['to_short'] = df['to_address'].str[:10] + '...'
    
    # Create exchange direction column
    def get_exchange_direction(row):
        if not row['exchange_involved']:
            return "No Exchange"
        
        # Check if from_address is exchange
        from_is_exchange = row['from_address'] in [
            "0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance
            "0x9696f59E4d72E237BE84fFD425DCaD154Bf96976",  # Coinbase
            "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b",  # OKX
        ]
        
        # Check if to_address is exchange
        to_is_exchange = row['to_address'] in [
            "0x28C6c06298d514Db089934071355E5743bf21d60",  # Binance
            "0x9696f59E4d72E237BE84fFD425DCaD154Bf96976",  # Coinbase
            "0x6cc5f688a315f3dc28a7781717a9a798a59fda7b",  # OKX
        ]
        
        if from_is_exchange and to_is_exchange:
            return "Exchange ↔ Exchange"
        elif from_is_exchange:
            return "From Exchange"  # ETH withdrawn from exchange
        elif to_is_exchange:
            return "To Exchange"    # ETH deposited to exchange
        else:
            return "Exchange Related"
    
    df['exchange_direction'] = df.apply(get_exchange_direction, axis=1)
    
    # Select columns for display
    display_df = df[[
        'timestamp', 'tx_hash_short', 'from_short', 'to_short',
        'value_eth', 'value_usd', 'priority_level', 'exchange_direction'
    ]].rename(columns={
        'timestamp': 'Time',
        'tx_hash_short': 'Transaction Hash',
        'from_short': 'From',
        'to_short': 'To',
        'value_eth': 'Value (ETH)',
        'value_usd': 'Value (USD)',
        'priority_level': 'Priority',
        'exchange_direction': 'Exchange Action'
    })
    
    st.subheader("Recent Whale Transactions")
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )



def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🐋 Whale Tracker v0</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Settings")
    
    # Backend status
    status = get_backend_status()
    if status.get("status") == "ok":
        st.sidebar.success("✅ Backend Connected")
    else:
        st.sidebar.error("❌ Backend Error")
        st.sidebar.text(f"Error: {status.get('message', 'Unknown')}")
    
    # Filters
    st.sidebar.subheader("Filters")
    hours_back = st.sidebar.slider("Hours Back", 1, 168, 24)
    limit = st.sidebar.slider("Max Transactions", 10, 200, 50)
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Main content
    st.header("Dashboard Overview")
    
    # Get data
    data = get_whale_transactions(limit=limit, hours_back=hours_back)
    
    if data and data.get('whales'):
        whales_data = data['whales']
        
        # Metrics
        create_metrics_row(whales_data)
        
        # Recent transactions (most important for trading)
        create_transaction_table(whales_data[:10])  # Show only first 10
        
    else:
        st.warning("No whale transactions found in the selected time range.")
        st.info("Try adjusting the filters or check if the worker is running.")

if __name__ == "__main__":
    main()
