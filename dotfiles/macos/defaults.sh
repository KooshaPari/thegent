#!/usr/bin/env bash
# thegent dotfiles — macOS system defaults
# Applies opinionated macOS settings for developer machines
# Idempotent: safe to run multiple times
set -euo pipefail

echo "  Applying macOS system defaults..."

# ── Finder ────────────────────────────────────────────────────────────────────
# Show all filename extensions
defaults write NSGlobalDomain AppleShowAllExtensions -bool true
# Show hidden files by default
defaults write com.apple.finder AppleShowAllFiles -bool true
# Show path bar
defaults write com.apple.finder ShowPathbar -bool true
# Show status bar
defaults write com.apple.finder ShowStatusBar -bool true
# Display full POSIX path as Finder window title
defaults write com.apple.finder _FXShowPosixPathInTitle -bool true
# Keep folders on top when sorting by name
defaults write com.apple.finder _FXSortFoldersFirst -bool true
# Search the current folder by default
defaults write com.apple.finder FXDefaultSearchScope -string "SCcf"
# Disable the warning when changing a file extension
defaults write com.apple.finder FXEnableExtensionChangeWarning -bool false
# Use list view in Finder by default
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"

# ── Dock ──────────────────────────────────────────────────────────────────────
# Auto-hide the Dock
defaults write com.apple.dock autohide -bool true
# Remove the auto-hide delay
defaults write com.apple.dock autohide-delay -float 0
# Remove the animation delay when hiding/showing the Dock
defaults write com.apple.dock autohide-time-modifier -float 0.3
# Don't show recent applications in Dock
defaults write com.apple.dock show-recents -bool false
# Minimize windows into their application's icon
defaults write com.apple.dock minimize-to-application -bool true
# Small icon size
defaults write com.apple.dock tilesize -int 40

# ── Keyboard ─────────────────────────────────────────────────────────────────
# Enable full keyboard access for all controls
defaults write NSGlobalDomain AppleKeyboardUIMode -int 3
# Set fast key repeat rate
defaults write NSGlobalDomain KeyRepeat -int 2
defaults write NSGlobalDomain InitialKeyRepeat -int 15
# Disable press-and-hold for keys in favor of key repeat
defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false
# Disable auto-correct
defaults write NSGlobalDomain NSAutomaticSpellingCorrectionEnabled -bool false
# Disable smart quotes and dashes
defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
defaults write NSGlobalDomain NSAutomaticDashSubstitutionEnabled -bool false

# ── Trackpad ─────────────────────────────────────────────────────────────────
# Tap to click
defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true
defaults write com.apple.AppleMultitouchTrackpad Clicking -bool true
defaults -currentHost write NSGlobalDomain com.apple.mouse.tapBehavior -int 1
defaults write NSGlobalDomain com.apple.mouse.tapBehavior -int 1

# ── Screenshots ───────────────────────────────────────────────────────────────
# Save screenshots to Desktop/Screenshots
mkdir -p "${HOME}/Desktop/Screenshots"
defaults write com.apple.screencapture location -string "${HOME}/Desktop/Screenshots"
# Save screenshots as PNG
defaults write com.apple.screencapture type -string "png"
# Disable screenshot shadow
defaults write com.apple.screencapture disable-shadow -bool true

# ── Safari / WebKit ───────────────────────────────────────────────────────────
# Enable the Develop menu and Web Inspector
defaults write com.apple.Safari IncludeInternalDebugMenu -bool true
defaults write com.apple.Safari IncludeDevelopMenu -bool true
defaults write com.apple.Safari WebKitDeveloperExtrasEnabledPreferenceKey -bool true

# ── Activity Monitor ─────────────────────────────────────────────────────────
# Show all processes
defaults write com.apple.ActivityMonitor ShowCategory -int 0
# Sort by CPU usage
defaults write com.apple.ActivityMonitor SortColumn -string "CPUUsage"
defaults write com.apple.ActivityMonitor SortDirection -int 0

# ── TextEdit ─────────────────────────────────────────────────────────────────
# Use plain text by default
defaults write com.apple.TextEdit RichText -int 0
# Open files as UTF-8
defaults write com.apple.TextEdit PlainTextEncoding -int 4
defaults write com.apple.TextEdit PlainTextEncodingForWrite -int 4

# ── Terminal ─────────────────────────────────────────────────────────────────
# Only use UTF-8 in Terminal.app
defaults write com.apple.terminal StringEncodings -array 4
# Enable Secure Keyboard Entry
defaults write com.apple.terminal SecureKeyboardEntry -bool true

# ── System UI ─────────────────────────────────────────────────────────────────
# Show battery percentage
defaults write com.apple.menuextra.battery ShowPercent -string "YES"
# Clock: show seconds
defaults write com.apple.menuextra.clock ShowSeconds -bool true

# ── Restart affected applications ────────────────────────────────────────────
for app in "Finder" "Dock" "SystemUIServer" "Terminal"; do
  killall "${app}" &>/dev/null || true
done

echo "  macOS defaults applied — some changes require a logout to take effect"
