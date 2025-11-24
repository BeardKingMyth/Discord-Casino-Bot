from discord.ext import commands
import json
from pathlib import Path
from datetime import datetime, timedelta
import random
from utils.helpers import load_balances, save_balances, load_claims, save_claims, is_user_banned, is_user_frozen

class Daily(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        self.bot = bot
        self.balances = load_balances()
        self.frozen_users = frozen_users if frozen_users is not None else set()
        self.banned_users = banned_users if banned_users is not None else set()
        print("Daily cog initialized.")
        self.balances = load_balances()
        self.claims = load_claims()

    @commands.command(name="daily")
    async def daily(self, ctx):
        """Claim your daily reward (24h cooldown)."""
        user_id = str(ctx.author.id)
        now = datetime.now(datetime.timezone.utc)

        # Use helper functions
        if is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

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
    # Pass in frozen/banned sets from the admin cog if desired
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(Daily(bot, frozen_users=frozen, banned_users=banned))
