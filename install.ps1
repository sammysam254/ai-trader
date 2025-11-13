Write-Host "Installing AI Forex Trader Dependencies..." -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Installing core packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install pandas numpy scikit-learn joblib

Write-Host ""
Write-Host "[2/3] Installing technical analysis and visualization..." -ForegroundColor Yellow
python -m pip install ta matplotlib seaborn

Write-Host ""
Write-Host "[3/3] Installing web framework and MT5..." -ForegroundColor Yellow
python -m pip install flask flask-cors python-dotenv MetaTrader5

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy .env.example to .env"
Write-Host "2. Edit .env with your MT5 credentials"
Write-Host "3. Run: python app.py"
Write-Host ""
