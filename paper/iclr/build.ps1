$ErrorActionPreference = "Stop"

$PaperDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DownloadsPdf = "C:\Users\wangz\Downloads\tokenized_world_model_iclr2027_submission.pdf"

Push-Location $PaperDir
try {
    foreach ($aux in @("main.pdf", "main.aux", "main.out", "main.log", "main.bbl", "main.blg", "main.toc", "main.fls", "main.fdb_latexmk")) {
        if (Test-Path $aux) {
            Remove-Item -Force $aux
        }
    }

    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    bibtex main
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    pdflatex -interaction=nonstopmode -halt-on-error main.tex

    if (-not (Test-Path "main.pdf")) {
        throw "main.pdf was not created"
    }

    $pdf = Get-Item "main.pdf"
    if ($pdf.Length -le 0) {
        throw "main.pdf is empty"
    }

    Copy-Item -Force "main.pdf" $DownloadsPdf
    Write-Host "Built $($pdf.FullName)"
    Write-Host "Copied submission PDF to $DownloadsPdf"
}
finally {
    Pop-Location
}

exit 0
