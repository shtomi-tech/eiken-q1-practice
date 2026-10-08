param(
    [string]$Inventory = 'out/mock-audio-ipa-20261008/inventory.json',
    [string]$Ffmpeg = 'C:\Users\shtom\ffmpeg\bin\ffmpeg.exe'
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskJobs = Get-Content -LiteralPath (Join-Path $taskRoot $Inventory) -Raw -Encoding UTF8 | ConvertFrom-Json
$taskOutput = Join-Path $taskRoot 'out/mock-audio-ipa-20261008'
New-Item -ItemType Directory -Path $taskOutput -Force | Out-Null
Add-Type -AssemblyName System.Speech
$taskSynth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$taskSynth.SelectVoice('Microsoft Zira Desktop')
$taskSynth.Rate = -1
$taskSynth.Volume = 100
$taskResults = @()
try {
    foreach ($taskJob in $taskJobs.audio) {
        $taskTarget = [IO.Path]::GetFullPath((Join-Path $taskRoot $taskJob.target))
        if (-not $taskTarget.StartsWith(([IO.Path]::GetFullPath($taskRoot) + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'Audio path outside repository' }
        if ((Test-Path -LiteralPath $taskTarget) -and (Get-Item -LiteralPath $taskTarget).Length -gt 0) { continue }
        $taskSlug = [IO.Path]::GetFileNameWithoutExtension($taskTarget)
        $taskWave = Join-Path $taskOutput ($taskJob.dataset + '-' + $taskSlug + '.wav')
        $taskEncoded = Join-Path $taskOutput ($taskJob.dataset + '-' + $taskSlug + '.mp3')
        $taskSynth.SetOutputToWaveFile($taskWave)
        $taskSynth.Speak([string]$taskJob.surface)
        $taskSynth.SetOutputToNull()
        & $Ffmpeg -y -hide_banner -loglevel error -i $taskWave -codec:a libmp3lame -b:a 64k $taskEncoded
        if ($LASTEXITCODE -ne 0) { throw "MP3 encoding failed: $($taskJob.surface)" }
        New-Item -ItemType Directory -Path (Split-Path -Parent $taskTarget) -Force | Out-Null
        Copy-Item -LiteralPath $taskEncoded -Destination $taskTarget
        $taskResults += @{surface=$taskJob.surface; target=$taskJob.target; voice='Microsoft Zira Desktop'; locale='en-US'; rate=-1; codec='libmp3lame 64kbps'}
    }
} finally { $taskSynth.Dispose() }
$taskResults | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $taskOutput 'generated.json') -Encoding UTF8
Write-Output "Generated $($taskResults.Count) English MP3 files."
