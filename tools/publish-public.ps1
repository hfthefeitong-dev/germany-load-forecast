# Derive the public repository from this private one and, with -Push, publish it.
#
# The public history is this repository's history with the personal notes left
# out: only the paths in $keep survive, commits that touched nothing else are
# dropped, and commit messages and dates are unchanged. The rewrite is
# deterministic, so on a longer private history it only appends commits and the
# public branch always fast-forwards. Never force-push the result.
#
# Preview, without pushing (writes only to the mirror repository):
#   powershell -ExecutionPolicy Bypass -File E:\Coding\energy-ml-lab\tools\publish-public.ps1
# Publish; pushes only if the mirror has a remote called "public":
#   powershell -ExecutionPolicy Bypass -File E:\Coding\energy-ml-lab\tools\publish-public.ps1 -Push

param(
    [string]$Source = "E:\Coding\energy-ml-lab",
    [string]$Branch = "main",
    [string]$Mirror = "E:\Coding\energy-ml-lab\project\data\public-mirror.git",
    [switch]$Push
)

# git writes normal progress messages to stderr; ForEach-Object { "$_" } prints them as plain text.

# Everything else, including notes added later, stays private.
$keep = "README.md LICENSE .gitattributes .gitignore tools/run-live.ps1 tools/publish-public.ps1 project"
$drop = "project/docs project/.gitkeep"
$allowed = '^(README\.md|LICENSE|\.gitattributes|\.gitignore|tools/run-live\.ps1|tools/publish-public\.ps1|project/.+)$'
$denied = '^project/(docs/|\.gitkeep$)'

function Fail($text) { "publish-public: $text"; exit 1 }

if (-not (Test-Path $Mirror)) {
    git init -q --bare $Mirror 2>&1 | ForEach-Object { "$_" }
    if ($LASTEXITCODE -ne 0) { Fail "could not create $Mirror" }
}

git -C $Mirror fetch -q --no-tags $Source "+refs/heads/${Branch}:refs/heads/source" 2>&1 | ForEach-Object { "$_" }
if ($LASTEXITCODE -ne 0) { Fail "fetch from $Source failed" }
git -C $Mirror update-ref refs/heads/public refs/heads/source
if ($LASTEXITCODE -ne 0) { Fail "update-ref failed" }

$env:FILTER_BRANCH_SQUELCH_WARNING = "1"
$filter = "git rm -r -q --cached --ignore-unmatch -- . && git reset -q `$GIT_COMMIT -- $keep && git rm -r -q --cached --ignore-unmatch -- $drop"
git -C $Mirror filter-branch -f --prune-empty --index-filter $filter -- public 2>&1 | ForEach-Object { "$_" } | Where-Object { $_ -notmatch "^Rewrite " }
if ($LASTEXITCODE -ne 0) { Fail "filter-branch failed" }
# Only the filtered branch may stay; the unfiltered refs would carry the notes along with any push.
git -C $Mirror update-ref -d refs/original/refs/heads/public
git -C $Mirror update-ref -d refs/heads/source

# Check the result before anything leaves this computer.
$paths = git -C $Mirror log --format= --name-only public | Where-Object { $_ } | Sort-Object -Unique
$bad = $paths | Where-Object { $_ -notmatch $allowed -or $_ -match $denied }
if ($bad) { Fail ("paths that must stay private: " + ($bad -join ", ")) }
git -C $Mirror cat-file -e public:README.md
if ($LASTEXITCODE -ne 0) { Fail "no README.md at the root of the public branch" }

$head = git -C $Mirror rev-parse --short public
$count = git -C $Mirror rev-list --count public
"publish-public: public branch at $head, $count commits, $($paths.Count) paths, none private"

if (-not $Push) { exit 0 }
git -C $Mirror remote get-url public 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { "publish-public: no remote 'public' in $Mirror, nothing pushed"; exit 0 }
$placeholder = git -C $Mirror show public:README.md | Select-String -Quiet -SimpleMatch "PUBLICATION_DATE"
if ($placeholder) { Fail "README.md still says PUBLICATION_DATE: fill in the date before the first push" }
git -C $Mirror push public public:main 2>&1 | ForEach-Object { "$_" }
if ($LASTEXITCODE -ne 0) { Fail "push failed (a rejected push means the histories diverged: never force it)" }
"publish-public: pushed $head"
