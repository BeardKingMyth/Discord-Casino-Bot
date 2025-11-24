from discord.ext import commands
import json
from pathlib import Path
from datetime import datetime, timedelta
import random
from utils.helpers import load_balances, save_balances, load_claims, save_claims

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Daily cog initialized.")
        self.balances = load_balances()
        self.claims = load_claims()

    @commands.command(name="daily")
    async def daily(self, ctx):
        """Claim your daily reward (24h cooldown)."""
        user_id = str(ctx.author.id)
        now = datetime.utcnow()

        # Ensure player exists
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        # Check last claim
        last_claim_str = self.claims.get(user_id)
        if last_claim_str:
            last_claim = datetime.fromisoformat(last_claim_str)
            if now - last_claim < timedelta(hours=24):
                remaining = timedelta(hours=24) - (now - last_claim)
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                await ctx.send(
                    f"{ctx.author.mention} You already claimed your daily reward! "
                    f"Try again in {hours}h {minutes}m {seconds}s."
                )
                return

        # Generate reward
        reward = random.randint(100, 500)  # Adjust range as needed
        self.balances[user_id] += reward
        self.claims[user_id] = now.isoformat()

        # Save data
        save_balances(self.balances)
        save_claims(self.claims)

        await ctx.send(
            f"{ctx.author.mention} You claimed your daily reward of **${reward}**! "
            f"New Balance: **${self.balances[user_id]}**"
        )

# Setup cog
async def setup(bot):
    print("Daily cog loaded.")
    await bot.add_cog(Daily(bot))
