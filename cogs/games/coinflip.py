from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances

class CoinFlip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()

    @commands.command(name="coinflip")
    async def coinflip(self, ctx, bet: int, choice: str):
        """Flip a coin and bet money. Usage: !coinflip <bet> <heads/tails>"""
        user_id = str(ctx.author.id)
        
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
    await bot.add_cog(CoinFlip(bot))
