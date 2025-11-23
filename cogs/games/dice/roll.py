import random
from discord.ext import commands

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roll")
    async def roll(self, ctx, *, dice: str = None):
        """
        Roll dice.
        Default: !roll → 1d20
        Format: !roll 3d6 or !roll 2 d12
        """

        # DEFAULT ROLL
        if dice is None:
            result = random.randint(1, 20)
            return await ctx.send(f"{ctx.author.mention} rolled **1d20 → {result}**")

        # CLEAN INPUT (remove spaces)
        dice = dice.lower().replace(" ", "")

        # ─────────────────────────────────────────────
        # MATCHING FORMATS:
        #   "3d6"    → 3 dice, 6 sides
        #   "d6"     → 1 die, 6 sides
        #   "6"      → 1 die, 6 sides (shortcut)
        # ─────────────────────────────────────────────
        if "d" in dice:
            parts = dice.split("d")
            try:
                num = int(parts[0]) if parts[0] else 1
                sides = int(parts[1])
            except ValueError:
                return await ctx.send("Invalid format. Use `!roll 3d6`.")

        else:
            # if only a number: treat as 1dX
            try:
                num = 1
                sides = int(dice)
            except ValueError:
                return await ctx.send("Invalid format. Use `!roll 3d6`.")

        # LIMITS (avoid abuse/flooding)
        if num < 1 or num > 100:
            return await ctx.send("Number of dice must be between 1 and 100.")
        if sides < 2 or sides > 1000:
            return await ctx.send("Dice sides must be between 2 and 1000.")

        rolls = [random.randint(1, sides) for _ in range(num)]
        total = sum(rolls)

        if num == 1:
            return await ctx.send(
                f"{ctx.author.mention} rolled **1d{sides} → {rolls[0]}**"
            )

        return await ctx.send(
            f"{ctx.author.mention} rolled **{num}d{sides}** → {rolls}\n"
            f"**Total: {total}**"
        )


async def setup(bot):
    await bot.add_cog(Roll(bot))