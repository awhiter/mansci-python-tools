param(
    [Parameter(Mandatory = $true)][string]$LauncherDirectory,
    [Parameter(Mandatory = $true)][string]$SupportDirectory
)

$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$icon = Join-Path $SupportDirectory 'icons\vscode.ico'

$mainPath = Join-Path $desktop 'ManSci VS Code.lnk'
Remove-Item $mainPath -Force -ErrorAction SilentlyContinue
$main = $shell.CreateShortcut($mainPath)
$main.TargetPath = Join-Path $env:WINDIR 'System32\wscript.exe'
$main.Arguments = '"' + (Join-Path $LauncherDirectory 'windows-hidden-launch.vbs') + '" "' + (Join-Path $LauncherDirectory 'launch-vscode-windows.bat') + '"'
$main.WorkingDirectory = $LauncherDirectory
$main.IconLocation = $icon
$main.Save()

$check = $shell.CreateShortcut((Join-Path $desktop 'ManSci VS Code Check.lnk'))
$check.TargetPath = Join-Path $LauncherDirectory 'check-vscode-windows.bat'
$check.WorkingDirectory = $LauncherDirectory
$check.IconLocation = $icon
$check.Save()
