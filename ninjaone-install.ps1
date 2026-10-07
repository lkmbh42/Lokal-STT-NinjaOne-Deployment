<#
  NinjaOne - install or update Lokal-STT-Portable 1.1 for all users on a device.
  Run As: SYSTEM.  Script timeout in NinjaOne: 30 minutes.

  Works under PowerShell Constrained Language Mode (__PSLockdownPolicy=4):
  no Add-Type, no .NET method calls, no COM objects. The zip is unpacked with the
  built-in tar.exe (fallback: Expand-Archive) and the Start Menu / Desktop shortcut
  ships prebuilt inside the zip (_deploy\Lokal-STT.lnk), so it is only copied.

  Integrity: the zip and the exe are checked against known SHA-256 values; on any
  mismatch nothing is installed. Per-user data in %LOCALAPPDATA% is never touched.
#>
param(
    # ============================ CONFIG ============================
    # Where the device gets the zip: UNC share (readable by "Domain Computers"),
    # internal HTTPS URL, or just the file name of a NinjaOne script attachment.
    [string]$Source = '\\srv1\configurator$\Packages\Lokal-STT-Portable-1.1.zip',
    [string]$InstallDir = 'C:\Program Files\Lokal-STT',
    # ===============================================================
    # Only overridden for tests - keep the defaults in NinjaOne.
    [string]$StartMenuDir = (Join-Path $env:ProgramData 'Microsoft\Windows\Start Menu\Programs'),
    [string]$DesktopDir = (Join-Path $env:PUBLIC 'Desktop')
)

$ErrorActionPreference = 'Stop'

$ExpectedZipSha256 = '61BB025D5918976E28E9DBA05592929E0D8417A6DBBC7A37A461C8E1BDF6D661'
$ExpectedExeSha256 = '50148EAD01B7301A8BCF91D49ED549FBC5DA2AEC16DB4118E705BF22028BBF6D'
$ExeName = 'Lokal-STT-Portable.exe'
$ShortcutTargetDir = 'C:\Program Files\Lokal-STT\Lokal-STT-Portable'  # baked into _deploy\Lokal-STT.lnk
$staging = Join-Path $env:TEMP 'lokal-stt-deploy.zip'

try {
    # --- 1. fetch ---------------------------------------------------------
    if ($Source -notmatch '^(https?://|\\\\|[A-Za-z]:\\)') {
        $candidate = Join-Path $PSScriptRoot $Source   # NinjaOne script attachment
        if (Test-Path -LiteralPath $candidate) { $Source = $candidate }
    }
    $drive = Get-PSDrive -Name ($env:SystemDrive -replace ':$', '')
    if ($drive.Free -lt 5GB) { throw "Not enough disk space on $($env:SystemDrive): need 5 GB free, have $([int]($drive.Free / 1GB)) GB." }

    Write-Output "Fetching $Source"
    if ($Source -match '^https?://') {
        Invoke-WebRequest -Uri $Source -OutFile $staging -UseBasicParsing
    } else {
        Copy-Item -LiteralPath $Source -Destination $staging -Force
    }

    # --- 2. verify the zip before touching the current installation ------
    $zipHash = (Get-FileHash -LiteralPath $staging -Algorithm SHA256).Hash
    if ($zipHash -ne $ExpectedZipSha256) {
        throw "Zip integrity check FAILED (expected $ExpectedZipSha256, got $zipHash). Wrong or damaged file - nothing was changed."
    }
    Write-Output "Zip OK:         $zipHash"

    # --- 3. stop only the copy that is being replaced ---------------------
    Get-Process -Name ($ExeName -replace '\.exe$', '') -ErrorAction SilentlyContinue |
        Where-Object { -not $_.Path -or $_.Path -like "$InstallDir\*" } |
        Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2

    # --- 4. unpack into a fresh folder ------------------------------------
    if (Test-Path -LiteralPath $InstallDir) { Remove-Item -LiteralPath $InstallDir -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    $tar = Get-Command tar.exe -ErrorAction SilentlyContinue
    $unpacked = $false
    if ($tar) {
        & $tar.Source -xf $staging -C $InstallDir
        $unpacked = ($LASTEXITCODE -eq 0)
        if (-not $unpacked) { Write-Output "tar.exe failed (exit $LASTEXITCODE) - falling back to Expand-Archive" }
    }
    if (-not $unpacked) {
        Remove-Item -LiteralPath $InstallDir -Recurse -Force
        Expand-Archive -LiteralPath $staging -DestinationPath $InstallDir -Force
    }

    # --- 5. verify what was installed ------------------------------------
    $exe = Get-ChildItem -LiteralPath $InstallDir -Recurse -Filter $ExeName | Select-Object -First 1 -ExpandProperty FullName
    if (-not $exe) { throw "$ExeName not found after unpacking." }
    $appPath = Split-Path $exe
    $exeHash = (Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash
    if ($exeHash -ne $ExpectedExeSha256) {
        Remove-Item -LiteralPath $InstallDir -Recurse -Force -ErrorAction SilentlyContinue
        throw "EXE integrity check FAILED (expected $ExpectedExeSha256, got $exeHash) - installation removed."
    }
    if (-not (Test-Path -LiteralPath (Join-Path $appPath '_internal\frontend\assets\ds2-support.js'))) {
        throw "Unpacked build has no DS2 support files - wrong zip?"
    }
    Write-Output "EXE OK:         $exeHash"

    # Remove "downloaded from the internet" marks on the vetted files.
    Get-ChildItem -LiteralPath $InstallDir -Recurse -File | Unblock-File

    # --- 6. shortcuts (prebuilt, copied) ----------------------------------
    $lnk = Join-Path $appPath '_deploy\Lokal-STT.lnk'
    if ($appPath -ne $ShortcutTargetDir) {
        Write-Warning "Installed to $appPath, but the shipped shortcut points to $ShortcutTargetDir."
    }
    foreach ($dir in @($StartMenuDir, $DesktopDir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Copy-Item -LiteralPath $lnk -Destination (Join-Path $dir 'Lokal-STT.lnk') -Force
        Write-Output "Shortcut:       $(Join-Path $dir 'Lokal-STT.lnk')"
    }

    Write-Output "Installed:      $exe"
    Get-Content -LiteralPath (Join-Path $appPath 'VERSION.txt') -TotalCount 2 | ForEach-Object { Write-Output "Version:        $_" }
    exit 0
}
catch {
    Write-Output "FAILED: $($_.Exception.Message)"
    exit 1
}
finally {
    Remove-Item -LiteralPath $staging -Force -ErrorAction SilentlyContinue
}
