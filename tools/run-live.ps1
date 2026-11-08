# Daily live forecast: issue tomorrow's forecast, update the interim report,
# commit and push, then update the public repository (tools/publish-public.ps1).
# Scheduled at 11:16 local time, with a backup run at 11:41.
#
# Manual run:
#   powershell -ExecutionPolicy Bypass -File E:\Coding\energy-ml-lab\tools\run-live.ps1
# Test without storing a real forecast or pushing:
#   powershell -ExecutionPolicy Bypass -File E:\Coding\energy-ml-lab\tools\run-live.ps1 -DryRun

param([switch]$DryRun)

# git and wsl write normal progress messages to stderr. PowerShell 5.1 turns those
# into red NativeCommandError records; ForEach-Object { "$_" } logs them as plain text.

$repo = "E:\Coding\energy-ml-lab"
$logDir = Join-Path $repo "project\data\live_logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$log = Join-Path $logDir ("{0:yyyy-MM-dd}.log" -f (Get-Date))
$target = "{0:yyyy-MM-dd}" -f (Get-Date).AddDays(1)

function Log($text) { "[{0:HH:mm:ss}] {1}" -f (Get-Date), $text | Out-File -Append -Encoding utf8 $log }

Log "start, target day $target, dry run: $DryRun"
$flag = if ($DryRun) { " --dry-run" } else { "" }
$bash = "source ~/venvs/cs336/bin/activate && export HF_HOME=/mnt/e/Coding/energy-ml-lab/data/hf && cd /mnt/e/Coding/energy-ml-lab/project && python -m loadfc live$flag && python -m loadfc live_eval"
wsl.exe -d Ubuntu-24.04 -- bash -lc $bash 2>&1 | ForEach-Object { "$_" } | Out-File -Append -Encoding utf8 $log
Log "python finished with exit code $LASTEXITCODE"
if ($DryRun) { Log "dry run: no commit, no push"; exit 0 }

git -C $repo add project/live project/reports/LIVE.md 2>&1 | ForEach-Object { "$_" } | Out-File -Append -Encoding utf8 $log
git -C $repo commit -m "live: forecast for $target" 2>&1 | ForEach-Object { "$_" } | Out-File -Append -Encoding utf8 $log
git -C $repo push 2>&1 | ForEach-Object { "$_" } | Out-File -Append -Encoding utf8 $log
Log "git push finished with exit code $LASTEXITCODE"
if ($LASTEXITCODE -ne 0) { Log "private push failed: public repository not updated"; exit 1 }

# The public repository is derived from the commits just pushed, so it never holds a forecast the private push log lacks.
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repo "tools\publish-public.ps1") -Push 2>&1 | ForEach-Object { "$_" } | Out-File -Append -Encoding utf8 $log
Log "publish-public finished with exit code $LASTEXITCODE"
