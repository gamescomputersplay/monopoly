# Monopoly simulator

_This is Monopoly Simulator version 2, rewritten from scratch. For the previous version of the simulator, check the "version-1" branch. This one is much better, though._

The Monopoly Simulator does exactly what it says: it simulates playing a Monopoly game with several players. It handles player movements on the board, property purchases, rent payments, and actions related to Community Chest and Chance cards. On my M1 Mac laptop, it can play about 200-300 games per second. The resulting data includes the winning (or, more precisely, "not losing" or "survival") rates for players, game length, and other metrics.

The simulator allows for assigning different behavior rules to each player, such as "don't buy things if you have less than 200 dollars" or "never build hotels." Pitting a player with specific behaviors against regular players allows for testing whether such strategies are beneficial.

The simulator is a hobby project. There are still many things I am working on, and I hope to improve them someday.

## How to use

1. Edit setting.py for whatever parameters you want to have in your simulation
2. Run monopoly_simulator.py
3. Marvel at the results


## Implemented rules

The rules in this simulation are based on official Hasbro's manual for playing monopoly with potential of tweaking parameters here and there to see how they affect the results of the game. Some of the more complex rules are still "Work In progress", see the TODO section for details

## Player behavior

Players in the simulation follow the most common sense logic to play, which is:
- Buy whatever you have landed on
- Build at first opportunity
- Unmortgage the property as soon as possible
- Get out of jail on doubles, do not pay the fine until you have to
- Have a certain threshold of cash that the player wouldn't want to go below (he would not buy, improve, unmortgage property if it puts him below the threshold).
- Trade 1-on-1, with the goal of complete player's monopoly. Players who give cheaper property, should provide compensation, equal to the difference of the official price. Don't agree to a trade if the properties are too unequal.

## Experiments

The main use of the simulator is to run experiments - either testing game rules or player behaviors.

### Testing game rules

For that we can run 2 simulations with different game rules, and see if the outcome is different.
For example:
- will Free parking rule affect the average player survival time (answer: not really)
- will reducing salary reduce number of draw games (answer, yes, very much so)

### Testing player behavior

Another way to use the simulator is to test various player behavior traits to see if it affects this player winning rate (or, to be precise, survival rate). For that we run a simulation for three "Standard" players and one "Experiment" player that follows different rules. The difference in the survival rate would answer if this behavior was beneficial.
For example:
- Is ignoring Indigo properties a good idea? (answer: no, it would lower survival rate by about 10-12%)
- Is it better to have $500 unspendable threshold or $0 (answer: $0 is better, it raises survival rate by about 15-20%)

## Adjustable parameters (and their defaults)

### Simulation related:
- Number of games to play (1000)

### Game related:
- Max number of turns (1000)
- Random seed to start with, for replicable simulations
- Number of dice (2)
- Number of sides on a dice (6)
- Number of players (4)
- Shuffling player order between simulations (True)
- Starting money, either same for all or per player going 1st, 2nd etc ($1500 for all)
- Available houses (36)
- Available hotels (12)
- Salary, i.e. money for passing GO ($200)
- Luxury Tax ($200)
- Income tax (2$00 or 10%)
- Mortgage value (50%)
- Mortgage cost (10%)
- Exit Jail fine ($50)
- Free Parking accumulate all player fines to give to whoever lands on it (False)

### Player Behavior related:
- Threshold, below which not to spend money ($200)
- Ignore property of certain color (None)
- Participate in trades (True)
- Maximum difference between to property value to agree to trade ($200 or 2x)


## TODOs:

As I mentioned, it's a hobby project, so no guarantees here. But if I ever get to improve on this simulator these are the things I'd do:

### Game rules, that are still not perfectly in line with official rules:
- Auctions (none right now)
- Whoever buys bankrupt's player property has to unmortgage it right away or pay more
- How to mortgage property with hotels on it (this of is somewhat ambiguous in official rules)

### Simulation replated:
- log out players net worth

### Game related
- Adjustable max jail time

### Player Behavior related:
- Three-way trades
- Different building strategies
- Auctioning strategies

### Experiments to set up:
- is ignoring property ever beneficial
- best jail behavior
- best unspendable cache
- is negative unspendable cache beneficial
- what is fair starting money
- what is fair trade price
- what is fair auction price
