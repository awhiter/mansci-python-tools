Option Explicit
Dim shell, status, command
Set shell = CreateObject("WScript.Shell")
If WScript.Arguments.Count <> 2 Then
    MsgBox "This launcher is incomplete. Rerun the ManSci installer.", 16, "ManSci"
    WScript.Quit 1
End If
command = Chr(34) & WScript.Arguments(0) & Chr(34) & " " & Chr(34) & WScript.Arguments(1) & Chr(34)
status = shell.Run(command, 0, True)
If status <> 0 Then MsgBox "The tool could not start. See ManagementScience/Logs/launch.log in your user application-data folder, or rerun the installer.", 16, "ManSci"
WScript.Quit status
