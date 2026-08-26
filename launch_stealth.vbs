Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

pythonExe = "pythonw.exe"
If FSO.FileExists(scriptDir & "\.venv\Scripts\pythonw.exe") Then
    pythonExe = """" & scriptDir & "\.venv\Scripts\pythonw.exe"""
ElseIf FSO.FileExists(scriptDir & "\venv\Scripts\pythonw.exe") Then
    pythonExe = """" & scriptDir & "\venv\Scripts\pythonw.exe"""
End If

WshShell.Run pythonExe & " """ & scriptDir & "\main.py""", 0, False
