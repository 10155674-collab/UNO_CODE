import random
from vex import *

# Initialize EXP Brain
brain = Brain()

# --- HARDWARE & MOTOR SETUP ---
# Standard VEX EXP Smart Motors on Ports 1 and 6 (Adjust ports if needed)
left_motor = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
right_motor = Motor(Ports.PORT6, GearSetting.RATIO_18_1, True)

SCREEN_ROWS = 5
SCREEN_COLS = 16

# --- ROBOT MOVEMENT HELPERS ---

def drive_forward(units=1):
    """Drives the robot forward by specified unit distances."""
    for _ in range(units):
        left_motor.spin_for(FORWARD, 360, DEGREES, False)
        right_motor.spin_for(FORWARD, 360, DEGREES, True)
        wait(200, MSEC)

def turn_left_90():
    """Turns the robot 90 degrees to the left."""
    left_motor.spin_for(REVERSE, 180, DEGREES, False)
    right_motor.spin_for(FORWARD, 180, DEGREES, True)
    wait(200, MSEC)

def turn_right_90():
    """Turns the robot 90 degrees to the right."""
    left_motor.spin_for(FORWARD, 180, DEGREES, False)
    right_motor.spin_for(REVERSE, 180, DEGREES, True)
    wait(200, MSEC)

def move_to_center():
    """Drives forward 2 units to the center game pile."""
    brain.screen.clear_screen()
    display_line(1, "DRIVING TO")
    display_line(2, "CENTER PILE...")
    drive_forward(2)

def return_to_player():
    """Turns 180 degrees and drives 2 units back to the player."""
    brain.screen.clear_screen()
    display_line(1, "RETURNING TO")
    display_line(2, "PLAYER...")
    # Turn 180 degrees (two 90-degree turns)
    turn_right_90()
    turn_right_90()
    # Drive back to player position
    drive_forward(2)
    # Re-orient back to face center
    turn_right_90()
    turn_right_90()

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

# --- ATTACK CHECK & MULTIPLAYER MENUS ---

def check_attack_phase(hand, deck):
    """Asks if real player attacked. Plays Draw 2 counter or forces robot to draw 2."""
    brain.screen.clear_screen()
    display_line(1, "ATTACK PHASE")
    display_line(2, "Did opponent")
    display_line(3, "play Draw 2?")
    display_line(4, "<L/R> NO")
    display_line(5, "[Check] YES")

    btn = wait_for_button_press()
    if btn == "CHECK":
        draw2_indices = [i for i, c in enumerate(hand) if "Draw 2" in c]
        
        if len(draw2_indices) > 0:
            played_card = hand.pop(draw2_indices[0])
            print("\nAttack countered! Robot driving to discard: " + played_card)
            
            # Physical drive action
            move_to_center()
            return_to_player()
            
            brain.screen.clear_screen()
            display_line(1, "COUNTER ATTACK!")
            display_line(2, "Robot played:")
            display_line(3, played_card)
            display_line(5, "[Check] Continue")
            while wait_for_button_press() != "CHECK":
                pass
            return played_card
        else:
            print("\nRobot has no Draw 2! Driving to center to draw 2 penalty cards...")
            
            # Physical drive action
            move_to_center()
            
            drawn_cards = []
            for _ in range(2):
                if len(deck) > 0:
                    c = deck.pop(0)
                    hand.append(c)
                    drawn_cards.append(c)
            
            return_to_player()

            brain.screen.clear_screen()
            display_line(1, "NO DRAW 2 CARD!")
            display_line(2, "Took 2 cards:")
            if len(drawn_cards) > 0:
                display_line(3, drawn_cards[0][:16])
            if len(drawn_cards) > 1:
                display_line(4, drawn_cards[1][:16])
            display_line(5, "[Check] Continue")
            while wait_for_button_press() != "CHECK":
                pass
            return None
    return None

def set_discard_pile_menu():
    """Prompt the player to select the card played by the real-life opponent."""
    colors = ['Red', 'Yellow', 'Green', 'Blue', 'Wild']
    color_idx = 0
    
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
        display_line(2, "Vs: " + top_discard)
        display_line(4, "Must draw 1 card")
        display_line(5, "[Check] Draw Card")
        
        print("\nNo playable cards against " + top_discard + ". Robot driving to draw...")
        while wait_for_button_press() != "CHECK":
            pass
            
        # Drive to center to draw
        move_to_center()
        
        if len(deck) > 0:
            drawn_card = deck.pop(0)
            hand.append(drawn_card)
            print("Robot added drawn card: " + drawn_card)
            
        return_to_player()
            
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
                print("Robot playing card: " + played_card)
                
                # Drive to center to discard card and return
                move_to_center()
                return_to_player()
                
                brain.screen.clear_screen()
                display_line(1, "PLAYED CARD:")
                display_line(2, played_card)
                display_line(5, "[Check] Confirm")
                while wait_for_button_press() != "CHECK":
                    pass
                return played_card
            else:
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
    top_discard = "Red 0"

    while not game_over:
        print("\n====================")
        print("ROUND " + str(turn_count))
        print_hand_to_terminal(player_hand)

        # 1. Ask "Do you have an attack?"
        counter_card = check_attack_phase(player_hand, uno_deck)

        if counter_card is not None:
            top_discard = counter_card
        else:
            # 2. Select card played by real-life opponent
            top_discard = set_discard_pile_menu()
            # 3. Choose available card from hand & perform drive/return sequence
            top_discard = player_turn_menu(player_hand, uno_deck, top_discard)

        if len(player_hand) == 0:
            brain.screen.clear_screen()
            display_line(1, "ROBOT HAND EMPTY")
            display_line(3, "YOU WIN!")
            print("\n*** GAME OVER: Robot player has cleared all stored cards! ***")
            game_over = True
        else:
            turn_count += 1

# Run game assistant
run_multiplayer_game()