#!/usr/bin/env python3
"""
Enhanced NBA Monte Carlo Simulator
- Tighter variance (10-15% instead of 15-30%)
- Contextual adjustments (injuries, rest, home/away)
- Real game validation
- Detailed breakdown reporting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import the original simulator as base
from main import NBAMonteCarloSimulator, find_games_against_opponent

class EnhancedNBAMonteCarloSimulator(NBAMonteCarloSimulator):
    def __init__(self):
        super().__init__()
        self.adjustment_details = {}  # Track all adjustments for reporting
    
    def find_real_games_between_teams(self, player_name, opponent_team, season="2023-24"):
        """Find all actual games where player faced opponent team"""
        print(f"🔍 Searching for real games: {player_name} vs {opponent_team} in {season}")
        
        games = find_games_against_opponent(player_name, opponent_team, season)
        
        if games is not None and len(games) > 0:
            game_list = []
            for _, game in games.iterrows():
                game_info = {
                    'date': game['GAME_DATE'].strftime('%Y-%m-%d'),
                    'matchup': game['MATCHUP'],
                    'home_away': 'HOME' if 'vs.' in game['MATCHUP'] else 'AWAY'
                }
                game_list.append(game_info)
            
            print(f"✅ Found {len(game_list)} real games")
            return game_list
        else:
            print(f"❌ No games found between {player_name} and {opponent_team}")
            return []
    
    def get_rest_status(self, player_name, game_date, season="2023-24"):
        """Check rest status: back-to-back, days of rest, etc."""
        try:
            # Get player's game log
            game_logs = self.fetch_player_game_logs(player_name, season)
            if game_logs is None or len(game_logs) == 0:
                return {'days_rest': 2, 'is_back_to_back': False, 'rest_advantage': False}
            
            game_logs['GAME_DATE'] = pd.to_datetime(game_logs['GAME_DATE'])
            game_logs = game_logs.sort_values('GAME_DATE')
            
            target_date = pd.to_datetime(game_date)
            
            # Find the game before target date
            previous_games = game_logs[game_logs['GAME_DATE'] < target_date]
            
            if len(previous_games) == 0:
                return {'days_rest': 3, 'is_back_to_back': False, 'rest_advantage': True}
            
            last_game_date = previous_games.iloc[-1]['GAME_DATE']
            days_rest = (target_date - last_game_date).days
            
            rest_status = {
                'days_rest': days_rest,
                'is_back_to_back': days_rest <= 1,
                'rest_advantage': days_rest >= 3,
                'last_game_date': last_game_date.strftime('%Y-%m-%d')
            }
            
            return rest_status
            
        except Exception as e:
            print(f"⚠️  Could not determine rest status: {e}")
            return {'days_rest': 2, 'is_back_to_back': False, 'rest_advantage': False}
    
    def calculate_contextual_adjustments(self, player_name, player_team, opponent_team, 
                                       game_date, location='HOME'):
        """Calculate all contextual adjustments with detailed breakdown"""
        adjustments = {
            'injury_boost': 0.0,
            'rest_adjustment': 0.0,
            'home_away_adjustment': 0.0,
            'total_adjustment': 0.0,
            'breakdown': [],
            'details': {}
        }
        
        # 1. Home/Away adjustment (reduced from original)
        if location == 'HOME':
            home_adj = 0.02  # +2% (reduced from +3%)
            adjustments['home_away_adjustment'] = home_adj
            adjustments['breakdown'].append(f"🏠 Home court advantage: +{home_adj*100:.1f}%")
        else:
            away_adj = -0.025  # -2.5% (reduced from -3%)
            adjustments['home_away_adjustment'] = away_adj
            adjustments['breakdown'].append(f"✈️  Away game penalty: {away_adj*100:.1f}%")
        
        # 2. Rest/Fatigue adjustment
        rest_status = self.get_rest_status(player_name, game_date)
        adjustments['details']['rest_status'] = rest_status
        
        if rest_status['is_back_to_back']:
            rest_adj = -0.06  # -6% for back-to-back
            adjustments['rest_adjustment'] = rest_adj
            adjustments['breakdown'].append(f"😴 Back-to-back game penalty: {rest_adj*100:.1f}%")
        elif rest_status['rest_advantage']:
            rest_adj = 0.015  # +1.5% for 3+ days rest
            adjustments['rest_adjustment'] = rest_adj
            adjustments['breakdown'].append(f"😌 Well-rested bonus ({rest_status['days_rest']} days): +{rest_adj*100:.1f}%")
        else:
            adjustments['breakdown'].append(f"😐 Normal rest ({rest_status['days_rest']} days): 0%")
        
        # 3. Injury adjustment (placeholder - would use Sportradar API)
        # For now, simulate some injury impact
        if hasattr(self, 'injury_api') and self.injury_api:
            try:
                injury_context = self.injury_api.get_injury_context_for_game(
                    player_team, opponent_team, game_date
                )
                adjustments['injury_boost'] = injury_context['total_boost']
                adjustments['breakdown'].extend(injury_context['player_team_injuries'])
                adjustments['details']['injury_context'] = injury_context
            except Exception as e:
                print(f"⚠️  Could not fetch injury data: {e}")
                adjustments['breakdown'].append("🏥 Injury data unavailable")
        else:
            # Simulate injury impact for demo
            import random
            if random.random() < 0.3:  # 30% chance of teammate injury
                simulated_boost = random.choice([0.02, 0.05])  # 2% or 5%
                adjustments['injury_boost'] = simulated_boost
                player_type = "starter" if simulated_boost == 0.02 else "superstar"
                adjustments['breakdown'].append(f"🏥 Simulated teammate injury ({player_type}): +{simulated_boost*100:.1f}%")
            else:
                adjustments['breakdown'].append("🏥 No significant injuries (simulated)")
        
        # Calculate total adjustment
        adjustments['total_adjustment'] = (
            adjustments['injury_boost'] + 
            adjustments['rest_adjustment'] + 
            adjustments['home_away_adjustment']
        )
        
        return adjustments
    
    def run_enhanced_monte_carlo_simulation(self, player_name, opponent_team, game_date, 
                                          player_team=None, n_simulations=10000):
        """
        Enhanced Monte Carlo with tighter variance and contextual adjustments
        """
        # Validate inputs
        game_date_dt = pd.to_datetime(game_date)
        current_date = pd.to_datetime('2024-07-30')  # Current date
        
        if game_date_dt > current_date:
            print(f"❌ Future date provided: {game_date}. Please use a past date.")
            return None, None, None
        
        # Get historical data (same as original)
        current_season_logs = self.fetch_player_game_logs(player_name, "2023-24")
        last_season_logs = self.fetch_player_game_logs(player_name, "2022-23")
        
        if current_season_logs is None and last_season_logs is None:
            print(f"❌ No historical data available for {player_name}")
            return None, None, None
        
        # Filter data up to game date
        game_date_pd = pd.to_datetime(game_date)
        
        if current_season_logs is not None:
            current_season_logs = current_season_logs[current_season_logs['GAME_DATE'] < game_date_pd]
        
        if last_season_logs is not None:
            last_season_logs = last_season_logs[last_season_logs['GAME_DATE'] < game_date_pd]
        
        # Build training dataset (same logic as original)
        training_data = {'PTS': [], 'REB': [], 'AST': []}
        
        # Add current season data with exponential decay weighting
        if current_season_logs is not None and len(current_season_logs) > 0:
            current_games = current_season_logs.copy()
            current_games['DAYS_AGO'] = (game_date_pd - current_games['GAME_DATE']).dt.days
            
            for _, game in current_games.iterrows():
                days_ago = game['DAYS_AGO']
                weight = max(1, int(np.exp(-days_ago / 30) * 5))
                
                context_multiplier = 1.0
                if days_ago <= 1:
                    context_multiplier *= 0.9
                
                if 'MATCHUP' in game and opponent_team.upper() in game['MATCHUP'].upper():
                    context_multiplier *= 1.2
                
                final_weight = max(1, int(weight * context_multiplier))
                
                training_data['PTS'].extend([game['PTS']] * final_weight)
                training_data['REB'].extend([game['REB']] * final_weight)
                training_data['AST'].extend([game['AST']] * final_weight)
        
        # Add last season data with reduced weight
        if last_season_logs is not None and len(last_season_logs) > 0:
            estimated_days_ago = 365 + (game_date_pd - pd.Timestamp('2023-10-01')).days
            
            for _, game in last_season_logs.iterrows():
                weight = max(1, int(np.exp(-estimated_days_ago / 365) * 2))
                
                training_data['PTS'].extend([game['PTS']] * weight)
                training_data['REB'].extend([game['REB']] * weight)
                training_data['AST'].extend([game['AST']] * weight)
        
        if not any(training_data.values()):
            print(f"❌ Insufficient training data for {player_name}")
            return None, None, None
        
        # Determine location
        # This is a simplification - in reality you'd check the actual game location
        location = 'HOME' if not player_team or player_team.lower() in opponent_team.lower() else 'AWAY'
        
        # Calculate contextual adjustments
        adjustments = self.calculate_contextual_adjustments(
            player_name, player_team, opponent_team, game_date, location
        )
        
        # Get base projections from original algorithm
        base_projections = {}
        for stat in ['PTS', 'REB', 'AST']:
            base_projections[stat] = np.mean(training_data[stat])
        
        # Apply contextual adjustments
        adjusted_projections = {}
        total_adj = adjustments['total_adjustment']
        for stat in ['PTS', 'REB', 'AST']:
            adjusted_projections[stat] = base_projections[stat] * (1 + total_adj)
        
        # Run enhanced Monte Carlo with TIGHTER variance
        simulation_results = {'PTS': [], 'REB': [], 'AST': []}
        
        for _ in range(n_simulations):
            # Sample from historical performance distributions
            pts_sample = np.random.choice([s for s in training_data['PTS'] if s > 0], 1)[0]
            reb_sample = np.random.choice([s for s in training_data['REB'] if s > 0], 1)[0]
            ast_sample = np.random.choice([s for s in training_data['AST'] if s > 0], 1)[0]
            
            # ENHANCED: Much tighter variance
            pts_variance = pts_sample * 0.10  # Reduced from 0.15
            reb_variance = reb_sample * 0.15  # Reduced from 0.25
            ast_variance = ast_sample * 0.15  # Reduced from 0.25
            
            # Generate stats with tighter variance
            pts = max(0, int(np.random.normal(pts_sample, pts_variance)))
            reb = max(0, int(np.random.normal(reb_sample, reb_variance)))
            ast = max(0, int(np.random.normal(ast_sample, ast_variance)))
            
            # Apply contextual adjustments
            pts = max(0, int(pts * (1 + total_adj)))
            reb = max(0, int(reb * (1 + total_adj)))
            ast = max(0, int(ast * (1 + total_adj)))
            
            # Apply opponent adjustments (from original algorithm)
            base_stats = {'PTS': pts, 'REB': reb, 'AST': ast}
            adjusted_stats = self.adjust_for_opponent(base_stats, opponent_team, location)
            
            for stat in ['PTS', 'REB', 'AST']:
                simulation_results[stat].append(adjusted_stats[stat])
        
        return simulation_results, adjustments, {
            'base_projections': base_projections,
            'adjusted_projections': adjusted_projections,
            'training_data_size': {stat: len(data) for stat, data in training_data.items()}
        }
    
    def calculate_enhanced_percentiles(self, simulation_results):
        """Calculate enhanced confidence intervals with tighter ranges"""
        percentiles = {}
        for stat, values in simulation_results.items():
            percentiles[stat] = {
                '5th': np.percentile(values, 5),
                '10th': np.percentile(values, 10),
                '25th': np.percentile(values, 25),
                '50th': np.percentile(values, 50),
                '75th': np.percentile(values, 75),
                '90th': np.percentile(values, 90),
                '95th': np.percentile(values, 95),
                'mean': np.mean(values),
                'std': np.std(values)
            }
        return percentiles
    
    def display_enhanced_breakdown(self, player_name, opponent_team, game_date, 
                                  adjustments, percentiles, actual_stats=None):
        """Display detailed breakdown of enhanced simulation"""
        print(f"\n🎮 ENHANCED DEMO: Real Game Analysis")
        print("═" * 60)
        print(f"Game: {player_name} vs {opponent_team} on {game_date}")
        
        # Show contextual analysis
        print(f"\n📋 CONTEXTUAL ANALYSIS:")
        print("═" * 30)
        for breakdown_item in adjustments['breakdown']:
            print(f"   {breakdown_item}")
        
        print(f"\n📊 TOTAL ADJUSTMENTS: {adjustments['total_adjustment']*100:+.1f}%")
        
        # Show enhanced projections
        print(f"\n🔮 ENHANCED MONTE CARLO PROJECTION:")
        print("═" * 40)
        for stat in ['PTS', 'REB', 'AST']:
            p = percentiles[stat]
            print(f"{stat}:")
            print(f"  Mean: {p['mean']:.1f}")
            print(f"  Confidence intervals:")
            print(f"    50% range: {p['25th']:.1f} - {p['75th']:.1f}")
            print(f"    80% range: {p['10th']:.1f} - {p['90th']:.1f}")
            print(f"  Standard deviation: {p['std']:.1f} (tighter variance)")
        
        # Show actual performance comparison if provided
        if actual_stats:
            print(f"\n🏀 ACTUAL vs PROJECTED PERFORMANCE:")
            print("═" * 40)
            stats_names = ['PTS', 'REB', 'AST']
            for i, stat in enumerate(stats_names):
                if i < len(actual_stats):
                    actual = actual_stats[i]
                    predicted = percentiles[stat]['mean']
                    diff = actual - predicted
                    diff_pct = (diff / predicted * 100) if predicted > 0 else 0
                    
                    if diff_pct > 10:
                        performance = "✅ OVERPERFORMED"
                    elif diff_pct < -10:
                        performance = "❌ UNDERPERFORMED"
                    else:
                        performance = "✓ MET EXPECTATION"
                    
                    print(f"{stat}: {actual} vs {predicted:.1f} projected ({diff:+.1f}, {diff_pct:+.1f}%) {performance}")

# Test function
def test_enhanced_simulator():
    """Test the enhanced Monte Carlo simulator"""
    simulator = EnhancedNBAMonteCarloSimulator()
    
    # Test with a real player
    player_name = "LeBron James"
    opponent_team = "Warriors"
    game_date = "2024-01-27"  # Use a past date
    
    print(f"🧪 Testing Enhanced Monte Carlo Simulator")
    print(f"Player: {player_name}")
    print(f"Opponent: {opponent_team}")
    print(f"Date: {game_date}")
    
    # Run enhanced simulation
    simulation_results, adjustments, metadata = simulator.run_enhanced_monte_carlo_simulation(
        player_name, opponent_team, game_date, player_team="Lakers", n_simulations=10000
    )
    
    if simulation_results:
        percentiles = simulator.calculate_enhanced_percentiles(simulation_results)
        
        # Display results
        simulator.display_enhanced_breakdown(
            player_name, opponent_team, game_date, adjustments, percentiles
        )
    else:
        print("❌ Simulation failed")

if __name__ == "__main__":
    test_enhanced_simulator()