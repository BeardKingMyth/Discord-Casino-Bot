from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances

class Doubles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()

    @commands.command(name="doubles")
    async def doubles(self, ctx, bet: int, choice: str):
        """
        Play the Doubles dice game.
        Usage: !doubles <bet> <odds/evens/doubles>
        """
        user_id = str(ctx.author.id)

        # Initialize user balance if needed
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        # Validate bet
        if bet <= 0:
            await ctx.send("Your bet must be more than zero.")
            return
        
        if bet > self.balances[user_id]:
            await ctx.send("You don't have enough money for that bet.")
            return

        # Validate choice
        choice = choice.lower()
        if choice not in ["odds", "evens", "doubles"]:
            await ctx.send("Your choice must be 'odds', 'evens', or 'doubles'.")
            return

        # Roll dice
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        is_double = (d1 == d2)

        # Determine outcome
        if choice == "doubles":
            if is_double:
                winnings = bet * 10
                self.balances[user_id] += winnings
                result_msg = (
                    f"You rolled **{d1} + {d2} = {total}** — a **DOUBLE!**\n"
                    f"You won **${winnings}**. You now have **${self.balances[user_id]}**."
                )
            else:
                self.balances[user_id] -= bet
                result_msg = (
                    f"You rolled **{d1} + {d2} = {total}** — not a double.\n"
                    f"You lost **${bet}**. You now have **${self.balances[user_id]}**."
                )

        elif choice == "odds":
            if total % 2 == 1:
                self.balances[user_id] += bet
                result_msg = (
                    f"You rolled **{d1} + {d2} = {total}** — **odd**.\n"
                    f"You won **${bet}**. You now have **${self.balances[user_id]}**."
                )
            else:
                self.balances[user_id] -= bet
                result_msg = (
                    f"You rolled **{d1} + {d2} = {total}** — **even**.\n"
                    f"You lost **${bet}**. You now have **${self.balances[user_id]}**."
                )

        elif choice == "evens":
            if total % 2 == 0:
                self.balances[user_id] += bet
                result_msg = (
                    f"You rolled **{d1} + {d2} = {total}** — **even**.\n"
                    f"You won **${bet}**. You now have **${self.balances[user_id]}**."
                )
            else:
                self.balances[user_id] -= bet
                result_msg = (
                    f"You rolled **{d1} + {d2} = {total}** — **odd**.\n"
                    f"You lost **${bet}**. You now have **${self.balances[user_id]}**."
                )

        save_balances(self.balances)
        await ctx.send(result_msg)

async def setup(bot):
    await bot.add_cog(Doubles(bot))
