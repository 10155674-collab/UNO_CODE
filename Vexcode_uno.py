import random

def create_uno_deck():
    colors = ['Red', 'Yellow', 'Green', 'Blue']
    values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw 2']
    deck = []

    # 1. Add Colored Cards (100 total)
    for color in colors:
        for val in values:
            card_name = color + " " + val
            if val == '0':
                deck.append(card_name)  # 1 zero per color
            else:
                deck.append(card_name)  # 2 of each 1-9 and actions per color
                deck.append(card_name)

    # 2. Add Wild Cards (8 total)
    for _ in range(4):
        deck.append("Wild")
        deck.append("Wild Draw 4")

    return deck

def custom_shuffle(deck):
    # Fisher-Yates manual shuffle using random.randint
    n = len(deck)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        # Swap cards at position i and j
        deck[i], deck[j] = deck[j], deck[i]

# 1. Build Deck
uno_deck = create_uno_deck()

# 2. Shuffle using custom loop (No random.shuffle)
custom_shuffle(uno_deck)

# 3. Print shuffled deck to terminal
print("Total cards in deck: " + str(len(uno_deck)))
print("-------------------------")

card_number = 1
for card in uno_deck:
    print(str(card_number) + ": " + card)
    card_number = card_number + 1
# --- ADD THIS TO THE BOTTOM OF YOUR CODE ---

def deal_hand(deck, num_cards=7):
    """
    Draws cards from the deck, prints them to terminal,
    and displays all 7 cards across two pages on the VEX EXP screen.
    """
    hand = []
    
    # Draw cards off the top
    for _ in range(num_cards):
        if len(deck) > 0:
            hand.append(deck.pop(0))

    # 1. Print to Terminal Console
    print("--- NEW STARTING HAND (" + str(len(hand)) + " Cards) ---")
    for idx, card in enumerate(hand, start=1):
        print(str(idx) + ": " + card)
    print("Remaining deck count: " + str(len(deck)))
    print("---------------------------------")

    # 2. Print to VEX EXP Screen (5 Rows x 16 Cols)
    brain.screen.clear_screen()
    
    # Page 1: Cards 1 to 4
    brain.screen.set_cursor(1, 1)
    brain.screen.print("HAND 1-4 (5x16)")

    for idx in range(min(4, len(hand))):
        brain.screen.set_cursor(idx + 2, 1)
        display_text = str(idx + 1) + ":" + hand[idx]
        if len(display_text) > 16:
            display_text = display_text[:16]
        brain.screen.print(display_text)

    # Pause 3 seconds to read page 1
    wait(3, SECONDS)

    # Page 2: Cards 5 to 7
    if len(hand) > 4:
        brain.screen.clear_screen()
        brain.screen.set_cursor(1, 1)
        brain.screen.print("HAND 5-7 (5x16)")

        for idx in range(4, len(hand)):
            brain.screen.set_cursor(idx - 2, 1)
            display_text = str(idx + 1) + ":" + hand[idx]
            if len(display_text) > 16:
                display_text = display_text[:16]
            brain.screen.print(display_text)

    return hand

# Execute the deal function using your existing shuffled deck
player_hand = deal_hand(uno_deck, 7)