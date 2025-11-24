from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

# Probabilities for two dice totals
# 2-12 : number of ways to roll that total with two dice
PROBABILITIES = {
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 6,
    8: 5,
    9: 4,
    10: 3,
    11: 2,
    12: 1
}

class TargetRoll(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        print("Targetroll cog initialized.")
        self.bot = bot
        self.balances = {}
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()

    async def async_init(self):
        self.balances = await load_balances()
        print("Targetroll cog async initialized")


    @commands.command(name="target")
    async def target(self, ctx, bet: int, target: int):
        """
        Bet on a dice total (2-12).
        Usage: !target <bet> <target_number>
        """
        user_id = str(ctx.author.id)

        # Use helper functions
        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        # Initialize balance if new user
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        # Validate bet
        if bet <= 0:
            await ctx.send("Your bet must be greater than zero.")
            return

        if bet > self.balances[user_id]:
            await ctx.send("You don’t have enough money for that bet.")
            return

        # Validate target
        if target < 2 or target > 12:
            await ctx.send("Your target must be between 2 and 12.")
            return

        # Roll the dice
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        total = die1 + die2

        # Calculate payout
        # Total combinations = 36, payout proportional to probability
        ways = PROBABILITIES[target]
        payout = round(bet * (36 / ways))

        # Win or lose
        if total == target:
            self.balances[user_id] += payout
            message = (
                f"You rolled {die1} + {die2} = {total}\n"
                f"You hit your target! You win ${payout}. "
                f"New balance: ${self.balances[user_id]}"
            )
        else:
            self.balances[user_id] -= bet
            message = (
                f"🎲 You rolled {die1} + {die2} = {total}\n"
                f"Sorry, you missed your target. You lose ${bet}. "
                f"New balance: ${self.balances[user_id]}"
            )

        await save_balances(self.balances)
        await ctx.send(message)


async def setup(bot):
    print("Targetroll cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    cog = TargetRoll(bot, frozen_users=frozen, banned_users=banned)
    await bot.add_cog(cog)
    await cog.async_init()  # now safely await DB setup

