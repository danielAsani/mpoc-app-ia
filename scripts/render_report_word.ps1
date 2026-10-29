$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$docPath = Join-Path $taskRoot 'rapport\Rapport_Projet_Stage_UQAC_complete.docx'
$qaPath = Join-Path $taskRoot 'rapport\qa'
New-Item -ItemType Directory -Path $qaPath -Force | Out-Null
$pdfPath = Join-Path $qaPath 'rapport.pdf'
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $document = $word.Documents.Open($docPath, $false, $false)
    foreach ($toc in $document.TablesOfContents) { $toc.Update() }
    $document.Repaginate()
    $document.Save()
    $document.ExportAsFixedFormat($pdfPath, 17)
    Write-Output "PDF exporte : $pdfPath"
    Write-Output "Pages : $($document.ComputeStatistics(2))"
} finally {
    if ($null -ne $document) { $document.Close(0) }
    if ($null -ne $word) { $word.Quit() }
}
