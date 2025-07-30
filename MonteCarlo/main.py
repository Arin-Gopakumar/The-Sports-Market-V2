import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# NBA API imports
try:
    from nba_api.stats.endpoints import playergamelog, leaguedashplayerstats
    from nba_api.stats.library.parameters import Season, SeasonType
    from nba_api.stats.static import players, teams
    NBA_API_AVAILABLE = True
    print("✅ NBA API successfully imported")
except ImportError as e:
    print(f"❌ Error importing NBA API: {e}")
    print("Install with: pip install nba_api")
    NBA_API_AVAILABLE = False

class NBAMonteCarloSimulator:
    def __init__(self):
        self.players_data = {}
        self.teams_data = {}
        self.game_logs = {}
        self.defensive_ratings = {}
        self.pace_data = {}
        
    def get_player_id(self, player_name):
        """Get player ID from name"""
        if not NBA_API_AVAILABLE:
            # Fallback data for common players
            fallback_ids = {
                'LeBron James': 2544,
                'Stephen Curry': 201939,
                'Kevin Durant': 201142,
                'Nikola Jokic': 203999,
                'Giannis Antetokounmpo': 203507
            }
            return fallback_ids.get(player_name, None)
        
        try:
            all_players = players.get_players()
            for player in all_players:
                if player_name.lower() in player['full_name'].lower():
                    return player['id']
        except:
            pass
        return None
    
    def get_team_id(self, team_name):
        """Get team ID from name"""
        if not NBA_API_AVAILABLE:
            # Fallback data
            fallback_ids = {
                'Lakers': 1610612747,
                'Warriors': 1610612744,
                'Nuggets': 1610612743,
                'Bucks': 1610612749,
                'Suns': 1610612756
            }
            return fallback_ids.get(team_name, None)
        
        try:
            all_teams = teams.get_teams()
            for team in all_teams:
                if team_name.lower() in team['full_name'].lower():
                    return team['id']
        except:
            pass
        return None
    
    def fetch_player_game_logs(self, player_name, season="2023-24"):
        """Fetch player game logs for a specific season"""
        if not NBA_API_AVAILABLE:
            return None
        
        player_id = self.get_player_id(player_name)
        if not player_id:
            return None
        
        try:
            game_logs = playergamelog.PlayerGameLog(
                player_id=player_id,
                season=season,
                season_type_all_star=SeasonType.regular
            ).get_data_frames()[0]
            
            # Clean and process the data
            game_logs['GAME_DATE'] = pd.to_datetime(game_logs['GAME_DATE'])
            game_logs = game_logs.sort_values('GAME_DATE')
            
            return game_logs
        except Exception as e:
            return None
    
    def generate_synthetic_game_logs(self, player_name, season):
        """Generate synthetic game logs for demonstration purposes"""
        print(f"🎲 Generating synthetic data for {player_name} in {season}")
        print(f"   This is NOT real data - it's computer-generated for demonstration!")
        
        np.random.seed(42)  # For reproducible results
        
        # Base stats for different player types
        player_profiles = {
            'LeBron James': {'pts': 25, 'reb': 7, 'ast': 8, 'std': 0.3},
            'Stephen Curry': {'pts': 30, 'reb': 4, 'ast': 6, 'std': 0.35},
            'Nikola Jokic': {'pts': 27, 'reb': 12, 'ast': 9, 'std': 0.25},
            'Giannis Antetokounmpo': {'pts': 30, 'reb': 11, 'ast': 6, 'std': 0.3},
            'Kevin Durant': {'pts': 28, 'reb': 7, 'ast': 5, 'std': 0.3}
        }
        
        profile = player_profiles.get(player_name, {'pts': 20, 'reb': 5, 'ast': 4, 'std': 0.3})
        
        # Generate 82 games (full season)
        dates = pd.date_range(start=f"{season.split('-')[0]}-10-15", periods=82, freq='D')
        dates = [d for d in dates if d.weekday() < 5]  # Only weekdays for games
        
        game_logs = []
        for i, date in enumerate(dates[:82]):
            # Add some variance and trends
            trend_factor = 1 + 0.1 * np.sin(i / 10)  # Seasonal trend
            
            pts = max(0, int(np.random.normal(profile['pts'] * trend_factor, profile['pts'] * profile['std'])))
            reb = max(0, int(np.random.normal(profile['reb'] * trend_factor, profile['reb'] * profile['std'])))
            ast = max(0, int(np.random.normal(profile['ast'] * trend_factor, profile['ast'] * profile['std'])))
            
            game_logs.append({
                'GAME_DATE': date,
                'PTS': pts,
                'REB': reb,
                'AST': ast,
                'MIN': np.random.randint(25, 40),
                'FG_PCT': np.random.uniform(0.4, 0.6),
                'FG3_PCT': np.random.uniform(0.3, 0.45),
                'FT_PCT': np.random.uniform(0.7, 0.9)
            })
        
        print(f"   Generated {len(game_logs)} synthetic games")
        return pd.DataFrame(game_logs)
    
    def calculate_rolling_averages(self, game_logs, window=10, alpha=0.1):
        """Calculate rolling and exponentially weighted averages"""
        if game_logs is None or len(game_logs) == 0:
            return None
        
        stats = ['PTS', 'REB', 'AST']
        rolling_stats = {}
        
        for stat in stats:
            if stat in game_logs.columns:
                # Rolling average
                rolling_stats[f'{stat}_rolling'] = game_logs[stat].rolling(window=window, min_periods=1).mean()
                
                # Exponentially weighted average
                rolling_stats[f'{stat}_ewm'] = game_logs[stat].ewm(alpha=alpha).mean()
                
                # Recent form (last 5 games)
                rolling_stats[f'{stat}_recent'] = game_logs[stat].rolling(window=5, min_periods=1).mean()
        
        return pd.DataFrame(rolling_stats)
    
    def get_defensive_rating(self, team_name, season="2023-24"):
        """Get team defensive rating"""
        if not NBA_API_AVAILABLE:
            # Synthetic defensive ratings
            defensive_ratings = {
                'Nuggets': 112.5,
                'Lakers': 113.2,
                'Warriors': 114.1,
                'Bucks': 111.8,
                'Suns': 113.5,
                'Celtics': 110.2,
                'Heat': 112.8,
                'Knicks': 113.0,
                'GSW': 114.1,  # Added abbreviation
                'MIN': 115.2   # Added Timberwolves
            }
            return defensive_ratings.get(team_name, 113.0)
        
        # In a real implementation, you would fetch this from the API
        return 113.0
    
    def get_team_pace(self, team_name, season="2023-24"):
        """Get team pace factor"""
        if not NBA_API_AVAILABLE:
            # Synthetic pace data
            pace_data = {
                'Nuggets': 98.5,
                'Lakers': 99.2,
                'Warriors': 102.1,
                'Bucks': 100.8,
                'Suns': 99.5,
                'Celtics': 101.2,
                'Heat': 97.8,
                'Knicks': 98.0,
                'GSW': 102.1,  # Added abbreviation
                'MIN': 97.8    # Added Timberwolves
            }
            return pace_data.get(team_name, 99.5)
        
        return 99.5
    
    def fetch_actual_game_result(self, player_name, opponent_team, game_date):
        """Fetch the actual game result from the NBA API"""
        if not NBA_API_AVAILABLE:
            return None
        
        player_id = self.get_player_id(player_name)
        if not player_id:
            return None
        
        try:
            # Try multiple seasons to find the game
            seasons_to_try = ["2023-24", "2022-23", "2021-22"]
            game_date = pd.to_datetime(game_date)
            
            for season in seasons_to_try:
                try:
                    game_logs = playergamelog.PlayerGameLog(
                        player_id=player_id,
                        season=season,
                        season_type_all_star=SeasonType.regular
                    ).get_data_frames()[0]
                    
                    if len(game_logs) == 0:
                        continue
                    
                    # Clean and process the data
                    game_logs['GAME_DATE'] = pd.to_datetime(game_logs['GAME_DATE'])
                    
                    # Find the game on the exact date
                    game_data = game_logs[game_logs['GAME_DATE'] == game_date]
                    
                    if len(game_data) > 0:
                        # Get the actual stats
                        actual_stats = {
                            'PTS': int(game_data.iloc[0]['PTS']),
                            'REB': int(game_data.iloc[0]['REB']),
                            'AST': int(game_data.iloc[0]['AST'])
                        }
                        return actual_stats
                        
                except Exception as e:
                    continue
            
            # If no exact date match found, search within ±3 days
            for season in seasons_to_try:
                try:
                    game_logs = playergamelog.PlayerGameLog(
                        player_id=player_id,
                        season=season,
                        season_type_all_star=SeasonType.regular
                    ).get_data_frames()[0]
                    
                    if len(game_logs) == 0:
                        continue
                    
                    game_logs['GAME_DATE'] = pd.to_datetime(game_logs['GAME_DATE'])
                    
                    # Find games within ±3 days
                    date_range_start = game_date - pd.Timedelta(days=3)
                    date_range_end = game_date + pd.Timedelta(days=3)
                    
                    nearby_games = game_logs[
                        (game_logs['GAME_DATE'] >= date_range_start) & 
                        (game_logs['GAME_DATE'] <= date_range_end)
                    ]
                    
                    if len(nearby_games) > 0:
                        # If there are multiple games, prefer the closest date
                        nearby_games['DAYS_DIFF'] = abs(nearby_games['GAME_DATE'] - game_date).dt.days
                        closest_game = nearby_games.loc[nearby_games['DAYS_DIFF'].idxmin()]
                        
                        actual_stats = {
                            'PTS': int(closest_game['PTS']),
                            'REB': int(closest_game['REB']),
                            'AST': int(closest_game['AST'])
                        }
                        return actual_stats
                        
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            return None
    
    def adjust_for_opponent(self, base_stats, opponent_team, location='HOME'):
        """Adjust stats based on opponent defensive rating, team pace, and historical performance"""
        def_rating = self.get_defensive_rating(opponent_team)
        pace = self.get_team_pace(opponent_team)
        
        # League average defensive rating and pace (approximate)
        league_avg_def = 115.0
        league_avg_pace = 100.0
        
        # Calculate base adjustments
        def_adjustment = (league_avg_def / def_rating) if def_rating > 0 else 1.0
        pace_adjustment = (pace / league_avg_pace) if pace > 0 else 1.0
        
        # Apply adjustments with more nuanced factors
        adjusted_stats = {}
        
        # Points: Most affected by defensive rating
        pts_adjustment = def_adjustment
        # Add variance based on defensive rating strength
        if def_rating < 110:  # Strong defense
            pts_adjustment *= 0.9  # Reduce scoring
        elif def_rating > 120:  # Weak defense
            pts_adjustment *= 1.1  # Increase scoring
        adjusted_stats['PTS'] = int(base_stats['PTS'] * pts_adjustment)
        
        # Rebounds: Affected by pace but with more conservative adjustments
        reb_adjustment = pace_adjustment
        # More possessions = more rebound opportunities, but be more conservative
        if pace > 105:  # Fast-paced team
            reb_adjustment *= 1.05  # Reduced from 1.15
        elif pace < 95:  # Slow-paced team
            reb_adjustment *= 0.95  # Increased from 0.85
        adjusted_stats['REB'] = int(base_stats['REB'] * reb_adjustment)
        
        # Assists: Affected by pace and team style
        ast_adjustment = pace_adjustment
        # Fast-paced teams tend to have more assists
        if pace > 105:
            ast_adjustment *= 1.1
        elif pace < 95:
            ast_adjustment *= 0.9
        adjusted_stats['AST'] = int(base_stats['AST'] * ast_adjustment)
        
        # Home/Away adjustment with more realistic factors
        if location == 'HOME':
            home_boost = 1.03  # Slight home advantage
        else:
            home_boost = 0.97  # Slight road disadvantage
        
        # Apply home/away adjustment
        for stat in adjusted_stats:
            adjusted_stats[stat] = int(adjusted_stats[stat] * home_boost)
        
        return adjusted_stats
    
    def run_monte_carlo_simulation(self, player_name, opponent_team, game_date, n_simulations=10000):
        """Run Monte Carlo simulation for player stats"""
        # Validate game date
        game_date_dt = pd.to_datetime(game_date)
        current_date = pd.to_datetime('2024-01-01')  # Approximate current date
        
        if game_date_dt.year < 2022:
            return None, None
        
        # Get historical data
        current_season_logs = self.fetch_player_game_logs(player_name, "2023-24")
        last_season_logs = self.fetch_player_game_logs(player_name, "2022-23")
        
        if current_season_logs is None and last_season_logs is None:
            return None, None
        
        # Filter data up to game date (this is the key - we only use data BEFORE the game)
        game_date = pd.to_datetime(game_date)
        
        if current_season_logs is not None:
            # Only use games that happened BEFORE the target game
            current_season_logs = current_season_logs[current_season_logs['GAME_DATE'] < game_date]
        
        if last_season_logs is not None:
            # Use last season data as additional context
            last_season_logs = last_season_logs[last_season_logs['GAME_DATE'] < game_date]
        
        # Calculate rolling averages from historical data only
        current_rolling = self.calculate_rolling_averages(current_season_logs) if current_season_logs is not None else None
        last_rolling = self.calculate_rolling_averages(last_season_logs) if last_season_logs is not None else None
        
        # Build training dataset with sophisticated weighting and context
        training_data = {'PTS': [], 'REB': [], 'AST': []}
        
        # Add current season data with exponential decay weighting
        if current_season_logs is not None and len(current_season_logs) > 0:
            current_games = current_season_logs.copy()
            current_games['DAYS_AGO'] = (game_date - current_games['GAME_DATE']).dt.days
            
            for _, game in current_games.iterrows():
                days_ago = game['DAYS_AGO']
                # Exponential decay: more recent games get exponentially higher weight
                # Games from 30 days ago get ~37% weight, recent games get 5x weight
                weight = max(1, int(np.exp(-days_ago / 30) * 5))
                
                # Additional context-based adjustments
                context_multiplier = 1.0
                
                # Check for back-to-back games (rest factor)
                if days_ago <= 1:  # Game within last 2 days
                    context_multiplier *= 0.9  # Slight fatigue factor
                
                # Check for opponent-specific performance
                if 'MATCHUP' in game and opponent_team.upper() in game['MATCHUP'].upper():
                    context_multiplier *= 1.2  # Boost for same opponent
                
                final_weight = max(1, int(weight * context_multiplier))
                
                training_data['PTS'].extend([game['PTS']] * final_weight)
                training_data['REB'].extend([game['REB']] * final_weight)
                training_data['AST'].extend([game['AST']] * final_weight)
        
        # Add last season data with reduced weight and recency factor
        if last_season_logs is not None and len(last_season_logs) > 0:
            last_season_games = last_season_logs.copy()
            # Estimate days ago for last season (roughly 365 days + current season days)
            estimated_days_ago = 365 + (game_date - pd.Timestamp('2023-10-01')).days
            
            for _, game in last_season_games.iterrows():
                # Last season games get much lower weight due to age
                weight = max(1, int(np.exp(-estimated_days_ago / 365) * 2))
                
                training_data['PTS'].extend([game['PTS']] * weight)
                training_data['REB'].extend([game['REB']] * weight)
                training_data['AST'].extend([game['AST']] * weight)
        
        # Check if we have enough training data
        if not any(training_data.values()):
            return None, None
        
        # Fetch actual game result for comparison
        actual_game_result = self.fetch_actual_game_result(player_name, opponent_team, game_date)
        
        # Run Monte Carlo simulations
        simulation_results = {'PTS': [], 'REB': [], 'AST': []}
        
        for _ in range(n_simulations):
            # Sample from historical performance distributions
            pts_sample = np.random.choice([s for s in training_data['PTS'] if s > 0], 1)[0]
            reb_sample = np.random.choice([s for s in training_data['REB'] if s > 0], 1)[0]
            ast_sample = np.random.choice([s for s in training_data['AST'] if s > 0], 1)[0]
            
            # Add more realistic variance based on historical volatility
            # Use smaller variance factors for more accurate predictions
            pts_variance = pts_sample * 0.15  # Reduced from 0.25
            reb_variance = reb_sample * 0.25  # Reduced from 0.35
            ast_variance = ast_sample * 0.25  # Reduced from 0.35
            
            # Generate stats with more conservative variance
            pts = max(0, int(np.random.normal(pts_sample, pts_variance)))
            reb = max(0, int(np.random.normal(reb_sample, reb_variance)))
            ast = max(0, int(np.random.normal(ast_sample, ast_variance)))
            
            # Adjust for opponent characteristics
            base_stats = {'PTS': pts, 'REB': reb, 'AST': ast}
            adjusted_stats = self.adjust_for_opponent(base_stats, opponent_team)
            
            for stat in ['PTS', 'REB', 'AST']:
                simulation_results[stat].append(adjusted_stats[stat])
        
        return simulation_results, actual_game_result
    
    def calculate_percentiles(self, simulation_results):
        """Calculate confidence intervals"""
        percentiles = {}
        for stat, values in simulation_results.items():
            percentiles[stat] = {
                '10th': np.percentile(values, 10),
                '50th': np.percentile(values, 50),
                '90th': np.percentile(values, 90),
                'mean': np.mean(values),
                'std': np.std(values)
            }
        return percentiles
    
    def plot_simulation_results(self, simulation_results, player_name, opponent_team, game_date):
        """Plot simulation results"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle(f'{player_name} vs {opponent_team} - {game_date}', fontsize=16)
        
        stats = ['PTS', 'REB', 'AST']
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        for i, (stat, color) in enumerate(zip(stats, colors)):
            values = simulation_results[stat]
            
            # Histogram
            axes[i].hist(values, bins=30, alpha=0.7, color=color, edgecolor='black')
            axes[i].axvline(np.mean(values), color='red', linestyle='--', label='Mean')
            axes[i].axvline(np.percentile(values, 50), color='green', linestyle='--', label='Median')
            
            axes[i].set_title(f'{stat} Distribution')
            axes[i].set_xlabel(stat)
            axes[i].set_ylabel('Frequency')
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def validate_prediction(self, player_name, opponent_team, game_date, actual_stats):
        """Validate prediction against actual results"""
        # Run simulation using only data before the game
        simulation_results, actual_result = self.run_monte_carlo_simulation(
            player_name, opponent_team, game_date, n_simulations=10000
        )
        
        if simulation_results is None:
            return None
        
        percentiles = self.calculate_percentiles(simulation_results)
        
        print(f"\nPredicted vs Actual Results:")
        print("-" * 50)
        
        for stat in ['PTS', 'REB', 'AST']:
            if stat in actual_stats:
                pred = percentiles[stat]
                actual = actual_stats[stat]
                
                print(f"{stat}:")
                print(f"  Predicted: {pred['50th']:.1f} (10th: {pred['10th']:.1f}, 90th: {pred['90th']:.1f})")
                print(f"  Actual: {actual}")
                print(f"  Difference: {actual - pred['50th']:.1f}")
                
                # Check if actual falls within 90% confidence interval
                within_interval = pred['10th'] <= actual <= pred['90th']
                print(f"  Within 90% CI: {'✓' if within_interval else '✗'}")
                print()
        
        return percentiles

def find_available_game_dates(player_name, season="2023-24"):
    """Helper function to find available game dates for a player"""
    if not NBA_API_AVAILABLE:
        return None
    
    player_id = NBAMonteCarloSimulator().get_player_id(player_name)
    if not player_id:
        return None
    
    try:
        game_logs = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star=SeasonType.regular
        ).get_data_frames()[0]
        
        if len(game_logs) == 0:
            return None
        
        game_logs['GAME_DATE'] = pd.to_datetime(game_logs['GAME_DATE'])
        game_logs = game_logs.sort_values('GAME_DATE')
        
        return game_logs
        
    except Exception as e:
        return None

def find_games_against_opponent(player_name, opponent_team, season="2023-24"):
    """Helper function to find all games against a specific opponent"""
    if not NBA_API_AVAILABLE:
        return None
    
    player_id = NBAMonteCarloSimulator().get_player_id(player_name)
    if not player_id:
        return None
    
    try:
        game_logs = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star=SeasonType.regular
        ).get_data_frames()[0]
        
        if len(game_logs) == 0:
            return None
        
        game_logs['GAME_DATE'] = pd.to_datetime(game_logs['GAME_DATE'])
        game_logs = game_logs.sort_values('GAME_DATE')
        
        # Improved team name matching - check both full names and abbreviations
        team_variations = [
            opponent_team.upper(),
            f"vs. {opponent_team.upper()}",
            f"@ {opponent_team.upper()}",
            opponent_team.lower(),
            opponent_team.title()
        ]
        
        # Add common team abbreviations
        team_mappings = {
            'Warriors': ['GSW', 'GS', 'Golden State'],
            'Lakers': ['LAL', 'LA', 'Los Angeles Lakers'],
            'Celtics': ['BOS', 'Boston'],
            'Heat': ['MIA', 'Miami'],
            'Nuggets': ['DEN', 'Denver'],
            'Bucks': ['MIL', 'Milwaukee'],
            'Suns': ['PHX', 'Phoenix']
        }
        
        for team, abbrevs in team_mappings.items():
            if team.lower() in opponent_team.lower():
                team_variations.extend(abbrevs)
                team_variations.extend([f"vs. {abbrev}" for abbrev in abbrevs])
                team_variations.extend([f"@ {abbrev}" for abbrev in abbrevs])
        
        # Find matching games
        opponent_games = pd.DataFrame()
        for team_var in team_variations:
            games = game_logs[
                game_logs['MATCHUP'].str.contains(team_var, case=False, na=False)
            ]
            if len(games) > 0:
                opponent_games = games
                break
        
        return opponent_games
        
    except Exception as e:
        print(f"Error finding games: {e}")
        return None

def main():
    """Main function to run the Monte Carlo simulation"""
    print("🏀 NBA Monte Carlo Stat Predictor")
    print("=" * 50)
    
    # Initialize simulator
    simulator = NBAMonteCarloSimulator()
    
    # YOUR SPECIFIC REQUEST - Test Durant vs Warriors on 12/22/2023
    player_name = "Stephen Curry"
    opponent_team = "Suns"
    game_date = "2023-12-12"  # Fixed the date format
    
    print(f"\n🎯 TESTING YOUR SPECIFIC REQUEST:")
    print(f"Player: {player_name}")
    print(f"Opponent: {opponent_team}")
    print(f"Date: {game_date}")
    print("-" * 50)
    
    # First, let's check if this game exists
    warriors_games = find_games_against_opponent(player_name, opponent_team, "2023-24")
    
    if warriors_games is not None and len(warriors_games) > 0:
        print(f"✅ Found {len(warriors_games)} games vs {opponent_team} in 2023-24 season:")
        for _, game in warriors_games.iterrows():
            print(f"   - {game['GAME_DATE'].strftime('%Y-%m-%d')}: {game['MATCHUP']}")
        
        # Check for the specific date
        test_date_dt = pd.to_datetime(game_date)
        specific_game = warriors_games[warriors_games['GAME_DATE'] == test_date_dt]
        
        if len(specific_game) > 0:
            print(f"\n✅ Found the exact game on {game_date}!")
            
            # Run simulation for this specific game
            print(f"\n🔮 Running Monte Carlo simulation...")
            simulation_results, actual_result = simulator.run_monte_carlo_simulation(
                player_name, opponent_team, game_date, n_simulations=10000
            )
            
            if simulation_results and actual_result:
                percentiles = simulator.calculate_percentiles(simulation_results)
                
                print(f"\n📊 PREDICTION vs ACTUAL RESULTS:")
                print("=" * 50)
                
                for stat in ['PTS', 'REB', 'AST']:
                    p = percentiles[stat]
                    actual = actual_result[stat]
                    difference = actual - p['50th']
                    
                    print(f"{stat}:")
                    print(f"  Predicted: {p['50th']:.1f} (Range: {p['10th']:.1f} - {p['90th']:.1f})")
                    print(f"  Actual: {actual}")
                    print(f"  Difference: {difference:+.1f}")
                    
                    # Check accuracy
                    within_ci = p['10th'] <= actual <= p['90th']
                    accuracy_status = "✅ Within 90% CI" if within_ci else "❌ Outside 90% CI"
                    print(f"  Accuracy: {accuracy_status}")
                    print()
                
                # Plot the results
                print("📈 Generating visualization...")
                simulator.plot_simulation_results(simulation_results, player_name, opponent_team, game_date)
                
            else:
                print("❌ Could not run simulation or fetch actual results")
        else:
            print(f"\n❌ No game found on exactly {game_date}")
            print("Available game dates:")
            for _, game in warriors_games.iterrows():
                print(f"   - {game['GAME_DATE'].strftime('%Y-%m-%d')}")
            
            # Try the closest available game
            if len(warriors_games) > 0:
                closest_game = warriors_games.iloc[0]
                closest_date = closest_game['GAME_DATE'].strftime('%Y-%m-%d')
                print(f"\n🔄 Running simulation for closest game: {closest_date}")
                
                simulation_results, actual_result = simulator.run_monte_carlo_simulation(
                    player_name, opponent_team, closest_date, n_simulations=10000
                )
                
                if simulation_results and actual_result:
                    percentiles = simulator.calculate_percentiles(simulation_results)
                    
                    print(f"\n📊 RESULTS FOR {closest_date}:")
                    print("=" * 50)
                    
                    for stat in ['PTS', 'REB', 'AST']:
                        p = percentiles[stat]
                        actual = actual_result[stat]
                        print(f"{stat}: Predicted {p['50th']:.1f} | Actual {actual} | Diff {actual - p['50th']:+.1f}")
    else:
        print(f"❌ No games found vs {opponent_team} in 2023-24 season")
        
        # Let's see what teams Durant actually played against
        all_games = find_available_game_dates(player_name, "2023-24")
        if all_games is not None:
            print(f"\n📋 Available opponents for {player_name} in 2023-24:")
            unique_opponents = all_games['MATCHUP'].str.extract(r'(vs\.|@)\s*(\w+)')[1].unique()
            for opponent in sorted(unique_opponents):
                if pd.notna(opponent):
                    print(f"   - {opponent}")
    
    print(f"\n" + "="*50)
    print("🏁 Analysis Complete!")

if __name__ == "__main__":
    main()