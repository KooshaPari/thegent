# TheGent Canonical PowerShell Profile Template
# ---------------------------------------------------------
# This file provides a high-performance, agent-friendly environment
# that mirrors the POSIX Zsh experience in native Windows 11.
# ---------------------------------------------------------

# 1. Performance: Disable telemetry and progress bars for speed
$ProgressPreference = "SilentlyContinue"
$InformationPreference = "SilentlyContinue"

# 2. Path Management: Ensure thegent and common CLI tools are in PATH
$localBin = Join-Path $env:USERPROFILE ".local\bin"
if (-not ($env:Path -split ";" | Where-Object { $_ -eq $localBin })) {
    $env:Path = "$localBin;$env:Path"
}

# 3. mise (Polyglot Version Manager) activation
if (Get-Command mise -ErrorAction SilentlyContinue) {
    # mise activate pwsh | Out-String | Invoke-Expression  # Slow
    # Fast path: manual activation
    $env:MISE_SHELL = "pwsh"
    # Note: Full activation might be needed for some tools
}

# 4. Starship (Prompt) activation
if (Get-Command starship -ErrorAction SilentlyContinue) {
    Invoke-Expression (&starship init powershell)
}

# 5. Zoxide (Smart directory navigation) activation
if (Get-Command zoxide -ErrorAction SilentlyContinue) {
    Invoke-Expression (&zoxide init powershell)
}

# 6. Aliases: Mirroring POSIX standards for workstation QOL
function Get-Aliases {
    # Git
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Set-Alias -Name g -Value git
    }

    # Better ls (eza)
    if (Get-Command eza -ErrorAction SilentlyContinue) {
        function ls { eza --icons --git --group-directories-first $args }
        function ll { eza -l --icons --git --group-directories-first $args }
        function la { eza -la --icons --git --group-directories-first $args }
    } else {
        # Fallback to standard ls but colored if possible
    }

    # Better cat (bat)
    if (Get-Command bat -ErrorAction SilentlyContinue) {
        function cat { bat --paging=never $args }
    }

    # Better find (fd)
    if (Get-Command fd -ErrorAction SilentlyContinue) {
        Set-Alias -Name f -Value fd
    }

    # Better grep (rg)
    if (Get-Command rg -ErrorAction SilentlyContinue) {
        Set-Alias -Name grep -Value rg
    }

    # Editor (NeoVim/VSCode)
    if (Get-Command nvim -ErrorAction SilentlyContinue) {
        Set-Alias -Name v -Value nvim
    } elseif (Get-Command code -ErrorAction SilentlyContinue) {
        Set-Alias -Name v -Value code
    }

    # thegent shortcuts
    Set-Alias -Name thg -Value thegent

    # Modernization Aliases
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        function pip { uv pip $args }
    }
    if (Get-Command bun -ErrorAction SilentlyContinue) {
        Set-Alias -Name npm -Value bun
        Set-Alias -Name npx -Value bunx
    }
}
Get-Aliases

# 7. WSL2 Interop Helpers
function Use-Wsl {
    param([string]$cmd)
    if (Get-Command wsl -ErrorAction SilentlyContinue) {
        wsl --exec bash -c "$cmd"
    }
}

# Fast wslpath equivalent for Windows
function Resolve-WslPath {
    param([string]$WindowsPath)
    if ($WindowsPath -match "^([A-Za-z]):\\(.*)") {
        $drive = $Matches[1].ToLower()
        $rest = $Matches[2] -replace "\\", "/"
        return "/mnt/$drive/$rest"
    }
    return $WindowsPath
}

# 8. thegent Shell Hooks (Command Interception)
# This allows thegent to monitor your commands and provide proactive assistance.
if (Get-Command thegent -ErrorAction SilentlyContinue) {
    # Placeholder for hook registration
    # thegent hook init powershell | Out-String | Invoke-Expression
}

# 9. QOL: Terminal Title and Coloring
$Host.UI.RawUI.WindowTitle = "TheGent | $(Get-Location)"
function Set-WindowTitle {
    $Host.UI.RawUI.WindowTitle = "TheGent | $(Get-Location)"
}

# Hook location change to update title
if (Get-Command Set-PSReadLineKeyHandler -ErrorAction SilentlyContinue) {
    # Custom keybindings or handlers
}

Write-Host "thegent profile loaded. Ready for work." -ForegroundColor Cyan
