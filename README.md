# 🏀 Sports Market Simulation System

A comprehensive Python system for simulating stock market-style trading of athletes based on their performance statistics.

## Overview

This system implements three core algorithms for the Sports Market concept:

1. **Base Price Algorithm** - Sets initial stock prices for rookies and non-rookies
2. **Intragame Simulation Algorithm** - Updates prices based on single game performance
3. **Timeframe/Season Algorithm** - Adjusts prices over weekly, monthly, or seasonal periods

## Features

- **Stored Player Data**: Pre-loaded game-by-game stats for Malik Monk, Devin Booker, and Miles McBride
- **Multiple Algorithms**: Choose from base price, intragame, or timeframe simulations
- **Custom Input**: Input your own player stats for any simulation
- **Detailed Outputs**: See all intermediate calculations and final price changes
- **Interactive Interface**: User-friendly command-line interface

## Installation

1. Clone or download the project files
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main simulation system:
```bash
python main.py
```

### Available Options

1. **Base Price (Rookie/Non-Rookie)** - Calculate initial stock prices
2. **Intragame Simulation** - Update prices based on single game performance
3. **Timeframe/Season Simulation** - Adjust prices over time periods
4. **Custom Input** - Use your own player data
5. **Exit** - Quit the program

### Stored Players

The system includes detailed game-by-game data for:

- **Malik Monk** (2024-2025): 65 games with full stat tracking
- **Devin Booker** (2024-2025): 60 games with complete performance data
- **Miles McBride** (2024-2025): 65 games with comprehensive statistics

## Algorithm Details

### Base Price Algorithm

**Non-Rookie Players:**
- Uses PRS (Player Rating Score) based on league averages
- Calculates z-scores for each stat category
- Applies weighted formula: `Base Price = 10 + (PRS × 50)`
- Range: $10 - $60

**Rookie Players:**
- Uses DRS (Draft Rating Score) based on draft position
- Formula: `DRS = max(0.1, 1 – log2(pick) / log2(60))`
- Base Price: `10 + (DRS × 25)`
- Range: $12.5 - $35

### Intragame Simulation Algorithm

1. **Input**: Actual game stats (PTS, REB, AST, TO, STOCKS, 3PM, TS%)
2. **Projected Stats**: `0.5 × Season Avg + 0.5 × Last 5 Games Avg`
3. **Z-Scores**: `(actual - projected) / std dev` (TO inverted)
4. **PPS**: Weighted z-score combination
5. **DIS**: Demand Imbalance Score calculation
6. **Price Change**: Dampened delta applied to current price

### Timeframe/Season Algorithm

**Timeframes:**
- **Weekly**: Past 4 games
- **Monthly**: Past 12 games  
- **Season**: Full season stats

**Process:**
1. Calculate projected stats per game based on timeframe
2. Compute actual averages over the period
3. Calculate z-scores and PPS
4. Apply timeframe-specific dampening rules
5. Update stock price

## File Structure

```
sports_market_project/
├── main.py                    # Main interface and user interaction
├── sports_market.py           # Player data storage and management
├── base_price_algorithm.py    # Base price calculation algorithms
├── intragame_algorithm.py     # Single game simulation algorithm
├── timeframe_algorithm.py     # Timeframe/season simulation algorithm
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Example Usage

### Base Price Calculation
```
🏀 SPORTS MARKET SIMULATION SYSTEM 🏀
==================================================
Available Players:
1. Malik Monk
2. Devin Booker
3. Miles McBride

Algorithms:
1. Base Price (Rookie/Non-Rookie)
2. Intragame Simulation
3. Timeframe/Season Simulation
4. Custom Input
5. Exit
==================================================

Enter your choice (1-5): 1
```

### Intragame Simulation
```
🎯 INTRAGAME SIMULATION
------------------------------
Use stored player data? (y/n): y

Available players:
1. Malik Monk
2. Devin Booker
3. Miles McBride

Select player (number): 1

Using Malik Monk data:
Actual Game: PTS=2, REB=0, AST=1, TO=1, STOCKS=0, 3PM=0, TS%=0.333
Enter current stock price: $25.50

📊 INTRAGAME SIMULATION RESULTS:
Projected Stats: (15.2, 3.1, 5.8, 2.3, 1.2, 2.1, 0.567)
Standard Deviations: {'pts': 4.5, 'reb': 1.7, 'ast': 2.2, 'to': 1.1, 'stocks': 0.8, 'threepm': 1.1, 'ts%': 0.07}
Z-Scores: {'pts': -2.93, 'reb': -1.82, 'ast': -2.18, 'to': 1.18, 'stocks': -1.50, 'threepm': -1.91, 'ts%': -3.34}
PPS: -2.45
DIS: -0.37
Raw Delta: -2.01
Dampened Delta: -0.80
Old Price: $25.50
New Price: $5.10
Price Change: -80.00%
```

## Dependencies

- **numpy**: Numerical computations and array operations
- **scipy**: Statistical functions (normal CDF for z-score transformations)

## Contributing

This system is designed for the Sports Market concept where athletes are traded like stocks. The algorithms are based on performance metrics and simulated market demand.

## License

This project is for educational and research purposes related to sports analytics and market simulation. 