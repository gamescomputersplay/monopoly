# Monopoly simulator

_This is Monopoly Simulator version 2, rewritten from scratch. For the previous version of the simulator, check the "version-1" branch. This one is much better, though._

The Monopoly Simulator does exactly what it says: it simulates playing a Monopoly game with several players. It handles player movements on the board, property purchases, rent payments, and actions related to Community Chest and Chance cards. On my M1 Mac laptop, it can play about 200-300 games per second. The resulting data includes the winning (or, more precisely, "not losing" or "survival") rates for players, game length, and other metrics.

The simulator allows for assigning different behavior rules to each player, such as "don't buy things if you have less than 200 dollars" or "never build hotels." Pitting a player with specific behaviors against regular players allows for testing whether such strategies are beneficial.

The simulator is a hobby project. There are still many things I am working on, and I hope to improve it someday.



TODOs:

Game related:

Simulation replated:
- log out players net worth

Behaviour related:
- three-way trade
- Auctions

Experiemnts:
- ignore property
- jail behaviour
- unspendable cache
- negative unspendable cache
- fair starting money
- fair trade price
- fair auction price
- build 4
