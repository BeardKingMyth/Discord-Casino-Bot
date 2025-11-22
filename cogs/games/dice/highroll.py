from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances

class HighRoll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()

    @commands.command(name="highroll")
    async def highroll(self, ctx, bet: int):
        """
        Classic High Roll: you roll a die, the house rolls a die,
        highest number wins. Usage: !highroll <bet>
        """
        user_id = str(ctx.author.id)

        # Initialize balance if player is new
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        # Validate bet
        if bet <= 0:
            await ctx.send("Your bet must be greater than zero.")
            return
        
        if bet > self.balances[user_id]:
            await ctx.send("You don't have enough money for that bet.")
            return

        # Player and House rolls
        player_roll = random.randint(1, 6)
        house_roll = random.randint(1, 6)

        # Determine winner
        if player_roll > house_roll:
            self.balances[user_id] += bet
            result = (f"You rolled **{player_roll}**. "
                      f"The house rolled **{house_roll}**. "
                      f"You won ${bet}! Your new balance is ${self.balances[user_id]}.")
        elif player_roll < house_roll:
            self.balances[user_id] -= bet
            result = (f"You rolled **{player_roll}**. "
                      f"The house rolled **{house_roll}**. "
                      f"You lost ${bet}. Your new balance is ${self.balances[user_id]}.")
        else:
            result = (f"You rolled **{player_roll}**. "
                      f"The house rolled **{house_roll}**. "
                      f"It's a tie — no money changes hands.")

        save_balances(self.balances)
        await ctx.send(result)

async def setup(bot):
    await bot.add_cog(HighRoll(bot))
