from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances

class OverUnder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()

    @commands.command(name="overunder")
    async def overunder(self, ctx, bet: int, choice: str):
        """
        Usage: !overunder <bet> <over/under/seven>
        Rolls 2 dice and pays out based on the result.
        """
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

        # Validate choice
        choice = choice.lower()
        if choice not in ["over", "under", "seven"]:
            await ctx.send("Your choice must be **over**, **under**, or **seven**.")
            return

        # Roll the dice
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2

        # Determine result
        if total > 7:
            result = "over"
        elif total < 7:
            result = "under"
        else:
            result = "seven"

        # Determine payout
        win = (choice == result)

        if win:
            if result == "seven":
                payout = bet * 4
                self.balances[user_id] += payout
                message = (
                    f"You hit **exactly 7**! Dice were {d1} and {d2} (Total: {total}).\n"
                    f"You win **${payout}**! New balance: ${self.balances[user_id]}."
                )
            else:
                payout = bet
                self.balances[user_id] += payout
                message = (
                    f"You called **{choice}** and won! Dice were {d1} and {d2} (Total: {total}).\n"
                    f"You win **${payout}**! New balance: ${self.balances[user_id]}."
                )
        else:
            self.balances[user_id] -= bet
            message = (
                f"You guessed **{choice}**, but it was **{result}**.\n"
                f"Dice were {d1} and {d2} (Total: {total}).\n"
                f"You lost **${bet}**. New balance: ${self.balances[user_id]}."
            )

        save_balances(self.balances)
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(OverUnder(bot))
