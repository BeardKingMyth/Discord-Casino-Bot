from discord.ext import commands
from utils.helpers import load_balances, save_balances

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()
        print("Economy cog initialized")

    @commands.command(name="balance")
    async def balance(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.balances:
            self.balances[user_id] = 1000
            save_balances(self.balances)
        await ctx.send(f"{ctx.author.name}, you have ${self.balances[user_id]}")

async def setup(bot):
    await bot.add_cog(Economy(bot))
    print("Economy cog loaded")
