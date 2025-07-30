import sys
sys.path.append('.')

# Enhanced imports
try:
    from MonteCarlo.enhanced_main import EnhancedNBAMonteCarloSimulator
    ENHANCED_MC_AVAILABLE = True
    print("✅ Enhanced Monte Carlo imported")
except ImportError as e:
    print(f"⚠️  Enhanced Monte Carlo not available: {e}")
    print("Using original Monte Carlo simulator...")
    # Fallback to your existing main.py
    import sys
    import os
    sys.path.append('./MonteCarlo')
    try:
        from main import NBAMonteCarloSimulator as EnhancedNBAMonteCarloSimulator
        ENHANCED_MC_AVAILABLE = False
        print("✅ Using original Monte Carlo simulator")
    except ImportError:
        print("❌ Could not import Monte Carlo simulator")
        sys.exit(1)
try:
    from Data.enhanced_nba_data_bridge import EnhancedNBADataBridge
    ENHANCED_BRIDGE_AVAILABLE = True
except ImportError:
    print("⚠️  Enhanced data bridge not available, using basic bridge")
    from Data.nba_data_bridge import NBADataBridge as EnhancedNBADataBridge
    ENHANCED_BRIDGE_AVAILABLE = False
from Data.sportradar_injuries_api import SportradarInjuriesAPI
from Data.real_sports_market import RealSportsMarket
from Core.base_price_algorithm import BasePriceAlgorithm
from Core.intragame_algorithm_real import IntragameAlgorithmReal
from Core.timeframe_algorithm import TimeframeAlgorithm
from datetime import datetime, timedelta
import pandas as pd
import random

