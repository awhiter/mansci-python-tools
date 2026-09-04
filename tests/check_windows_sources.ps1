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
$stub += ' namespace System.Management { public class ManagementObject { public object this[string key] {get {return null;}} } public class ManagementObjectSearcher : System.IDisposable { public ManagementObjectSearcher(string q) {} public System.Collections.Generic.List<ManagementObject> Get() {return new System.Collections.Generic.List<ManagementObject>();} public void Dispose() {} } }'
$source = Get-Content (Join-Path $root 'installer/WindowsLauncher.cs') -Raw
Add-Type -TypeDefinition ($source + "`n" + $stub)
if (-not [ManSciTaskbar]::MatchesProfileArgs(@('Code.exe','--user-data-dir','/tmp/ManSci Profile'), '/tmp/ManSci Profile')) { throw 'Exact profile match failed' }
if ([ManSciTaskbar]::MatchesProfileArgs(@('Code.exe','--user-data-dir','/tmp/ManSci Profile-other'), '/tmp/ManSci Profile')) { throw 'Unrelated profile matched' }
if ([ManSciTaskbar]::MatchesProfileArgs(@('Code.exe','/tmp/ManSci Profile'), '/tmp/ManSci Profile')) { throw 'Folder argument mistaken for profile' }
if (-not [ManSciTaskbar]::MatchesProfileArgs(@('Code.exe','--user-data-dir=/tmp/ManSci Profile'), '/tmp/ManSci Profile')) { throw 'Equals-form profile match failed' }
Write-Output 'PowerShell syntax, C# compilation and profile matching PASS (Forms/WMI stubs; no Windows COM execution).'
