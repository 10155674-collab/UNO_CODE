import random
from vex import *

# Initialize EXP Brain
brain = Brain()

# --- HARDWARE CONSTANTS ---
SCREEN_ROWS = 5
SCREEN_COLS = 16

# --- DECK & HAND SETUP ---

def create_uno_deck():
    colors = ['Red', 'Yellow', 'Green', 'Blue']
    values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw 2']
    deck = []

    for color in colors:
        for val in values:
            card_name = color + " " + val
            if val == '0':
                deck.append(card_name)
            else:
                deck.append(card_name)
                deck.append(card_name)

    for _ in range(4):
        deck.append("Wild")
        deck.append("Wild Draw 4")

    return deck

def custom_shuffle(deck):
    n = len(deck)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]

def deal_hand(deck, num_cards=7):
    hand = []
    for _ in range(num_cards):
        if len(deck) > 0:
            hand.append(deck.pop(0))
    return hand

# --- SCREEN & BUTTON HELPERS ---

def display_line(row, text):
    """Prints text safely within the 16-character hardware screen limit."""
    brain.screen.set_cursor(row, 1)
    if len(text) > SCREEN_COLS:
        text = text[:SCREEN_COLS]
    brain.screen.print(text)

def wait_for_button_press():
    """Waits for Left, Right, or Check button input."""
    while True:
        if brain.buttonLeft.pressing():
            while brain.buttonLeft.pressing():
                wait(20, MSEC)
            return "LEFT"
        elif brain.buttonRight.pressing():
            while brain.buttonRight.pressing():
                wait(20, MSEC)
            return "RIGHT"
        elif brain.buttonCheck.pressing():
            while brain.buttonCheck.pressing():
                wait(20, MSEC)
            return "CHECK"
        wait(20, MSEC)

def print_hand_to_terminal(hand):
    """Outputs current stored hand to terminal console."""
    print("\n--- ROBOT STORED HAND (" + str(len(hand)) + " Cards) ---")
    for idx, card in enumerate(hand, start=1):
        print(str(idx) + ": " + card)
    print("---------------------------------------")

# --- MULTIPLAYER MENUS ---

def set_discard_pile_menu():
    """Prompt the player to select the card played by the real-life opponent."""
    colors = ['Red', 'Yellow', 'Green', 'Blue', 'Wild']
    color_idx = 0
    
    # 1. Select Color
    while True:
        brain.screen.clear_screen()
        display_line(1, "OPPONENT PLAYED:")
        display_line(2, "Color: " + colors[color_idx])
        display_line(4, "<L/R> Change")
        display_line(5, "[Check] Next")

        btn = wait_for_button_press()
        if btn == "LEFT":
            color_idx = (color_idx - 1) % len(colors)
        elif btn == "RIGHT":
            color_idx = (color_idx + 1) % len(colors)
        elif btn == "CHECK":
            selected_color = colors[color_idx]
            break

    if selected_color == "Wild":
        print("Opponent played: Wild")
        return "Wild"

    # 2. Select Value
    values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw 2']
    val_idx = 0

    while True:
        brain.screen.clear_screen()
        display_line(1, "OPPONENT PLAYED:")
        display_line(2, selected_color)
        display_line(3, "Val: " + values[val_idx])
        display_line(5, "<L/R>  [Check]")

        btn = wait_for_button_press()
        if btn == "LEFT":
            val_idx = (val_idx - 1) % len(values)
        elif btn == "RIGHT":
            val_idx = (val_idx + 1) % len(values)
        elif btn == "CHECK":
            selected_val = values[val_idx]
            break

    top_card = selected_color + " " + selected_val
    print("Opponent played: " + top_card)
    return top_card

def is_valid_play(card, top_card):
    """Accurately checks if a stored card matches the opponent's card or is Wild."""
    if "Wild" in card:
        return True

    if top_card == "Wild" or top_card == "Wild Draw 4":
        return True

    if " " in card and " " in top_card:
        card_color, card_val = card.split(" ", 1)
        top_color, top_val = top_card.split(" ", 1)

        if card_color == top_color or card_val == top_val:
            return True

    return False

def player_turn_menu(hand, deck, top_discard):
    """Allows cycling through stored cards to see what is AVAILABLE vs INVALID."""
    playable_indices = [i for i, c in enumerate(hand) if is_valid_play(c, top_discard)]
    
    # Forced Draw if no cards match
    if len(playable_indices) == 0:
        brain.screen.clear_screen()
        display_line(1, "NO VALID CARDS!")
        display_line(2, "Opponent: " + top_discard)
        display_line(4, "Must draw 1 card")
        display_line(5, "[Check] Draw Card")
        
        print("\nNo playable cards against " + top_discard + ". Drawing card...")
        while wait_for_button_press() != "CHECK":
            pass
            
        if len(deck) > 0:
            drawn_card = deck.pop(0)
            hand.append(drawn_card)
            print("Robot added drawn card: " + drawn_card)
            
            brain.screen.clear_screen()
            display_line(1, "DRAWN CARD:")
            display_line(2, drawn_card)
            display_line(5, "[Check] End Turn")
            while wait_for_button_press() != "CHECK":
                pass
        return top_discard

    # Interactive Navigation of Hand
    cursor_idx = 0
    while True:
        selected_card = hand[cursor_idx]
        can_play = is_valid_play(selected_card, top_discard)
        
        brain.screen.clear_screen()
        display_line(1, "Vs: " + top_discard)
        display_line(2, "Card " + str(cursor_idx + 1) + "/" + str(len(hand)))
        display_line(3, selected_card)
        display_line(4, "Status: " + ("AVAILABLE" if can_play else "INVALID"))
        display_line(5, "<L/R>  [Check]")

        btn = wait_for_button_press()
        if btn == "LEFT":
            cursor_idx = (cursor_idx - 1) % len(hand)
        elif btn == "RIGHT":
            cursor_idx = (cursor_idx + 1) % len(hand)
        elif btn == "CHECK":
            if can_play:
                played_card = hand.pop(cursor_idx)
                print("Played card from robot: " + played_card)
                
                brain.screen.clear_screen()
                display_line(1, "PLAYING CARD:")
                display_line(2, played_card)
                display_line(5, "[Check] Confirm")
                while wait_for_button_press() != "CHECK":
                    pass
                return played_card
            else:
                # Feedback if user attempts to select an invalid card
                brain.screen.clear_screen()
                display_line(1, "CANNOT PLAY!")
                display_line(2, "Card is INVALID")
                display_line(3, "Must match color")
                display_line(4, "or value.")
                display_line(5, "[Check] Back")
                while wait_for_button_press() != "CHECK":
                    pass

# --- MAIN GAME LOOP ---

def run_multiplayer_game():
    uno_deck = create_uno_deck()
    custom_shuffle(uno_deck)
    player_hand = deal_hand(uno_deck, 7)

    game_over = False
    turn_count = 1
    
    # Set initial board state
    top_discard = set_discard_pile_menu()

    while not game_over:
        print("\n====================")
        print("ROUND " + str(turn_count))
        print_hand_to_terminal(player_hand)

        # Player checks available cards and picks one to play or draws
        top_discard = player_turn_menu(player_hand, uno_deck, top_discard)

        if len(player_hand) == 0:
            brain.screen.clear_screen()
            display_line(1, "ROBOT HAND EMPTY")
            display_line(3, "YOU WIN!")
            print("\n*** GAME OVER: Robot player has cleared all stored cards! ***")
            game_over = True
        else:
            turn_count += 1
            # Next turn starts by entering what the real-life player played
            top_discard = set_discard_pile_menu()

# Run game assistant
run_multiplayer_game()