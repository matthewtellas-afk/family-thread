# Publishes The Family Thread to GitHub Pages under matthewtellas-afk/family-thread (public repo, required for free Pages).
# Run from PowerShell:  powershell -ExecutionPolicy Bypass -File C:\Users\matth\family-thread-site\deploy-github.ps1
# Re-running after a rebuild just commits and pushes the changes.
$ErrorActionPreference = 'Stop'
$gh = "C:\Program Files\GitHub CLI\gh.exe"
Set-Location C:\Users\matth\family-thread-site
git branch -M main
$hasRemote = (git remote) -contains 'origin'
if (-not $hasRemote) {
  & $gh repo create family-thread --public --description "The Family Thread: a family history in pictures"
  git remote add origin https://github.com/matthewtellas-afk/family-thread.git
}
git add -A
git -c user.name="Matt Tellas" -c user.email="matthewtellas@gmail.com" commit -m "Update The Family Thread" --allow-empty | Out-Null
git push -u origin main
# Turn on Pages from the main branch root (idempotent; the second call updates an existing site)
try { & $gh api -X POST repos/matthewtellas-afk/family-thread/pages -f "source[branch]=main" -f "source[path]=/" | Out-Null }
catch { & $gh api -X PUT repos/matthewtellas-afk/family-thread/pages -f "source[branch]=main" -f "source[path]=/" | Out-Null }
Write-Host ""
Write-Host "Pushed. The site builds in about a minute at:"
Write-Host "  https://matthewtellas-afk.github.io/family-thread/"
Write-Host "Check status: & '$gh' api repos/matthewtellas-afk/family-thread/pages --jq .status"