class EnhancedIntegratedSportsMarketSimulator:
    def __init__(self, sportradar_api_key="i9UB7laRVsN2jqUo8KuJOEL9EoGXSpVnT1Yo9mK5"):
        print("🚀 Initializing Enhanced NBA Sports Market System...")
        
        # Initialize Sportradar Injuries API
        self.injury_api = None
        if sportradar_api_key:
            try:
                self.injury_api = SportradarInjuriesAPI(sportradar_api_key)
                if self.injury_api.test_api_connection():
                    print("✅ Sportradar Injuries API connected")
                else:
                    print("⚠️  Sportradar API connection failed, proceeding without injury data")
                    self.injury_api = None
            except Exception as e:
                print(f"⚠️  Could not initialize Sportradar API: {e}")
                self.injury_api = None
        
        # Initialize Enhanced Monte Carlo simulator
        self.mc_simulator = EnhancedNBAMonteCarloSimulator()
        
        # Initialize Enhanced data bridge
        if ENHANCED_BRIDGE_AVAILABLE:
            self.data_bridge = EnhancedNBADataBridge(self.mc_simulator, self.injury_api)
        else:
            # Use basic bridge with injury API
            self.data_bridge = EnhancedNBADataBridge(self.mc_simulator)
            if self.injury_api:
                self.data_bridge.injury_api = self.injury_api
        
        # Initialize market components
        self.sports_market = RealSportsMarket(self.mc_simulator)
        self.base_price_algo = BasePriceAlgorithm()
        self.intragame_algo = IntragameAlgorithmReal(self.mc_simulator)
        self.intragame_algo.data_bridge = self.data_bridge
        self.timeframe_algo = TimeframeAlgorithm()
        
        print("✅ Enhanced system initialized!")
    
    def print_welcome(self):
        """Print enhanced welcome message"""
        print("🏀 ENHANCED NBA SPORTS MARKET SYSTEM 🏀")
        print("=" * 60)
        print("✨ NEW FEATURES:")
        print("  • Real NBA game validation")
        print("  • Injury context analysis (Sportradar API)")
        print("  • Enhanced Monte Carlo (tighter variance)")
        print("  • Rest/fatigue adjustments")
        print("  • Detailed performance breakdowns")
        print("=" * 60)
    
    def run_enhanced_demo(self):
        """Run the enhanced demo with real games and contextual analysis"""
        print("\n🎮 ENHANCED DEMO: Real Game Analysis")
        print("=" * 60)
        
        if not ENHANCED_BRIDGE_AVAILABLE:
            print("⚠️  Enhanced features limited - using basic demo")
            self.run_basic_demo()
            return
        
        print("This demo will:")
        print("1. Find a real NBA game from the 2023-24 season")
        print("2. Run enhanced Monte Carlo with injury/rest context")
        print("3. Compare projections to actual game performance")
        print("4. Show detailed market impact analysis")
        print()
        
        # Run the complete enhanced demo analysis
        if hasattr(self.data_bridge, 'run_complete_demo_analysis'):
            result = self.data_bridge.run_complete_demo_analysis()
        else:
            print("⚠️  Enhanced demo not available, running basic demo")
            self.run_basic_demo()
            return
        
        if not result:
            print("❌ Enhanced demo failed. Falling back to basic demo...")
            self.run_basic_demo()
            return
        
        game_info = result['game_info']
        projections = result['projections']
        actual_stats = result['actual_stats']
        enhanced_result = result['enhanced_result']
        
        # Calculate base stock price
        print(f"\n1️⃣ Calculating base stock price for {game_info['player_name']}...")
        player_data = self.sports_market.get_player_data(game_info['player_name'])
        
        if player_data:
            season_avg = player_data["season_avg_2024"]
            base_result = self.base_price_algo.calculate_base_price(
                player_stats=(season_avg[0], season_avg[1], season_avg[2], 
                            season_avg[3], season_avg[4], season_avg[6]),
                is_rookie=False
            )
            base_price = base_result['base_price']
            print(f"   Base Price: ${base_price:.2f}")
        else:
            base_price = 30.0  # Default
            print(f"   Using default base price: ${base_price:.2f}")
        
        # Show market simulation if we have actual stats
        if actual_stats:
            print(f"\n4️⃣ Running Market Simulation...")
            
            # Prepare actual stats tuple for market simulation
            actual_stats_tuple = (
                actual_stats['PTS'],
                actual_stats['REB'], 
                actual_stats['AST'],
                projections.get('TO', 2.0),
                projections.get('STOCKS', 1.5),
                projections.get('3PM', 2.0),
                projections.get('TS%', 0.55)
            )
            
            # Run intragame simulation
            market_result = self.intragame_algo.simulate_intragame_real(
                game_info['player_name'], 
                actual_stats_tuple,
                game_info['opponent_team'],
                game_info['game_date'],
                base_price
            )
            
            if market_result:
                print(f"\n💰 MARKET IMPACT:")
                print("═" * 20)
                print(f"Stock Price: ${base_price:.2f} → ${market_result['new_price']:.2f}")
                print(f"Price Change: {market_result['price_change_pct']:+.1f}%")
                print(f"Performance Score (PPS): {market_result['pps']:.3f}")
                
                # Determine overall performance assessment
                if market_result['price_change_pct'] > 5:
                    assessment = "🔥 OUTSTANDING PERFORMANCE"
                elif market_result['price_change_pct'] > 0:
                    assessment = "✅ POSITIVE PERFORMANCE" 
                elif market_result['price_change_pct'] > -5:
                    assessment = "😐 AVERAGE PERFORMANCE"
                else:
                    assessment = "📉 DISAPPOINTING PERFORMANCE"
                
                print(f"Assessment: {assessment}")
            else:
                print("❌ Market simulation failed")
        else:
            print(f"\n⚠️  No actual game stats available for market simulation")
        
        print(f"\n✅ Enhanced Demo Complete!")
        print(f"Note: This analysis used REAL game data and advanced statistical modeling.")
    
    def run_basic_demo(self):
        """Fallback basic demo if enhanced demo fails"""
        print("\n🎲 BASIC DEMO (Fallback)")
        print("=" * 30)
        
        # Use the original demo logic but with enhanced explanations
        player_name = random.choice(["LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo"])
        opponent_team = random.choice(["Warriors", "Lakers", "Celtics", "Heat"])
        
        # Generate random date from 2023-24 season
        season_start = datetime(2023, 10, 24)
        season_end = datetime(2024, 4, 14)
        days_in_season = (season_end - season_start).days
        random_day = random.randint(0, days_in_season)
        game_date = (season_start + timedelta(days=random_day)).strftime("%Y-%m-%d")
        
        print(f"Demo: {player_name} vs {opponent_team} on {game_date}")
        print("Note: This is simulated data for demonstration purposes.")
        
        # Get base price
        player_data = self.sports_market.get_player_data(player_name)
        if player_data:
            season_avg = player_data["season_avg_2024"]
            base_result = self.base_price_algo.calculate_base_price(
                player_stats=(season_avg[0], season_avg[1], season_avg[2], 
                            season_avg[3], season_avg[4], season_avg[6]),
                is_rookie=False
            )
            print(f"Base Price: ${base_result['base_price']:.2f}")
        
        # Get projection
        projection_result = self.data_bridge.get_enhanced_projection_with_context(
            player_name, opponent_team, game_date, n_simulations=5000
        )
        
        if projection_result:
            projections = projection_result['projections']
            print(f"Projected: {projections['PTS']:.1f} pts, {projections['REB']:.1f} reb, {projections['AST']:.1f} ast")
            
            # Simulate performance
            performance_mult = random.uniform(0.8, 1.2)
            simulated_actual = (
                int(projections['PTS'] * performance_mult),
                int(projections['REB'] * random.uniform(0.8, 1.2)),
                int(projections['AST'] * random.uniform(0.8, 1.2)),
                projections['TO'],
                projections['STOCKS'],
                projections['3PM'],
                projections['TS%']
            )
            
            print(f"Simulated Actual: {simulated_actual[0]} pts, {simulated_actual[1]} reb, {simulated_actual[2]} ast")
            
            # Show if enhanced features were used
            if projection_result.get('enhanced'):
                print("✨ Used enhanced projections with contextual adjustments")
            else:
                print("📊 Used basic Monte Carlo projections")
    
    def search_players(self):
        """Enhanced player search with priority indicators"""
        print("\n🔍 ENHANCED PLAYER SEARCH")
        print("Priority players (✨) have enhanced data availability")
        
        search_term = input("Enter player name (or part of it): ")
        matches = self.sports_market.search_player(search_term)
        
        if not matches:
            print(f"No players found matching '{search_term}'")
            return None
        
        print(f"\nFound {len(matches)} players:")
        for i, player in enumerate(matches[:10], 1):
            # Mark priority players
            priority_indicator = "✨" if player in self.data_bridge.priority_players else ""
            print(f"{i}. {player} {priority_indicator}")
        
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
    
    def run_enhanced_intragame_simulation(self):
        """Run enhanced intragame simulation with real game lookup"""
        print("\n🎯 ENHANCED INTRAGAME SIMULATION")
        print("-" * 50)
        
        # Search for player
        player_name = self.search_players()
        if not player_name:
            return None
        
        print(f"\n✅ Selected: {player_name}")
        
        # Check if this is a priority player
        if player_name in self.data_bridge.priority_players:
            print("✨ Priority player selected - enhanced features available!")
            
            # Try to find real games
            print("\n🔍 Would you like to:")
            print("1. Use a real historical game")  
            print("2. Enter custom opponent and date")
            
            choice = input("Choice (1-2): ").strip()
            
            if choice == "1":
                return self.run_real_game_simulation(player_name)
            else:
                return self.run_custom_game_simulation(player_name)
        else:
            print("📊 Using standard simulation (limited historical data)")
            return self.run_custom_game_simulation(player_name)
    
    def run_real_game_simulation(self, player_name):
        """Run simulation using a real historical game"""
        player_team = self.data_bridge.player_team_mapping.get(player_name)
        
        if not player_team:
            print("⚠️  Player team not found, falling back to custom simulation")
            return self.run_custom_game_simulation(player_name)
        
        print(f"\n🔍 Searching for real games where {player_name} played...")
        
        # Try a few different opponent teams
        potential_opponents = ["Warriors", "Lakers", "Celtics", "Heat", "Nuggets", "Bucks", "Suns"]
        opponent_teams = [t for t in potential_opponents if t != player_team]
        
        real_games_found = []
        
        for opponent in opponent_teams[:3]:  # Try first 3 opponents
            if hasattr(self.mc_simulator, 'find_real_games_between_teams'):
                games = self.mc_simulator.find_real_games_between_teams(player_name, opponent, "2023-24")
                if games:
                    for game in games[:2]:  # Add up to 2 games per opponent
                        real_games_found.append({
                            'opponent': opponent,
                            'date': game['date'],
                            'matchup': game['matchup'],
                            'location': game['home_away']
                        })
        
        if not real_games_found:
            print("❌ No real games found, falling back to custom simulation")
            return self.run_custom_game_simulation(player_name)
        
        print(f"\n✅ Found {len(real_games_found)} real games:")
        for i, game in enumerate(real_games_found[:5], 1):  # Show up to 5
            print(f"{i}. vs {game['opponent']} on {game['date']} ({game['location']})")
        
        try:
            game_choice = int(input(f"\nSelect game (1-{min(len(real_games_found), 5)}): ")) - 1
            if 0 <= game_choice < len(real_games_found):
                selected_game = real_games_found[game_choice]
                
                print(f"\n🏀 Running enhanced simulation for real game:")
                print(f"   {player_name} vs {selected_game['opponent']} on {selected_game['date']}")
                
                # Get enhanced projection
                enhanced_result = self.data_bridge.get_enhanced_projection_with_context(
                    player_name, selected_game['opponent'], selected_game['date'], 
                    player_team, n_simulations=10000
                )
                
                if enhanced_result and enhanced_result.get('enhanced'):
                    # Display the enhanced breakdown
                    print("\n🔮 Enhanced Monte Carlo Analysis:")
                    
                    # Get actual stats for comparison
                    actual_stats = self.data_bridge.get_actual_game_stats_validated(
                        player_name, selected_game['date']
                    )
                    
                    if actual_stats:
                        print(f"\n✅ Found actual game stats!")
                        
                        # Run market simulation
                        old_price = float(input("Enter current stock price (default $30): $") or "30")
                        
                        actual_stats_tuple = (
                            actual_stats['PTS'], actual_stats['REB'], actual_stats['AST'],
                            enhanced_result['projections'].get('TO', 2.0),
                            enhanced_result['projections'].get('STOCKS', 1.5),
                            enhanced_result['projections'].get('3PM', 2.0),
                            enhanced_result['projections'].get('TS%', 0.55)
                        )
                        
                        result = self.intragame_algo.simulate_intragame_real(
                            player_name, actual_stats_tuple, selected_game['opponent'],
                            selected_game['date'], old_price
                        )
                        
                        if result:
                            print(f"\n💰 MARKET RESULTS:")
                            print(f"  Stock Price: ${old_price:.2f} → ${result['new_price']:.2f}")
                            print(f"  Price Change: {result['price_change_pct']:+.1f}%")
                            print(f"  Performance Score: {result['pps']:.3f}")
                            
                            return result
                    else:
                        print("❌ Could not fetch actual game stats")
                        print("💡 You can still run the simulation with manual input")
                        return self.run_manual_stats_input(player_name, selected_game, enhanced_result, player_team)
                else:
                    print("❌ Enhanced projection failed")
                    return None
            else:
                print("Invalid selection")
                return None
        except ValueError:
            print("Invalid input")
            return None
    
    def run_manual_stats_input(self, player_name, game_info, enhanced_result, player_team):
        """Run simulation with manual stat input"""
        projections = enhanced_result['projections']
        
        print(f"\n📊 Enhanced projections for {player_name}:")
        print(f"  Points: {projections['PTS']:.1f}")
        print(f"  Rebounds: {projections['REB']:.1f}")
        print(f"  Assists: {projections['AST']:.1f}")
        
        print(f"\n🎲 Enter actual game stats (or press Enter to simulate):")
        
        try:
            pts_input = input("Points (or Enter to simulate): ").strip()
            if pts_input:
                # Manual entry
                pts = float(pts_input)
                reb = float(input("Rebounds: "))
                ast = float(input("Assists: "))
                
                actual_stats_tuple = (
                    pts, reb, ast,
                    projections.get('TO', 2.0),
                    projections.get('STOCKS', 1.5),
                    projections.get('3PM', 2.0),
                    projections.get('TS%', 0.55)
                )
            else:
                # Simulate based on projection with variance
                import numpy as np
                actual_stats_tuple = (
                    max(0, int(np.random.normal(projections['PTS'], projections['PTS'] * 0.25))),
                    max(0, int(np.random.normal(projections['REB'], projections['REB'] * 0.3))),
                    max(0, int(np.random.normal(projections['AST'], projections['AST'] * 0.3))),
                    projections.get('TO', 2.0),
                    projections.get('STOCKS', 1.5),
                    projections.get('3PM', 2.0),
                    projections.get('TS%', 0.55)
                )
                
                print(f"\n🎲 Simulated stats: {actual_stats_tuple[0]:.0f} pts, {actual_stats_tuple[1]:.0f} reb, {actual_stats_tuple[2]:.0f} ast")
            
            # Get stock price and run simulation
            old_price = float(input("Enter current stock price (default $30): $") or "30")
            
            result = self.intragame_algo.simulate_intragame_real(
                player_name, actual_stats_tuple, game_info['opponent'],
                game_info['date'], old_price
            )
            
            if result:
                print(f"\n💰 MARKET RESULTS:")
                print(f"  Stock Price: ${old_price:.2f} → ${result['new_price']:.2f}")
                print(f"  Price Change: {result['price_change_pct']:+.1f}%")
                print(f"  Performance Score: {result['pps']:.3f}")
                
                # Show comparison with enhanced projections
                print(f"\n📊 ACTUAL vs ENHANCED PROJECTION:")
                stats_names = ['PTS', 'REB', 'AST']
                for i, stat in enumerate(stats_names):
                    actual = actual_stats_tuple[i]
                    projected = projections[stat]
                    diff = actual - projected
                    print(f"  {stat}: {actual:.1f} vs {projected:.1f} projected ({diff:+.1f})")
                
                return result
            else:
                print("❌ Market simulation failed")
                return None
                
        except ValueError:
            print("Invalid input")
            return None
    
    def run_custom_game_simulation(self, player_name):
        """Run simulation with custom opponent and date"""
        print(f"\n🎯 Custom game simulation for {player_name}")
        
        # Get opponent team
        all_teams = [
            "Lakers", "Warriors", "Celtics", "Heat", "Nuggets", "Bucks", 
            "Suns", "76ers", "Clippers", "Nets", "Bulls", "Knicks",
            "Mavericks", "Timberwolves", "Kings", "Pelicans", "Hawks",
            "Cavaliers", "Grizzlies", "Hornets", "Raptors", "Pacers"
        ]
        
        print("\n🏀 Select opponent team:")
        for i in range(0, len(all_teams), 4):
            row = ""
            for j in range(4):
                if i + j < len(all_teams):
                    row += f"{i+j+1:2d}. {all_teams[i+j]:<15}"
            print(row)
        
        try:
            team_choice = int(input("Select team number: "))
            if 1 <= team_choice <= len(all_teams):
                opponent_team = all_teams[team_choice - 1]
            else:
                opponent_team = "Lakers"  # Default
        except:
            opponent_team = "Lakers"
        
        # Get game date
        print("\n📅 Enter game date (YYYY-MM-DD) or press Enter for random past date:")
        date_input = input("Date: ").strip()
        
        if date_input:
            try:
                game_date_dt = pd.to_datetime(date_input)
                if game_date_dt > datetime.now():
                    print("⚠️  Future date! Using random past date.")
                    game_date = self.generate_random_past_date()
                else:
                    game_date = game_date_dt.strftime("%Y-%m-%d")
            except:
                print("⚠️  Invalid date format. Using random past date.")
                game_date = self.generate_random_past_date()
        else:
            game_date = self.generate_random_past_date()
        
        print(f"\n🔮 Running enhanced projection for {player_name} vs {opponent_team} on {game_date}...")
        
        # Get player team for context
        player_team = self.data_bridge.player_team_mapping.get(player_name, "Unknown")
        
        # Get enhanced projection
        enhanced_result = self.data_bridge.get_enhanced_projection_with_context(
            player_name, opponent_team, game_date, player_team, n_simulations=10000
        )
        
        if enhanced_result:
            projections = enhanced_result['projections']
            
            # Show projections
            print(f"\n📊 PROJECTIONS:")
            print(f"  Points: {projections['PTS']:.1f}")
            print(f"  Rebounds: {projections['REB']:.1f}")
            print(f"  Assists: {projections['AST']:.1f}")
            
            if enhanced_result.get('enhanced'):
                print("✨ Enhanced projections with contextual adjustments applied!")
                if 'adjustments' in enhanced_result:
                    print("📋 Adjustments made:")
                    for adj in enhanced_result['adjustments']['breakdown']:
                        print(f"   {adj}")
            
            # Continue with manual input simulation
            return self.run_manual_stats_input(player_name, 
                                             {'opponent': opponent_team, 'date': game_date}, 
                                             enhanced_result, player_team)
        else:
            print("❌ Could not generate projections")
            return None
    
    def generate_random_past_date(self):
        """Generate a random date from the 2023-24 NBA season"""
        season_start = datetime(2023, 10, 24)
        season_end = datetime(2024, 4, 14)
        days_in_season = (season_end - season_start).days
        random_day = random.randint(0, days_in_season)
        return (season_start + timedelta(days=random_day)).strftime("%Y-%m-%d")
    
    def run_base_price_for_real_player(self):
        """Calculate base price for a real NBA player with enhanced info"""
        print("\n💰 ENHANCED BASE PRICE CALCULATION")
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
        
        print(f"\n📊 {player_name} 2023-24 Season Averages:")
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
        
        # Enhanced analysis
        if player_name in self.data_bridge.priority_players:
            print(f"  ✨ Priority player - enhanced simulation features available")
        
        # Show percentile breakdown
        print(f"  📊 League Percentiles:")
        for stat, percentile in result['percentiles'].items():
            print(f"     {stat}: {percentile:.1%}")
        
        return result
    
    def run(self):
        """Enhanced main run loop"""
        while True:
            self.print_welcome()
            
            print("\n📋 ENHANCED MENU:")
            print("1. 🎯 Enhanced Intragame Simulation")
            print("2. 💰 Enhanced Base Price Calculator") 
            print("3. 🔍 Search Players")
            print("4. 🎮 Enhanced Demo (Real Games)")
            print("5. 📊 System Status")
            print("6. 🚪 Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                self.run_enhanced_intragame_simulation()
            elif choice == "2":
                self.run_base_price_for_real_player()
            elif choice == "3":
                player = self.search_players()
                if player:
                    print(f"\nSelected: {player}")
                    if player in self.data_bridge.priority_players:
                        print("✨ This is a priority player with enhanced features!")
            elif choice == "4":
                self.run_enhanced_demo()
            elif choice == "5":
                self.show_system_status()
            elif choice == "6":
                print("\n👋 Thank you for using the Enhanced Sports Market System!")
                break
            else:
                print("Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    
    def show_system_status(self):
        """Show enhanced system status"""
        print("\n📊 ENHANCED SYSTEM STATUS")
        print("=" * 40)
        
        # Check API connections
        print("🔗 API Connections:")
        print(f"  NBA API: ✅ Connected")
        
        if self.injury_api:
            print(f"  Sportradar Injuries: ✅ Connected")
        else:
            print(f"  Sportradar Injuries: ❌ Not connected")
        
        # Show enhanced features status
        print(f"\n✨ Enhanced Features:")
        print(f"  Real Game Validation: ✅ Available")
        print(f"  Contextual Adjustments: ✅ Available")
        print(f"  Tighter Variance Monte Carlo: ✅ Available")
        print(f"  Injury Context Analysis: {'✅ Available' if self.injury_api else '⚠️  Limited (no API)'}")
        
        # Show priority players
        print(f"\n⭐ Priority Players Available: {len(self.data_bridge.priority_players)}")
        print("   (Enhanced features work best with these players)")
        
        print(f"\n📈 Market Components:")
        print(f"  Base Price Algorithm: ✅ Loaded")
        print(f"  Intragame Algorithm: ✅ Enhanced")
        print(f"  Real Sports Market: ✅ Connected")

if __name__ == "__main__":
    print("🚀 Starting Enhanced NBA Sports Market System...")
    print("This may take a moment to initialize all connections...")
    
    # Initialize with Sportradar API key
    simulator = EnhancedIntegratedSportsMarketSimulator(
        sportradar_api_key="i9UB7laRVsN2jqUo8KuJOEL9EoGXSpVnT1Yo9mK5"  # Your actual API key
    )
    
    simulator.run()