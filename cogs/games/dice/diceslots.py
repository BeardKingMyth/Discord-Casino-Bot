from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

class DiceSlots(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        print("Diceslots cog initialized.")
        self.bot = bot
        self.balances = load_balances()
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()


    @commands.command(name="diceslots")
    async def diceslots(self, ctx, bet: int):
        """Roll 3 dice and win based on combinations! Usage: !diceslots <bet>"""
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
    print("Diceslots cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(DiceSlots(bot, frozen_users=frozen, banned_users=banned))

