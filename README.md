# Monopoly Simulator

_This is Monopoly Simulator version 2, rewritten from scratch. For the previous version of the simulator, check the "version-1" branch. This one is much better, though._

The Monopoly Simulator does exactly what it says: it simulates playing a Monopoly game with several players. It handles player movements on the board, property purchases, rent payments, and actions related to Community Chest and Chance cards. On my M1 Mac laptop, it can play about 200-300 games per second. The resulting data includes the winning (or, more precisely, "not losing" or "survival") rates for players, game length, and other metrics.

The simulator allows for assigning different behavior rules to each player, such as "don't buy things if you have less than 200 dollars" or "never build hotels." Pitting a player with specific behaviors against regular players allows for testing whether such strategies are beneficial.

The simulator is a hobby project. There are still many things I am working on, and I hope to improve them someday.

## How to Use

1. Edit `settings.py` to set the parameters you want for your simulation.
2. Run `simulate.py` to start the simulation.
3. Marvel at the results at the console and in the gamelog.txt, datalog.txt

## Implemented Rules

The rules in this simulation are based on Hasbro's official manual for playing Monopoly, with the potential for tweaking parameters here and there to see how they affect the game's results. Some of the more complex rules are still a "Work In Progress"; see the TODO section for details.

## Player Behavior

Players in the simulation follow the most common-sense logic to play, which is:

- Buy whatever you land on.
- Build at the first opportunity.
- Unmortgage property as soon as possible.
- Get out of jail on doubles; do not pay the fine until you have to.
- Maintain a certain cash threshold below which the player won't buy, improve, or unmortgage property.
- Trade 1-on-1 with the goal of completing the player's monopoly. Players who give cheaper property should provide compensation equal to the difference in the official price. Don't agree to a trade if the properties are too unequal.

## Experiments

The main use of the simulator is to run experiments, either testing game rules or player behaviors.

### Testing Game Rules

You can run two simulations with different game rules and see if the outcomes are different.
For example:

- Will the Free Parking rule affect the average player survival time? (Answer: Not really)
- Will reducing salary reduce the number of draw games? (Answer: Yes, very much so)

### Testing Player Behavior

Another way to use the simulator is to test various player behavior traits to see if they affect a player's winning rate (or, to be precise, survival rate). For that, you run a simulation with three "Standard" players and one "Experiment" player that follows different rules. The difference in the survival rate would indicate if this behavior was beneficial.
For example:

- Is ignoring Indigo properties a good idea? (Answer: No, it would lower the survival rate by about 10-12%)
- Is it better to have a $500 unspendable threshold or $0? (Answer: $0 is better, it raises the survival rate by about 15-20%)

## Adjustable Parameters (and Their Defaults)

### Simulation-Related:
- Number of games to play (1000)
- Max number of turns (1000)
- Random seed to start with, for replicable simulations

### Game-Related:
- Number of players (4)
- Shuffling player order between simulations (True)
- Starting money, either the same for all or per player going 1st, 2nd, etc. ($1500 for all)
- Starting properties, allows to simulate specific mid-game situation (nothing for all, like in regular game start) 
 
### Rules-Related:
- Number of dice (2)
- Number of sides on a die (6)
- Available houses (36)
- Available hotels (12)
- Salary, i.e., money for passing GO ($200)
- Luxury Tax ($200)
- Income tax ($200 or 10%)
- Mortgage value (50%)
- Mortgage cost (10%)
- Exit Jail fine ($50)
- Free Parking accumulates all player fines to give to whoever lands on it (False)

### Player Behavior-Related:

- Threshold below which not to spend money ($200)
- Ignore property of a certain color (None)
- Participate in trades (True)
- Maximum difference between property values to agree to a trade ($200 or 2x)

## TODOs:

As I mentioned, it's a hobby project, so no guarantees here. But if I ever get to improve on this simulator, these are the things I'd do:

### Game Rules That Are Still Not Perfectly in Line with Official Rules:
- Auctions (none right now)
- Whoever buys a bankrupt player's property has to unmortgage it right away or pay more.
- How to mortgage property with hotels on it (this is somewhat ambiguous in official rules).

### Simulation-Related:
- Log out players' net worth.

### Game-Related:
- Adjustable max jail time.

### Player Behavior-Related:
- Three-way trades.
- Different building strategies.
- Auctioning strategies.

### Experiments to Set Up:
- Is ignoring property ever beneficial?
- Best jail behavior.
- Best unspendable cash threshold.
- Is a negative unspendable cash threshold beneficial?
- What is fair starting money?
- What is a fair trade price?
- What is a fair auction price?
