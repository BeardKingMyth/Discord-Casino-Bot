from discord.ext import commands
from utils.helpers import load_balances, save_balances, is_user_frozen, is_user_banned

class Economy(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        self.bot = bot
        self.balances = {}  # placeholder
        self.frozen_users = frozen_users if frozen_users is not None else set()
        self.banned_users = banned_users if banned_users is not None else set()
        print("Economy cog initialized")

    async def async_init(self):
        self.balances = await load_balances()
        print("Economy cog async initialized")


    @commands.command(name="balance")
    async def balance(self, ctx):
        user_id = str(ctx.author.id)

        # Use helper functions
        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        # Ensure player exists
        if user_id not in self.balances:
            self.balances[user_id] = 1000
            await save_balances(self.balances)
        await ctx.send(f"{ctx.author.name}, you have ${self.balances[user_id]}")

async def setup(bot):
    # Pass in frozen/banned sets from the admin cog if desired
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    
    cog = Economy(bot, frozen_users=frozen, banned_users=banned)
    await bot.add_cog(cog)
    await cog.async_init()  # now safely await DB setup
    print("Economy cog loaded")
