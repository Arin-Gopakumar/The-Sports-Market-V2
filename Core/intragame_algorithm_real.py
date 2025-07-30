from Core.intragame_algorithm import IntragameAlgorithm  # Capital C  # Updated path
import math

class IntragameAlgorithmReal(IntragameAlgorithm):
    """Modified intragame algorithm that uses Monte Carlo projections"""
    
    def __init__(self, monte_carlo_simulator):
        super().__init__()
        self.mc_simulator = monte_carlo_simulator
        self.data_bridge = None  # Will be set by main system
    
    def calculate_projected_stats_monte_carlo(self, player_name, opponent_team, game_date):
        """Get projections from Monte Carlo simulation instead of simple average"""
        projections = self.data_bridge.get_monte_carlo_projection(
            player_name, opponent_team, game_date
        )
        
        if projections is None:
            # Fallback to original method
            return None
            
        # Convert to tuple format expected by the system
        return (
            projections['PTS'],
            projections['REB'],
            projections['AST'],
            projections['TO'],
            projections['STOCKS'],
            projections['3PM'],
            projections['TS%']
        )
    
    def simulate_intragame_real(self, player_name, actual_stats, opponent_team, 
                               game_date, old_price, player_archetype=None):
        """
        Complete intragame simulation using Monte Carlo projections
        
        Args:
            player_name: str, real NBA player name
            actual_stats: tuple of actual game stats (pts, reb, ast, to, stocks, 3pm, ts%)
            opponent_team: str, opponent team name
            game_date: str, game date
            old_price: float, current stock price
            player_archetype: str, optional player archetype
        
        Returns:
            dict with all calculations and results
        """
        # Step 1: Get Monte Carlo projections
        projected_stats = self.calculate_projected_stats_monte_carlo(
            player_name, opponent_team, game_date
        )
        
        if projected_stats is None:
            # If MC fails, get player data and use original method
            player_data = self.data_bridge.get_real_player_data(player_name)
            if player_data is None:
                return None
                
            season_avg = player_data["season_avg_2024"]
            games = player_data["games"]
            last_5_avg = self._calculate_last_n_averages(games[-5:])
            projected_stats = self.calculate_projected_stats(season_avg, last_5_avg)
        
        # Step 2-8: Use existing logic from parent class
        std_devs = self.calculate_standard_deviations(projected_stats)
        z_scores = self.calculate_z_scores(actual_stats, projected_stats, std_devs)
        pps = self.calculate_pps(z_scores, player_archetype)
        dis = self.calculate_dis(pps)
        raw_delta = self.calculate_raw_delta(pps, dis)
        dampened_delta = self.apply_dampening(raw_delta)
        new_price, price_change_pct = self.calculate_new_price(old_price, dampened_delta)
        
        return {
            'projected_stats': projected_stats,
            'standard_deviations': std_devs,
            'z_scores': z_scores,
            'pps': pps,
            'dis': dis,
            'raw_delta': raw_delta,
            'dampened_delta': dampened_delta,
            'new_price': new_price,
            'price_change_pct': price_change_pct,
            'old_price': old_price,
            'monte_carlo_used': True
        }
    
    def _calculate_last_n_averages(self, games):
        """Helper to calculate averages from last n games"""
        if not games:
            return (0, 0, 0, 0, 0, 0, 0)
        
        totals = [0] * 7
        for game in games:
            for i in range(7):
                totals[i] += game[i]
        
        n_games = len(games)
        return tuple(total / n_games for total in totals)