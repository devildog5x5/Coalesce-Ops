# Build CoalesceOps-<version>.zip for Hostinger public_html.
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
$ZipName = "CoalesceOps-$Version.zip"
$Zip = Join-Path $Out $ZipName

function Invoke-SitePython {
    param([string[]]$PyArgs)
    $runner = $null
    $prefix = @()
    foreach ($candidate in @("python3", "python")) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            $runner = $candidate
            break
        }
    }
    if (-not $runner -and (Get-Command py -ErrorAction SilentlyContinue)) {
        $runner = "py"
        $prefix = @("-3")
    }
    if (-not $runner) {
        throw "Python 3 is required to build the zip (menu check and search-engine config)."
    }
    & $runner @prefix @PyArgs
    if ($LASTEXITCODE -ne 0) { throw "Python failed ($runner): $($PyArgs -join ' ')" }
}

Invoke-SitePython @((Join-Path $Root "check_site.py"))

New-Item -ItemType Directory -Force -Path $Out | Out-Null
if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null

Get-ChildItem -Path $Root -Filter "*.html" | Copy-Item -Destination $Stage
Copy-Item -Path (Join-Path $Root "LICENSE") -Destination $Stage
Copy-Item -Path (Join-Path $Root ".htaccess") -Destination $Stage
Copy-Item -Path (Join-Path $Root "robots.txt") -Destination $Stage
Copy-Item -Path (Join-Path $Root "sitemap.xml") -Destination $Stage
Copy-Item -Path (Join-Path $Root "site.webmanifest") -Destination $Stage
$siteConfig = Get-Content -Path (Join-Path $Root "site.config.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$indexNowKey = "$($siteConfig.indexNowKey)".Trim()
if (-not $indexNowKey) { throw "indexNowKey is missing in site.config.json" }
$indexNowFile = Join-Path $Root ($indexNowKey + ".txt")
if (-not (Test-Path $indexNowFile)) { throw "IndexNow key file is missing: $indexNowFile" }
Copy-Item -Path $indexNowFile -Destination (Join-Path $Stage ($indexNowKey + ".txt"))
$bingFile = Join-Path $Root "BingSiteAuth.xml"
if (Test-Path $bingFile) { Copy-Item -Path $bingFile -Destination $Stage }
Copy-Item -Path (Join-Path $Root "assets") -Destination (Join-Path $Stage "assets") -Recurse

Invoke-SitePython @((Join-Path $Root "apply_site_config.py"), "--stage", $Stage)

Get-ChildItem -Path $Out -Filter "CoalesceOps-*.zip" -ErrorAction SilentlyContinue | Remove-Item -Force

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
    foreach ($required in @(
        'assets/favicon.svg',
        'assets/favicon-32.png',
        'assets/apple-touch-icon.png',
        'assets/icon-192.png',
        'assets/icon-512.png',
        'assets/og.png',
        'robots.txt',
        'sitemap.xml',
        'site.webmanifest',
        'secops-consulting.html',
        'infrastructure-assessment.html',
        'incident-response-readiness.html',
        'cloud-cost-reliability.html',
        'fractional-devops-sre.html',
        ($indexNowKey + '.txt')
    )) {
        if ($names -notcontains $required) { throw "Zip is missing $required" }
    }
}
finally {
    $packed.Dispose()
}

Write-Host "Built v$Version"
Write-Host "  $Zip"
Write-Host ("Size {0:N1} KB" -f ((Get-Item $Zip).Length / 1KB))
Write-Host "Hostinger: unzip into public_html (files at zip root, forward-slash paths, not a nested folder)"
