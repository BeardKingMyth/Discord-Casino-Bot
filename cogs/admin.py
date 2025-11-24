from discord.ext import commands
from utils.helpers import load_balances, save_balances

class EconomyAdmin(commands.Cog):
    """Commands for admins/mods to adjust user balances."""

    def __init__(self, bot):
        self.bot = bot
        self.balances = load_balances()
        self.frozen_users = set()  # user_ids of frozen users
        self.banned_users = set()  # user_ids banned from economy
        print("EconomyAdmin cog initialized.")

    # -----------------------------
    #      Add/Subtract Balance
    # -----------------------------
    @commands.command(name="add_balance")
    @commands.has_permissions(manage_roles=True)
    async def add_balance(self, ctx, member: commands.MemberConverter, amount: int):
        """Add or remove balance from a user. Positive adds, negative removes."""
        user_id = str(member.id)

        if user_id not in self.balances:
            self.balances[user_id] = 1000  # default starting balance

        self.balances[user_id] += amount
        save_balances(self.balances)

        action = "added to" if amount >= 0 else "removed from"
        await ctx.send(
            f"${abs(amount)} has been {action} {member.display_name}'s balance. "
            f"New balance: ${self.balances[user_id]}"
        )

    # -----------------------------
    #      Set Balance Directly
    # -----------------------------
    @commands.command(name="set_balance")
    @commands.has_permissions(manage_roles=True)
    async def set_balance(self, ctx, member: commands.MemberConverter, amount: int):
        """Set a user's balance directly to a specific amount."""
        user_id = str(member.id)

        if amount < 0:
            await ctx.send("Balance cannot be set to a negative value.")
            return

        self.balances[user_id] = amount
        save_balances(self.balances)

        await ctx.send(
            f"{member.display_name}'s balance has been set to ${self.balances[user_id]}"
        )

    # -----------------------------
    #      Freeze Player
    # -----------------------------
    @commands.command(name="freeze_player")
    @commands.has_permissions(manage_roles=True)
    async def freeze_player(self, ctx, member: commands.MemberConverter):
        user_id = str(member.id)
        self.frozen_users.add(user_id)
        await ctx.send(f"{member.display_name} is now frozen and cannot play any games.")

    # -----------------------------
    #      Unfreeze Player
    # -----------------------------
    @commands.command(name="unfreeze_player")
    @commands.has_permissions(manage_roles=True)
    async def unfreeze_player(self, ctx, member: commands.MemberConverter):
        user_id = str(member.id)
        self.frozen_users.discard(user_id)
        await ctx.send(f"{member.display_name} has been unfrozen and can play again.")

    # -----------------------------
    #      Ban from Economy
    # -----------------------------
    @commands.command(name="ban_economy")
    @commands.has_permissions(manage_roles=True)
    async def ban_economy(self, ctx, member: commands.MemberConverter):
        user_id = str(member.id)
        self.banned_users.add(user_id)
        await ctx.send(f"{member.display_name} has been banned from the economy system.")

    # -----------------------------
    #      Unban from Economy
    # -----------------------------
    @commands.command(name="unban_economy")
    @commands.has_permissions(manage_roles=True)
    async def unban_economy(self, ctx, member: commands.MemberConverter):
        user_id = str(member.id)
        self.banned_users.discard(user_id)
        await ctx.send(f"{member.display_name} has been unbanned from the economy system.")

    # -----------------------------
    #      Mass Payout
    # -----------------------------
    @commands.command(name="mass_payout")
    @commands.has_permissions(manage_roles=True)
    async def mass_payout(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("Payout amount must be positive.")
            return
        for user_id in self.balances:
            self.balances[user_id] += amount
        save_balances(self.balances)
        await ctx.send(f"Mass payout complete! Every user received ${amount}.")

# -----------------------------
#      Setup Cog
# -----------------------------
async def setup(bot):
    print("EconomyAdmin cog loaded.")
    await bot.add_cog(EconomyAdmin(bot))
