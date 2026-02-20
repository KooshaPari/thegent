# thegent bootstrap — full system installer (Windows)
#
# Usage:
#   irm https://raw.githubusercontent.com/kooshapari/thegent/main/scripts/install.ps1 | iex
#   irm ... | iex -Args install
#   irm ... | iex -Args install,-NoSetup
#
# Phases: install thegent → install -t all → install-shims → setup → doctor
#
# Parameters:
#   install     Full bootstrap (default)
#   -NoSetup    Install CLI only
#   -Full       Use thegent setup --full
#   -Help       Show this help
#
# Environment:
#   $env:THGENT_BOOTSTRAP_SYSTEM_SHIMS = "1"  Install git wrapper to system path
#   $env:THGENT_BOOTSTRAP_QUIET       = "1"  Suppress non-critical warnings

# Support: irm ... | iex  and  .\install.ps1 -NoSetup
# Env vars (for piped use): THGENT_BOOTSTRAP_NO_SETUP=1, THGENT_BOOTSTRAP_FULL=1
param(
    [switch]$NoSetup,
    [switch]$Full,
    [switch]$Help
)

if ($env:THGENT_BOOTSTRAP_NO_SETUP -eq "1") { $NoSetup = $true }
if ($env:THGENT_BOOTSTRAP_FULL -eq "1") { $Full = $true }

$ErrorActionPreference = "Stop"
$GITHUB_RAW = "https://raw.githubusercontent.com/kooshapari/thegent/main"

function Write-Step { param($Msg) Write-Host ""; Write-Host "==> $Msg" -ForegroundColor Cyan }
function Write-Warn  { param($Msg) if (-not $env:THGENT_BOOTSTRAP_QUIET) { Write-Host "Warning: $Msg" -ForegroundColor Yellow } }
function Write-Die   { param($Msg) Write-Host "Error: $Msg" -ForegroundColor Red; exit 1 }

function Show-Usage {
    @"
thegent install — full system installer (Windows)

Phases: install thegent → install -t all → install-shims → setup → doctor

Usage:
  irm $GITHUB_RAW/scripts/install.ps1 | iex

Parameters (when run directly):
  -NoSetup    Install CLI only
  -Full       Use thegent setup --full
  -Help       Show this help

Environment (for piped irm | iex):
  THGENT_BOOTSTRAP_NO_SETUP=1     Install CLI only
  THGENT_BOOTSTRAP_FULL=1         Use thegent setup --full
  THGENT_BOOTSTRAP_SYSTEM_SHIMS=1 Install git wrapper to system path
  THGENT_BOOTSTRAP_QUIET=1        Suppress non-critical warnings
"@
}

if ($Help) { Show-Usage; exit 0 }

# Ensure local bin in PATH
$localBin = Join-Path $env:USERPROFILE ".local\bin"
$env:Path = "$localBin;$env:Path"
if (Test-Path (Join-Path $env:USERPROFILE "AppData\Roaming\Python\Scripts")) {
    $env:Path = "$env:USERPROFILE\AppData\Roaming\Python\Scripts;$env:Path"
}

Write-Host "thegent bootstrap"
Write-Host "================="

