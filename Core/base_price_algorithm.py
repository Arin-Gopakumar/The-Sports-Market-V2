import numpy as np
from scipy.stats import norm

class BasePriceAlgorithm:
    def __init__(self):
        # League averages and standard deviations (example values - should be updated with real data)
        self.league_stats = {
            'pts': {'mean': 15.0, 'std': 8.0},
            'ast': {'mean': 4.0, 'std': 3.0},
            'reb': {'mean': 4.0, 'std': 2.5},
            'to': {'mean': 2.0, 'std': 1.5},
            'stocks': {'mean': 1.5, 'std': 1.0},
            'ts%': {'mean': 0.55, 'std': 0.08}
        }
    
    def calculate_non_rookie_base_price(self, player_stats):
        """
        Calculate base price for non-rookie players using PRS (Player Rating Score)
        
        Args:
            player_stats: tuple of (pts, reb, ast, to, stocks, ts%)
        
        Returns:
            base_price: float between $10 and $60
        """
        pts, reb, ast, to, stocks, ts_pct = player_stats
        
        # Step 1: Calculate z-scores
        z_scores = {}
        z_scores['pts'] = (pts - self.league_stats['pts']['mean']) / self.league_stats['pts']['std']
        z_scores['ast'] = (ast - self.league_stats['ast']['mean']) / self.league_stats['ast']['std']
        z_scores['reb'] = (reb - self.league_stats['reb']['mean']) / self.league_stats['reb']['std']
        z_scores['to'] = (to - self.league_stats['to']['mean']) / self.league_stats['to']['std']
        z_scores['stocks'] = (stocks - self.league_stats['stocks']['mean']) / self.league_stats['stocks']['std']
        z_scores['ts%'] = (ts_pct - self.league_stats['ts%']['mean']) / self.league_stats['ts%']['std']
        
        # Step 2: Transform z-scores to percentiles using normal CDF
        percentiles = {}
        for stat, z_score in z_scores.items():
            percentiles[stat] = norm.cdf(z_score)
        
        # Step 3: Calculate PRS with weights
        prs = (0.40 * percentiles['pts'] + 
               0.25 * percentiles['ast'] + 
               0.20 * percentiles['reb'] - 
               0.10 * percentiles['to'] + 
               0.15 * percentiles['stocks'] + 
               0.10 * percentiles['ts%'])
        
        # Step 4: Cap between 0 and 1
        prs = max(0, min(1, prs))
        
        # Step 5: Calculate base price
        base_price = 10 + (prs * 50)
        
        return {
            'base_price': base_price,
            'prs': prs,
            'z_scores': z_scores,
            'percentiles': percentiles
        }
    
    def calculate_rookie_base_price(self, draft_pick):
        """
        Calculate base price for rookie players using DRS (Draft Rating Score)
        
        Args:
            draft_pick: int (1-60)
        
        Returns:
            base_price: float between $12.5 and $35
        """
        # Step 1: Calculate DRS
        drs = max(0.1, 1 - np.log2(draft_pick) / np.log2(60))
        
        # Step 2: Calculate base price
        base_price = 10 + (drs * 25)
        
        return {
            'base_price': base_price,
            'drs': drs,
            'draft_pick': draft_pick
        }
    
    def calculate_base_price(self, player_stats=None, draft_pick=None, is_rookie=False):
        """
        Main function to calculate base price for either rookie or non-rookie
        
        Args:
            player_stats: tuple of (pts, reb, ast, to, stocks, ts%) for non-rookies
            draft_pick: int (1-60) for rookies
            is_rookie: boolean to determine which algorithm to use
        
        Returns:
            dict with base price and calculation details
        """
        if is_rookie:
            if draft_pick is None:
                raise ValueError("Draft pick number required for rookie players")
            return self.calculate_rookie_base_price(draft_pick)
        else:
            if player_stats is None:
                raise ValueError("Player stats required for non-rookie players")
            return self.calculate_non_rookie_base_price(player_stats) 