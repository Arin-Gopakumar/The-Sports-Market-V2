# enhanced_nba_data_bridge.py
"""
Enhanced NBA Data Bridge with real game validation and contextual projections
"""

import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import random
from typing import Dict, List, Tuple, Optional

# Import the enhanced Monte Carlo simulator
try:
    from MonteCarlo.enhanced_main import EnhancedNBAMonteCarloSimulator
except ImportError:
    # Fallback to original if enhanced not available
    from MonteCarlo.main import NBAMonteCarloSimulator as EnhancedNBAMonteCarloSimulator

from Data.nba_data_bridge import NBADataBridge

class EnhancedNBADataBridge(NBADataBridge):
    """Enhanced bridge with real game validation and contextual adjustments"""
    
    def __init__(self, monte_carlo_simulator, injury_api=None):
        # Use enhanced simulator if available
        if hasattr(monte_carlo_simulator, 'run_enhanced_monte_carlo_simulation'):
            self.mc_simulator = monte_carlo_simulator
        else:
            # Wrap with enhanced capabilities
            self.mc_simulator = EnhancedNBAMonteCarloSimulator()
        
        self.injury_api = injury_api
        if injury_api:
            self.mc_simulator.injury_api = injury_api
        
        self._cache = {}
        
        # Popular NBA players with good data availability
        self.priority_players = [
            "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo",
            "Nikola Jokic", "Luka Doncic", "Joel Embiid", "Jayson Tatum",
            "Damian Lillard", "Anthony Davis", "Jimmy Butler", "Paul George",
            "Kawhi Leonard", "Devin Booker", "Donovan Mitchell", "Trae Young",
            "Ja Morant", "Anthony Edwards", "LaMelo Ball", "Jaylen Brown"
        ]
        
        # Team mappings for 2023-24 season
        self.player_team_mapping = {
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
    
    def find_real_games_for_demo(self, max_attempts=50) -> Optional[Dict]:
        """
        Find a real game for demo purposes
        Prioritizes popular players with good data availability
        """
        print("🎯 Searching for optimal demo game...")
        
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            
            # Pick a priority player
            player_name = random.choice(self.priority_players)
            player_team = self.player_team_mapping.get(player_name)
            
            if not player_team:
                continue
            
            # Pick a different opponent team
            all_teams = [
                "Lakers", "Warriors", "Celtics", "Heat", "Nuggets", "Bucks", 
                "Suns", "76ers", "Clippers", "Nets", "Bulls", "Knicks",
                "Mavericks", "Cavaliers", "Hawks", "Grizzlies", "Timberwolves",
                "Hornets", "Pacers", "Magic", "Pistons", "Rockets", "Kings"
            ]
            
            opponent_teams = [t for t in all_teams if t != player_team]
            opponent_team = random.choice(opponent_teams)
            
            # Try to find real games between these teams
            if hasattr(self.mc_simulator, 'find_real_games_between_teams'):
                real_games = self.mc_simulator.find_real_games_between_teams(
                    player_name, opponent_team, "2023-24"
                )
            else:
                # Fallback: use find_games_against_opponent from original
                from MonteCarlo.main import find_games_against_opponent
                games_df = find_games_against_opponent(player_name, opponent_team, "2023-24")
                
                if games_df is not None and len(games_df) > 0:
                    real_games = []
                    for _, game in games_df.iterrows():
                        game_info = {
                            'date': game['GAME_DATE'].strftime('%Y-%m-%d'),
                            'matchup': game['MATCHUP'],
                            'home_away': 'HOME' if 'vs.' in game['MATCHUP'] else 'AWAY'
                        }
                        real_games.append(game_info)
                else:
                    real_games = []
            
            if real_games:
                # Pick a random game from the available ones
                selected_game = random.choice(real_games)
                
                game_info = {
                    'player_name': player_name,
                    'player_team': player_team,
                    'opponent_team': opponent_team,
                    'game_date': selected_game['date'],
                    'matchup': selected_game['matchup'],
                    'location': selected_game['home_away'],
                    'attempts_needed': attempts
                }
                
                print(f"✅ Found demo game after {attempts} attempts:")
                print(f"   {player_name} ({player_team}) vs {opponent_team}")
                print(f"   Date: {selected_game['date']}")
                print(f"   Location: {selected_game['home_away']}")
                
                return game_info
        
        print(f"❌ Could not find suitable demo game after {max_attempts} attempts")
        return None
    
    def get_enhanced_projection_with_context(self, player_name, opponent_team, 
                                           game_date, player_team=None, n_simulations=10000):
        """Get enhanced projection with full contextual analysis"""
        
        # Use enhanced simulator if available
        if hasattr(self.mc_simulator, 'run_enhanced_monte_carlo_simulation'):
            simulation_results, adjustments, metadata = self.mc_simulator.run_enhanced_monte_carlo_simulation(
                player_name, opponent_team, game_date, player_team, n_simulations
            )
            
            if simulation_results is None:
                return None
            
            # Calculate percentiles
            percentiles = self.mc_simulator.calculate_enhanced_percentiles(simulation_results)
            
            # Convert to the format expected by the market system
            projections = {}
            for stat in ['PTS', 'REB', 'AST']:
                projections[stat] = percentiles[stat]['mean']
            
            # Add other required stats (using player data or defaults)
            player_data = self.get_real_player_data(player_name)
            if player_data:
                season_avg = player_data['season_avg_2024']
                projections['TO'] = season_avg[3]
                projections['STOCKS'] = season_avg[4]
                projections['3PM'] = season_avg[5]
                projections['TS%'] = season_avg[6]
            else:
                projections['TO'] = 2.0
                projections['STOCKS'] = 1.5
                projections['3PM'] = 2.0
                projections['TS%'] = 0.55
            
            # Return projections with context
            return {
                'projections': projections,
                'percentiles': percentiles,
                'adjustments': adjustments,
                'metadata': metadata,
                'enhanced': True
            }
        else:
            # Fallback to original method
            projections = self.get_monte_carlo_projection(
                player_name, opponent_team, game_date, n_simulations
            )
            
            return {
                'projections': projections,
                'enhanced': False
            } if projections else None
    
    def get_actual_game_stats_validated(self, player_name, game_date):
        """Get actual game stats with validation"""
        try:
            # Use the existing fetch method from the Monte Carlo simulator
            actual_stats = self.mc_simulator.fetch_actual_game_result(
                player_name, None, game_date
            )
            
            if actual_stats:
                print(f"✅ Found actual game stats for {player_name} on {game_date}")
                return actual_stats
            else:
                print(f"❌ No actual game stats found for {player_name} on {game_date}")
                return None
                
        except Exception as e:
            print(f"⚠️  Error fetching actual stats: {e}")
            return None
    
    def run_complete_demo_analysis(self) -> Optional[Dict]:
        """
        Run a complete demo analysis with real game, projections, and actual results
        """
        # Step 1: Find a suitable real game
        game_info = self.find_real_games_for_demo()
        if not game_info:
            return None
        
        player_name = game_info['player_name']
        player_team = game_info['player_team']
        opponent_team = game_info['opponent_team']
        game_date = game_info['game_date']
        
        print(f"\n🎮 RUNNING COMPLETE DEMO ANALYSIS")
        print("=" * 50)
        print(f"Selected Game: {player_name} ({player_team}) vs {opponent_team}")
        print(f"Date: {game_date}")
        print(f"Location: {game_info['location']}")
        
        # Step 2: Get enhanced projections
        enhanced_result = self.get_enhanced_projection_with_context(
            player_name, opponent_team, game_date, player_team, n_simulations=10000
        )
        
        if not enhanced_result:
            print("❌ Could not generate projections")
            return None
        
        projections = enhanced_result['projections']
        
        # Step 3: Get actual game stats
        actual_stats = self.get_actual_game_stats_validated(player_name, game_date)
        
        # Step 4: Display enhanced breakdown
        if enhanced_result.get('enhanced') and 'adjustments' in enhanced_result:
            self.mc_simulator.display_enhanced_breakdown(
                player_name, opponent_team, game_date,
                enhanced_result['adjustments'], 
                enhanced_result['percentiles'],
                actual_stats=[actual_stats['PTS'], actual_stats['REB'], actual_stats['AST']] if actual_stats else None
            )
        else:
            # Display basic projections
            print(f"\n🔮 MONTE CARLO PROJECTIONS:")
            print(f"  Points: {projections['PTS']:.1f}")
            print(f"  Rebounds: {projections['REB']:.1f}")
            print(f"  Assists: {projections['AST']:.1f}")
            
            if actual_stats:
                print(f"\n🏀 ACTUAL PERFORMANCE:")
                print(f"  Points: {actual_stats['PTS']}")
                print(f"  Rebounds: {actual_stats['REB']}")
                print(f"  Assists: {actual_stats['AST']}")
        
        return {
            'game_info': game_info,
            'projections': projections,
            'actual_stats': actual_stats,
            'enhanced_result': enhanced_result
        }

# Test function
def test_enhanced_bridge():
    """Test the enhanced NBA data bridge"""
    from MonteCarlo.enhanced_main import EnhancedNBAMonteCarloSimulator
    
    # Initialize components
    mc_simulator = EnhancedNBAMonteCarloSimulator()
    bridge = EnhancedNBADataBridge(mc_simulator)
    
    # Run complete demo
    result = bridge.run_complete_demo_analysis()
    
    if result:
        print("✅ Enhanced demo completed successfully!")
    else:
        print("❌ Enhanced demo failed")

if __name__ == "__main__":
    test_enhanced_bridge()