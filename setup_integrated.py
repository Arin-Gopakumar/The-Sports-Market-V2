# setup_integrated.py
#!/usr/bin/env python3
"""
Setup script for the integrated NBA Monte Carlo + Sports Market system
"""

import subprocess
import sys
import os

def install_requirements():
    """Install all required packages"""
    print("📦 Installing required packages...")
    
    # Combined requirements
    requirements = [
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "nba_api>=1.1.0",
        "requests>=2.25.0"
    ]
    
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", req])
    
    print("✅ All packages installed successfully!")

def create_directory_structure():
    """Ensure proper directory structure"""
    print("\n📁 Setting up directory structure...")
    
    dirs = ["cache", "logs", "data"]
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created {dir_name}/")

def test_nba_api():
    """Test NBA API connection"""
    print("\n🏀 Testing NBA API connection...")
    try:
        from nba_api.stats.static import players
        active_players = players.get_active_players()
        print(f"✅ NBA API working! Found {len(active_players)} active players")
        return True
    except Exception as e:
        print(f"❌ NBA API test failed: {e}")
        return False

def create_example_config():
    """Create example configuration file"""
    config_content = """# config.json
{
    "monte_carlo": {
        "default_simulations": 10000,
        "cache_enabled": true,
        "cache_ttl_hours": 24
    },
    "market": {
        "default_base_price": 25.0,
        "price_floor": 1.0,
        "price_ceiling": 100.0
    },
    "data": {
        "default_season": "2023-24",
        "max_players_to_load": 50
    }
}
"""
    
    with open("config.json", "w") as f:
        f.write(config_content)
    
    print("✅ Created config.json")

def main():
    print("🚀 INTEGRATED NBA SPORTS MARKET SETUP")
    print("=" * 50)
    
    # Install packages
    install_requirements()
    
    # Create directories
    create_directory_structure()
    
    # Test NBA API
    api_working = test_nba_api()
    
    # Create config
    create_example_config()
    
    print("\n" + "=" * 50)
    print("✅ SETUP COMPLETE!")
    print("\nTo run the integrated system:")
    print("  python main_integrated.py")
    print("\nTo run in demo mode:")
    print("  python main_integrated.py --demo")
    
    if not api_working:
        print("\n⚠️  WARNING: NBA API connection failed.")
        print("The system will use synthetic data as fallback.")

if __name__ == "__main__":
    main()