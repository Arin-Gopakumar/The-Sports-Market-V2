# sports_market_wrapper.py
"""
Wrapper to maintain backward compatibility with existing sports market code
while using real NBA data under the hood
"""

from Data.real_sports_market import RealSportsMarket
from main import NBAMonteCarloSimulator

class SportsMarketWrapper:
   """Wrapper that makes RealSportsMarket work with existing interfaces"""
   
   def __init__(self):
       # Initialize Monte Carlo simulator
       mc_sim = NBAMonteCarloSimulator()
       
       # Initialize real sports market
       self.real_market = RealSportsMarket(mc_sim)
       
       # Map synthetic player names to real NBA players for compatibility
       self.player_mapping = self._create_player_mapping()
   
   def _create_player_mapping(self):
       """Create mapping from synthetic names to real NBA players"""
       # This allows existing code that expects synthetic names to work
       mapping = {}
       synthetic_names = [
           "James Smith", "Michael Johnson", "David Williams", "John Brown"
       ]
       real_names = [
           "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo"
       ]
       
       for syn, real in zip(synthetic_names, real_names):
           mapping[syn] = real
           
       return mapping
   
   def get_player_data(self, player_name):
       """Get player data, handling both synthetic and real names"""
       # Check if it's a synthetic name
       if player_name in self.player_mapping:
           real_name = self.player_mapping[player_name]
           return self.real_market.get_player_data(real_name)
       else:
           # Assume it's a real NBA player name
           return self.real_market.get_player_data(player_name)
   
   def list_players(self):
       """List players - returns real NBA players"""
       return self.real_market.list_players()