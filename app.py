# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
import random

# Import your existing modules
from MonteCarlo.main import NBAMonteCarloSimulator
from Data.real_sports_market import RealSportsMarket
from Core.base_price_algorithm import BasePriceAlgorithm
from Core.intragame_algorithm_real import IntragameAlgorithmReal
from Core.timeframe_algorithm import TimeframeAlgorithm
from Data.nba_data_bridge import NBADataBridge

# Page config
st.set_page_config(
    page_title="NBA Sports Market",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    }
    
    /* Cards */
    .css-1r6slb0 {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 15px;
        border-radius: 10px;
        color: white;
        backdrop-filter: blur(10px);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: rgba(0, 0, 0, 0.2);
    }
    
    /* Success/Error boxes */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'simulator' not in st.session_state:
    with st.spinner("🚀 Initializing NBA Sports Market System..."):
        mc_simulator = NBAMonteCarloSimulator()
        data_bridge = NBADataBridge(mc_simulator)
        
        st.session_state.simulator = {
            'mc_simulator': mc_simulator,
            'sports_market': RealSportsMarket(mc_simulator),
            'base_price_algo': BasePriceAlgorithm(),
            'intragame_algo': IntragameAlgorithmReal(mc_simulator),
            'timeframe_algo': TimeframeAlgorithm(),
            'data_bridge': data_bridge
        }
        
        # Set data bridge for intragame algo
        st.session_state.simulator['intragame_algo'].data_bridge = data_bridge

