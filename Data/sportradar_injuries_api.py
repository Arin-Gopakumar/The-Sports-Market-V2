#!/usr/bin/env python3
"""
Sportradar NBA Injuries API Integration
Handles fetching and processing NBA injury data for contextual adjustments
"""

import requests
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple, Optional

class SportradarInjuriesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sportradar.com/nba/trial/v8/en"
        self.headers = {
            "accept": "application/json"
        }
        self.cache = {}  # Simple cache to avoid repeated API calls
        self.last_request_time = 0
        self.rate_limit_delay = 1  # 1 second between requests for trial API
        
        # Player impact categories based on typical NBA roles
        self.superstar_keywords = [
            "lebron", "curry", "durant", "giannis", "jokic", "luka", "embiid", 
            "tatum", "butler", "leonard", "harden", "westbrook", "paul", "davis",
            "booker", "mitchell", "young", "morant", "williamson", "towns"
        ]
        
        self.starter_keywords = [
            # This will be determined dynamically based on minutes played
            # For now, we'll use a threshold-based approach
        ]
    
    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make API request with rate limiting"""
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request_time < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - (current_time - self.last_request_time))
        
        # Add API key as query parameter (not header)
        if '?' in endpoint:
            url = f"{self.base_url}{endpoint}&api_key={self.api_key}"
        else:
            url = f"{self.base_url}{endpoint}?api_key={self.api_key}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️  Rate limit exceeded. Waiting 60 seconds...")
                time.sleep(60)
                return self._make_request(endpoint)  # Retry once
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_current_injuries(self) -> Optional[Dict]:
        """Get current NBA injuries snapshot"""
        cache_key = "current_injuries"
        
        # Check cache (valid for 5 minutes due to 300 second TTL)
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if time.time() - cached_time < 300:  # 5 minutes
                return cached_data
        
        print("🏥 Fetching current NBA injuries...")
        data = self._make_request("/league/injuries.json")
        
        if data:
            self.cache[cache_key] = (time.time(), data)
            return data
        
        return None
    
    def get_daily_injuries(self, date: str) -> Optional[Dict]:
        """
        Get injuries for a specific date using Daily Injuries endpoint
        Args:
            date: Date in YYYY-MM-DD format
        """
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            year = date_obj.strftime("%Y")
            month = date_obj.strftime("%m")
            day = date_obj.strftime("%d")
            
            cache_key = f"daily_injuries_{date}"
            
            # Check cache
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if time.time() - cached_time < 3600:  # 1 hour for historical data
                    return cached_data
            
            print(f"🏥 Fetching injuries for {date}...")
            endpoint = f"/league/{year}/{month}/{day}/daily_injuries.json"
            data = self._make_request(endpoint)
            
            if data:
                self.cache[cache_key] = (time.time(), data)
                return data
            
            return None
            
        except ValueError as e:
            print(f"❌ Invalid date format: {date}. Use YYYY-MM-DD")
            return None
    
    def get_team_injuries_for_date(self, team_name: str, date: str) -> List[Dict]:
        """
        Get injuries for a specific team on a specific date
        Now uses the proper Daily Injuries endpoint
        """
        # Try Daily Injuries endpoint first (more accurate for historical dates)
        daily_injuries = self.get_daily_injuries(date)
        
        if daily_injuries and 'teams' in daily_injuries:
            for team in daily_injuries['teams']:
                if self._team_name_matches(team.get('name', ''), team_name):
                    team_players = team.get('players', [])
                    injured_players = []
                    
                    for player in team_players:
                        if 'injuries' in player and player['injuries']:
                            injured_players.extend(player['injuries'])
                    
                    return injured_players
        
        # Fallback to current injuries if daily injuries unavailable
        current_injuries = self.get_current_injuries()
        
        if current_injuries and 'teams' in current_injuries:
            for team in current_injuries['teams']:
                if self._team_name_matches(team.get('name', ''), team_name):
                    team_players = team.get('players', [])
                    injured_players = []
                    
                    for player in team_players:
                        if 'injuries' in player and player['injuries']:
                            injured_players.extend(player['injuries'])
                    
                    return injured_players
        
        return []
    
    def _team_name_matches(self, api_team_name: str, search_team_name: str) -> bool:
        """Check if team names match (flexible matching)"""
        api_name_lower = api_team_name.lower()
        search_name_lower = search_team_name.lower()
        
        # Direct match
        if search_name_lower in api_name_lower or api_name_lower in search_name_lower:
            return True
        
        # Common team name mappings
        team_mappings = {
            'warriors': ['golden state', 'gsw', 'golden state warriors'],
            'lakers': ['los angeles lakers', 'lal', 'la lakers'],
            'celtics': ['boston', 'bos', 'boston celtics'],
            'heat': ['miami', 'mia', 'miami heat'],
            'nuggets': ['denver', 'den', 'denver nuggets'],
            'bucks': ['milwaukee', 'mil', 'milwaukee bucks'],
            'suns': ['phoenix', 'phx', 'phoenix suns'],
            '76ers': ['philadelphia', 'sixers', 'phi', 'philadelphia 76ers'],
            'clippers': ['la clippers', 'lac', 'los angeles clippers'],
            'nets': ['brooklyn', 'bkn', 'brooklyn nets'],
            'knicks': ['new york', 'nyk', 'new york knicks'],
            'bulls': ['chicago', 'chi', 'chicago bulls'],
            'cavaliers': ['cleveland', 'cle', 'cleveland cavaliers'],
            'hawks': ['atlanta', 'atl', 'atlanta hawks'],
            'hornets': ['charlotte', 'cha', 'charlotte hornets'],
            'pistons': ['detroit', 'det', 'detroit pistons'],
            'pacers': ['indiana', 'ind', 'indiana pacers'],
            'magic': ['orlando', 'orl', 'orlando magic'],
            'wizards': ['washington', 'was', 'washington wizards'],
            'raptors': ['toronto', 'tor', 'toronto raptors'],
            'timberwolves': ['minnesota', 'min', 'minnesota timberwolves'],
            'thunder': ['oklahoma city', 'okc', 'oklahoma city thunder'],
            'trail blazers': ['portland', 'por', 'portland trail blazers', 'blazers'],
            'jazz': ['utah', 'uta', 'utah jazz'],
            'kings': ['sacramento', 'sac', 'sacramento kings'],
            'mavericks': ['dallas', 'dal', 'dallas mavericks'],
            'rockets': ['houston', 'hou', 'houston rockets'],
            'grizzlies': ['memphis', 'mem', 'memphis grizzlies'],
            'pelicans': ['new orleans', 'nop', 'new orleans pelicans'],
            'spurs': ['san antonio', 'sas', 'san antonio spurs']
        }
        
        for key, variations in team_mappings.items():
            if (key in search_name_lower and any(var in api_name_lower for var in variations)) or \
               (key in api_name_lower and any(var in search_name_lower for var in variations)):
                return True
        
        return False
    
    def categorize_player_impact(self, player_name: str, team_injuries: List[Dict] = None) -> str:
        """
        Determine if player is superstar/starter/role player
        Returns: "superstar", "starter", "role_player"
        """
        player_name_lower = player_name.lower()
        
        # Check if player is a known superstar
        for superstar in self.superstar_keywords:
            if superstar in player_name_lower:
                return "superstar"
        
        # Enhanced categorization based on full name matching
        superstar_full_names = [
            "lebron james", "stephen curry", "kevin durant", "giannis antetokounmpo",
            "nikola jokic", "luka doncic", "joel embiid", "jayson tatum",
            "damian lillard", "anthony davis", "jimmy butler", "paul george",
            "kawhi leonard", "devin booker", "donovan mitchell", "trae young",
            "ja morant", "zion williamson", "karl-anthony towns", "bradley beal",
            "kyrie irving", "james harden", "russell westbrook", "chris paul",
            "jaylen brown", "pascal siakam", "fred vanvleet"
        ]
        
        for superstar in superstar_full_names:
            if superstar in player_name_lower or player_name_lower in superstar:
                return "superstar"
        
        # If we have injury data with player info, use that for better categorization
        if team_injuries:
            for injury in team_injuries:
                # This would need more sophisticated logic based on the injury data structure
                # For now, default to starter if not superstar
                return "starter"
        
        # Default assumption for unknown players
        return "starter"  # Conservative assumption
    
    def calculate_injury_boost(self, team_name: str, date: str) -> Tuple[float, List[str]]:
        """
        Calculate total stat boost from missing players
        Returns: (boost_percentage, injured_player_details)
        """
        team_injuries = self.get_team_injuries_for_date(team_name, date)
        
        if not team_injuries:
            return 0.0, []
        
        total_boost = 0.0
        injury_details = []
        
        for injury in team_injuries:
            if 'player' not in injury:
                continue
                
            player = injury['player']
            player_name = player.get('full_name', 'Unknown Player')
            injury_status = injury.get('status', 'Unknown')
            
            # Only count players who are definitively OUT
            if injury_status.upper() in ['OUT', 'INACTIVE']:
                impact_level = self.categorize_player_impact(player_name, team_injuries)
                
                if impact_level == "superstar":
                    boost = 0.05  # 5%
                    injury_details.append(f"{player_name} - OUT (Superstar impact: +5.0%)")
                elif impact_level == "starter":
                    boost = 0.02  # 2%
                    injury_details.append(f"{player_name} - OUT (Starter impact: +2.0%)")
                else:  # role_player
                    boost = 0.005  # 0.5%
                    injury_details.append(f"{player_name} - OUT (Role player impact: +0.5%)")
                
                total_boost += boost
            
            elif injury_status.upper() in ['QUESTIONABLE', 'DOUBTFUL']:
                # Partial impact for questionable players
                impact_level = self.categorize_player_impact(player_name, team_injuries)
                
                if impact_level == "superstar":
                    boost = 0.02  # 2% for questionable superstar
                    injury_details.append(f"{player_name} - Questionable (Superstar impact: +2.0%)")
                elif impact_level == "starter":
                    boost = 0.01  # 1% for questionable starter
                    injury_details.append(f"{player_name} - Questionable (Starter impact: +1.0%)")
                else:
                    boost = 0.002  # 0.2% for questionable role player
                    injury_details.append(f"{player_name} - Questionable (Role player impact: +0.2%)")
                
                total_boost += boost
        
        return total_boost, injury_details
    
    def get_injury_context_for_game(self, player_team: str, opponent_team: str, date: str) -> Dict:
        """
        Get comprehensive injury context for both teams
        Returns detailed breakdown for market adjustment
        """
        print(f"🏥 Analyzing injury context for {date}...")
        
        # Get injury boosts for both teams
        player_team_boost, player_team_injuries = self.calculate_injury_boost(player_team, date)
        opponent_team_boost, opponent_team_injuries = self.calculate_injury_boost(opponent_team, date)
        
        # Player benefits from their own team's injuries (more usage)
        # Player may benefit slightly from opponent injuries (easier defense)
        total_boost = player_team_boost + (opponent_team_boost * 0.1)  # 10% of opponent injuries
        
        context = {
            'player_team_boost': player_team_boost,
            'opponent_team_boost': opponent_team_boost,
            'total_boost': total_boost,
            'player_team_injuries': player_team_injuries,
            'opponent_team_injuries': opponent_team_injuries,
            'has_injury_data': len(player_team_injuries) > 0 or len(opponent_team_injuries) > 0
        }
        
        return context
    
    def test_api_connection(self) -> bool:
        """Test if API connection is working"""
        print("🔍 Testing Sportradar API connection...")
        
        data = self.get_current_injuries()
        
        if data:
            print("✅ Sportradar API connection successful!")
            
            # Show some sample data
            if 'teams' in data:
                total_injuries = sum(len(team.get('injuries', [])) for team in data['teams'])
                print(f"📊 Found injury data for {len(data['teams'])} teams with {total_injuries} total injuries")
            
            return True
        else:
            print("❌ Sportradar API connection failed!")
            return False

# Test function
def test_sportradar_api():
    """Test the Sportradar API with the provided key"""
    api = SportradarInjuriesAPI("i9UB7laRVsN2jqUo8KuJOEL9EoGXSpVnT1Yo9mK5")  # Your actual API key
    
    # Test connection
    if api.test_api_connection():
        # Test injury context for a recent date
        context = api.get_injury_context_for_game("Lakers", "Warriors", "2024-03-20")
        print(f"\n📋 Sample injury context: {context}")
        
        # Test daily injuries
        daily_data = api.get_daily_injuries("2024-03-20")
        if daily_data:
            print(f"\n📅 Daily injuries data found for 2024-03-20")
        else:
            print(f"\n❌ No daily injuries data for 2024-03-20")
    else:
        print("❌ API test failed")
if __name__ == "__main__":
    test_sportradar_api()