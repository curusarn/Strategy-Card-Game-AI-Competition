import sys
import math

# --- Constants ---
MINION = 0
GREEN = 1
RED = 2
BLUE = 3

BOARD = 1
FOE = -1
HAND = 0


# --- Classes ---
class Card:
    def __init__(self, card_name, instance_id, location, card_type, cost, attack, defense,
                 abilities, my_health_change, opponent_health_change, card_draw, lane):
        self.card_name = card_name
        self.instance_id = instance_id
        self.location = location
        self.type = card_type
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.abilities = abilities
        self.my_health_change = my_health_change
        self.opponent_health_change = opponent_health_change
        self.card_draw = card_draw
        self.lane = lane
        self.can_attack = False


# --- Main Game Loop ---
turn = 0
n = -1

while True:
    # Read both players
    for i in range(2):
        player_health, player_mana, player_deck, player_draw = [int(j) for j in input().split()]
        if i == 0:
            health = player_health
            mana = player_mana

    # Opponent info
    opponent_hand, opponent_actions = [int(i) for i in input().split()]
    for i in range(opponent_actions):
        input()  # Ignore opponent actions

    # Read cards
    card_count = int(input())
    cards = []

    for i in range(card_count):
        inputs = input().split()
        card_name = int(inputs[0])
        instance_id = int(inputs[1])
        location = int(inputs[2])
        card_type = int(inputs[3])
        cost = int(inputs[4])
        attack = int(inputs[5])
        defense = int(inputs[6])
        abilities = inputs[7]
        my_health_change = int(inputs[8])
        opponent_health_change = int(inputs[9])
        card_draw = int(inputs[10])
        lane = int(inputs[11])

        card = Card(card_name, instance_id, location, card_type, cost, attack, defense,
                    abilities, my_health_change, opponent_health_change, card_draw, lane)
        cards.append(card)

    # Set can_attack for creatures already on board
    for c in cards:
        if c.location == BOARD:
            c.can_attack = True
        else:
            c.can_attack = False

    # --- Deck Construction Phase ---
    # If we have many cards with location 0 and instance_id -1, we're choosing a deck
    if all(c.instance_id == -1 for c in cards) and len(cards) > 30:
        # Choose 30 cards for constructed deck
        chosen_cards = []
        # Prefer creatures with good stats and guards
        creatures = [c for c in cards if c.type == MINION]
        # Sort by value (cost-efficiency)
        creatures.sort(key=lambda x: (x.attack + x.defense) / max(1, x.cost), reverse=True)

        # Take best 30 cards
        for c in creatures[:30]:
            chosen_cards.append(f"CHOOSE {c.card_name}")

        if len(chosen_cards) < 30:
            # Add any remaining cards if we don't have enough creatures
            for c in cards:
                if len(chosen_cards) >= 30:
                    break
                if f"CHOOSE {c.card_name}" not in chosen_cards:
                    chosen_cards.append(f"CHOOSE {c.card_name}")

        print(" ; ".join(chosen_cards[:30]))

    # --- Draft Phase ---
    elif mana == 0 and len(cards) == 3:
        # Pick the best card from 3 choices
        pick = 0
        # Prefer guards first
        for n in (0, 1, 2):
            if 'G' in cards[n].abilities and cards[n].type == MINION:
                pick = n
                break
        # Otherwise pick highest attack creature
        if pick == 0:
            best_attack = -1
            for n in (0, 1, 2):
                if cards[n].type == MINION and cards[n].attack > best_attack:
                    pick = n
                    best_attack = cards[n].attack
        print('PICK', pick)

    # --- Battle Phase ---
    else:
        actions = []
        summoned_this_turn = []
        attacked_this_turn = []
        items_used_this_turn = []

        # Get current board state
        on_board = [c for c in cards if c.location == BOARD]
        foes = [c for c in cards if c.location == FOE]
        in_hand = [c for c in cards if c.location == HAND]

        # Summon creatures
        for c in in_hand:
            if c.type == MINION and c.cost <= mana:
                lane = n % 2
                n += 1
                actions.append(f'SUMMON {c.instance_id} {lane}')
                mana -= c.cost
                c.location = BOARD
                # Only charge creatures can attack immediately
                c.can_attack = 'C' in c.abilities
                summoned_this_turn.append(c)
                on_board.append(c)

        # Use items on friendly creatures
        for c in in_hand:
            if c.type == GREEN and c.cost <= mana and len(on_board) > 0 and not items_used_this_turn:
                actions.append(f'USE {c.instance_id} {on_board[0].instance_id}')
                items_used_this_turn.append(c)
                mana -= c.cost

        # Use items on enemy creatures
        for c in in_hand:
            if c.type == RED and c.cost <= mana and len(foes) > 0 and not items_used_this_turn:
                actions.append(f'USE {c.instance_id} {foes[0].instance_id}')
                items_used_this_turn.append(c)
                mana -= c.cost

        # Use blue items
        for c in in_hand:
            if c.type == BLUE and c.cost <= mana and not items_used_this_turn:
                actions.append(f'USE {c.instance_id} -1')
                items_used_this_turn.append(c)
                mana -= c.cost

        # Attack with creatures
        for c in cards:
            if c.location == BOARD and c.can_attack and c not in attacked_this_turn:
                # Check for guards in the same lane
                guards = [enemy for enemy in foes if 'G' in enemy.abilities and enemy.lane == c.lane]

                if guards:
                    # Must attack guard first
                    target = guards[0].instance_id
                else:
                    # Attack face
                    target = -1

                actions.append(f'ATTACK {c.instance_id} {target}')
                attacked_this_turn.append(c)
                c.can_attack = False

        # Output actions
        if actions:
            print(';'.join(actions))
        else:
            print("PASS")

    turn += 1