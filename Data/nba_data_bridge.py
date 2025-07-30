# nba_data_bridge.py
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from nba_api.stats.endpoints import playergamelog, leaguedashplayerstats
from nba_api.stats.static import players, teams
from nba_api.stats.library.parameters import Season, SeasonType

class NBADataBridge:
    """Bridge between NBA API data and Sports Market system"""
    
    def __init__(self, monte_carlo_simulator):
        self.mc_simulator = monte_carlo_simulator
        self._cache = {}
        
    def get_real_player_data(self, player_name, season="2023-24"):
        """Get real player data in the format expected by sports market"""
        cache_key = f"{player_name}_{season}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get player ID
        player_id = self.mc_simulator.get_player_id(player_name)
        if not player_id:
            return None
            
        # Fetch game logs
        game_logs = self.mc_simulator.fetch_player_game_logs(player_name, season)
        if game_logs is None or len(game_logs) == 0:
            return None
            
        # Convert to sports market format
        games_list = []
        for _, game in game_logs.iterrows():
            # Calculate STOCKS (steals + blocks) and other derived stats
            stocks = game.get('STL', 0) + game.get('BLK', 0)
            
            # Calculate True Shooting % if not available
            if 'TS_PCT' not in game:
                fga = game.get('FGA', 0)
                fta = game.get('FTA', 0)
                pts = game.get('PTS', 0)
                if (fga + 0.44 * fta) > 0:
                    ts_pct = pts / (2 * (fga + 0.44 * fta))
                else:
                    ts_pct = 0
            else:
                ts_pct = game['TS_PCT']
            
            game_tuple = (
                float(game.get('PTS', 0)),
                float(game.get('REB', 0)),
                float(game.get('AST', 0)),
                float(game.get('TOV', 0)),
                float(stocks),
                float(game.get('FG3M', 0)),
                float(ts_pct)
            )
            games_list.append(game_tuple)
        
        # Calculate season averages
        season_avg = self._calculate_season_averages(games_list)
        
        # Get previous season data for comparison
        prev_season = self._get_previous_season(season)
        prev_game_logs = self.mc_simulator.fetch_player_game_logs(player_name, prev_season)
        
        if prev_game_logs is not None and len(prev_game_logs) > 0:
            prev_games_list = []
            for _, game in prev_game_logs.iterrows():
                stocks = game.get('STL', 0) + game.get('BLK', 0)
                fga = game.get('FGA', 0)
                fta = game.get('FTA', 0)
                pts = game.get('PTS', 0)
                ts_pct = pts / (2 * (fga + 0.44 * fta)) if (fga + 0.44 * fta) > 0 else 0
                
                prev_game_tuple = (
                    float(game.get('PTS', 0)),
                    float(game.get('REB', 0)),
                    float(game.get('AST', 0)),
                    float(game.get('TOV', 0)),
                    float(stocks),
                    float(game.get('FG3M', 0)),
                    float(ts_pct)
                )
                prev_games_list.append(prev_game_tuple)
            
            prev_season_avg = self._calculate_season_averages(prev_games_list)
        else:
            # Use current season avg as fallback
            prev_season_avg = season_avg
        
        player_data = {
            "games": games_list,
            "season_avg_2023": prev_season_avg,  # Previous season
            "season_avg_2024": season_avg        # Current season
        }
        
        self._cache[cache_key] = player_data
        return player_data
    
    def _calculate_season_averages(self, games):
        """Calculate season averages from game data"""
        if not games:
            return (0, 0, 0, 0, 0, 0, 0)
        
        totals = [0] * 7
        for game in games:
            for i in range(7):
                totals[i] += game[i]
        
        n_games = len(games)
        return tuple(total / n_games for total in totals)
    
    def _get_previous_season(self, season):
        """Get previous season string"""
        year = int(season.split('-')[0])
        prev_year = year - 1
        return f"{prev_year}-{str(year)[-2:]}"
    
    def get_monte_carlo_projection(self, player_name, opponent_team, game_date, n_simulations=10000):
        """Get projection from Monte Carlo simulation"""
        sim_results, _ = self.mc_simulator.run_monte_carlo_simulation(
            player_name, opponent_team, game_date, n_simulations
        )
        
        if sim_results is None:
            return None
            
        # Calculate mean projections
        projections = {}
        for stat in ['PTS', 'REB', 'AST']:
            projections[stat] = np.mean(sim_results[stat])
        
        # We need to add projections for other stats required by the market system
        # For now, use historical averages
        player_data = self.get_real_player_data(player_name)
        if player_data:
            season_avg = player_data['season_avg_2024']
            projections['TO'] = season_avg[3]  # Turnovers
            projections['STOCKS'] = season_avg[4]  # Steals + Blocks
            projections['3PM'] = season_avg[5]  # 3-pointers made
            projections['TS%'] = season_avg[6]  # True shooting %
        else:
            # Fallback values
            projections['TO'] = 2.0
            projections['STOCKS'] = 1.5
            projections['3PM'] = 2.0
            projections['TS%'] = 0.55
            
        return projections
    
    def clear_cache(self):
        """Clear the data cache"""
        self._cache = {}