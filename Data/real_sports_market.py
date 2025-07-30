from Data.sports_market import SportsMarket  # Updated path
from Data.nba_data_bridge import NBADataBridge

class RealSportsMarket(SportsMarket):
    """Sports Market that uses real NBA player data"""
    
    def __init__(self, monte_carlo_simulator):
        self.data_bridge = NBADataBridge(monte_carlo_simulator)
        self.players = {}  # Will be populated on demand
        self.available_players = self._get_available_players()
    
    def _get_available_players(self):
        """Get list of available NBA players"""
        try:
            from nba_api.stats.static import players
            all_players = players.get_active_players()
            # Return top 50 most popular players for performance
            popular_players = [
                "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo",
                "Nikola Jokic", "Luka Doncic", "Joel Embiid", "Jayson Tatum",
                "Damian Lillard", "Anthony Davis", "Jimmy Butler", "Paul George",
                "Kawhi Leonard", "Devin Booker", "Donovan Mitchell", "Trae Young",
                "Ja Morant", "Zion Williamson", "Karl-Anthony Towns", "Bradley Beal",
                "Kyrie Irving", "James Harden", "Russell Westbrook", "Chris Paul",
                "Draymond Green", "Klay Thompson", "Anthony Edwards", "LaMelo Ball",
                "Tyrese Haliburton", "Paolo Banchero", "Cade Cunningham", "Scottie Barnes",
                "Evan Mobley", "Franz Wagner", "Alperen Sengun", "Jalen Green",
                "Josh Giddey", "Anfernee Simons", "Tyler Herro", "Bam Adebayo",
                "Mikal Bridges", "OG Anunoby", "Pascal Siakam", "Fred VanVleet",
                "DeMar DeRozan", "Zach LaVine", "Nikola Vucevic", "Domantas Sabonis",
                "De'Aaron Fox", "CJ McCollum"
            ]
            return popular_players
        except:
            # Fallback list
            return ["LeBron James", "Stephen Curry", "Kevin Durant", "Giannis Antetokounmpo", "Nikola Jokic"]
    
    def get_player_data(self, player_name):
        """Get player data, fetching from NBA API if needed"""
        if player_name not in self.players:
            # Fetch real data
            player_data = self.data_bridge.get_real_player_data(player_name)
            if player_data:
                self.players[player_name] = player_data
            else:
                return None
        return self.players.get(player_name)
    
    def list_players(self):
        """List available NBA players"""
        return self.available_players
    
    def search_player(self, search_term):
        """Search for players by name"""
        matches = []
        for player in self.available_players:
            if search_term.lower() in player.lower():
                matches.append(player)
        return matches