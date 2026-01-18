import random

# Function to load leaderboard from file
def load_leaderboard():
    try:
        with open("leaderboard.txt", "r") as f:
            lines = f.readlines()
            leaderboard = []
            for line in lines:
                username, attempts = line.strip().split(",")
                leaderboard.append({"username": username, "attempts": int(attempts)})
            return leaderboard
    except FileNotFoundError:
        return []

# Function to save leaderboard to file
def save_leaderboard(leaderboard):
    with open("leaderboard.txt", "w") as f:
        for entry in leaderboard:
            f.write(f"{entry['username']},{entry['attempts']}\n")

while True:  # Main game loop for restarts
    # Prompt for username
    username = input("Enter your username to start the game (or 'exit' to quit): ").strip()
    if username.lower() == 'exit':
        print("Exiting the game.")
        break
    if not username:
        print("Username is required. Try again.")
        continue

    target = random.randint(1, 100)
    attempts = 0
    won = False

    while True:
        userchoice = input("Guess the number:")
        if userchoice == "Q":
            print("Quitted the game")
            break

        userchoice = int(userchoice)
        attempts += 1

        if userchoice == target:
            rank = "Excellent" if attempts <= 3 else "Good" if attempts <= 6 else "Average" if attempts <= 10 else "Poor"
            print(f"You have Successfully guessed the Number in {attempts} attempts! Rank: {rank}")
            won = True
            break

        elif userchoice > target:
            print("The number you guessed is Big")
        else:
            print("The number you guessed is Small") 

    # Load, update, and save leaderboard if won
    leaderboard = load_leaderboard()
    if won:
        leaderboard.append({"username": username, "attempts": attempts})
        leaderboard.sort(key=lambda x: x["attempts"])  # Sort by attempts (ascending)

    save_leaderboard(leaderboard)

    # Display leaderboard
    print("\n---GAME OVER---")
    print("Rank List (sorted by attempts):")
    for i, entry in enumerate(leaderboard, 1):
        print(f"{i}. {entry['username']} - {entry['attempts']} attempts")
    
    print("\nRestarting game...\n")  # Indicate restart