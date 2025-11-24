# Discord Casino Bot

A modular Discord economy and gambling bot built using discord.py cogs. Features an expandable game system, admin economy controls, and persistent user balances.
---
## Features

### Economy

- User balances saved and loaded automatically.
- Admin commands to modify balances.
- Freeze and ban systems to prevent users from participating.

### Games

#### Dice Games

- Dice Blackjack
- Dice Slots
- Doubles
- High Roll
- Over/Under
- Roll
- Target Roll

#### Card Games

- Blackjack
- War (includes PvP challenge system)

#### Other Games

- Coin Flip
- Roulette
- Slots

### Daily Rewards

- !daily to claim a configurable daily payout.

---

## File Structure

cogs/

 ├─ games/
 
 │   ├─ cards/
 
 │   │   ├─ blackjack.py
 
 │   │   └─ war.py
 
 │   ├─ dice/
 
 │   │   ├─ dice_blackjack.py
 
 │   │   ├─ diceslots.py
 
 │   │   ├─ doubles.py
 
 │   │   ├─ highroll.py
 
 │   │   ├─ overunder.py
 
 │   │   ├─ roll.py
 
 │   │   └─ targetroll.py
 
 │   ├─ coinflip.py
 
 │   ├─ roulette.py
 
 │   └─ slots.py
 
 ├─ admin.py
 
 ├─ daily.py
 
 └─ economy.py
 

utils/

 └─ helpers.py

bot.py

---

## Requirements

- Python 3.10+
- discord.py 2.3+
- A Discord bot token

# Running the Bot

1. Create a .env file or otherwise supply your bot token.

2. Start the bot:

```python bot.py```

The bot will automatically load all cogs and create a balance file as needed.

# Notes

- All game logic is modular and can be expanded by adding new files to cogs/games/.
- Admin commands require the user to have the Manage Roles permission.
- Balances are stored using helper functions in utils/helpers.py.
- Main currently stores data in JSON files. Branch is in progress to implement database storage.