# Header with animation
st.markdown("""
<h1 style='text-align: center; color: white; font-size: 3em; margin-bottom: 0;'>
    🏀 NBA Sports Market
</h1>
<p style='text-align: center; color: #ffffff; font-size: 1.2em; opacity: 0.8;'>
    Real Players • Monte Carlo Projections • Live Market Mechanics
</p>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.freepik.com/free-vector/basketball-logo-design_1044-8251.jpg", width=150)
    
    selected = option_menu(
        menu_title="Navigation",
        options=["🏠 Dashboard", "🎯 Intragame Simulation", "💰 Base Price Calculator", 
                "📊 Market Analysis", "🎮 Live Demo"],
        icons=["house", "bullseye", "cash", "graph-up", "controller"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "rgba(0,0,0,0.2)"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {"color": "white", "font-size": "16px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "rgba(255,255,255,0.2)"},
        }
    )

# Player-team mapping
player_team_mapping = {
    "LeBron James": {"team": "Lakers", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png"},
    "Stephen Curry": {"team": "Warriors", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/201939.png"},
    "Kevin Durant": {"team": "Suns", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/201142.png"},
    "Giannis Antetokounmpo": {"team": "Bucks", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/203507.png"},
    "Nikola Jokic": {"team": "Nuggets", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/203999.png"},
    "Luka Doncic": {"team": "Mavericks", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/1629029.png"},
    "Joel Embiid": {"team": "76ers", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/203954.png"},
    "Jayson Tatum": {"team": "Celtics", "img": "https://cdn.nba.com/headshots/nba/latest/1040x760/1628369.png"},
}

# Dashboard Page
if selected == "🏠 Dashboard":
    st.markdown("### 📈 Market Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", "50+", "Active")
    with col2:
        st.metric("Avg Base Price", "$42.50", "+2.3%")
    with col3:
        st.metric("Market Volume", "$1.2M", "+15%")
    with col4:
        st.metric("Active Trades", "3,421", "+128")
    
    st.markdown("---")
    
    # Featured Players
    st.markdown("### ⭐ Featured Players")
    
    cols = st.columns(4)
    featured_players = ["LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo"]
    
    for idx, player in enumerate(featured_players):
        with cols[idx]:
            if player in player_team_mapping:
                st.image(player_team_mapping[player]["img"], use_column_width=True)
            st.markdown(f"**{player}**")
            st.markdown(f"Team: {player_team_mapping.get(player, {}).get('team', 'N/A')}")
            st.button(f"View Profile", key=f"profile_{player}")
    
    # Market Activity Chart
    st.markdown("### 📊 Market Activity (Last 7 Days)")
    
    # Generate sample data
    dates = pd.date_range(end=datetime.now(), periods=7)
    activity_data = pd.DataFrame({
        'Date': dates,
        'Volume': np.random.randint(800, 1500, 7),
        'Trades': np.random.randint(200, 500, 7)
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=activity_data['Date'],
        y=activity_data['Volume'],
        mode='lines+markers',
        name='Volume ($K)',
        line=dict(color='#00D9FF', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=400,
        showlegend=True,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Intragame Simulation Page
elif selected == "🎯 Intragame Simulation":
    st.markdown("### 🎯 Intragame Price Simulation")
    st.markdown("Simulate how a player's stock price changes based on their game performance")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Player selection
        st.markdown("#### 🏀 Select Player")
        all_players = list(player_team_mapping.keys()) + ["Damian Lillard", "Anthony Davis", "Jimmy Butler"]
        selected_player = st.selectbox("Choose a player:", all_players)
        
        # Show player image if available
        if selected_player in player_team_mapping:
            st.image(player_team_mapping[selected_player]["img"], width=200)
        
        # Team selection
        st.markdown("#### 🆚 Select Opponent")
        all_teams = ["Lakers", "Warriors", "Celtics", "Heat", "Nuggets", "Bucks", 
                    "Suns", "76ers", "Clippers", "Nets", "Bulls", "Knicks"]
        
        # Filter out player's own team
        player_team = player_team_mapping.get(selected_player, {}).get("team")
        if player_team and player_team in all_teams:
            opponent_teams = [t for t in all_teams if t != player_team]
        else:
            opponent_teams = all_teams
            
        opponent = st.selectbox("Choose opponent team:", opponent_teams)
        
        # Date selection
        st.markdown("#### 📅 Game Date")
        game_date = st.date_input(
            "Select date:",
            value=datetime(2024, 1, 15),
            min_value=datetime(2023, 10, 24),
            max_value=datetime(2024, 4, 14)
        )
        
        # Current price
        st.markdown("#### 💵 Current Stock Price")
        current_price = st.number_input("Enter current price ($):", value=30.0, min_value=1.0, max_value=100.0)
    
    with col2:
        if st.button("🔮 Generate Monte Carlo Projection", type="primary"):
            with st.spinner("Running 10,000 simulations..."):
                # Get projection
                mc_projection = st.session_state.simulator['data_bridge'].get_monte_carlo_projection(
                    selected_player, opponent, game_date.strftime("%Y-%m-%d"), n_simulations=10000
                )
                
                if mc_projection:
                    st.success("✅ Projection Complete!")
                    
                    # Display projections
                    st.markdown("### 📊 Monte Carlo Projections")
                    
                    proj_cols = st.columns(3)
                    with proj_cols[0]:
                        st.metric("Points", f"{mc_projection['PTS']:.1f}")
                    with proj_cols[1]:
                        st.metric("Rebounds", f"{mc_projection['REB']:.1f}")
                    with proj_cols[2]:
                        st.metric("Assists", f"{mc_projection['AST']:.1f}")
                    
                    # Actual performance input
                    st.markdown("### 🎮 Enter Actual Performance")
                    
                    perf_cols = st.columns(3)
                    with perf_cols[0]:
                        actual_pts = st.number_input("Points:", value=int(mc_projection['PTS']), min_value=0)
                    with perf_cols[1]:
                        actual_reb = st.number_input("Rebounds:", value=int(mc_projection['REB']), min_value=0)
                    with perf_cols[2]:
                        actual_ast = st.number_input("Assists:", value=int(mc_projection['AST']), min_value=0)
                    
                    if st.button("💰 Calculate Price Change", type="secondary"):
                        # Run simulation
                        actual_stats = (
                            actual_pts, actual_reb, actual_ast,
                            mc_projection['TO'], mc_projection['STOCKS'],
                            mc_projection['3PM'], mc_projection['TS%']
                        )
                        
                        result = st.session_state.simulator['intragame_algo'].simulate_intragame_real(
                            selected_player, actual_stats, opponent, 
                            game_date.strftime("%Y-%m-%d"), current_price
                        )
                        
                        if result:
                            # Show results
                            st.markdown("### 💹 Market Results")
                            
                            res_cols = st.columns(3)
                            with res_cols[0]:
                                st.metric("Old Price", f"${result['old_price']:.2f}")
                            with res_cols[1]:
                                st.metric("New Price", f"${result['new_price']:.2f}")
                            with res_cols[2]:
                                delta_color = "green" if result['price_change_pct'] > 0 else "red"
                                st.metric("Change", f"{result['price_change_pct']:+.1f}%")
                            
                            # Performance gauge
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=result['pps'],
                                title={'text': "Performance Score (PPS)"},
                                domain={'x': [0, 1], 'y': [0, 1]},
                                gauge={
                                    'axis': {'range': [-3, 3]},
                                    'bar': {'color': "lightblue"},
                                    'steps': [
                                        {'range': [-3, -1], 'color': "red"},
                                        {'range': [-1, 1], 'color': "yellow"},
                                        {'range': [1, 3], 'color': "green"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "white", 'width': 4},
                                        'thickness': 0.75,
                                        'value': result['pps']
                                    }
                                }
                            ))
                            
                            fig.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                font={'color': "white"},
                                height=300
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)

# Base Price Calculator Page
elif selected == "💰 Base Price Calculator":
    st.markdown("### 💰 Calculate Base Stock Price")
    st.markdown("Determine initial stock prices based on player statistics")
    
    tab1, tab2 = st.tabs(["NBA Player", "Custom Stats"])
    
    with tab1:
        # Player selection
        all_players = st.session_state.simulator['sports_market'].list_players()
        selected_player = st.selectbox("Select NBA Player:", all_players[:20])  # Show first 20
        
        if st.button("Calculate Base Price", type="primary"):
            with st.spinner("Calculating..."):
                # Get player data
                player_data = st.session_state.simulator['sports_market'].get_player_data(selected_player)
                
                if player_data:
                    season_avg = player_data["season_avg_2024"]
                    
                    # Display stats
                    st.markdown("#### 📊 Season Averages")
                    stat_cols = st.columns(6)
                    stats = ["PTS", "REB", "AST", "TO", "STL+BLK", "TS%"]
                    values = [season_avg[0], season_avg[1], season_avg[2], 
                             season_avg[3], season_avg[4], season_avg[6]]
                    
                    for col, stat, val in zip(stat_cols, stats, values):
                        col.metric(stat, f"{val:.1f}")
                    
                    # Calculate base price
                    result = st.session_state.simulator['base_price_algo'].calculate_base_price(
                        player_stats=(season_avg[0], season_avg[1], season_avg[2],
                                     season_avg[3], season_avg[4], season_avg[6]),
                        is_rookie=False
                    )
                    
                    # Display result
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1,2,1])
                    
                    with col2:
                        st.markdown(
                            f"""
                            <div style='text-align: center; background: rgba(255,255,255,0.1); 
                                        padding: 30px; border-radius: 15px; border: 2px solid #00D9FF;'>
                                <h1 style='color: #00D9FF; margin: 0;'>${result['base_price']:.2f}</h1>
                                <p style='color: white; font-size: 1.2em; margin: 10px 0 0 0;'>Base Stock Price</p>
                                <p style='color: #aaa; font-size: 0.9em;'>PRS Score: {result['prs']:.3f}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
    
    with tab2:
        st.markdown("#### Enter Custom Stats")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pts = st.number_input("Points per game:", value=20.0, min_value=0.0)
            reb = st.number_input("Rebounds per game:", value=5.0, min_value=0.0)
            ast = st.number_input("Assists per game:", value=5.0, min_value=0.0)
        
        with col2:
            to = st.number_input("Turnovers per game:", value=2.0, min_value=0.0)
            stocks = st.number_input("Steals + Blocks per game:", value=1.5, min_value=0.0)
            ts_pct = st.number_input("True Shooting %:", value=0.55, min_value=0.0, max_value=1.0)
        
        if st.button("Calculate Custom Price", type="primary"):
            result = st.session_state.simulator['base_price_algo'].calculate_base_price(
                player_stats=(pts, reb, ast, to, stocks, ts_pct),
                is_rookie=False
            )
            
            st.markdown(
                f"""
                <div style='text-align: center; background: rgba(255,255,255,0.1); 
                            padding: 30px; border-radius: 15px; border: 2px solid #00D9FF;'>
                    <h1 style='color: #00D9FF; margin: 0;'>${result['base_price']:.2f}</h1>
                    <p style='color: white; font-size: 1.2em; margin: 10px 0 0 0;'>Base Stock Price</p>
                    <p style='color: #aaa; font-size: 0.9em;'>PRS Score: {result['prs']:.3f}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Market Analysis Page
elif selected == "📊 Market Analysis":
    st.markdown("### 📊 Advanced Market Analytics")
    
    # Player comparison
    st.markdown("#### 🔍 Compare Players")
    
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("Player 1:", ["LeBron James", "Stephen Curry", "Kevin Durant"])
    with col2:
        player2 = st.selectbox("Player 2:", ["Giannis Antetokounmpo", "Nikola Jokic", "Luka Doncic"])
    
    # Create comparison chart
    categories = ['Points', 'Rebounds', 'Assists', 'Efficiency', 'Defense']
    
    fig = go.Figure()
    
    # Sample data (in real app, fetch from your data)
    fig.add_trace(go.Scatterpolar(
        r=[90, 70, 85, 88, 75],
        theta=categories,
        fill='toself',
        name=player1,
        line_color='#00D9FF'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=[85, 95, 78, 92, 88],
        theta=categories,
        fill='toself',
        name=player2,
        line_color='#FF6B6B'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.2)',
                tickfont=dict(color='white')
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.2)',
                tickfont=dict(color='white')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Live Demo Page
elif selected == "🎮 Live Demo":
    st.markdown("### 🎮 Live Market Demo")
    
    if st.button("🚀 Run Random Demo", type="primary"):
        with st.spinner("Running demo simulation..."):
            # Random player selection
            demo_players = ["LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo"]
            player = random.choice(demo_players)
            
            # Random opponent (not player's team)
            all_teams = ["Lakers", "Warriors", "Celtics", "Heat", "Nuggets", "Bucks"]
            player_team = player_team_mapping.get(player, {}).get("team")
            opponent_teams = [t for t in all_teams if t != player_team]
            opponent = random.choice(opponent_teams)
            
            # Random date
            start_date = datetime(2023, 11, 1)
            end_date = datetime(2024, 3, 1)
            random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            
            st.info(f"🏀 Simulating: **{player}** vs **{opponent}** on **{random_date.strftime('%Y-%m-%d')}**")
            
            # Get player data
            player_data = st.session_state.simulator['sports_market'].get_player_data(player)
            if player_data:
                season_avg = player_data["season_avg_2024"]
                base_result = st.session_state.simulator['base_price_algo'].calculate_base_price(
                    player_stats=(season_avg[0], season_avg[1], season_avg[2],
                                 season_avg[3], season_avg[4], season_avg[6]),
                    is_rookie=False
                )
                
                st.metric("Base Price", f"${base_result['base_price']:.2f}")
                
                # Get projection
                mc_projection = st.session_state.simulator['data_bridge'].get_monte_carlo_projection(
                    player, opponent, random_date.strftime("%Y-%m-%d"), n_simulations=5000
                )
                
                if mc_projection:
                    # Simulate performance
                    performance_mult = random.uniform(0.7, 1.3)
                    actual_stats = (
                        int(mc_projection['PTS'] * performance_mult),
                        int(mc_projection['REB'] * random.uniform(0.8, 1.2)),
                        int(mc_projection['AST'] * random.uniform(0.8, 1.2)),
                        mc_projection['TO'],
                        mc_projection['STOCKS'],
                        mc_projection['3PM'],
                        mc_projection['TS%']
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📊 Projected**")
                        st.write(f"PTS: {mc_projection['PTS']:.1f}")
                        st.write(f"REB: {mc_projection['REB']:.1f}")
                        st.write(f"AST: {mc_projection['AST']:.1f}")
                    
                    with col2:
                        st.markdown("**🎯 Actual**")
                        st.write(f"PTS: {actual_stats[0]}")
                        st.write(f"REB: {actual_stats[1]}")
                        st.write(f"AST: {actual_stats[2]}")
                    
                    # Calculate price change
                    result = st.session_state.simulator['intragame_algo'].simulate_intragame_real(
                        player, actual_stats, opponent,
                        random_date.strftime("%Y-%m-%d"), base_result['base_price']
                    )
                    
                    with col3:
                        st.markdown("**💰 Result**")
                        if result['price_change_pct'] > 0:
                            st.success(f"📈 +{result['price_change_pct']:.1f}%")
                        else:
                            st.error(f"📉 {result['price_change_pct']:.1f}%")
                        st.write(f"New: ${result['new_price']:.2f}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; opacity: 0.7;'>
        <p>NBA Sports Market System • Real-time Monte Carlo Simulations • Advanced Market Mechanics</p>
    </div>
    """,
    unsafe_allow_html=True
)
