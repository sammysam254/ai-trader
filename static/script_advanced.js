let connected = false;
let mt5Modal;
let logRefreshInterval;
let currentSignal = null;

document.addEventListener('DOMContentLoaded', () => {
    mt5Modal = new bootstrap.Modal(document.getElementById('mt5Modal'));
    loadSavedCredentials();
    startLogRefresh();
    startPositionRefresh();
});

// Connect button
document.getElementById('connect-btn').addEventListener('click', () => {
    if (connected) {
        disconnect();
    } else {
        mt5Modal.show();
    }
});

// Connection form
document.getElementById('connect-submit').addEventListener('click', async () => {
    const btn = document.getElementById('connect-submit');
    const errorDiv = document.getElementById('connection-error');
    
    const login = document.getElementById('mt5-login').value.trim();
    const password = document.getElementById('mt5-password').value;
    const server = document.getElementById('mt5-server').value.trim();
    const path = document.getElementById('mt5-path').value.trim();
    const saveCredentials = document.getElementById('save-credentials').checked;
    
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
            
            if (saveCredentials) {
                localStorage.setItem('mt5_credentials', JSON.stringify({ login, server, path }));
            }
            
            document.getElementById('connection-status').textContent = 'Connected';
            document.getElementById('connection-status').className = 'badge bg-success me-2';
            
            const accountTypeBadge = document.getElementById('account-type-badge');
            accountTypeBadge.textContent = data.account_type;
            accountTypeBadge.className = `badge me-2 ${data.account_type === 'DEMO' ? 'bg-warning text-dark' : 'bg-danger'}`;
            accountTypeBadge.classList.remove('d-none');
            
            document.getElementById('connect-btn').textContent = 'Disconnect';
            document.getElementById('connect-btn').className = 'btn btn-outline-danger btn-sm';
            
            updateAccountInfo(data.account);
            enableButtons();
            mt5Modal.hide();
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

function loadSavedCredentials() {
    const saved = localStorage.getItem('mt5_credentials');
    if (saved) {
        try {
            const creds = JSON.parse(saved);
            document.getElementById('mt5-login').value = creds.login || '';
            document.getElementById('mt5-server').value = creds.server || '';
            document.getElementById('mt5-path').value = creds.path || 'C:\\Program Files\\MetaTrader 5\\terminal64.exe';
            document.getElementById('save-credentials').checked = true;
        } catch (e) {}
    }
}

async function disconnect() {
    try {
        await fetch('/api/disconnect', { method: 'POST' });
        connected = false;
        document.getElementById('connection-status').textContent = 'Disconnected';
        document.getElementById('connection-status').className = 'badge bg-danger me-2';
        document.getElementById('account-type-badge').classList.add('d-none');
        document.getElementById('connect-btn').textContent = 'Connect MT5';
        document.getElementById('connect-btn').className = 'btn btn-outline-light btn-sm';
        disableButtons();
    } catch (error) {
        console.error('Disconnect error:', error);
    }
}

function updateAccountInfo(account) {
    document.getElementById('account-balance').textContent = '$' + account.balance.toFixed(2);
    document.getElementById('account-equity').textContent = '$' + account.equity.toFixed(2);
    
    const profit = account.profit;
    const profitEl = document.getElementById('account-profit');
    profitEl.textContent = '$' + profit.toFixed(2);
    profitEl.className = profit >= 0 ? 'text-success' : 'text-danger';
}

function enableButtons() {
    document.getElementById('analyze-btn').disabled = false;
    document.getElementById('train-btn').disabled = false;
    document.getElementById('start-auto-btn').disabled = false;
}

function disableButtons() {
    document.getElementById('analyze-btn').disabled = true;
    document.getElementById('train-btn').disabled = true;
    document.getElementById('start-auto-btn').disabled = true;
    document.getElementById('stop-auto-btn').disabled = true;
}

// Analyze
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
        
        displaySignal(data);
        
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Analyze';
    }
});

function displaySignal(data) {
    currentSignal = data;
    
    const resultDiv = document.getElementById('signal-result');
    resultDiv.classList.remove('d-none');
    
    const signalText = document.getElementById('signal-text');
    const signalAlert = document.getElementById('signal-alert');
    
    signalText.textContent = data.signal_text;
    document.getElementById('signal-confidence').textContent = (data.confidence * 100).toFixed(1) + '%';
    
    signalAlert.className = 'alert text-center ';
    if (data.signal === 1) {
        signalAlert.classList.add('signal-buy');
    } else if (data.signal === -1) {
        signalAlert.classList.add('signal-sell');
    } else {
        signalAlert.classList.add('signal-neutral');
    }
    
    document.getElementById('buy-score').textContent = data.buy_score.toFixed(1);
    document.getElementById('sell-score').textContent = data.sell_score.toFixed(1);
    
    const patternsDiv = document.getElementById('patterns-found');
    let patternsHtml = '<small class="text-muted">Patterns Found:</small><br>';
    if (data.bullish_patterns > 0) {
        patternsHtml += `<span class="badge bg-success pattern-badge">Bullish: ${data.bullish_patterns}</span>`;
    }
    if (data.bearish_patterns > 0) {
        patternsHtml += `<span class="badge bg-danger pattern-badge">Bearish: ${data.bearish_patterns}</span>`;
    }
    if (data.bullish_patterns === 0 && data.bearish_patterns === 0) {
        patternsHtml += '<span class="badge bg-secondary pattern-badge">None</span>';
    }
    patternsDiv.innerHTML = patternsHtml;
    
    document.getElementById('ind-rsi').textContent = data.indicators.rsi.toFixed(2);
    document.getElementById('ind-macd').textContent = data.indicators.macd.toFixed(5);
    document.getElementById('ind-adx').textContent = data.indicators.adx.toFixed(2);
    document.getElementById('ind-atr').textContent = data.indicators.atr.toFixed(5);
    
    document.getElementById('execute-btn').disabled = false;
}

