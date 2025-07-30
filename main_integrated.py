#!/usr/bin/env python3
"""
Integrated NBA Monte Carlo + Sports Market System
Real NBA players with advanced projections and market mechanics
"""

import sys
sys.path.append('.')  # Ensure imports work

# Updated imports to match your folder structure
from MonteCarlo.main import NBAMonteCarloSimulator  # Changed from monte_carlo to MonteCarlo
from Data.real_sports_market import RealSportsMarket  # Changed from data to Data
from Core.base_price_algorithm import BasePriceAlgorithm  # Changed from core to Core
from Core.intragame_algorithm_real import IntragameAlgorithmReal
from Core.timeframe_algorithm import TimeframeAlgorithm
from Data.nba_data_bridge import NBADataBridge
from datetime import datetime, timedelta
import pandas as pd
import random

class IntegratedSportsMarketSimulator:
    def __init__(self):
        # Initialize Monte Carlo simulator
        self.mc_simulator = NBAMonteCarloSimulator()
        
        # Initialize data bridge
        self.data_bridge = NBADataBridge(self.mc_simulator)
        
        # Initialize market components with real data
        self.sports_market = RealSportsMarket(self.mc_simulator)
        self.base_price_algo = BasePriceAlgorithm()
        self.intragame_algo = IntragameAlgorithmReal(self.mc_simulator)
        self.intragame_algo.data_bridge = self.data_bridge
        self.timeframe_algo = TimeframeAlgorithm()
    
    def print_welcome(self):
        """Print welcome message"""
        print("🏀 NBA INTEGRATED SPORTS MARKET SYSTEM 🏀")
        print("=" * 50)
        print("Real NBA Players + Monte Carlo Projections + Market Mechanics")
        print("=" * 50)
    
    def search_players(self):
        """Interactive player search"""
        print("\n🔍 PLAYER SEARCH")
        search_term = input("Enter player name (or part of it): ")
        
        matches = self.sports_market.search_player(search_term)
        
        if not matches:
            print(f"No players found matching '{search_term}'")
            return None
        
        print(f"\nFound {len(matches)} players:")
        for i, player in enumerate(matches[:10], 1):  # Show max 10
            print(f"{i}. {player}")
        
        if len(matches) > 10:
            print(f"... and {len(matches) - 10} more")
        
        if len(matches) == 1:
            return matches[0]
        
        try:
            choice = int(input("\nSelect player number (or 0 to cancel): "))
            if 1 <= choice <= min(len(matches), 10):
                return matches[choice - 1]
        except:
            pass
        
        return None
    
    def run_intragame_simulation_real(self):
        """Run intragame simulation with real NBA player"""
        print("\n🎯 REAL NBA INTRAGAME SIMULATION")
        print("-" * 50)
        
        # Search for player
        player_name = self.search_players()
        if not player_name:
            return None
        
        print(f"\n✅ Selected: {player_name}")
        
        # Player-team mapping (2023-24 season)
        player_teams = {
            "LeBron James": "Lakers",
            "Stephen Curry": "Warriors",
            "Kevin Durant": "Suns",
            "Giannis Antetokounmpo": "Bucks",
            "Nikola Jokic": "Nuggets",
            "Luka Doncic": "Mavericks",
            "Joel Embiid": "76ers",
            "Jayson Tatum": "Celtics",
            "Damian Lillard": "Bucks",
            "Anthony Davis": "Lakers",
            "Jimmy Butler": "Heat",
            "Paul George": "Clippers",
            "Kawhi Leonard": "Clippers",
            "Devin Booker": "Suns",
            "Donovan Mitchell": "Cavaliers",
            "Trae Young": "Hawks",
            "Ja Morant": "Grizzlies",
            "Zion Williamson": "Pelicans",
            "Karl-Anthony Towns": "Timberwolves",
            "Bradley Beal": "Suns",
            "Kyrie Irving": "Mavericks",
            "James Harden": "Clippers",
            "Russell Westbrook": "Clippers",
            "Chris Paul": "Warriors",
            "Draymond Green": "Warriors",
            "Klay Thompson": "Warriors",
            "Anthony Edwards": "Timberwolves",
            "LaMelo Ball": "Hornets",
            "Tyrese Haliburton": "Pacers",
            "Paolo Banchero": "Magic",
            "Cade Cunningham": "Pistons",
            "Scottie Barnes": "Raptors",
            "Evan Mobley": "Cavaliers",
            "Franz Wagner": "Magic",
            "Alperen Sengun": "Rockets",
            "Jalen Green": "Rockets",
            "Josh Giddey": "Thunder",
            "Anfernee Simons": "Trail Blazers",
            "Tyler Herro": "Heat",
            "Bam Adebayo": "Heat",
            "Mikal Bridges": "Nets",
            "OG Anunoby": "Knicks",
            "Pascal Siakam": "Raptors",
            "Fred VanVleet": "Rockets",
            "DeMar DeRozan": "Bulls",
            "Zach LaVine": "Bulls",
            "Nikola Vucevic": "Bulls",
            "Domantas Sabonis": "Kings",
            "De'Aaron Fox": "Kings",
            "CJ McCollum": "Pelicans",
            "Jaylen Brown": "Celtics"
        }
        
        player_team = player_teams.get(player_name, None)
        
        # Get opponent team
        print("\n🏀 Select opponent team:")
        all_teams = [
            "Lakers", "Warriors", "Celtics", "Heat", "Nuggets", "Bucks", 
            "Suns", "76ers", "Clippers", "Nets", "Bulls", "Knicks",
            "Mavericks", "Timberwolves", "Kings", "Pelicans", "Hawks",
            "Cavaliers", "Grizzlies", "Hornets", "Raptors", "Pacers",
            "Magic", "Pistons", "Rockets", "Spurs", "Jazz", "Thunder",
            "Trail Blazers", "Wizards"
        ]
        
        # Filter out player's own team if known
        if player_team and player_team in all_teams:
            teams = [t for t in all_teams if t != player_team]
            print(f"(Excluding {player_team} - {player_name}'s team)")
        else:
            teams = all_teams
            if player_team:
                print(f"(Note: {player_name} plays for {player_team})")
        
        # Display teams in columns for better readability
        for i in range(0, len(teams), 3):
            row = ""
            for j in range(3):
                if i + j < len(teams):
                    row += f"{i+j+1:2d}. {teams[i+j]:<20}"
            print(row)
        
        try:
            team_choice = int(input("\nSelect team number: "))
            if 1 <= team_choice <= len(teams):
                opponent_team = teams[team_choice - 1]
            else:
                opponent_team = teams[0]  # Default to first available
        except:
            opponent_team = teams[0]
        
        # Get game date - make sure it's in the past
        print("\n📅 Enter game date (YYYY-MM-DD) or press Enter for a random 2023-24 season date:")
        print("   (Season runs from Oct 2023 to Apr 2024)")
        date_input = input("Date: ").strip()
        
        if date_input:
            try:
                game_date_dt = pd.to_datetime(date_input)
                
                # Validate it's not in the future
                if game_date_dt > datetime.now():
                    print("⚠️  Future date detected! Using a random past date instead.")
                    # Generate random date from 2023-24 season
                    import random
                    season_start = datetime(2023, 10, 24)
                    season_end = datetime(2024, 4, 14)
                    days_in_season = (season_end - season_start).days
                    random_day = random.randint(0, days_in_season)
                    game_date = (season_start + timedelta(days=random_day)).strftime("%Y-%m-%d")
                else:
                    game_date = game_date_dt.strftime("%Y-%m-%d")
            except:
                print("⚠️  Invalid date format. Using a random past date.")
                # Generate random date from 2023-24 season
                import random
                season_start = datetime(2023, 10, 24)
                season_end = datetime(2024, 4, 14)
                days_in_season = (season_end - season_start).days
                random_day = random.randint(0, days_in_season)
                game_date = (season_start + timedelta(days=random_day)).strftime("%Y-%m-%d")
        else:
            # Generate random date from 2023-24 season
            import random
            season_start = datetime(2023, 10, 24)
            season_end = datetime(2024, 4, 14)
            days_in_season = (season_end - season_start).days
            random_day = random.randint(0, days_in_season)
            game_date = (season_start + timedelta(days=random_day)).strftime("%Y-%m-%d")
        
        print(f"\n🔮 Running Monte Carlo projection for {player_name} vs {opponent_team} on {game_date}...")
        
        # Get Monte Carlo projection
        mc_projection = self.data_bridge.get_monte_carlo_projection(
            player_name, opponent_team, game_date, n_simulations=10000
        )
        
        if mc_projection:
            print("\n📊 MONTE CARLO PROJECTIONS:")
            print(f"  Points: {mc_projection['PTS']:.1f}")
            print(f"  Rebounds: {mc_projection['REB']:.1f}")
            print(f"  Assists: {mc_projection['AST']:.1f}")
            print(f"  Turnovers: {mc_projection['TO']:.1f}")
            print(f"  Stocks: {mc_projection['STOCKS']:.1f}")
            print(f"  3PM: {mc_projection['3PM']:.1f}")
            print(f"  TS%: {mc_projection['TS%']:.3f}")
        
        # Simulate actual game performance
        print("\n🎲 Enter ACTUAL game stats (or press Enter to simulate):")
        
        try:
            pts_input = input("Points (or Enter to simulate): ").strip()
            if pts_input:
                # Manual entry
                pts = float(pts_input)
                reb = float(input("Rebounds: "))
                ast = float(input("Assists: "))
                to = float(input("Turnovers: "))
                stocks = float(input("Steals + Blocks: "))
                threepm = float(input("3-Pointers Made: "))
                ts_pct = float(input("True Shooting % (0.0-1.0): "))
                
                actual_stats = (pts, reb, ast, to, stocks, threepm, ts_pct)
            else:
                # Simulate based on projection with variance
                import numpy as np
                actual_stats = (
                    max(0, int(np.random.normal(mc_projection['PTS'], mc_projection['PTS'] * 0.3))),
                    max(0, int(np.random.normal(mc_projection['REB'], mc_projection['REB'] * 0.4))),
                    max(0, int(np.random.normal(mc_projection['AST'], mc_projection['AST'] * 0.4))),
                    max(0, int(np.random.normal(mc_projection['TO'], mc_projection['TO'] * 0.5))),
                    max(0, int(np.random.normal(mc_projection['STOCKS'], mc_projection['STOCKS'] * 0.6))),
                    max(0, int(np.random.normal(mc_projection['3PM'], mc_projection['3PM'] * 0.5))),
                    max(0.2, min(1.0, np.random.normal(mc_projection['TS%'], 0.1)))
                )
                
                print(f"\n🎲 Simulated actual stats:")
                print(f"  PTS={actual_stats[0]}, REB={actual_stats[1]}, AST={actual_stats[2]}")
                print(f"  TO={actual_stats[3]}, STOCKS={actual_stats[4]}, 3PM={actual_stats[5]}, TS%={actual_stats[6]:.3f}")
        except:
            print("Invalid input, using projected stats")
            actual_stats = tuple(mc_projection.values())
        
        # Get current stock price
        old_price = float(input("\nEnter current stock price (default $25): $") or "25")
        
        # Run the integrated simulation
        result = self.intragame_algo.simulate_intragame_real(
            player_name, actual_stats, opponent_team, game_date, old_price
        )
        
        if result:
            self.display_intragame_results(result)
            
            # Show comparison with projections
            print("\n📊 ACTUAL vs PROJECTED:")
            stats_names = ['PTS', 'REB', 'AST', 'TO', 'STOCKS', '3PM', 'TS%']
            for i, stat in enumerate(stats_names):
                actual = actual_stats[i]
                projected = result['projected_stats'][i]
                diff = actual - projected
                print(f"  {stat}: Actual={actual:.1f}, Projected={projected:.1f}, Diff={diff:+.1f}")
        
        return result
    
    def display_intragame_results(self, result):
        """Display intragame simulation results"""
        print(f"\n💰 MARKET SIMULATION RESULTS:")
        print(f"  PPS (Performance Score): {result['pps']:.3f}")
        print(f"  DIS (Demand Imbalance): {result['dis']:.3f}")
        print(f"  Raw Delta: {result['raw_delta']:.3f}")
        print(f"  Dampened Delta: {result['dampened_delta']:.3f}")
        print(f"  Old Price: ${result['old_price']:.2f}")
        print(f"  New Price: ${result['new_price']:.2f}")
        print(f"  Price Change: {result['price_change_pct']:+.2f}%")
        
        if result.get('monte_carlo_used'):
            print(f"  ✅ Used Monte Carlo projections")
    
    def run_base_price_for_real_player(self):
        """Calculate base price for a real NBA player"""
        print("\n💰 BASE PRICE CALCULATION (Real NBA Player)")
        print("-" * 50)
        
        player_name = self.search_players()
        if not player_name:
            return None
        
        # Get player data
        player_data = self.sports_market.get_player_data(player_name)
        if not player_data:
            print(f"Could not fetch data for {player_name}")
            return None
        
        # Use current season averages
        season_avg = player_data["season_avg_2024"]
        
        print(f"\n📊 {player_name} Season Averages:")
        print(f"  PTS: {season_avg[0]:.1f}, REB: {season_avg[1]:.1f}, AST: {season_avg[2]:.1f}")
        print(f"  TO: {season_avg[3]:.1f}, STOCKS: {season_avg[4]:.1f}, 3PM: {season_avg[5]:.1f}, TS%: {season_avg[6]:.3f}")
        
        # Calculate base price
        result = self.base_price_algo.calculate_base_price(
            player_stats=(season_avg[0], season_avg[1], season_avg[2], 
                         season_avg[3], season_avg[4], season_avg[6]),
            is_rookie=False
        )
        
        print(f"\n📈 BASE PRICE RESULTS:")
        print(f"  Base Price: ${result['base_price']:.2f}")
        print(f"  PRS Score: {result['prs']:.3f}")
        print(f"  Z-Scores: {result['z_scores']}")
        
        return result
    
    def run_demo(self):
        """Run a demonstration of the integrated system"""
        import random
        from datetime import datetime, timedelta
        
        print("\n🎮 INTEGRATED SYSTEM DEMO")
        print("=" * 50)
        
        # Player-Team mappings (2023-24 season)
        player_team_mapping = {
            "LeBron James": "Lakers",
            "Stephen Curry": "Warriors",
            "Kevin Durant": "Suns",
            "Giannis Antetokounmpo": "Bucks",
            "Nikola Jokic": "Nuggets",
            "Luka Doncic": "Mavericks",
            "Joel Embiid": "76ers",
            "Jayson Tatum": "Celtics",
            "Damian Lillard": "Bucks",  # Traded to Bucks
            "Anthony Davis": "Lakers",
            "Jimmy Butler": "Heat",
            "Paul George": "Clippers",
            "Kawhi Leonard": "Clippers",
            "Devin Booker": "Suns",
            "Donovan Mitchell": "Cavaliers",
            "Trae Young": "Hawks",
            "Ja Morant": "Grizzlies",
            "Anthony Edwards": "Timberwolves",
            "LaMelo Ball": "Hornets",
            "Jaylen Brown": "Celtics"
        }
        
        # All NBA teams
        all_teams = [
            "Lakers", "Warriors", "Celtics", "Heat", "Nuggets", "Bucks", 
            "Suns", "76ers", "Clippers", "Nets", "Bulls", "Knicks",
            "Mavericks", "Timberwolves", "Kings", "Pelicans", "Hawks",
            "Cavaliers", "Grizzlies", "Hornets", "Raptors", "Pacers",
            "Wizards", "Magic", "Pistons", "Rockets", "Spurs", "Jazz",
            "Trail Blazers", "Thunder"
        ]
        
        # Select random player
        available_players = list(player_team_mapping.keys())
        player_name = random.choice(available_players)
        player_team = player_team_mapping[player_name]
        
        # Select opponent team (NOT the player's own team)
        opponent_teams = [team for team in all_teams if team != player_team]
        opponent_team = random.choice(opponent_teams)
        
        # Generate a PAST date from the 2023-24 season
        # NBA season runs October to April, let's use dates from that range
        season_start = datetime(2023, 10, 24)  # 2023-24 season start
        season_end = datetime(2024, 4, 14)     # Regular season end
        
        # Generate random date within the season
        days_in_season = (season_end - season_start).days
        random_day = random.randint(0, days_in_season)
        game_date = (season_start + timedelta(days=random_day)).strftime("%Y-%m-%d")
        
        print(f"Demo: {player_name} ({player_team}) vs {opponent_team} on {game_date}")
        
        # 1. Show base price
        print(f"\n1️⃣ Calculating base price for {player_name}...")
        player_data = self.sports_market.get_player_data(player_name)
        
        if player_data:
            season_avg = player_data["season_avg_2024"]
            base_result = self.base_price_algo.calculate_base_price(
                player_stats=(season_avg[0], season_avg[1], season_avg[2], 
                            season_avg[3], season_avg[4], season_avg[6]),
                is_rookie=False
            )
            print(f"   Base Price: ${base_result['base_price']:.2f}")
            base_price = base_result['base_price']
        else:
            print(f"   Could not fetch data for {player_name}")
            base_price = 25.0  # Default
        
        # 2. Show Monte Carlo projection
        print(f"\n2️⃣ Running Monte Carlo projection...")
        mc_projection = self.data_bridge.get_monte_carlo_projection(
            player_name, opponent_team, game_date, n_simulations=5000
        )
        
        if mc_projection:
            print(f"   Projected: {mc_projection['PTS']:.1f} pts, {mc_projection['REB']:.1f} reb, {mc_projection['AST']:.1f} ast")
            
            # 3. Simulate game with random performance variance
            print(f"\n3️⃣ Simulating game performance...")
            
            # Random performance multipliers (70% to 130% of projection)
            pts_mult = random.uniform(0.7, 1.3)
            reb_mult = random.uniform(0.7, 1.3)
            ast_mult = random.uniform(0.7, 1.3)
            
            actual_stats = (
                int(mc_projection['PTS'] * pts_mult),
                int(mc_projection['REB'] * reb_mult),
                int(mc_projection['AST'] * ast_mult),
                mc_projection['TO'] * random.uniform(0.8, 1.2),
                mc_projection['STOCKS'] * random.uniform(0.7, 1.3),
                mc_projection['3PM'] * random.uniform(0.6, 1.4),
                mc_projection['TS%'] * random.uniform(0.9, 1.1)
            )
            
            print(f"   Actual: {actual_stats[0]} pts, {actual_stats[1]} reb, {actual_stats[2]} ast")
            
            # Determine performance
            performance_ratio = (actual_stats[0] / mc_projection['PTS'] + 
                            actual_stats[1] / mc_projection['REB'] + 
                            actual_stats[2] / mc_projection['AST']) / 3
            
            if performance_ratio > 1.1:
                performance_desc = "Overperformed! 🔥"
            elif performance_ratio < 0.9:
                performance_desc = "Underperformed 📉"
            else:
                performance_desc = "Met expectations ✓"
            
            old_price = base_price
            result = self.intragame_algo.simulate_intragame_real(
                player_name, actual_stats, opponent_team, game_date, old_price
            )
            
            if result:
                print(f"\n4️⃣ Market Result:")
                print(f"   Stock Price: ${old_price:.2f} → ${result['new_price']:.2f} ({result['price_change_pct']:+.1f}%)")
                print(f"   Performance vs Projection: {performance_desc}")
        else:
            print("   Could not generate projection (no historical data available)")
        
        print("\n✅ Demo complete!")
        print("\nNote: This demo uses SIMULATED performance against Monte Carlo projections.")
        print("For real games, use option 1 to input actual game stats.")
    
    def run(self):
        """Main run loop"""
        while True:
            self.print_welcome()
            
            print("\n📋 MENU:")
            print("1. Run Intragame Simulation (Real NBA Player)")
            print("2. Calculate Base Price (Real NBA Player)")
            print("3. Search Players")
            print("4. Run Demo")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                self.run_intragame_simulation_real()
            elif choice == "2":
                self.run_base_price_for_real_player()
            elif choice == "3":
                player = self.search_players()
                if player:
                    print(f"\nSelected: {player}")
            elif choice == "4":
                self.run_demo()
            elif choice == "5":
                print("\n👋 Thank you for using the Integrated Sports Market System!")
                break
            elif choice == "6":
                self.data_bridge.clear_cache()
                print("✅ Cache cleared! Fresh data will be fetched.")
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("🚀 Starting Integrated NBA Sports Market System...")
    print("This may take a moment to initialize NBA data connections...")
    
    simulator = IntegratedSportsMarketSimulator()
    simulator.run()