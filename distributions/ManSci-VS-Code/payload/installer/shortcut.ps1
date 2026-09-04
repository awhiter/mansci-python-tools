param([Parameter(Mandatory=$true)][string]$Name,
      [Parameter(Mandatory=$true)][string]$Executable,
      [Parameter(Mandatory=$true)][string]$Icon,
      [string]$AppId = '')
$ErrorActionPreference = 'Stop'
$target = $Executable
foreach ($file in @($target, $Icon)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Launcher dependency missing: $file" }
}
$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
$programs = Join-Path ([Environment]::GetFolderPath('Programs')) 'Management Science'
New-Item -ItemType Directory -Force -Path $programs | Out-Null
if ($AppId) {
    Add-Type -Path (Join-Path $PSScriptRoot 'WindowsLauncher.cs') -ReferencedAssemblies System.dll,System.Core.dll,System.Windows.Forms.dll,System.Management.dll
}
foreach ($folder in @($desktop, $programs)) {
$shortcutPath = Join-Path $folder ($Name + '.lnk')
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.Arguments = ''
$shortcut.WorkingDirectory = Split-Path -Parent $Executable
$shortcut.IconLocation = $Icon + ',0'
$shortcut.Save()
if ($AppId) { [ManSciTaskbar]::SetShortcut($shortcutPath, $AppId) }
$check = $shell.CreateShortcut($shortcutPath)
if ($check.TargetPath -ne $target -or $check.Arguments -ne $shortcut.Arguments) { throw 'Shortcut verification failed.' }
Write-Host "PASS: $shortcutPath"
}
Write-Host 'Optional: find the ManSci entry in Start, right-click, then Pin to taskbar (or More > Pin to taskbar). Nothing has been pinned automatically.'
