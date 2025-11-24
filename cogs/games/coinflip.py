from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

class CoinFlip(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        print("Coinflip cog initialized.")
        self.bot = bot
        self.balances = load_balances()
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()

    @commands.command(name="coinflip")
    async def coinflip(self, ctx, bet: int, choice: str):
        """Flip a coin and bet money. Usage: !coinflip <bet> <heads/tails>"""
        user_id = str(ctx.author.id)

        if is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return
        
        # Check if user exists in balances
        if user_id not in self.balances:
            self.balances[user_id] = 1000
        
        # Validate bet
        if bet <= 0:
            await ctx.send("Bet must be a positive number!")
            return
        if bet > self.balances[user_id]:
            await ctx.send("You don’t have enough money for that bet!")
            return
        
        # Validate choice
        choice = choice.lower()
        if choice not in ["heads", "tails"]:
            await ctx.send("Choice must be 'heads' or 'tails'!")
            return

        # Flip the coin
        result = random.choice(["heads", "tails"])
        if choice == result:
            self.balances[user_id] += bet
            outcome = f"You won! It was {result}. You now have ${self.balances[user_id]}"
        else:
            self.balances[user_id] -= bet
            outcome = f"You lost! It was {result}. You now have ${self.balances[user_id]}"

        save_balances(self.balances)
        await ctx.send(outcome)

async def setup(bot):
    print("Coinflip cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(CoinFlip(bot, frozen_users=frozen, banned_users=banned))

