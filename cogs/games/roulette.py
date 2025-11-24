from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

# ============================
#      ROULETTE COG
# ============================

class Roulette(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        self.bot = bot
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()
        print("Roulette cog initialized.")
        self.balances = {}

    async def async_init(self):
        self.balances = await load_balances()
        print("Roulette cog async initialized")


        # American roulette numbers
        self.numbers = [
            '0', '00', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
            '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
            '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32',
            '33', '34', '35', '36'
        ]

        self.red_numbers = {
            '1','3','5','7','9','12','14','16','18','19','21','23','25','27','30','32','34','36'
        }

        self.black_numbers = {
            '2','4','6','8','10','11','13','15','17','20','22','24','26','28','29','31','33','35'
        }

        # Dozens mapping
        self.dozen_mapping = {str(i): '1st' if 1<=i<=12 else '2nd' if 13<=i<=24 else '3rd' for i in range(1,37)}

        # Columns mapping
        self.column_mapping = {}
        for i in range(1, 37):
            if i % 3 == 1: self.column_mapping[str(i)] = 'Left'
            elif i % 3 == 2: self.column_mapping[str(i)] = 'Middle'
            else: self.column_mapping[str(i)] = 'Right'

    def get_color(self, number):
        if number in self.red_numbers:
            return 'Red'
        elif number in self.black_numbers:
            return 'Black'
        else:
            return 'Green'

    def determine_bet_type(self, bet_value):
        val_lower = bet_value.lower()
        if bet_value in self.numbers:
            return 'number'
        elif val_lower in ['red', 'black']:
            return 'color'
        elif val_lower in ['odd', 'even']:
            return 'odd_even'
        elif val_lower in ['high', 'low']:
            return 'high_low'
        elif val_lower in ['1st', '2nd', '3rd']:
            return 'dozen'
        elif val_lower in ['left', 'middle', 'right']:
            return 'column'
        else:
            return None

    def calculate_payout(self, bet_type, bet_value, number):
        # Returns multiplier
        if bet_type == 'number' and bet_value == number:
            return 35
        elif bet_type == 'color' and bet_value.lower() == self.get_color(number).lower():
            return 1
        elif bet_type == 'odd_even':
            if number in ['0', '00']:
                return 0
            if bet_value.lower() == 'odd' and int(number) % 2 == 1:
                return 1
            if bet_value.lower() == 'even' and int(number) % 2 == 0:
                return 1
        elif bet_type == 'high_low':
            if number in ['0', '00']:
                return 0
            if bet_value.lower() == 'high' and 19 <= int(number) <= 36:
                return 1
            if bet_value.lower() == 'low' and 1 <= int(number) <= 18:
                return 1
        elif bet_type == 'dozen':
            if number in self.dozen_mapping and self.dozen_mapping[number] == bet_value:
                return 2
        elif bet_type == 'column':
            if number in self.column_mapping and self.column_mapping[number].lower() == bet_value.lower():
                return 2
        return 0

    @commands.command(name="roulette")
    async def roulette(self, ctx, bet_value: str = None, amount: int = None):
        """Place a roulette bet. Bet type is detected automatically."""
        if bet_value is None or amount is None:
            await ctx.send(f"{ctx.author.mention} Usage: `!roulette <bet_value> <amount>`")
            return

        user_id = str(ctx.author.id)

        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        # Ensure player exists
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        # Validate amount
        if amount <= 0:
            await ctx.send(f"{ctx.author.mention} Bet must be a positive number!")
            return
        if amount > self.balances[user_id]:
            await ctx.send(f"{ctx.author.mention} You don’t have enough balance for that bet!")
            return

        # Determine bet type
        bet_type = self.determine_bet_type(bet_value)
        if not bet_type:
            await ctx.send(f"{ctx.author.mention} Invalid bet value: {bet_value}")
            return

        # Spin the wheel
        spun_number = random.choice(self.numbers)
        payout_multiplier = self.calculate_payout(bet_type, bet_value, spun_number)

        # Deduct bet and calculate winnings
        self.balances[user_id] -= amount
        if payout_multiplier > 0:
            winnings = amount * payout_multiplier
            self.balances[user_id] += winnings
            outcome = f"You won **${winnings}**!"
        else:
            winnings = 0
            outcome = "You lost your bet."

        # Save balances
        await save_balances(self.balances)

        # Respond with result
        await ctx.send(
            f"🎡 **Roulette Spin** 🎡\n"
            f"The wheel landed on **{spun_number} ({self.get_color(spun_number)})**.\n"
            f"{outcome}\n"
            f"New Balance: **${self.balances[user_id]}**"
        )

# Setup cog
async def setup(bot):
    print("Roulette cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    cog = Roulette(bot, frozen_users=frozen, banned_users=banned)
    await bot.add_cog(cog)
    await cog.async_init()  # now safely await DB setup

