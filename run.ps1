Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

if (Get-ChildItem -Directory -Path .venv) {
    Write-Host "Activating Python virtual environment..."
    & .venv/Scripts/Activate.ps1
} else {
    Write-Host "No Python virtual environment found. Creating one now..."
    & python -m venv .venv
    Write-Host "Activating Python virtual environment..."
    & .venv/Scripts/Activate.ps1
    Write-Host "Installing python dependencies..."
    & pip install -r VintedAssistant/requirements.txt
}

Write-Host "Running streamlit..."
& streamlit run VintedAssistant/main.py --server.headless=true --server.port=8501