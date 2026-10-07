' Builds the Lokal-STT shortcut that ships inside the zip (the install script only copies it,
' because PowerShell Constrained Language Mode blocks creating shortcuts).
' usage: cscript //nologo make-shortcut.vbs <output.lnk>
Const APP = "C:\Program Files\Lokal-STT\Lokal-STT-Portable"
Set sh = CreateObject("WScript.Shell")
Set lnk = sh.CreateShortcut(WScript.Arguments(0))
lnk.TargetPath       = APP & "\Lokal-STT-Portable.exe"
lnk.WorkingDirectory = APP
lnk.IconLocation     = APP & "\Lokal-STT.ico,0"
lnk.Description      = "Lokal-STT - Lokale deutsche Spracherkennung (Speech-to-Text)"
lnk.Save
Set chk = sh.CreateShortcut(WScript.Arguments(0))
WScript.Echo "target=" & chk.TargetPath & " | dir=" & chk.WorkingDirectory & " | icon=" & chk.IconLocation
