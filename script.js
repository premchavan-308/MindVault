let sessionId = Math.random().toString(36).substr(2, 9);  // Unique session ID
let players = [];
let currentPlayer = 0;
let attempts = 0;
let multiplayerMode = false;
let gameActive = true;  // Flag to prevent guesses after win

// DOM Elements
const menu = document.getElementById('menu');
const levelSelection = document.getElementById('level-selection');
const gameArea = document.getElementById('game-area');
const multiplayerSetup = document.getElementById('multiplayer-setup');
const leaderboardDiv = document.getElementById('leaderboard');
const feedback = document.getElementById('feedback');
const guessInput = document.getElementById('guess-input');
const guessBtn = document.getElementById('guess-btn');
const quitBtn = document.getElementById('quit-btn');
const attemptsDisplay = document.getElementById('attempts');
const leaderboardList = document.getElementById('leaderboard-list');
const levelFilter = document.getElementById('level-filter');

// Event Listeners
document.getElementById('single-player-btn').addEventListener('click', () => startSinglePlayer());
document.getElementById('multiplayer-btn').addEventListener('click', () => showMultiplayerSetup());
document.getElementById('leaderboard-btn').addEventListener('click', () => showLeaderboard());
document.querySelectorAll('.level-btn').forEach(btn => btn.addEventListener('click', (e) => selectLevel(parseInt(e.target.dataset.level))));
document.getElementById('start-multiplayer-btn').addEventListener('click', () => startMultiplayer());
guessBtn.addEventListener('click', () => makeGuess());
quitBtn.addEventListener('click', () => quitGame());
levelFilter.addEventListener('change', () => updateLeaderboard());

// Functions
async function startSinglePlayer() {
    players = [prompt('Enter your username:') || 'Player'];
    multiplayerMode = false;
    showLevelSelection();
}

function showMultiplayerSetup() {
    menu.style.display = 'none';
    multiplayerSetup.style.display = 'block';
}

async function startMultiplayer() {
    const count = parseInt(document.getElementById('player-count').value);
    players = [];
    for (let i = 1; i <= count; i++) {
        players.push(prompt(`Enter Player ${i} username:`) || `Player${i}`);
    }
    multiplayerMode = true;
    showLevelSelection();
}

function showLevelSelection() {
    multiplayerSetup.style.display = 'none';
    levelSelection.style.display = 'block';
}

async function selectLevel(level) {
    try {
        const response = await fetch('/start_game', {
            method: 'POST',
            body: new URLSearchParams({ session_id: sessionId, level, players: JSON.stringify(players) })
        });
        if (!response.ok) throw new Error('Failed to start game');
        levelSelection.style.display = 'none';
        gameArea.style.display = 'block';
        feedback.textContent = multiplayerMode ? `${players[currentPlayer]}'s turn!` : '';
        attempts = 0;
        gameActive = true;
        updateAttempts();
    } catch (error) {
        alert('Error starting game: ' + error.message);
    }
}

async function makeGuess() {
    if (!gameActive) return alert('Game not active. Wait for next player or restart.');
    const guess = parseInt(guessInput.value);
    if (isNaN(guess)) return alert('Enter a valid number!');
    try {
        const response = await fetch('/guess', {
            method: 'POST',
            body: new URLSearchParams({ session_id: sessionId, guess })
        });
        if (!response.ok) throw new Error('Guess failed');
        const data = await response.json();
        attempts++;
        updateAttempts();
        if (data.result === 'win') {
            feedback.textContent = `You guessed it! (${attempts} attempts)`;
            gameActive = false;  // Prevent further guesses
            setTimeout(() => {
                if (multiplayerMode) {
                    nextPlayer();  // Switch after showing message
                } else {
                    endGame();
                }
            }, 2000);  // Show message for 2 seconds
        } else if (data.result === 'high') {
            feedback.textContent = 'Too High';
        } else {
            feedback.textContent = 'Too Low';
        }
        guessInput.value = '';
    } catch (error) {
        alert('Error making guess: ' + error.message);
    }
}

async function nextPlayer() {
    try {
        const response = await fetch('/next_player', {
            method: 'POST',
            body: new URLSearchParams({ session_id: sessionId })
        });
        if (!response.ok) throw new Error('Failed to switch player');
        const data = await response.json();
        if (data.result === 'game_over') {
            feedback.textContent = 'Game Over! Leaderboard: ' + data.leaderboard.map(p => `${p[0]}: ${p[1]}`).join(', ');
            setTimeout(() => resetToMenu(), 5000);
        } else {
            currentPlayer++;
            feedback.textContent = `${data.player}'s turn!`;
            attempts = 0;
            gameActive = true;  // Re-enable guesses
            updateAttempts();
        }
    } catch (error) {
        alert('Error switching player: ' + error.message);
    }
}

async function quitGame() {
    try {
        await fetch('/quit', { method: 'POST', body: new URLSearchParams({ session_id: sessionId }) });
        feedback.textContent = 'Quitted the game';
        gameActive = false;
        setTimeout(() => resetToMenu(), 2000);
    } catch (error) {
        alert('Error quitting: ' + error.message);
    }
}

function endGame() {
    gameActive = false;
    setTimeout(() => resetToMenu(), 2000);
}

function resetToMenu() {
    gameArea.style.display = 'none';
    menu.style.display = 'block';
    feedback.textContent = '';
    gameActive = true;
}

function updateAttempts() {
    attemptsDisplay.textContent = `Attempts: ${attempts}`;
}

async function showLeaderboard() {
    menu.style.display = 'none';
    leaderboardDiv.style.display = 'block';
    updateLeaderboard();
}

async function updateLeaderboard() {
    try {
        const level = levelFilter.value;
        const response = await fetch(`/leaderboard?level=${level}`);
        if (!response.ok) throw new Error('Failed to load leaderboard');
        const data = await response.json();
        leaderboardList.innerHTML = data.map((entry, i) => `<li>${i+1}. ${entry.name}: ${entry.attempts} attempts</li>`).join('');
    } catch (error) {
        alert('Error loading leaderboard: ' + error.message);
    }
}

function hideLeaderboard() {
    leaderboardDiv.style.display = 'none';
    menu.style.display = 'block';
}

// Initial setup
resetToMenu();