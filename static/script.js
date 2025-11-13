let connected = false;
let currentSignal = null;
let mt5Modal;

// Initialize modal
document.addEventListener('DOMContentLoaded', () => {
    mt5Modal = new bootstrap.Modal(document.getElementById('mt5Modal'));
    loadSavedCredentials();
});

// Connect to MT5 - Show modal
document.getElementById('connect-btn').addEventListener('click', () => {
    if (connected) {
        disconnect();
    } else {
        mt5Modal.show();
    }
});

// Handle connection form submission
document.getElementById('connect-submit').addEventListener('click', async () => {
    const btn = document.getElementById('connect-submit');
    const errorDiv = document.getElementById('connection-error');
    
    // Get form values
    const login = document.getElementById('mt5-login').value.trim();
    const password = document.getElementById('mt5-password').value;
    const server = document.getElementById('mt5-server').value.trim();
    const path = document.getElementById('mt5-path').value.trim();
    const saveCredentials = document.getElementById('save-credentials').checked;
    
    // Validate
    if (!login || !password || !server) {
        errorDiv.textContent = 'Please fill in all required fields';
        errorDiv.classList.remove('d-none');
        return;
    }
    
    errorDiv.classList.add('d-none');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Connecting...';
    
    try {
        const response = await fetch('/api/connect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login, password, server, path })
        });
        
        const data = await response.json();
        
        if (data.success) {
            connected = true;
            
            // Save credentials if requested
            if (saveCredentials) {
                localStorage.setItem('mt5_credentials', JSON.stringify({
                    login, server, path
                }));
            }
            
            // Update UI
            document.getElementById('connection-status').textContent = 'Connected';
            document.getElementById('connection-status').className = 'badge bg-success me-3';
            
            // Show account type badge
            const accountTypeBadge = document.getElementById('account-type-badge');
            accountTypeBadge.textContent = data.account_type;
            accountTypeBadge.className = `badge me-3 ${data.account_type === 'DEMO' ? 'bg-warning text-dark' : 'bg-danger'}`;
            accountTypeBadge.classList.remove('d-none');
            
            const connectBtn = document.getElementById('connect-btn');
            connectBtn.textContent = 'Disconnect';
            connectBtn.className = 'btn btn-outline-danger btn-sm';
            
            // Update account info
            updateAccountInfo(data.account);
            
            // Enable buttons
            enableButtons();
            
            // Start auto-refresh
            startAutoRefresh();
            
            // Close modal
            mt5Modal.hide();
            
            // Clear password field
            document.getElementById('mt5-password').value = '';
            
        } else {
            errorDiv.textContent = data.message || 'Connection failed';
            errorDiv.classList.remove('d-none');
        }
    } catch (error) {
        errorDiv.textContent = 'Error: ' + error.message;
        errorDiv.classList.remove('d-none');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-plug-fill"></i> Connect';
    }
});

// Load saved credentials
function loadSavedCredentials() {
    const saved = localStorage.getItem('mt5_credentials');
    if (saved) {
        try {
            const creds = JSON.parse(saved);
            document.getElementById('mt5-login').value = creds.login || '';
            document.getElementById('mt5-server').value = creds.server || '';
            document.getElementById('mt5-path').value = creds.path || 'C:\\Program Files\\MetaTrader 5\\terminal64.exe';
            document.getElementById('save-credentials').checked = true;
        } catch (e) {
            console.error('Error loading saved credentials:', e);
        }
    }
}

async function disconnect() {
    const btn = document.getElementById('connect-btn');
    
    try {
        await fetch('/api/disconnect', { method: 'POST' });
        connected = false;
        document.getElementById('connection-status').textContent = 'Disconnected';
        document.getElementById('connection-status').className = 'badge bg-danger me-3';
        
        // Hide account type badge
        document.getElementById('account-type-badge').classList.add('d-none');
        
        btn.textContent = 'Connect MT5';
        btn.className = 'btn btn-outline-light btn-sm';
        
        disableButtons();
        stopAutoRefresh();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

function updateAccountInfo(account) {
    document.getElementById('account-balance').textContent = '$' + account.balance.toFixed(2);
    document.getElementById('account-equity').textContent = '$' + account.equity.toFixed(2);
    
    const profit = account.profit;
    const profitEl = document.getElementById('account-profit');
    profitEl.textContent = '$' + profit.toFixed(2);
    profitEl.className = profit >= 0 ? 'text-success' : 'text-danger';
    
    document.getElementById('account-margin').textContent = '$' + account.free_margin.toFixed(2);
}

function enableButtons() {
    document.getElementById('analyze-btn').disabled = false;
    document.getElementById('backtest-btn').disabled = false;
    document.getElementById('train-model-btn').disabled = false;
    document.getElementById('start-trading-btn').disabled = false;
}

function disableButtons() {
    document.getElementById('analyze-btn').disabled = true;
    document.getElementById('backtest-btn').disabled = true;
    document.getElementById('train-model-btn').disabled = true;
    document.getElementById('start-trading-btn').disabled = true;
    document.getElementById('stop-trading-btn').disabled = true;
}

// Analyze pair
document.getElementById('analyze-btn').addEventListener('click', async () => {
    const btn = document.getElementById('analyze-btn');
    const symbol = document.getElementById('symbol-select').value;
    const timeframe = document.getElementById('timeframe-select').value;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, timeframe })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        currentSignal = data;
        displaySignal(data);
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Analyze';
    }
});

