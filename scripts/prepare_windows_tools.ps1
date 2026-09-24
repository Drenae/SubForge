$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $projectRoot 'src\assets\tools\windows'
if ((Test-Path (Join-Path $tools 'ffmpeg.exe')) -and
    (Test-Path (Join-Path $tools 'ffprobe.exe'))) {
    Write-Host "FFmpeg et FFprobe déjà préparés dans $tools"
    return
}
$archiveUrl = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-8.1.2-essentials_build.zip'
$working = Join-Path ([System.IO.Path]::GetTempPath()) ('subforge-ffmpeg-' + [guid]::NewGuid())

New-Item -ItemType Directory -Path $working -Force | Out-Null
try {
    $archive = Join-Path $working 'ffmpeg.zip'
    $checksum = Join-Path $working 'ffmpeg.zip.sha256'
    Invoke-WebRequest -Uri $archiveUrl -OutFile $archive
    Invoke-WebRequest -Uri ($archiveUrl + '.sha256') -OutFile $checksum
    $match = [regex]::Match((Get-Content $checksum -Raw), '[a-fA-F0-9]{64}')
    if (-not $match.Success) { throw 'Impossible de lire la somme SHA-256 de FFmpeg.' }
    $actual = (Get-FileHash $archive -Algorithm SHA256).Hash
    if ($actual -ne $match.Value) { throw 'La somme SHA-256 de FFmpeg ne correspond pas.' }
    $unpacked = Join-Path $working 'unpacked'
    Expand-Archive -Path $archive -DestinationPath $unpacked
    $ffmpeg = Get-ChildItem $unpacked -Recurse -Filter 'ffmpeg.exe' -File | Select-Object -First 1
    $ffprobe = Get-ChildItem $unpacked -Recurse -Filter 'ffprobe.exe' -File | Select-Object -First 1
    if (-not $ffmpeg -or -not $ffprobe) { throw 'Archive FFmpeg incomplète.' }
    New-Item -ItemType Directory -Path $tools -Force | Out-Null
    Copy-Item $ffmpeg.FullName (Join-Path $tools 'ffmpeg.exe') -Force
    Copy-Item $ffprobe.FullName (Join-Path $tools 'ffprobe.exe') -Force
    Write-Host "FFmpeg et FFprobe préparés dans $tools"
} finally {
    Remove-Item $working -Recurse -Force -ErrorAction SilentlyContinue
}