// Execute trade
document.getElementById('execute-btn').addEventListener('click', async () => {
    if (!currentSignal) {
        alert('Please analyze a pair first');
        return;
    }
    
    const stake = parseFloat(document.getElementById('stake-input').value);
    if (stake < 5 || stake > 1000) {
        alert('Stake must be between $5 and $1000');
        return;
    }
    
    const signalType = currentSignal.signal === 1 ? 'BUY' : 'SELL';
    if (!confirm(`Execute ${signalType} trade on ${currentSignal.symbol} with $${stake} stake?`)) {
        return;
    }
    
    const btn = document.getElementById('execute-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Executing...';
    
    try {
        const response = await fetch('/api/execute-trade', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symbol: currentSignal.symbol,
                signal: currentSignal.signal,
                stake: stake
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Trade executed successfully!\n\nSymbol: ${data.order.symbol}\nType: ${data.order.type.toUpperCase()}\nSize: ${data.order.volume} lots\nEntry: ${data.order.entry.toFixed(5)}\nStop Loss: ${data.order.sl.toFixed(5)}\nTake Profit: ${data.order.tp.toFixed(5)}`);
            refreshPositions();
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

// Auto trading
document.getElementById('start-auto-btn').addEventListener('click', async () => {
    if (!confirm('Start automated trading? Ensure you have tested the system thoroughly.')) return;
    
    try {
        const response = await fetch('/api/start-auto-trading', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('start-auto-btn').disabled = true;
            document.getElementById('stop-auto-btn').disabled = false;
            alert('Auto trading started! Watch the logs.');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

document.getElementById('stop-auto-btn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/stop-auto-trading', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('start-auto-btn').disabled = false;
            document.getElementById('stop-auto-btn').disabled = true;
            alert('Auto trading stopped');
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
});

// Train model
document.getElementById('train-btn').addEventListener('click', async () => {
    if (!confirm('Train AI model? This will take 2-3 minutes and analyze 3000+ historical bars.')) return;
    
    const btn = document.getElementById('train-btn');
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
            alert(`AI Model Trained Successfully!\n\nTraining Accuracy: ${(data.train_score * 100).toFixed(2)}%\nTesting Accuracy: ${(data.test_score * 100).toFixed(2)}%\n\nThe AI is now ready for high-accuracy predictions!`);
        } else {
            alert('Training failed: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-cpu"></i> Train AI Model';
    }
});

// Refresh positions
async function refreshPositions() {
    try {
        const response = await fetch('/api/positions');
        const positions = await response.json();
        
        const listDiv = document.getElementById('positions-list');
        
        if (!positions || positions.length === 0) {
            listDiv.innerHTML = '<p class="text-muted text-center">No open positions</p>';
            // Update totals
            document.getElementById('total-usd-used').textContent = '$0.00';
            document.getElementById('open-positions-count').textContent = '0 positions';
            return;
        }
        
        // Calculate total USD used (margin per position)
        let totalUsdUsed = 0;
        positions.forEach(pos => {
            // Estimate margin per lot based on symbol
            let marginPerLot = 1000; // Default for forex (1:100 leverage)
            
            if (pos.symbol.includes('XAU') || pos.symbol.includes('GOLD')) {
                marginPerLot = 2000; // Higher for gold
            } else if (pos.symbol.includes('JPY')) {
                marginPerLot = 800; // Slightly less for JPY pairs
            }
            
            totalUsdUsed += pos.volume * marginPerLot;
        });
        
        // Update display
        document.getElementById('total-usd-used').textContent = '$' + totalUsdUsed.toFixed(2);
        document.getElementById('open-positions-count').textContent = positions.length + ' position' + (positions.length !== 1 ? 's' : '');
        
        listDiv.innerHTML = positions.map(pos => `
            <div class="position-card ${pos.type}">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <strong>${pos.symbol}</strong>
                    <span class="badge bg-${pos.type === 'buy' ? 'success' : 'danger'}">${pos.type.toUpperCase()}</span>
                </div>
                <div class="small">
                    <div>Volume: ${pos.volume} lots</div>
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

// Close position - GLOBAL FUNCTION
window.closePosition = async function(ticket) {
    if (!confirm('Close this position?')) return;
    
    try {
        const response = await fetch(`/api/close-position/${ticket}`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Position closed successfully!');
            refreshPositions();
        } else {
            alert('Failed to close position: ' + data.message);
        }
    } catch (error) {
        alert('Error closing position: ' + error.message);
    }
};

function startPositionRefresh() {
    setInterval(refreshPositions, 3000);
}

// Logs
function startLogRefresh() {
    logRefreshInterval = setInterval(refreshLogs, 1000);
}

async function refreshLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        
        const container = document.getElementById('log-container');
        container.innerHTML = logs.map(log => `
            <div class="log-entry">
                <span class="log-timestamp">[${log.timestamp}]</span>
                <span class="log-${log.level}">${log.message}</span>
            </div>
        `).join('');
        
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error('Log refresh error:', error);
    }
}

document.getElementById('clear-logs-btn').addEventListener('click', () => {
    document.getElementById('log-container').innerHTML = '<div class="log-entry"><span class="log-info">Logs cleared</span></div>';
});
