$envName = "venv"

if (-Not (Test-Path $envName)) {
    Write-Host "Creating virtual environment $envName..."
    py -3.11 -m venv $envName
} else {
    Write-Host "$envName already exists"
}

# Активация venv
$activateScript = ".\$envName\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "No activation script found"
    exit 1
}

# Обновление pip, setuptools, wheel
pip -m pip install --upgrade pip setuptools wheel

# Установка библиотек
pip install pytest
pip install icontract
pip install typeguard
pip install numpy
pip install beartype
pip install matplotlib
pip install seaborn
pip install pandas

Write-Host "`nInstalled into $envName"