# --- Phase 0: System Dependencies ---
if ($env:THGENT_BOOTSTRAP_DEPS -eq "1") {
    Write-Step "Installing optional tools (Modern Unix)..."
    if (Get-Command brew -ErrorAction SilentlyContinue) {
        brew install ripgrep fd jq eza bat zoxide delta duf dust procs bottom yazi xh sd `
                     zellij starship hyperfine tokei onefetch lazygit lazydocker grex `
                     mise proto pixi pkgx wasmtime wasmer zig
    } elseif (Get-Command winget -ErrorAction SilentlyContinue) {
        $pkgs = "BurntSushi.ripgrep", "sharkdp.fd", "jqlang.jq", "eza-community.eza", "sharkdp.bat", "ajeetdsouza.zoxide", "dandavison.delta", "muesli.duf", "sharkdp.dust", "dalance.procs", "ClementTsang.bottom", "sxyazi.yazi", "ducaale.xh", "chmln.sd", `
                "Zellij.Zellij", "Starship.Starship", "sharkdp.hyperfine", "XAMPPRocky.tokei", "dalance.onefetch", "JesseDuffield.LazyGit", "JesseDuffield.LazyDocker", "pemistahl.grex", `
                "jdx.mise", "proto.proto", "prefix-dev.pixi", "pkgx.pkgx", "BytecodeAlliance.Wasmtime", "Wasmer.Wasmer", "zig.zig"
        foreach ($pkg in $pkgs) {
            try { winget install $pkg --silent --accept-package-agreements --accept-source-agreements } catch {}
        }
    }
}

# --- Phase 1: Install thegent ---
$thegentInstalled = Get-Command thegent -ErrorAction SilentlyContinue
    if ($thegentInstalled) {
    Write-Host "==> thegent already installed: $(thegent --version 2>$null)"
} else {
    Write-Step "Installing thegent..."

    $installed = $false
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        uv tool install thegent
        $installed = $true
    } elseif (Get-Command bun -ErrorAction SilentlyContinue) {
        bun install -g thegent
        $installed = $true
    } elseif (Get-Command pipx -ErrorAction SilentlyContinue) {
        pipx install thegent
        $installed = $true
    } elseif (Get-Command pip -ErrorAction SilentlyContinue) {
        pip install --user thegent
        $installed = $true
    } elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
        pip3 install --user thegent
        $installed = $true
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        py -m pip install --user thegent
        $installed = $true
    }

    if (-not $installed) {
        Write-Die "No installer (uv, bun, pipx, pip) found. Install Python from https://python.org or uv from https://astral.sh/uv"
    }
}

# Refresh PATH and verify
$env:Path = "$localBin;$env:Path"
$env:Path = "$env:USERPROFILE\AppData\Roaming\Python\Scripts;$env:Path"
if (-not (Get-Command thegent -ErrorAction SilentlyContinue)) {
    Write-Die "thegent not in PATH. Add to your profile: `$env:Path = `"$localBin;`$env:Path`""
}

# --- Phase 2–5: Post-install ---
if ($NoSetup) {
    Write-Host ""
    Write-Host "==> Install complete (-NoSetup). Run when ready:"
    Write-Host "    thegent install -t all; thegent setup; thegent doctor"
    exit 0
}

if ($Full) {
    Write-Step "Running thegent setup --full..."
    try {
        thegent setup --full
    } catch {
        Write-Warn "setup --full had issues. Run 'thegent doctor' to diagnose."
    }
} else {
    Write-Step "Running thegent install -t all..."
    try { thegent install -t all } catch { Write-Warn "install -t all had issues. Run 'thegent doctor'." }

    Write-Step "Running thegent install-shims..."
    try { thegent install-shims } catch { Write-Warn "install-shims had issues. Run 'thegent doctor'." }

    if ($env:THGENT_BOOTSTRAP_SYSTEM_SHIMS -eq "1") {
        Write-Step "Running thegent install-shims --system..."
        try { thegent install-shims --system } catch { Write-Warn "install-shims --system skipped." }
    }

    Write-Step "Running thegent setup..."
    try { thegent setup } catch { Write-Warn "setup had issues. Run 'thegent setup' manually." }
}

# --- Phase 6: Verify ---
Write-Step "Running thegent doctor..."
try {
    thegent doctor
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "Bootstrap complete. Try: thegent run `"Hello`" free"
    } else {
        Write-Host ""
        Write-Host "Some checks failed. Run 'thegent doctor --fix' or see docs/guides/TROUBLESHOOTING.md"
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "Doctor failed. Run 'thegent doctor' to diagnose."
    exit 1
}
