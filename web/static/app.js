// RAYVEN Web Interface - Grid Animation Controller

const socket = io();

// State
let currentState = {
    level: 1,
    balance: 59.85,
    progress: 0,
    target: 85.0,
    coin: "BTC",
    current_step: 0,
    trades: []
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeCycleGrid();
    initializeHistoryGrid();
    console.log("🤖 RAYVEN Interface Loaded");
});

// Initialize 9-step cycle grid
function initializeCycleGrid() {
    const grid = document.getElementById('cycle-grid');
    grid.innerHTML = '';

    for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.className = 'cycle-cell inactive';
        cell.id = `step-${i}`;
        cell.textContent = '░';
        grid.appendChild(cell);
    }
}

// Initialize trade history grid (50 empty cells initially)
function initializeHistoryGrid() {
    const grid = document.getElementById('history-grid');
    grid.innerHTML = '';

    for (let i = 0; i < 50; i++) {
        const cell = document.createElement('div');
        cell.className = 'trade-cell empty';
        grid.appendChild(cell);
    }
}

// Update cycle grid step
function updateCycleStep(stepNum, state = 'active') {
    // Reset all to inactive first
    for (let i = 0; i < 9; i++) {
        const cell = document.getElementById(`step-${i}`);
        if (i < stepNum) {
            // Completed steps
            cell.className = 'cycle-cell completed';
            if (i === 5) cell.classList.add('decision'); // Decision step
            cell.textContent = '█';
        } else if (i === stepNum) {
            // Active step
            cell.className = 'cycle-cell active';
            cell.textContent = '⚡';
        } else {
            // Upcoming steps
            cell.className = 'cycle-cell inactive';
            cell.textContent = '░';
        }
    }
}

// Add trade to history grid
function addTradeToHistory(tradeData) {
    const grid = document.getElementById('history-grid');
    const cells = grid.querySelectorAll('.trade-cell');

    // Find first empty cell
    for (let cell of cells) {
        if (cell.classList.contains('empty')) {
            cell.classList.remove('empty');

            // Set color based on outcome
            if (tradeData.outcome === 'win') {
                cell.classList.add('win');
            } else if (tradeData.outcome === 'loss') {
                cell.classList.add('loss');
            } else {
                cell.classList.add('hold');
            }

            // Add tooltip
            const tooltip = `${tradeData.pattern || 'HOLD'} | ${tradeData.profit || 'N/A'}`;
            cell.setAttribute('data-tooltip', tooltip);

            break;
        }
    }
}

// Update UI elements
function updateUI(state) {
    // Level and progress
    document.getElementById('level-badge').textContent = `LVL ${state.level}`;
    document.getElementById('progress-bar').style.width = `${state.progress}%`;
    document.getElementById('progress-text').textContent = `${Math.round(state.progress)}%`;

    // Coin and balance
    document.getElementById('coin').textContent = state.coin;
    document.getElementById('balance').textContent = `$${state.balance.toFixed(2)}`;

    // Status message
    document.getElementById('status-text').textContent = state.status || 'Running...';
}

// Level up animation
function triggerLevelUp(levelData) {
    const window = document.querySelector('.window');
    window.classList.add('levelup');

    // Play for 3 seconds
    setTimeout(() => {
        window.classList.remove('levelup');
    }, 3000);

    // Update status with achievement
    const statusText = document.getElementById('status-text');
    statusText.textContent = `🎉 LEVEL UP! ${levelData.achievement}`;
    statusText.style.color = '#ffff00';

    setTimeout(() => {
        statusText.style.color = '#00ffff';
    }, 3000);
}

// WebSocket Event Handlers

socket.on('connect', () => {
    console.log('✅ Connected to RAYVEN');
    document.getElementById('status-text').textContent = 'Connected to RAYVEN...';
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from RAYVEN');
    document.getElementById('status-text').textContent = 'Disconnected - Reconnecting...';
});

socket.on('state_update', (data) => {
    console.log('State update:', data);
    currentState = { ...currentState, ...data };
    updateUI(currentState);

    // Update cycle if step changed
    if (data.current_step !== undefined) {
        updateCycleStep(data.current_step);
    }

    // Update history if trades changed
    if (data.trades && data.trades.length > 0) {
        // Rebuild history grid with trades
        const grid = document.getElementById('history-grid');
        grid.innerHTML = '';

        // Add trades (newest first)
        data.trades.slice(0, 50).forEach(trade => {
            const cell = document.createElement('div');
            cell.className = `trade-cell ${trade.outcome}`;

            const tooltip = `${trade.pattern || 'HOLD'} | ${trade.profit || 'N/A'}`;
            cell.setAttribute('data-tooltip', tooltip);

            grid.appendChild(cell);
        });

        // Fill remaining with empty cells
        const remaining = 50 - data.trades.length;
        for (let i = 0; i < remaining; i++) {
            const cell = document.createElement('div');
            cell.className = 'trade-cell empty';
            grid.appendChild(cell);
        }
    }
});

socket.on('step_update', (data) => {
    console.log('Step:', data.step, data.name);
    updateCycleStep(data.step);
    document.getElementById('status-text').textContent = `Step ${data.step + 1}/9: ${data.name}`;
});

socket.on('trade_complete', (trade) => {
    console.log('Trade completed:', trade);
    addTradeToHistory(trade);

    // Flash message
    const statusText = document.getElementById('status-text');
    const emoji = trade.outcome === 'win' ? '✅' : trade.outcome === 'loss' ? '❌' : '⏸️';
    statusText.textContent = `${emoji} Trade: ${trade.pattern || 'HOLD'} | ${trade.profit || 'No change'}`;
});

socket.on('level_up', (data) => {
    console.log('Level up!', data);
    triggerLevelUp(data);
});

socket.on('status', (data) => {
    console.log('Status:', data.message);
    document.getElementById('status-text').textContent = data.message;
});

// Simulate random activity for testing (when not connected to RAYVEN)
let simulationInterval = null;

function startSimulation() {
    if (socket.connected) return; // Don't simulate if connected

    console.log('📊 Starting simulation mode');

    let step = 0;
    simulationInterval = setInterval(() => {
        updateCycleStep(step);
        step++;

        if (step >= 9) {
            step = 0;

            // Random trade outcome
            const outcomes = ['win', 'loss', 'hold'];
            const patterns = ['support_bounce', 'mean_reversion', 'breakout', 'trend_follow'];
            const outcome = outcomes[Math.floor(Math.random() * outcomes.length)];
            const pattern = patterns[Math.floor(Math.random() * patterns.length)];
            const profit = outcome === 'win' ? `+${(Math.random() * 5).toFixed(2)}%` :
                          outcome === 'loss' ? `-${(Math.random() * 2).toFixed(2)}%` : 'N/A';

            addTradeToHistory({ outcome, pattern, profit });

            // Update balance
            currentState.balance += outcome === 'win' ? 2 : outcome === 'loss' ? -1 : 0;
            currentState.progress = Math.min(100, currentState.progress + (outcome === 'win' ? 3 : 1));

            if (currentState.progress >= 100) {
                currentState.level++;
                currentState.progress = 0;
                triggerLevelUp({ achievement: '🎮 Simulated Level Up!' });
            }

            updateUI(currentState);
        }
    }, 500);
}

// Auto-start simulation if not connected after 3 seconds
setTimeout(() => {
    if (!socket.connected) {
        console.log('⚠️ Not connected to RAYVEN - starting demo mode');
        startSimulation();
    }
}, 3000);
