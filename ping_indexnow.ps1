# Submit every URL in sitemap.xml to IndexNow.
# Run this after the zip is uploaded and https://coalesceops.com/<key>.txt
# returns the key. -DryRun prints the request and does not send it.
param(
    [switch]$DryRun
)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$ConfigPath = Join-Path $Root "site.config.json"
$SitemapPath = Join-Path $Root "sitemap.xml"
if (-not (Test-Path $ConfigPath)) { throw "site.config.json is missing" }
if (-not (Test-Path $SitemapPath)) { throw "sitemap.xml is missing" }

$config = Get-Content -Path $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
$key = "$($config.indexNowKey)".Trim()
$siteUrl = "$($config.siteUrl)".Trim().TrimEnd("/")
if (-not $key -or $key -eq "PLACEHOLDER") { throw "indexNowKey is missing in site.config.json" }

$keyFile = Join-Path $Root ($key + ".txt")
if (-not (Test-Path $keyFile)) { throw "IndexNow key file is missing: $keyFile" }
$keyBody = (Get-Content -Path $keyFile -Raw -Encoding UTF8).Trim()
if ($keyBody -ne $key) { throw "IndexNow key file does not match site.config.json" }

$sitemap = Get-Content -Path $SitemapPath -Raw -Encoding UTF8
$urls = @([regex]::Matches($sitemap, "<loc>\s*([^<]+?)\s*</loc>") | ForEach-Object { $_.Groups[1].Value })
if ($urls.Count -eq 0) { throw "sitemap.xml has no loc entries" }

$hostName = ([Uri]$siteUrl).Host
$payload = [ordered]@{
    host = $hostName
    key = $key
    keyLocation = "$siteUrl/$key.txt"
    urlList = $urls
}
$body = $payload | ConvertTo-Json -Depth 5
Write-Host "IndexNow host: $hostName"
Write-Host "Key location: $siteUrl/$key.txt"
Write-Host "URLs: $($urls.Count)"

if ($DryRun) {
    Write-Host $body
    Write-Host "Dry run only. No request was sent."
    exit 0
}

$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$request = [System.Net.HttpWebRequest]::Create("https://api.indexnow.org/indexnow")
$request.Method = "POST"
$request.ContentType = "application/json; charset=utf-8"
$request.ContentLength = $bytes.Length
$stream = $request.GetRequestStream()
$stream.Write($bytes, 0, $bytes.Length)
$stream.Close()
try {
    $response = $request.GetResponse()
    Write-Host ("IndexNow status: " + [int]$response.StatusCode)
    $response.Close()
}
catch [System.Net.WebException] {
    $err = $_.Exception.Response
    if ($err) {
        Write-Host ("IndexNow status: " + [int]$err.StatusCode)
        $reader = New-Object System.IO.StreamReader($err.GetResponseStream())
        Write-Host $reader.ReadToEnd()
    }
    throw
}
