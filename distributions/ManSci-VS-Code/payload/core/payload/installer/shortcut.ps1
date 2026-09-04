param([Parameter(Mandatory=$true)][string]$Name,
      [Parameter(Mandatory=$true)][string]$Launcher,
      [Parameter(Mandatory=$true)][string]$Wrapper,
      [Parameter(Mandatory=$true)][string]$Icon)
$ErrorActionPreference = 'Stop'
$target = Join-Path $env:WINDIR 'System32\wscript.exe'
foreach ($file in @($target, $Launcher, $Wrapper, $Icon)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Launcher dependency missing: $file" }
}
$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop ($Name + '.lnk')
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.Arguments = '"' + $Wrapper + '" "' + $Launcher + '"'
$shortcut.WorkingDirectory = Split-Path -Parent $Launcher
$shortcut.IconLocation = $Icon + ',0'
$shortcut.Save()
$check = $shell.CreateShortcut($shortcutPath)
if ($check.TargetPath -ne $target -or $check.Arguments -ne $shortcut.Arguments) { throw 'Shortcut verification failed.' }
Write-Host "PASS: $shortcutPath"
