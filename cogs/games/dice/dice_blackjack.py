import random
from discord.ext import commands
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

class DiceBlackjack(commands.Cog):
    def __init__(self, bot, frozen_users=None, banned_users=None):
        print("Dice_blackjack cog initialized.")
        self.bot = bot
        self.balances = load_balances()
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()
        self.active_games = {}  # user_id -> { "total": int, "bet": int, "rolls": [] }

    # Start the game
    @commands.command(name="dice21")
    async def dice21(self, ctx, bet: int):
        user_id = str(ctx.author.id)

        # Use helper functions
        if is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        # Initialize balance
        if user_id not in self.balances:
            self.balances[user_id] = 1000

        if bet <= 0:
            await ctx.send("Your bet must be greater than zero.")
            return

        if bet > self.balances[user_id]:
            await ctx.send("You can't afford that bet.")
            return

        if user_id in self.active_games:
            await ctx.send("You already have an active Dice Blackjack game. Use !hit or !stand.")
            return

        # First roll
        roll = random.randint(1, 6)
        self.active_games[user_id] = {
            "total": roll,
            "bet": bet,
            "rolls": [roll]
        }

        await ctx.send(f"You rolled a **{roll}**. Total: **{roll}**.\nType **!hit** to roll again or **!stand** to stop.")

    # Hit command
    @commands.command(name="hit")
    async def hit(self, ctx):
        user_id = str(ctx.author.id)

        # Use helper functions
        if is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        if user_id not in self.active_games:
            await ctx.send("You don't have an active Dice Blackjack game. Start one with !dice21 <bet>.")
            return

        game = self.active_games[user_id]

        roll = random.randint(1, 6)
        game["total"] += roll
        game["rolls"].append(roll)

        if game["total"] > 21:
            # Player busts
            self.balances[user_id] -= game["bet"]
            save_balances(self.balances)
            del self.active_games[user_id]

            await ctx.send(f"You rolled a **{roll}** and busted at **{game['total']}**.\nYou lost your bet.")
            return

        await ctx.send(
            f"You rolled a **{roll}**. Total: **{game['total']}**.\n"
            f"Type **!hit** to roll again or **!stand** to stop."
        )

    # Stand command
    @commands.command(name="stand")
    async def stand(self, ctx):
        user_id = str(ctx.author.id)

        # Use helper functions
        if is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return


        if user_id not in self.active_games:
            await ctx.send("You aren't in an active Dice Blackjack game.")
            return

        game = self.active_games[user_id]
        player_total = game["total"]
        player_rolls_count = len(game["rolls"])
        bet = game["bet"]

        # House turn
        house_total = 0
        house_rolls = []

        while house_total < 16:
            r = random.randint(1, 6)
            house_total += r
            house_rolls.append(r)

        house_rolls_count = len(house_rolls)

        # Determine result
        outcome = ""
        win = False

        if house_total > 21:
            outcome = f"The house busted at **{house_total}**!"
            win = True
        elif player_total > house_total:
            outcome = f"You beat the house! {player_total} vs {house_total}."
            win = True
        elif player_total < house_total:
            outcome = f"The house wins with **{house_total}** against your **{player_total}**."
            win = False
        else:
            #Tie-breaker: fewest rolls wins
            if player_rolls_count < house_rolls_count:
                outcome = f"It's a tie at **{player_total}**, but you reached it in fewer rolls!"
                win = True
            elif player_rolls_count > house_rolls_count:
                outcome = f"It's a tie at **{player_total}**, but the house reached it in fewer rolls!"
                win = False
            else:
                outcome = f"It's a tie at **{player_total}**, both rolled the same number of times."
                win = "tie"

        # Apply money
        if win is True:
            self.balances[user_id] += bet
            result_msg = f"You won **${bet}**! New balance: ${self.balances[user_id]}."
        elif win == "tie":
            result_msg = f"You tied. Your bet is returned. Balance: ${self.balances[user_id]}."
        else:
            self.balances[user_id] -= bet
            result_msg = f"You lost **${bet}**. New balance: ${self.balances[user_id]}."

        save_balances(self.balances)
        del self.active_games[user_id]

        await ctx.send(
            f"House rolls: {house_rolls} (Total {house_total})\n"
            f"{outcome}\n{result_msg}"
        )

async def setup(bot):
    print("Dice_blackjack cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(DiceBlackjack(bot, frozen_users=frozen, banned_users=banned))
