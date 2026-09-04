param([Parameter(Mandatory=$true)][string]$PackageRoot,
      [Parameter(Mandatory=$true)][ValidateSet('Core','Spyder','Lab','VS-Code','Complete')][string]$Kind)
$ErrorActionPreference = 'Stop'
$logDir = Join-Path $env:LOCALAPPDATA 'ManagementScience\Logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ('install-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.log')
$status = 1
function Say([string]$message) { Write-Host $message }
function Agree([string]$message) { return (Read-Host ($message + ' [y/N]')) -match '^(y|yes)$' }
function Locate([string]$command, [string[]]$paths) {
    foreach ($p in $paths) { if ($p -and (Test-Path -LiteralPath $p -PathType Leaf)) { return $p } }
    $c = Get-Command $command -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    return $null
}
function Find-Code {
    return Locate 'code.cmd' @("$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd", "$env:ProgramFiles\Microsoft VS Code\bin\code.cmd")
}
function Find-Ollama {
    return Locate 'ollama.exe' @("$env:LOCALAPPDATA\Programs\Ollama\ollama.exe", "$env:ProgramFiles\Ollama\ollama.exe")
}
function Install-App([string]$id, [string]$label, [string]$url) {
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if (-not $winget -or -not (Agree "$label is missing. Download/install it with Windows Package Manager? Read and respond to any installer terms/prompts.")) {
        throw "Install $label inside Windows from $url, then rerun this installer. See README.md / DISTRIBUTION-GUIDE.md. No later stages have run."
    }
    & $winget.Source install --id $id --exact --interactive
    if ($LASTEXITCODE -ne 0) { throw "$label installation failed. Install it from $url and rerun. See the log for details." }
}
try {
    Start-Transcript -Path $log | Out-Null
    Say "Management Science $Kind installer - staff testing"
    Say 'Stages: 1 prerequisites; 2 terms; 3 Python environment; 4 local AI; 5 tool launchers.'
    Say 'Keep this window open. Downloads/installations can take many minutes, especially in a VM.'
    Say 'Watch for prompts here and in other installer windows. No account is required for local AI.'
    Say 'If Ollama opens, choose the LOCAL option, not sign in. We start its service automatically.'
    Say "Log: $log"
    Say 'Close all ManSci tools before continuing; updates must not run while they are open.'
    if (-not (Agree 'Ready to check/install the required software?')) { throw 'Cancelled. Nothing else was installed.' }
    Say '[1/5] Checking prerequisites BEFORE downloading Python packages...'
    $arch = if ($env:PROCESSOR_ARCHITEW6432) { $env:PROCESSOR_ARCHITEW6432 } else { $env:PROCESSOR_ARCHITECTURE }
    Say "Windows processor architecture: $arch"
    if ($arch -notin @('AMD64','ARM64')) { throw 'This distribution requires 64-bit Windows 11. See the installation guide.' }
    if ($arch -eq 'ARM64') {
        Say 'Windows ARM VM: this Miniconda setup uses Windows x64 emulation. Native Ollama/VS Code are separate.'
        if (-not (Agree 'Continue with this staff-testing x64 Python configuration on Windows ARM?')) { throw 'Cancelled on Windows ARM.' }
    }
    if ($Kind -in @('Complete','VS-Code')) {
        $env:MANSCI_CODE = Find-Code
        if (-not $env:MANSCI_CODE) { Install-App 'Microsoft.VisualStudioCode' 'Visual Studio Code' 'https://code.visualstudio.com/download'; $env:MANSCI_CODE = Find-Code }
        if (-not $env:MANSCI_CODE) { throw 'VS Code was not found after installation. Restart this installer, or install VS Code in its standard per-user location.' }
    }
    $env:MANSCI_OLLAMA = Find-Ollama
    if (-not $env:MANSCI_OLLAMA) { Install-App 'Ollama.Ollama' 'Ollama' 'https://ollama.com/download/windows'; $env:MANSCI_OLLAMA = Find-Ollama }
    if (-not $env:MANSCI_OLLAMA) { throw 'Ollama was not found after installation. Restart this installer. If asked, choose local use; no sign-in is needed.' }
    $saved = Join-Path $env:LOCALAPPDATA 'ManagementScience\Core\conda-path.txt'
    $candidates = @()
    if (Test-Path $saved) { $candidates += (Get-Content $saved -Raw).Trim() }
    if ($env:CONDA_EXE) { $candidates += $env:CONDA_EXE }
    $candidates += @("$env:USERPROFILE\miniconda3\Scripts\conda.exe", "$env:LOCALAPPDATA\miniconda3\Scripts\conda.exe", "$env:ProgramData\miniconda3\Scripts\conda.exe", "$env:USERPROFILE\anaconda3\Scripts\conda.exe", "$env:LOCALAPPDATA\anaconda3\Scripts\conda.exe", "$env:ProgramData\anaconda3\Scripts\conda.exe")
    $conda = Locate 'conda.exe' $candidates
    if (-not $conda) {
        $custom = Read-Host 'Conda not found. If already installed, paste its installation folder; otherwise press Enter for automatic Miniconda setup'
        if ($custom) { $conda = Locate 'conda.exe' @((Join-Path ($custom.Trim('"')) 'Scripts\conda.exe')); if (-not $conda) { throw 'No conda.exe in the specified folder. Check its location and rerun.' } }
    }
    if (-not $conda) {
        Say 'Miniconda terms: https://www.anaconda.com/legal'
        if (-not (Agree 'After reviewing the terms, do you agree and want Miniconda installed for this Windows user?')) { throw 'Miniconda consent declined. See the guide for manual installation.' }
        $target = Join-Path $env:USERPROFILE 'miniconda3'
        if (Test-Path $target) { throw "The folder $target already exists but no working Conda was found. It will not be overwritten; contact staff." }
        $temp = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString())
        New-Item -ItemType Directory -Path $temp | Out-Null
        $download = Join-Path $temp 'Miniconda.exe'
        Say 'Downloading Miniconda from Anaconda. Please wait; installation can also take several minutes.'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -UseBasicParsing 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile $download
        $signature = Get-AuthenticodeSignature $download
        if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Anaconda') { throw 'Miniconda publisher signature could not be verified. Download manually from Anaconda; this file was not executed.' }
        $process = Start-Process -FilePath $download -ArgumentList "/InstallationType=JustMe /RegisterPython=0 /AddToPath=0 /S /D=$target" -Wait -PassThru
        if ($process.ExitCode -ne 0) { throw "Miniconda installation returned $($process.ExitCode). See the log and installation guide." }
        $conda = Join-Path $target 'Scripts\conda.exe'
    }
    $basePython = Join-Path (Split-Path (Split-Path $conda)) 'python.exe'
    if (-not (Test-Path $basePython)) { throw 'Cannot find the Python belonging to Conda. Use its full Scripts\conda.exe path.' }
    $env:MANSCI_INSTALL_LOG = $log
    & $basePython -u (Join-Path $PSScriptRoot 'install.py') --package $PackageRoot --kind $Kind --conda $conda
    $status = $LASTEXITCODE
    if ($status -ne 0) { throw "Installation stopped. The error above identifies the failed stage. Log: $log" }
} catch {
    Say "INSTALLATION NOT COMPLETE: $($_.Exception.Message)"
    Say 'Fix the reported issue and rerun. Existing code and downloaded models are preserved.'
    $status = 1
} finally {
    Say "Share this log with staff if needed: $log"
    try { Stop-Transcript | Out-Null } catch { }
}
exit $status
