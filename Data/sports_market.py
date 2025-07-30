import numpy as np
from scipy.stats import norm
import math

class SportsMarket:
    def __init__(self):
        self.players = self._initialize_players()
    
    def _initialize_players(self):
        """Initialize player data with game stats and season averages"""
        import random
        
        # Set seed for reproducible results
        random.seed(42)
        
        players = {}
        
        # Enhanced player types with more diversity
        player_types = [
            # Original 100 players (keeping existing structure)
            # Role players (low stats, high efficiency)
            {'count': 20, 'pts_range': (5, 12), 'reb_range': (1, 4), 'ast_range': (1, 3), 
             'stocks_range': (0.5, 1.5), 'to_range': (0.5, 1.5), 'threepm_range': (0, 2), 'ts_range': (0.55, 0.65)},
            
            # Volume scorers (high points, lower efficiency)
            {'count': 15, 'pts_range': (18, 30), 'reb_range': (3, 7), 'ast_range': (2, 5), 
             'stocks_range': (0.8, 2.0), 'to_range': (2, 4), 'threepm_range': (1, 4), 'ts_range': (0.48, 0.58)},
            
            # Playmakers (high assists, moderate points)
            {'count': 15, 'pts_range': (12, 22), 'reb_range': (2, 6), 'ast_range': (6, 10), 
             'stocks_range': (0.8, 2.2), 'to_range': (2.5, 4.5), 'threepm_range': (1, 3), 'ts_range': (0.50, 0.60)},
            
            # Defensive specialists (high stocks, lower scoring)
            {'count': 15, 'pts_range': (8, 16), 'reb_range': (4, 8), 'ast_range': (1, 4), 
             'stocks_range': (2.0, 3.5), 'to_range': (1, 2.5), 'threepm_range': (0, 2), 'ts_range': (0.52, 0.62)},
            
            # 3-point specialists (high 3PM, moderate other stats)
            {'count': 15, 'pts_range': (10, 20), 'reb_range': (2, 5), 'ast_range': (1, 4), 
             'stocks_range': (0.5, 1.8), 'to_range': (1, 2.5), 'threepm_range': (2, 5), 'ts_range': (0.58, 0.68)},
            
            # Stars (high all-around stats)
            {'count': 10, 'pts_range': (20, 35), 'reb_range': (5, 10), 'ast_range': (4, 8), 
             'stocks_range': (1.5, 3.0), 'to_range': (2.5, 4.5), 'threepm_range': (2, 5), 'ts_range': (0.55, 0.65)},
            
            # Centers (high rebounds, moderate scoring)
            {'count': 10, 'pts_range': (8, 18), 'reb_range': (8, 12), 'ast_range': (1, 3), 
             'stocks_range': (1.5, 3.0), 'to_range': (1.5, 3), 'threepm_range': (0, 1), 'ts_range': (0.55, 0.65)},
            
            # NEW: 100 Additional Diverse Players
            
            # Superstars (elite all-around)
            {'count': 8, 'pts_range': (25, 35), 'reb_range': (6, 12), 'ast_range': (6, 10), 
             'stocks_range': (1.8, 3.5), 'to_range': (2.5, 4.5), 'threepm_range': (2, 6), 'ts_range': (0.58, 0.68)},
            
            # Elite 3-point shooters (high volume, high efficiency)
            {'count': 12, 'pts_range': (15, 25), 'reb_range': (2, 5), 'ast_range': (2, 5), 
             'stocks_range': (0.5, 1.5), 'to_range': (1.5, 3), 'threepm_range': (3, 6), 'ts_range': (0.60, 0.70)},
            
            # Elite defenders (very high stocks)
            {'count': 10, 'pts_range': (6, 14), 'reb_range': (3, 7), 'ast_range': (1, 4), 
             'stocks_range': (2.5, 4.0), 'to_range': (1, 2.5), 'threepm_range': (0, 2), 'ts_range': (0.50, 0.60)},
            
            # High-volume scorers (inefficient)
            {'count': 8, 'pts_range': (20, 30), 'reb_range': (3, 6), 'ast_range': (2, 5), 
             'stocks_range': (0.5, 1.8), 'to_range': (3, 5), 'threepm_range': (1, 4), 'ts_range': (0.45, 0.55)},
            
            # Elite playmakers (very high assists)
            {'count': 8, 'pts_range': (10, 20), 'reb_range': (2, 5), 'ast_range': (8, 12), 
             'stocks_range': (0.8, 2.0), 'to_range': (3, 5), 'threepm_range': (1, 3), 'ts_range': (0.52, 0.62)},
            
            # Rebounding machines (very high rebounds)
            {'count': 8, 'pts_range': (8, 16), 'reb_range': (10, 15), 'ast_range': (1, 3), 
             'stocks_range': (1.0, 2.5), 'to_range': (1.5, 3), 'threepm_range': (0, 1), 'ts_range': (0.55, 0.65)},
            
            # Bench warmers (very low stats)
            {'count': 10, 'pts_range': (2, 6), 'reb_range': (0.5, 2), 'ast_range': (0.5, 2), 
             'stocks_range': (0.2, 1.0), 'to_range': (0.5, 1.5), 'threepm_range': (0, 1), 'ts_range': (0.45, 0.55)},
            
            # High-efficiency role players
            {'count': 12, 'pts_range': (8, 15), 'reb_range': (3, 6), 'ast_range': (2, 4), 
             'stocks_range': (1.0, 2.0), 'to_range': (1, 2), 'threepm_range': (1, 3), 'ts_range': (0.62, 0.72)},
            
            # Turnover-prone players
            {'count': 6, 'pts_range': (12, 20), 'reb_range': (3, 6), 'ast_range': (4, 8), 
             'stocks_range': (0.8, 2.0), 'to_range': (4, 6), 'threepm_range': (1, 3), 'ts_range': (0.50, 0.60)},
            
            # One-dimensional scorers (high points, low everything else)
            {'count': 8, 'pts_range': (18, 28), 'reb_range': (1, 3), 'ast_range': (1, 3), 
             'stocks_range': (0.3, 1.2), 'to_range': (2, 4), 'threepm_range': (1, 4), 'ts_range': (0.52, 0.62)},
            
            # Versatile role players (moderate everything)
            {'count': 10, 'pts_range': (10, 18), 'reb_range': (4, 7), 'ast_range': (3, 6), 
             'stocks_range': (1.2, 2.2), 'to_range': (1.5, 3), 'threepm_range': (1, 3), 'ts_range': (0.54, 0.64)}
        ]
        
        # Enhanced name generation with more variety
        first_names = ["James", "Michael", "David", "John", "Robert", "William", "Richard", "Joseph", "Thomas", "Christopher",
                      "Charles", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
                      "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
                      "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
                      "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
                      # Additional names for variety
                      "Marcus", "Terry", "Sean", "Keith", "Tyler", "Jesse", "Aaron", "Adam", "Nathan", "Henry",
                      "Douglas", "Zachary", "Peter", "Kyle", "Walter", "Ethan", "Jeremy", "Harold", "Roger", "Carl",
                      "Gerald", "Keith", "Samuel", "Willie", "Ralph", "Lawrence", "Nicholas", "Roy", "Benjamin", "Bruce",
                      "Bryan", "Christian", "Eugene", "Louis", "Wayne", "Alan", "Juan", "Howard", "Ethan", "Jose",
                      "Billy", "Jordan", "Albert", "Dylan", "Corey", "Shane", "Cody", "Devin", "Cory", "Neil"]
        
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                     "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                     "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
                     "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
                     "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
                     # Additional names for variety
                     "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Stewart",
                     "Morris", "Morales", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Cooper",
                     "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson",
                     "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman",
                     "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons"]
        
        player_id = 1
        
        for player_type in player_types:
            for _ in range(player_type['count']):
                # Generate player name
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                player_name = f"{first_name} {last_name}"
                
                # Generate 2023-2024 stats with some variation
                pts_2023 = random.uniform(*player_type['pts_range'])
                reb_2023 = random.uniform(*player_type['reb_range'])
                ast_2023 = random.uniform(*player_type['ast_range'])
                stocks_2023 = random.uniform(*player_type['stocks_range'])
                to_2023 = random.uniform(*player_type['to_range'])
                threepm_2023 = random.uniform(*player_type['threepm_range'])
                ts_2023 = random.uniform(*player_type['ts_range'])
                
                # Generate 2024-2025 stats with slight variation from 2023-2024
                variation_factor = random.uniform(0.85, 1.15)  # ±15% variation
                pts_2024 = pts_2023 * variation_factor
                reb_2024 = reb_2023 * random.uniform(0.9, 1.1)
                ast_2024 = ast_2023 * random.uniform(0.9, 1.1)
                stocks_2024 = stocks_2023 * random.uniform(0.85, 1.15)
                to_2024 = to_2023 * random.uniform(0.9, 1.1)
                threepm_2024 = threepm_2023 * random.uniform(0.8, 1.2)
                ts_2024 = ts_2023 * random.uniform(0.95, 1.05)
                
                # Generate 60-80 random games for 2024-2025
                num_games = random.randint(60, 80)
                games_2024 = []
                
                for game in range(num_games):
                    # Generate game stats with realistic variance
                    game_pts = max(0, random.gauss(pts_2024, pts_2024 * 0.4))
                    game_reb = max(0, random.gauss(reb_2024, reb_2024 * 0.5))
                    game_ast = max(0, random.gauss(ast_2024, ast_2024 * 0.6))
                    game_stocks = max(0, random.gauss(stocks_2024, stocks_2024 * 0.7))
                    game_to = max(0, random.gauss(to_2024, to_2024 * 0.6))
                    game_threepm = max(0, random.gauss(threepm_2024, threepm_2024 * 0.8))
                    game_ts = max(0.2, min(1.0, random.gauss(ts_2024, 0.1)))
                    
                    games_2024.append((
                        round(game_pts, 1),
                        round(game_reb, 1),
                        round(game_ast, 1),
                        round(game_to, 1),
                        round(game_stocks, 1),
                        round(game_threepm, 1),
                        round(game_ts, 3)
                    ))
                
                # Store player data
                players[player_name] = {
                    "games": games_2024,
                    "season_avg_2023": (
                        round(pts_2023, 1),
                        round(reb_2023, 1),
                        round(ast_2023, 1),
                        round(to_2023, 1),
                        round(stocks_2023, 1),
                        round(threepm_2023, 1),
                        round(ts_2023, 3)
                    ),
                    "season_avg_2024": self._calculate_season_averages(games_2024)
                }
                
                player_id += 1
        
        return players
    
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
    
    def get_player_data(self, player_name):
        """Get player data by name"""
        return self.players.get(player_name)
    
    def list_players(self):
        """List all available players"""
        return list(self.players.keys())
    
    def get_last_n_games(self, player_name, n):
        """Get last n games for a player"""
        player_data = self.get_player_data(player_name)
        if not player_data:
            return []
        return player_data["games"][-n:]
    
    def calculate_last_n_averages(self, games, n):
        """Calculate averages for last n games"""
        if len(games) < n:
            return self._calculate_season_averages(games)
        
        last_n = games[-n:]
        return self._calculate_season_averages(last_n)
    
    def calculate_random_recent_averages(self, games, n, pool_size=None):
        """
        Calculate averages from randomly sampled recent games
        
        Args:
            games: list of game tuples
            n: number of games to sample
            pool_size: size of recent games pool to sample from (defaults to 2*n)
        
        Returns:
            tuple of averages from randomly sampled games
        """
        if len(games) < n:
            return self._calculate_season_averages(games)
        
        # Determine pool size - use more recent games for sampling
        if pool_size is None:
            pool_size = min(2 * n, len(games))  # Default to 2*n or all games if fewer
        
        # Get the most recent pool_size games
        recent_pool = games[-pool_size:]
        
        # Randomly sample n games from the pool
        import random
        sampled_games = random.sample(recent_pool, min(n, len(recent_pool)))
        
        return self._calculate_season_averages(sampled_games)
    
    def get_random_game_stats(self, player_name):
        """
        Get a random game's stats from any part of the player's season
        
        Args:
            player_name: str, name of the player
            
        Returns:
            tuple of random game stats (pts, reb, ast, to, stocks, 3pm, ts%)
        """
        player_data = self.get_player_data(player_name)
        if not player_data or not player_data["games"]:
            return None
        
        games = player_data["games"]
        import random
        random_game = random.choice(games)
        
        return random_game 