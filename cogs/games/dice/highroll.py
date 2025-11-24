from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

class HighRoll(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        print("Highroll cog initialized.")
        self.bot = bot
        self.balances = {}
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()

    async def async_init(self):
        self.balances = await load_balances()
        print("Highroll cog async initialized")

    @commands.command(name="highroll")
    async def highroll(self, ctx, bet: int):
        """
        Classic High Roll: you roll a die, the house rolls a die,
        highest number wins. Usage: !highroll <bet>
        """
        user_id = str(ctx.author.id)

        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return
        
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

        await save_balances(self.balances)
        await ctx.send(result)

async def setup(bot):
    print("Highroll cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    cog = HighRoll(bot, frozen_users=frozen, banned_users=banned)
    await bot.add_cog(cog)
    await cog.async_init()  # now safely await DB setup