function displaySignal(data) {
    const resultDiv = document.getElementById('signal-result');
    resultDiv.classList.remove('d-none');
    
    const signalText = document.getElementById('signal-text');
    const signalAlert = document.getElementById('signal-alert');
    
    signalText.textContent = data.signal_text;
    document.getElementById('signal-confidence').textContent = (data.confidence * 100).toFixed(1) + '%';
    
    // Update alert styling
    signalAlert.className = 'alert text-center ';
    if (data.signal === 1) {
        signalAlert.classList.add('signal-buy');
    } else if (data.signal === -1) {
        signalAlert.classList.add('signal-sell');
    } else {
        signalAlert.classList.add('signal-neutral');
    }
    
    // Update indicators
    document.getElementById('ind-rsi').textContent = data.indicators.rsi.toFixed(2);
    document.getElementById('ind-macd').textContent = data.indicators.macd.toFixed(5);
    document.getElementById('ind-adx').textContent = data.indicators.adx.toFixed(2);
    document.getElementById('ind-atr').textContent = data.indicators.atr.toFixed(5);
    
    // Enable/disable execute button
    document.getElementById('execute-trade-btn').disabled = data.signal === 0;
}

// Execute trade
document.getElementById('execute-trade-btn').addEventListener('click', async () => {
    if (!currentSignal || currentSignal.signal === 0) {
        alert('No valid signal to execute');
        return;
    }
    
    if (!confirm(`Execute ${currentSignal.signal_text} trade on ${currentSignal.symbol}?`)) {
        return;
    }
    
    const btn = document.getElementById('execute-trade-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Executing...';
    
    try {
        const response = await fetch('/api/execute-trade', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbol: currentSignal.symbol,
                signal: currentSignal.signal
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Trade executed successfully!');
            refreshPositions();
            refreshAccount();
        } else {
            alert('Trade failed: ' + data.message);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-lightning-fill"></i> Execute Trade';
    }
});

// Refresh positions
async function refreshPositions() {
    if (!connected) return;
    
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();
        
        const listDiv = document.getElementById('positions-list');
        
        if (positions.length === 0) {
            listDiv.innerHTML = '<p class="text-muted text-center">No open positions</p>';
            return;
        }
        
        listDiv.innerHTML = positions.map(pos => `
            <div class="position-card ${pos.type}">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <strong>${pos.symbol}</strong>
                    <span class="badge bg-${pos.type === 'buy' ? 'success' : 'danger'}">${pos.type.toUpperCase()}</span>
                </div>
                <div class="small">
                    <div>Entry: ${pos.price_open.toFixed(5)}</div>
                    <div>Current: ${pos.price_current.toFixed(5)}</div>
                    <div>SL: ${pos.sl.toFixed(5)} | TP: ${pos.tp.toFixed(5)}</div>
                    <div class="${pos.profit >= 0 ? 'profit-positive' : 'profit-negative'}">
                        P&L: $${pos.profit.toFixed(2)}
                    </div>
                </div>
                <button class="btn btn-sm btn-danger w-100 mt-2" onclick="closePosition(${pos.ticket})">
                    Close Position
                </button>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error refreshing positions:', error);
    }
}

async function closePosition(ticket) {
    if (!confirm('Close this position?')) return;
    
    try {
        const response = await fetch(`/api/close-position/${ticket}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            alert('Position closed');
            refreshPositions();
            refreshAccount();
        } else {
            alert('Failed to close position');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function refreshAccount() {
    if (!connected) return;
    
    try {
        const response = await fetch('/api/account');
        const account = await response.json();
        updateAccountInfo(account);
    } catch (error) {
        console.error('Error refreshing account:', error);
    }
}

// Backtest
document.getElementById('backtest-btn').addEventListener('click', async () => {
    const btn = document.getElementById('backtest-btn');
    const symbol = document.getElementById('symbol-select').value;
    const timeframe = document.getElementById('timeframe-select').value;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Running...';
    
    try {
        const response = await fetch('/api/backtest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, timeframe, bars: 2000 })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        displayBacktestResults(data);
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-play-circle"></i> Run Backtest';
    }
});

function displayBacktestResults(data) {
    const resultsDiv = document.getElementById('backtest-results');
    resultsDiv.classList.remove('d-none');
    
    document.getElementById('bt-winrate').textContent = data.win_rate.toFixed(1) + '%';
    document.getElementById('bt-trades').textContent = data.total_trades;
    
    const returnEl = document.getElementById('bt-return');
    returnEl.textContent = data.return_pct.toFixed(2) + '%';
    returnEl.className = data.return_pct >= 0 ? 'text-success' : 'text-danger';
}

// Train model
document.getElementById('train-model-btn').addEventListener('click', async () => {
    if (!confirm('Train ML model? This may take a few minutes.')) return;
    
    const btn = document.getElementById('train-model-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Training...';
    
    try {
        const symbol = document.getElementById('symbol-select').value;
        const response = await fetch('/api/train-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Model trained!\nTrain Score: ${(data.train_score * 100).toFixed(2)}%\nTest Score: ${(data.test_score * 100).toFixed(2)}%`);
        } else {
            alert('Training failed: ' + data.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-cpu"></i> Train ML Model';
    }
});

// Auto trading
document.getElementById('start-trading-btn').addEventListener('click', async () => {
    if (!confirm('Start automated trading? Make sure you have tested the system thoroughly.')) return;
    
    try {
        const response = await fetch('/api/start-trading', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('start-trading-btn').disabled = true;
            document.getElementById('stop-trading-btn').disabled = false;
            alert('Automated trading started');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

document.getElementById('stop-trading-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/stop-trading', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('start-trading-btn').disabled = false;
            document.getElementById('stop-trading-btn').disabled = true;
            alert('Automated trading stopped');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// Auto-refresh
let refreshInterval;

function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        refreshPositions();
        refreshAccount();
    }, 5000); // Refresh every 5 seconds
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}
