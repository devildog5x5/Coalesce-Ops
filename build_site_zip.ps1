# Build SpartanPhalanx-<version>.zip for Hostinger public_html.
# Entry names use forward slashes so Linux unzip (Hostinger) does not
# treat paths such as assets\favicon.svg as literal filenames.
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$Root = $PSScriptRoot
$VersionFile = Join-Path $Root "VERSION"
if (-not (Test-Path $VersionFile)) {
    throw "VERSION file is missing"
}
$Version = (Get-Content -Path $VersionFile -Raw).Trim()
if ($Version -notmatch '^\d+\.\d+\.\d+$') {
    throw "VERSION must be x.y.z (got '$Version')"
}

$Out = Join-Path $Root "installers"
$Stage = Join-Path $Root "build\sitedrop"
$ZipName = "SpartanPhalanx-$Version.zip"
$Zip = Join-Path $Out $ZipName

New-Item -ItemType Directory -Force -Path $Out | Out-Null
if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

Get-ChildItem -Path $Root -Filter "*.html" | Copy-Item -Destination $Stage
Copy-Item -Path (Join-Path $Root "LICENSE") -Destination $Stage
Copy-Item -Path (Join-Path $Root ".htaccess") -Destination $Stage
Copy-Item -Path (Join-Path $Root "robots.txt") -Destination $Stage
Copy-Item -Path (Join-Path $Root "sitemap.xml") -Destination $Stage
Copy-Item -Path (Join-Path $Root "assets") -Destination (Join-Path $Stage "assets") -Recurse

Get-ChildItem -Path $Out -Filter "SpartanPhalanx-*.zip" -ErrorAction SilentlyContinue | Remove-Item -Force

$archive = [System.IO.Compression.ZipFile]::Open($Zip, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    $stageRoot = $Stage.TrimEnd('\', '/')
    Get-ChildItem -Path $Stage -Recurse -File -Force | ForEach-Object {
        $relative = $_.FullName.Substring($stageRoot.Length).TrimStart('\', '/')
        $entryName = ($relative -replace '\\', '/')
        if ([string]::IsNullOrWhiteSpace($entryName)) { return }
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $archive,
            $_.FullName,
            $entryName,
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $archive.Dispose()
}

$packed = [System.IO.Compression.ZipFile]::OpenRead($Zip)
try {
    $names = @($packed.Entries | ForEach-Object { $_.FullName })
    foreach ($name in $names) {
        if ($name -match '\\') { throw "Zip entry contains a backslash: $name" }
        if ($name.StartsWith('/') -or $name.StartsWith('\')) { throw "Zip entry is absolute: $name" }
    }
    if ($names -notcontains 'index.html') { throw "index.html is not at the zip root" }
    if ($names -notcontains 'assets/favicon.svg') { throw "assets/favicon.svg is missing or not a forward-slash path" }
}
finally {
    $packed.Dispose()
}

Write-Host "Built v$Version"
Write-Host "  $Zip"
Write-Host ("Size {0:N1} KB" -f ((Get-Item $Zip).Length / 1KB))
Write-Host "Hostinger: unzip into public_html (files at zip root, forward-slash paths, not a nested folder)"
