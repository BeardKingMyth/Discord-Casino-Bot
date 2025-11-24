from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

# ============================
#       BLACKJACK COG
# ============================

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]

def hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        rank = card[:-1]
        if rank in ['J', 'Q', 'K']:
            value += 10
        elif rank == 'A':
            value += 11
            aces += 1
        else:
            value += int(rank)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

class Blackjack(commands.Cog):
    async def __init__(self, bot, frozen_users=None, banned_users=None):
        self.bot = bot
        print("Blackjack cog initialized.")
        self.balances = await load_balances()
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()
        self.active_games = {}  # Track ongoing games per user

    @commands.command(name="blackjack")
    async def blackjack(self, ctx, bet: int):
        """Start a game of blackjack!"""
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

        # Validate bet
        if bet <= 0:
            await ctx.send("Bet must be positive!")
            return
        if bet > self.balances[user_id]:
            await ctx.send("You don’t have enough balance for that bet!")
            return

        # Deduct bet
        self.balances[user_id] -= bet

        # Initialize deck and hands
        deck = create_deck()
        random.shuffle(deck)
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        # Save active game
        self.active_games[user_id] = {
            'deck': deck,
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'bet': bet
        }

        await self.show_hands(ctx, user_id, reveal_dealer=False)
        await ctx.send("Type `!bjhit` to draw a card or `!bjstand` to hold.")

    async def show_hands(self, ctx, user_id, reveal_dealer=False):
        game = self.active_games[user_id]
        player_hand = game['player_hand']
        dealer_hand = game['dealer_hand']

        dealer_display = (
            f"{dealer_hand[0]} | {'??' if not reveal_dealer else dealer_hand[1]}"
        )
        if reveal_dealer:
            dealer_display = ' | '.join(dealer_hand) + f" ({hand_value(dealer_hand)})"

        await ctx.send(
            f"**Your hand:** {' | '.join(player_hand)} ({hand_value(player_hand)})\n"
            f"**Dealer's hand:** {dealer_display}"
        )

    @commands.command(name="bjhit")
    async def hit(self, ctx):
        user_id = str(ctx.author.id)

        # Use helper functions
        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        if user_id not in self.active_games:
            await ctx.send("You don’t have an active blackjack game!")
            return

        game = self.active_games[user_id]
        deck = game['deck']
        game['player_hand'].append(deck.pop())

        if hand_value(game['player_hand']) > 21:
            await self.show_hands(ctx, user_id, reveal_dealer=True)
            await ctx.send("Bust! You lost your bet.")
            del self.active_games[user_id]
        else:
            await self.show_hands(ctx, user_id, reveal_dealer=False)
            await ctx.send("Type `!bjhit` to draw a card or `!bjstand` to hold.")

    @commands.command(name="bjstand")
    async def stand(self, ctx):
        user_id = str(ctx.author.id)

        # Use helper functions
        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        game = self.active_games[user_id]
        deck = game['deck']
        player_hand = game['player_hand']
        dealer_hand = game['dealer_hand']
        bet = game['bet']

        # Dealer plays
        while hand_value(dealer_hand) < 17:
            dealer_hand.append(deck.pop())

        player_total = hand_value(player_hand)
        dealer_total = hand_value(dealer_hand)

        await self.show_hands(ctx, user_id, reveal_dealer=True)

        if dealer_total > 21 or player_total > dealer_total:
            winnings = bet * 2
            self.balances[user_id] += winnings
            await ctx.send(f"You win! You earned **${winnings}**.")
        elif player_total == dealer_total:
            self.balances[user_id] += bet
            await ctx.send("Push! Your bet has been returned.")
        else:
            await ctx.send("You lost your bet.")

        del self.active_games[user_id]
        await save_balances(self.balances)

# Setup cog
async def setup(bot):
    print("Blackjack cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(Blackjack(bot, frozen_users=frozen, banned_users=banned))
