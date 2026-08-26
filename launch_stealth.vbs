Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
scriptDir = FSO.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = scriptDir

Dim pyCandidates(5)
pyCandidates(0) = scriptDir & "\.venv\Scripts\pythonw.exe"
pyCandidates(1) = scriptDir & "\venv\Scripts\pythonw.exe"
pyCandidates(2) = "D:\Python312\pythonw.exe"
pyCandidates(3) = "D:\JAADU_REBORN\.venv\Scripts\pythonw.exe"
pyCandidates(4) = "pythonw.exe"
pyCandidates(5) = "python.exe"

pythonExe = ""
For i = 0 To 5
    If InStr(pyCandidates(i), "\") > 0 Then
        If FSO.FileExists(pyCandidates(i)) Then
            pythonExe = """" & pyCandidates(i) & """"
            Exit For
        End If
    Else
        pythonExe = pyCandidates(i)
        Exit For
    End If
Next

If pythonExe = "" Then pythonExe = "pythonw.exe"

WshShell.Run pythonExe & " """ & scriptDir & "\main.py""", 0, False
