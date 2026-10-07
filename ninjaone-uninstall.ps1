<#
  NinjaOne - remove Lokal-STT-Portable from a device. Run As: SYSTEM.
  Works under PowerShell Constrained Language Mode (cmdlets only).
  Leaves each user's data (%LOCALAPPDATA%\Lokal-STT-Portable) untouched.
#>
param(
    [string]$InstallDir = 'C:\Program Files\Lokal-STT',
    [string]$StartMenuDir = (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs'),
    [string]$DesktopDir = (Join-Path $env:PUBLIC 'Desktop')
)

Get-Process -Name 'Lokal-STT-Portable' -ErrorAction SilentlyContinue |
    Where-Object { -not $_.Path -or $_.Path -like "$InstallDir\*" } |
    Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Remove-Item -LiteralPath $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $StartMenuDir 'Lokal-STT.lnk') -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath (Join-Path $DesktopDir 'Lokal-STT.lnk') -Force -ErrorAction SilentlyContinue

if (Test-Path -LiteralPath $InstallDir) {
    Write-Output "FAILED: $InstallDir could not be removed completely (file in use?)."
    exit 1
}
Write-Output "Removed Lokal-STT (per-user data in %LOCALAPPDATA% left in place)."
exit 0
