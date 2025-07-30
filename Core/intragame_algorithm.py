import numpy as np
import math

class IntragameAlgorithm:
    def __init__(self):
        pass
    
    def calculate_projected_stats(self, season_avg, last_5_avg):
        """
        Calculate projected stats using the formula:
        Projected Stat = 0.5 × Season Avg + 0.5 × Last 5 Games Avg
        """
        projected = []
        for i in range(len(season_avg)):
            projected.append(0.5 * season_avg[i] + 0.5 * last_5_avg[i])
        return tuple(projected)
    
    def calculate_standard_deviations(self, projected_stats):
        """
        Calculate standard deviations for each stat
        """
        pts, reb, ast, to, stocks, threepm, ts_pct = projected_stats
        
        std_devs = {
            'pts': 1.15 * math.sqrt(max(pts, 0.1)),
            'reb': 1.00 * math.sqrt(max(reb, 0.1)),
            'ast': 0.90 * math.sqrt(max(ast, 0.1)),
            'to': 0.75 * math.sqrt(max(to, 0.1)),
            'stocks': 0.75 * math.sqrt(max(stocks, 0.1)),
            'threepm': 0.75 * math.sqrt(max(threepm, 0.1)),
            'ts%': 0.07  # fixed
        }
        
        return std_devs
    
    def calculate_z_scores(self, actual_stats, projected_stats, std_devs):
        """
        Calculate z-scores for each stat
        Note: TO uses (projected - actual) / std dev
        """
        pts, reb, ast, to, stocks, threepm, ts_pct = actual_stats
        proj_pts, proj_reb, proj_ast, proj_to, proj_stocks, proj_threepm, proj_ts_pct = projected_stats
        
        z_scores = {
            'pts': (pts - proj_pts) / std_devs['pts'],
            'reb': (reb - proj_reb) / std_devs['reb'],
            'ast': (ast - proj_ast) / std_devs['ast'],
            'to': (proj_to - to) / std_devs['to'],  # inverted for TO
            'stocks': (stocks - proj_stocks) / std_devs['stocks'],
            'threepm': (threepm - proj_threepm) / std_devs['threepm'],
            'ts%': (ts_pct - proj_ts_pct) / std_devs['ts%']
        }
        
        return z_scores
    
    def calculate_pps(self, z_scores, player_archetype=None):
        """
        Calculate Weighted PPS (Performance Points Score) - Intragame uses default weights only
        """
        # Default weights (same as original)
        weights = {
            'pts': 0.45,
            'reb': 0.15,
            'ast': 0.15,
            'to': 0.05,
            'stocks': 0.10,
            'threepm': 0.05,
            'ts%': 0.05
        }
        
        pps = sum(weights[stat] * z_scores[stat] for stat in weights.keys())
        return pps
    
    def calculate_dis(self, pps):
        """
        Calculate Demand Imbalance Score (DIS)
        """
        buy_adj = 15 * pps
        sell_adj = -15 * pps
        
        buys = 50 + buy_adj + 2
        sells = 50 + sell_adj - 2
        
        dis = (buys - sells) / (buys + sells)
        return dis
    
    def calculate_raw_delta(self, pps, dis):
        """
        Calculate raw delta
        """
        return 0.8 * pps + 0.2 * dis
    
    def apply_dampening(self, raw_delta):
        """
        Apply conditional dampening
        """
        if raw_delta >= 0:
            dampened = (1.0 * raw_delta) / math.sqrt(1 + 4 * raw_delta**2)
        else:
            dampened = (1.0 * raw_delta) / math.sqrt(1 + 2.5 * raw_delta**2)
        
        return dampened
    
    def calculate_new_price(self, old_price, dampened_delta):
        """
        Calculate new price and price change percentage
        """
        new_price = old_price * (1 + dampened_delta)
        price_change_pct = dampened_delta * 100
        
        return new_price, price_change_pct
    
    def simulate_intragame(self, actual_stats, season_avg, last_5_avg, old_price, player_archetype=None):
        """
        Complete intragame simulation
        
        Args:
            actual_stats: tuple of (pts, reb, ast, to, stocks, 3pm, ts%)
            season_avg: tuple of season averages
            last_5_avg: tuple of last 5 games averages
            old_price: float, current stock price
            player_archetype: str, player archetype for PPS weighting
        
        Returns:
            dict with all calculations and results
        """
        # Step 1: Calculate projected stats
        projected_stats = self.calculate_projected_stats(season_avg, last_5_avg)
        
        # Step 2: Calculate standard deviations
        std_devs = self.calculate_standard_deviations(projected_stats)
        
        # Step 3: Calculate z-scores
        z_scores = self.calculate_z_scores(actual_stats, projected_stats, std_devs)
        
        # Step 4: Calculate PPS
        pps = self.calculate_pps(z_scores, player_archetype)
        
        # Step 5: Calculate DIS
        dis = self.calculate_dis(pps)
        
        # Step 6: Calculate raw delta
        raw_delta = self.calculate_raw_delta(pps, dis)
        
        # Step 7: Apply dampening
        dampened_delta = self.apply_dampening(raw_delta)
        
        # Step 8: Calculate new price
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
            'old_price': old_price
        } 