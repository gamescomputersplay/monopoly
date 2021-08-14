<!-- 
SPDX-FileCopyrightText: 2021 Games Computers Play, nfitzen, and nopeless

SPDX-License-Identifier: CC0-1.0
-->

# Monopoly simulator

## Original creator: Games Computer Play

* YouTube: https://www.youtube.com/channel/UCTrp88f-QJ1SqKX8o5IDhWQ

# Config file (optional)

`config.py` allows dynamic variable loading  
It is more versitle than `.env` files

example:
```py
log=True # disables override logs if False (default True)
showMap=True # overrides the showmap=False option in the main file
```

# Watching changes

Powershell:  
`get-content log.txt -wait -tail 30`

Bash:  
`tail log.txt -f`

## Copyright

Copyright (C) 2021 gamescomputersplay and nopeless

All code is licensed under [`GPL-3.0-or-later`].
That is, the GNU General Public License, either version 3,
or (at your option) any later version.
The [gitignore](.gitignore) and [requirements](requirements.txt) files are
marked with [CC0 1.0]. This README is also marked with [CC0 1.0].

See the [LICENSES](LICENSES/) folder for copies of the licenses.

[`GPL-3.0-or-later`]: https://spdx.org/licenses/GPL-3.0-or-later.html "GNU General Public License v3.0 or later"
[CC0 1.0]: https://creativecommons.org/publicdomain/zero/1.0/ "Creative Commons Zero 1.0 Universal"


== Intro ==


Monopoly Simulator simulates the game Monopoly (thanks, cap!). It throws dice, moves tokens, buys property, builds houses and hotels, tracks money, property, community chest and chance cards and so on. One game normally takes only a fraction of a second, so hundreds and thousands of games can be simulated in a matter of minutes.

Simulation can be used for testing various theories about Monopoly, such as the probability of an endless game, benefits and drawbacks of certain strategies and so on.

Some results of the tests done using this program can be found on the Youtube channel "Games Computers Play".

Program is not ideal: some features are still under development (jail time, variable starting capital), some may be disputed (trading logic), some were omitted completely (auctions). Still, it tries to be true to the original game and get as close as realistically possible to a game played by humans. 

There is quite a lot that can be done, so if you are interested in simulation Monopoly - feel free to fork or contribute to the project.

Note: I, GamesComputersPlay, the original author of the code, am not a professional programmer, so there can be some room for improvement regarding code quality. I am open to constructive criticism and help in this area.