#!/usr/bin/env python3
"""
Setup script for the Enhanced NBA Monte Carlo + Sports Market system
"""

import subprocess
import sys
import os

def install_enhanced_requirements():
    """Install all required packages for enhanced system"""
    print("📦 Installing enhanced system requirements...")
    
    requirements = [
        "pandas>=1.5.0",
        "numpy>=1.21.0", 
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "nba_api>=1.1.0",
        "requests>=2.25.0",
        "python-dateutil>=2.8.0"
    ]
    
    for req in requirements:
        print(f"Installing {req}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not install {req}: {e}")
    
    print("✅ All packages installed!")

def test_imports():
    """Test if all required imports work"""
    print("\n🧪 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas")
    except ImportError:
        print("❌ pandas")
    
    try:
        import numpy as np
        print("✅ numpy")
    except ImportError:
        print("❌ numpy")
    
    try:
        from nba_api.stats.static import players
        print("✅ nba_api")
    except ImportError:
        print("❌ nba_api")
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests")
    
    try:
        from datetime import datetime, timedelta
        print("✅ datetime")
    except ImportError:
        print("❌ datetime")

def create_enhanced_config():
    """Create enhanced configuration file"""
    config_content = '''# enhanced_config.json
{
    "sportradar": {
        "api_key": "i9UB7laRVsN2jqUo8KuJOEL9EoGXSpVnT1Yo9mK5",
        "base_url": "https://api.sportradar.com/nba/trial/v8/en",
        "rate_limit_delay": 1.0,
        "cache_ttl_seconds": 300
    },
    "monte_carlo": {
        "default_simulations": 10000,
        "enhanced_variance": {
            "points": 0.10,
            "rebounds": 0.15,
            "assists": 0.15
        },
        "contextual_adjustments": {
            "superstar_injury_boost": 0.05,
            "starter_injury_boost": 0.02,
            "role_player_injury_boost": 0.005,
            "home_court_boost": 0.02,
            "away_game_penalty": -0.025,
            "back_to_back_penalty": -0.06,
            "rest_advantage_boost": 0.015
        }
    },
    "market": {
        "default_base_price": 30.0,
        "price_floor": 1.0,
        "price_ceiling": 100.0
    },
    "data": {
        "default_season": "2023-24",
        "priority_players": [
            "LeBron James", "Stephen Curry", "Kevin Durant", 
            "Giannis Antetokounmpo", "Nikola Jokic", "Luka Doncic"
        ]
    }
}
'''
    
    with open("enhanced_config.json", "w") as f:
        f.write(config_content)
    
    print("✅ Created enhanced_config.json")

def test_sportradar_api():
    """Test Sportradar API connection"""
    print("\n🏥 Testing Sportradar API...")
    
    try:
        from Data.sportradar_injuries_api import SportradarInjuriesAPI
        
        api = SportradarInjuriesAPI("i9UB7laRVsN2jqUo8KuJOEL9EoGXSpVnT1Yo9mK5")  # Your actual API key
        
        if api.test_api_connection():
            print("✅ Sportradar API connection successful!")
            return True
        else:
            print("❌ Sportradar API connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Sportradar API test failed: {e}")
        return False

def test_nba_api():
    """Test NBA API connection"""
    print("\n🏀 Testing NBA API...")
    
    try:
        from nba_api.stats.static import players
        active_players = players.get_active_players()
        print(f"✅ NBA API working! Found {len(active_players)} active players")
        return True
    except Exception as e:
        print(f"❌ NBA API test failed: {e}")
        return False

def create_directory_structure():
    """Create enhanced directory structure"""
    print("\n📁 Setting up enhanced directory structure...")
    
    dirs = [
        "cache",
        "logs", 
        "data",
        "MonteCarlo",
        "Data",
        "Core",
        "exports"
    ]
    
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created {dir_name}/")
        
        # Create __init__.py files for Python packages
        if dir_name in ["MonteCarlo", "Data", "Core"]:
            init_file = os.path.join(dir_name, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write(f"# {dir_name}/__init__.py\n")
                print(f"Created {init_file}")

def main():
    print("🚀 ENHANCED NBA SPORTS MARKET SETUP")
    print("=" * 60)
    print("Setting up enhanced system with:")
    print("  • Sportradar Injuries API integration")
    print("  • Enhanced Monte Carlo simulations") 
    print("  • Real game validation")
    print("  • Contextual adjustments")
    print("=" * 60)
    
    # Install packages
    install_enhanced_requirements()
    
    # Test imports
    test_imports()
    
    # Create directories
    create_directory_structure()
    
    # Create config
    create_enhanced_config()
    
    # Test APIs
    nba_working = test_nba_api()
    sportradar_working = test_sportradar_api()
    
    print("\n" + "=" * 60)
    print("✅ ENHANCED SETUP COMPLETE!")
    print("\nTo run the enhanced system:")
    print("  python main_integrated_enhanced.py")
    
    print("\n📊 System Status:")
    print(f"  NBA API: {'✅ Working' if nba_working else '❌ Failed'}")
    print(f"  Sportradar API: {'✅ Connected' if sportradar_working else '❌ Failed'}")
    
    if not sportradar_working:
        print("\n⚠️  WARNING: Sportradar API not working.")
        print("Enhanced injury context features will be limited.")
        print("The system will still work with simulated injury data.")
    
    if not nba_working:
        print("\n⚠️  WARNING: NBA API not working.")
        print("The system will use fallback synthetic data.")
    
    print("\n🎮 Ready to run enhanced demos with real NBA data!")

if __name__ == "__main__":
    main()