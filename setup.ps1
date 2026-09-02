$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $PythonCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($PythonCommand) {
        & py -3 -m venv (Join-Path $ProjectDir ".venv")
    }
    else {
        $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
        if (-not $PythonCommand) {
            throw "未找到 Python 3。请先安装 Python 3.10 或更高版本。"
        }
        & python -m venv (Join-Path $ProjectDir ".venv")
    }
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $ProjectDir "requirements.txt")

Write-Host "依赖安装完成。请在本机创建 .env，且不要将其提交到 Git。"
