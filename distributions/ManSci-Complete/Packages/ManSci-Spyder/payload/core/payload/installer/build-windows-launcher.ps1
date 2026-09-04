param([Parameter(Mandatory=$true)][string]$Output,
      [Parameter(Mandatory=$true)][string]$Icon)
$ErrorActionPreference = 'Stop'
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $compiler)) {
    $compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
}
if (-not (Test-Path -LiteralPath $compiler)) {
    throw 'The Windows .NET Framework compiler is missing. Contact staff to repair the Windows .NET Framework installation.'
}
& $compiler /nologo /target:winexe /platform:anycpu /reference:System.Windows.Forms.dll "/win32icon:$Icon" "/out:$Output" (Join-Path $PSScriptRoot 'WindowsLauncher.cs')
if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Output -PathType Leaf)) {
    throw 'Could not build the pinnable launcher. Close all ManSci tools and rerun the installer.'
}
Write-Host "PASS: windowless, icon-bearing launcher $Output"
