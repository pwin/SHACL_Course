<#
.SYNOPSIS
    Open the Turtle Editor Viewer with a lesson's data and shapes already loaded.

.DESCRIPTION
    The editor is used online, at https://semantechs.co.uk/turtle-editor-viewer/.
    It accepts ?dot=<url> for the data, &shapes=<url> for a shapes graph opened
    in a second tab and selected for validation, and &inference=<mode> to
    preset the Inference dropdown. This script assembles the link from the
    course's own raw URLs on GitHub, which send the CORS header the editor
    needs, and opens it.

    Give it a lesson id and it reads the lesson's DATA and INFERENCE lines
    from the .ttl header. Give it -Data and -Shapes and it builds the link
    for any pair of files.

.PARAMETER Lesson
    A lesson id such as s20, or the start of one file name.

.PARAMETER Data
    A file from data/, when not taking it from a lesson.

.PARAMETER Shapes
    A path under shapes/, when not taking it from a lesson.

.PARAMETER Inference
    none, rdfs, rules or rules-iterated. Defaults to the lesson's, or none.

.PARAMETER List
    Print every lesson with its link without opening anything.

.EXAMPLE
    ./scripts/open-editor.ps1 s20
    ./scripts/open-editor.ps1 s51                         # sets inference=rules-iterated for you
    ./scripts/open-editor.ps1 -Data bookshop-trail-faulty.ttl -Shapes 11-putting-it-together/s64-the-whole-trail-in-one-shapes-graph.ttl
    ./scripts/open-editor.ps1 -List
#>
param(
    [string]$Lesson,
    [string]$Data,
    [string]$Shapes,
    [ValidateSet("", "none", "rdfs", "rules", "rules-iterated")]
    [string]$Inference = "",
    [string]$Editor = "https://semantechs.co.uk/turtle-editor-viewer/",
    [string]$Repo = "https://raw.githubusercontent.com/pwin/SHACL_Course",
    [string]$Branch = "main",
    [switch]$List
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$shapesDir = Join-Path $root "shapes"

function Raw([string]$relative) { return "$Repo/$Branch/$relative" }

function Link([string]$dataName, [string]$shapesRelative, [string]$mode) {
    $url = $Editor + "?dot=" + [uri]::EscapeDataString((Raw "data/$dataName"))
    if ($shapesRelative) { $url += "&shapes=" + [uri]::EscapeDataString((Raw "shapes/$shapesRelative")) }
    if ($mode -and $mode -ne "none") { $url += "&inference=$mode" }
    return $url
}

function LessonInfo([System.IO.FileInfo]$file) {
    $text = Get-Content -Raw -LiteralPath $file.FullName
    $data = if ($text -match '(?m)^#  DATA\s+(\S+)') { $Matches[1] } else { "bookshop-trail-1.1.ttl" }
    $mode = if ($text -match '(?m)^#  INFERENCE\s+(\S+)') { $Matches[1] } else { "none" }
    $rel = $file.FullName.Substring($shapesDir.Length + 1).Replace("\", "/")
    return @{ Id = $file.Name.Substring(0, 3); Title = ($file.BaseName.Substring(4) -replace "-", " "); Data = $data; Mode = $mode; Rel = $rel }
}

$lessons = Get-ChildItem -LiteralPath $shapesDir -Recurse -Filter "s*.ttl" | Sort-Object Name | ForEach-Object { LessonInfo $_ }

if ($List) {
    foreach ($l in $lessons) {
        $mode = if ($l.Mode -ne "none") { "  [$($l.Mode)]" } else { "" }
        Write-Host ("{0}  {1}{2}" -f $l.Id, $l.Title, $mode)
        Write-Host ("      " + (Link $l.Data $l.Rel $l.Mode))
    }
    return
}

if ($Lesson) {
    $match = $lessons | Where-Object { $_.Id -eq $Lesson.ToLower() -or $_.Rel -like "*/$Lesson*" } | Select-Object -First 1
    if (-not $match) { throw "No lesson matches '$Lesson'. Try -List." }
    $mode = if ($Inference) { $Inference } else { $match.Mode }
    $url = Link $match.Data $match.Rel $mode
    Write-Host ("{0}  {1}" -f $match.Id, $match.Title)
} elseif ($Data) {
    if ($Data -notlike "*.ttl") { $Data += ".ttl" }
    $url = Link $Data $Shapes $Inference
} else {
    $first = $lessons | Select-Object -First 1
    $url = Link $first.Data $first.Rel $first.Mode
    Write-Host ("{0}  {1}   (the first lesson; try -List)" -f $first.Id, $first.Title)
}

Write-Host $url
Start-Process $url
