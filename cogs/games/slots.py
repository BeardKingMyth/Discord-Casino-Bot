from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_frozen, is_user_banned

# ============================
#   WEIGHTED SYMBOLS
# ============================
# Symbol : weight (higher = more common)
WEIGHTED_SYMBOLS = {
    "🍒": 40,
    "🍋": 30,
    "⭐": 20,
    "💎": 7,
    "7️⃣": 3
}

SYMBOL_LIST = list(WEIGHTED_SYMBOLS.keys())
SYMBOL_WEIGHTS = list(WEIGHTED_SYMBOLS.values())

# Symbol-specific multiplier based on rarity
SYMBOL_PAYOUT_MULTIPLIER = {
    "🍒": 1,    # common
    "🍋": 1,    # common
    "⭐": 2,    # uncommon
    "💎": 5,    # rare
    "7️⃣": 10   # very rare
}

# ============================
#     MACHINE DEFINITIONS
# ============================
SLOT_MACHINES = {
    "small": {
        "reels": 3,
        "label": "🎰 **3-Reel Classic Machine**"
    },
    "big": {
        "reels": 5,
        "label": "💎 **5-Reel High Roller Machine**"
    }
}

# ============================
#       SLOTS COG
# ============================

class Slots(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        print("Slots cog initialized.")
        self.bot = bot
        self.balances = load_balances()
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()

    @commands.command(name="slots")
    async def slots(self, ctx, machine: str, bet: int):
        """Play the slot machine! Usage: !slots <small/big> <bet>"""
        user_id = str(ctx.author.id)

        # Use helper functions
        if is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        # Ensure player exists
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        # Validate machine
        machine = machine.lower()
        if machine not in SLOT_MACHINES:
            valid = ", ".join(SLOT_MACHINES.keys())
            await ctx.send(f"Invalid machine type! Choose: {valid}")
            return

        config = SLOT_MACHINES[machine]
        reels = config["reels"]

        # Validate bet
        if bet <= 0:
            await ctx.send("Bet must be a positive number!")
            return
        if bet > self.balances[user_id]:
            await ctx.send("You don’t have enough money for that bet!")
            return

        # Deduct bet
        self.balances[user_id] -= bet

        # Spin weighted reels
        result = random.choices(
            SYMBOL_LIST,
            weights=SYMBOL_WEIGHTS,
            k=reels
        )

        # Count matches
        symbol_counts = {}
        for symbol in result:
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1

        # Determine winning symbol (highest multiplier + count)
        winning_symbol = max(
            symbol_counts,
            key=lambda k: (symbol_counts[k], SYMBOL_PAYOUT_MULTIPLIER[k])
        )
        max_match = symbol_counts[winning_symbol]

        # Calculate payout (minimum 2 matching symbols to win)
        if max_match >= 2:
            multiplier = SYMBOL_PAYOUT_MULTIPLIER[winning_symbol] * max_match
            winnings = bet * multiplier
            self.balances[user_id] += winnings
            outcome = (
                f"You matched **{max_match} {winning_symbol}**!\n"
                f"You won **${winnings}**!"
            )
        else:
            winnings = 0
            outcome = "No matches! You lost your bet."

        # Save balances
        save_balances(self.balances)

        # Output final message
        await ctx.send(
            f"{config['label']}\n"
            f"[ {' | '.join(result)} ]\n"
            f"{outcome}\n"
            f"New Balance: **${self.balances[user_id]}**"
        )

# Setup cog
async def setup(bot):
    print("Slots cog loaded.")
    # Pass in frozen/banned sets from the admin cog if desired
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(Slots(bot, frozen_users=frozen, banned_users=banned))
