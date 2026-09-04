# Cross-platform syntax/compilation check, NOT Windows UI/COM verification.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot
Get-ChildItem (Join-Path $root 'installer/*.ps1') | ForEach-Object {
    $tokens = $null; $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors) { throw ($errors | Out-String) }
}
# Stand in for Windows Forms on Mac; production uses the real .NET assembly.
$stub = 'namespace System.Windows.Forms { public enum MessageBoxButtons { OK } public enum MessageBoxIcon { Error } public static class MessageBox { public static void Show(string a,string b,MessageBoxButtons c,MessageBoxIcon d) {} } }'
$source = Get-Content (Join-Path $root 'installer/WindowsLauncher.cs') -Raw
Add-Type -TypeDefinition ($source + "`n" + $stub)
Write-Output 'PowerShell syntax and launcher C# compilation PASS (Forms stub; no Windows execution).'
