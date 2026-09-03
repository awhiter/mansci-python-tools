Option Explicit
Dim shell, launcher, result
Set shell = CreateObject("WScript.Shell")
If WScript.Arguments.Count < 1 Then
    MsgBox "The ManSci VS Code launcher is incomplete. Rerun the installer.", 16, "ManSci VS Code"
    WScript.Quit 2
End If
launcher = WScript.Arguments(0)
shell.Environment("PROCESS")("MANSCI_HIDDEN_LAUNCH") = "1"
result = shell.Run(Chr(34) & launcher & Chr(34), 0, True)
If result <> 0 Then
    MsgBox "ManSci VS Code did not start correctly. Run ManSci VS Code Check or rerun the installer.", 16, "ManSci VS Code"
End If
WScript.Quit result

