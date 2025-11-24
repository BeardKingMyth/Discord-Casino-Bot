from discord.ext import commands
import random
from utils.helpers import load_balances, save_balances, is_user_banned, is_user_frozen

SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def create_deck():
    return [f"{rank}{suit}" for suit in SUITS for rank in RANKS]

def card_value(card):
    rank = card[:-1]
    if rank == 'A':
        return 14
    elif rank == 'K':
        return 13
    elif rank == 'Q':
        return 12
    elif rank == 'J':
        return 11
    else:
        return int(rank)

class War(commands.Cog):
    async def __init__(self, bot, frozen_users=None, banned_users=None):
        print("War cog initialized.")
        self.bot = bot
        self.balances = await load_balances()
        self.frozen_users = frozen_users if frozen_users else set()
        self.banned_users = banned_users if banned_users else set()
        self.active_games = {}  # game_id -> game state
        self.challenges = {}    # challenged_user_id -> challenger_user_id

    # -----------------------------
    #      Start Challenge
    # -----------------------------
    @commands.command(name="war_challenge")
    async def war_challenge(self, ctx, opponent: commands.MemberConverter, bet: int):
        """Challenge another player to War!"""
        challenger_id = str(ctx.author.id)
        opponent_id = str(opponent.id)

        # Use helper functions
        if await is_user_banned(challenger_id, self.banned_users):
            await ctx.send(f"{ctx.author.mention} is banned from the economy and cannot play games.")
            return
        if await is_user_frozen(challenger_id, self.frozen_users):
            await ctx.send(f"{ctx.author.mention} is currently frozen and cannot play games.")
            return
        if await is_user_banned(opponent_id, self.banned_users):
            await ctx.send(f"{opponent.mention} is banned from the economy and cannot play games.")
            return
        if await is_user_frozen(opponent_id, self.frozen_users):
            await ctx.send(f"{opponent.mention} is currently frozen and cannot play games.")
            return

        # Cannot challenge self
        if challenger_id == opponent_id:
            await ctx.send("You cannot challenge yourself.")
            return

        # Ensure both players exist in balances
        for uid in [challenger_id, opponent_id]:
            if uid not in self.balances:
                self.balances[uid] = 1000

        # Validate bets
        if bet <= 0:
            await ctx.send("Bet must be positive!")
            return
        if self.balances[challenger_id] < bet:
            await ctx.send("You don’t have enough balance for that bet!")
            return
        if self.balances[opponent_id] < bet:
            await ctx.send(f"{opponent.display_name} does not have enough balance for that bet!")
            return

        # Store challenge
        self.challenges[opponent_id] = {
            'challenger_id': challenger_id,
            'bet': bet
        }

        await ctx.send(f"{opponent.mention}, you have been challenged to War by {ctx.author.mention} for ${bet}! Type `!war_accept {ctx.author.display_name}` to accept.")

    # -----------------------------
    #      Accept Challenge
    # -----------------------------
    @commands.command(name="war_accept")
    async def war_accept(self, ctx, challenger: commands.MemberConverter):
        opponent_id = str(ctx.author.id)
        challenger_id = str(challenger.id)

        # Use helper functions
        if await is_user_banned(opponent_id, self.banned_users):
            await ctx.send(f"{ctx.author.mention} is banned from the economy and cannot play games.")
            return
        if await is_user_frozen(opponent_id, self.frozen_users):
            await ctx.send(f"{ctx.author.mention} is currently frozen and cannot play games.")
            return
        if await is_user_banned(challenger_id, self.banned_users):
            await ctx.send(f"{challenger.mention} is banned from the economy and cannot play games.")
            return
        if await is_user_frozen(challenger_id, self.frozen_users):
            await ctx.send(f"{challenger.mention} is currently frozen and cannot play games.")
            return

        if opponent_id not in self.challenges or self.challenges[opponent_id]['challenger_id'] != challenger_id:
            await ctx.send("No challenge found from that user.")
            return

        bet = self.challenges[opponent_id]['bet']

        # Deduct bets
        self.balances[challenger_id] -= bet
        self.balances[opponent_id] -= bet

        # Create game
        deck = create_deck()
        random.shuffle(deck)
        half = len(deck) // 2

        game_id = f"{challenger_id}_{opponent_id}"
        self.active_games[game_id] = {
            'player1_id': challenger_id,
            'player2_id': opponent_id,
            'player1_deck': deck[:half],
            'player2_deck': deck[half:],
            'war_pile': [],
            'bet': bet
        }

        # Remove challenge
        del self.challenges[opponent_id]

        await save_balances(self.balances)
        await ctx.send(f"War game started between {challenger.mention} and {ctx.author.mention}! Type `!war_flip` to play a turn.")

    # -----------------------------
    #      Single Player vs Dealer
    # -----------------------------
    @commands.command(name="war")
    async def war_solo(self, ctx, bet: int):
        """Play War against the dealer."""
        user_id = str(ctx.author.id)

        # Use helper functions
        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        if user_id not in self.balances:
            self.balances[user_id] = 1000

        if bet <= 0:
            await ctx.send("Bet must be positive!")
            return
        if self.balances[user_id] < bet:
            await ctx.send("You don’t have enough balance for that bet!")
            return

        self.balances[user_id] -= bet

        deck = create_deck()
        random.shuffle(deck)
        half = len(deck) // 2

        game_id = f"{user_id}_dealer"
        self.active_games[game_id] = {
            'player1_id': user_id,
            'player2_id': 'dealer',
            'player1_deck': deck[:half],
            'player2_deck': deck[half:],
            'war_pile': [],
            'bet': bet
        }

        await save_balances(self.balances)
        await ctx.send(f"War game started against the dealer! Type `!war_flip` to play a turn.")

    # -----------------------------
    #      Flip Command
    # -----------------------------
    @commands.command(name="war_flip")
    async def war_flip(self, ctx):
        """Flip top card for your active War game."""
        user_id = str(ctx.author.id)

        # Use helper functions
        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        # Find game
        game = None
        game_id = None
        for gid, g in self.active_games.items():
            if g['player1_id'] == user_id or g['player2_id'] == user_id:
                game = g
                game_id = gid
                break
        if not game:
            await ctx.send("You don’t have an active War game!")
            return

        # Draw top cards
        p1_card = game['player1_deck'].pop(0)
        p2_card = game['player2_deck'].pop(0)
        war_pile = [p1_card, p2_card]

        result_text = f"**{ctx.author.display_name} flipped {p1_card}!**\n"
        opponent_name = "Dealer" if game['player2_id'] == 'dealer' else f"<@{game['player2_id']}>"
        result_text += f"**{opponent_name} flipped {p2_card}!**\n"

        # Resolve round
        winner = None
        if card_value(p1_card) > card_value(p2_card):
            winner = game['player1_id']
        elif card_value(p2_card) > card_value(p1_card):
            winner = game['player2_id']
        else:
            # WAR! Show each step to players
            await ctx.send(f"WAR! Both players drew {p1_card}!")
            
            war_pile.append(p1_card)
            war_pile.append(p2_card)
            
            while True:
                # Determine how many face-down cards can be placed
                war_cards_needed = min(3, len(game['player1_deck']), len(game['player2_deck']))
                
                # Place face-down cards
                if war_cards_needed > 0:
                    p1_face_down = [game['player1_deck'].pop(0) for _ in range(war_cards_needed)]
                    p2_face_down = [game['player2_deck'].pop(0) for _ in range(war_cards_needed)]
                    war_pile.extend(p1_face_down + p2_face_down)
                    await ctx.send(f"Each player places {war_cards_needed} card(s) face-down...")
                
                # Check if anyone ran out of cards during war
                if len(game['player1_deck']) == 0:
                    winner = game['player2_id']
                    break
                if len(game['player2_deck']) == 0:
                    winner = game['player1_id']
                    break
            
                # Flip new war card
                p1_new = game['player1_deck'].pop(0)
                p2_new = game['player2_deck'].pop(0)
                war_pile.extend([p1_new, p2_new])
                await ctx.send(f"Flipping war cards: Player1 -> {p1_new}, Player2 -> {p2_new}")
                
                if card_value(p1_new) > card_value(p2_new):
                    winner = game['player1_id']
                    break
                elif card_value(p2_new) > card_value(p1_new):
                    winner = game['player2_id']
                    break
                else:
                    # Another tie, continue the loop for recursive war
                    await ctx.send("WAR continues! Another tie on war cards!")
                    continue


        # Assign cards
        if winner:
            if winner == game['player1_id']:
                game['player1_deck'].extend(war_pile)
                result_text += f"**Winner of this round: <@{game['player1_id']}>**\n"
            else:
                game['player2_deck'].extend(war_pile)
                if game['player2_id'] == 'dealer':
                    result_text += f"**Winner of this round: Dealer**\n"
                else:
                    result_text += f"**Winner of this round: <@{game['player2_id']}>**\n"
        else:
            result_text += "**Round tied! War continues next flip.**\n"

        # Check for game over
        if len(game['player1_deck']) == 0:
            loser = game['player1_id']
            winner_id = game['player2_id']
            winnings = 0 if winner_id != 'dealer' else 2 * game['bet']
            if winner_id != 'dealer':
                self.balances[winner_id] += 2 * game['bet']
            elif winner_id == 'dealer':
                self.balances[game['player1_id']] += 0  # player lost
            await save_balances(self.balances)
            del self.active_games[game_id]
            result_text += f"Game over! <@{winner_id}> wins the War!"
        elif len(game['player2_deck']) == 0:
            loser = game['player2_id']
            winner_id = game['player1_id']
            self.balances[winner_id] += 2 * game['bet']
            await save_balances(self.balances)
            del self.active_games[game_id]
            result_text += f"Game over! <@{winner_id}> wins the War!"

        await ctx.send(result_text)

    # -----------------------------
    #      Quit Command
    # -----------------------------
    @commands.command(name="war_quit")
    async def war_quit(self, ctx):
        """Forfeit your active War game."""
        user_id = str(ctx.author.id)

        # Use helper functions
        if await is_user_banned(user_id, self.banned_users):
            await ctx.send("You are banned from the economy and cannot play games.")
            return
        if await is_user_frozen(user_id, self.frozen_users):
            await ctx.send("You are currently frozen and cannot play games.")
            return

        game_to_delete = None
        for gid, g in self.active_games.items():
            if g['player1_id'] == user_id or g['player2_id'] == user_id:
                game_to_delete = gid
                break
        if not game_to_delete:
            await ctx.send("You have no active War game.")
            return
        bet = self.active_games[game_to_delete]['bet']
        # Player forfeits bet
        if self.active_games[game_to_delete]['player1_id'] == user_id:
            forfeited_player = self.active_games[game_to_delete]['player1_id']
            if self.active_games[game_to_delete]['player2_id'] != 'dealer':
                self.balances[self.active_games[game_to_delete]['player2_id']] += 2 * bet
        else:
            forfeited_player = self.active_games[game_to_delete]['player2_id']
            if self.active_games[game_to_delete]['player1_id'] != 'dealer':
                self.balances[self.active_games[game_to_delete]['player1_id']] += 2 * bet
        await save_balances(self.balances)
        del self.active_games[game_to_delete]
        await ctx.send(f"<@{user_id}> forfeited the War game!")

# -----------------------------
#      Setup Cog
# -----------------------------
async def setup(bot):
    print("War cog loaded.")
    from cogs.admin import EconomyAdmin
    frozen = getattr(bot.get_cog("EconomyAdmin"), "frozen_users", set())
    banned = getattr(bot.get_cog("EconomyAdmin"), "banned_users", set())
    await bot.add_cog(War(bot, frozen_users=frozen, banned_users=banned))
