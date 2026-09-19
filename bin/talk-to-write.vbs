Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strDir = fso.GetParentFolderName(WScript.ScriptFullName) & "\.."
WshShell.CurrentDirectory = strDir

guiExe = strDir & "\.venv\Scripts\talk-to-write-gui.exe"
pythonwExe = strDir & "\.venv\Scripts\pythonw.exe"

If fso.FileExists(guiExe) Then
    WshShell.Run """" & guiExe & """", 0, False
ElseIf fso.FileExists(pythonwExe) Then
    WshShell.Run """" & pythonwExe & """ -m talk_to_write", 0, False
Else
    WshShell.Run "pythonw -m talk_to_write", 0, False
End If
