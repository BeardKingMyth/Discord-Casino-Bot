from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

class OverUnder(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        print("Overunder cog initialized.")
        self.bot = bot
        self.balances = load_balances()
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()

    @commands.command(name="overunder")
    async def overunder(self, ctx, bet: int, choice: str):
        """
        Usage: !overunder <bet> <over/under/seven>
        Rolls 2 dice and pays out based on the result.
        """
        user_id = str(ctx.author.id)

        # Use helper functions
        if is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if is_user_frozen(user_id, self.frozen_users):
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
    print("Overunder cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(OverUnder(bot, frozen_users=frozen, banned_users=banned))

