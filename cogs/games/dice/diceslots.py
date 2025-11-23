from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances

class DiceSlots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()

    @commands.command(name="diceslots")
    async def diceslots(self, ctx, bet: int):
        """Roll 3 dice and win based on combinations! Usage: !diceslots <bet>"""
        user_id = str(ctx.author.id)

        # Initialize balance if new user
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        # Validate bet
        if bet <= 0:
            await ctx.send("Your bet must be greater than zero.")
            return
        if bet > self.balances[user_id]:
            await ctx.send("You don't have enough money for that bet.")
            return

        # Roll 3 dice
        dice = [random.randint(1, 6) for _ in range(3)]

        # Determine result
        payout = 0
        message = ""

        # Triple (all three the same)
        if dice[0] == dice[1] == dice[2]:
            payout = bet * 5
            message = f"Triple {dice[0]}! You win ${payout}!"
        # Two-of-a-kind
        elif dice[0] == dice[1] or dice[0] == dice[2] or dice[1] == dice[2]:
            payout = bet * 2
            message = f"Two of a kind ({dice})! You win ${payout}!"
        # Straight (any sequence of 3 numbers)
        elif sorted(dice) in ([1,2,3], [2,3,4], [3,4,5], [4,5,6]):
            payout = bet * 3
            message = f"Straight {dice}! You win ${payout}!"
        # Loss
        else:
            payout = -bet
            message = f"You rolled {dice}. You lost ${bet}."

        # Update balance
        self.balances[user_id] += payout
        save_balances(self.balances)

        # Send result
        await ctx.send(f"{ctx.author.name} rolled {dice}.\n{message}\nNew balance: ${self.balances[user_id]}")

async def setup(bot):
    await bot.add_cog(DiceSlots(bot))
