# home-manager module for thegent
# Usage:
#   imports = [ inputs.thegent.homeManagerModules.thegent ];
#   extraSpecialArgs = { thegent = inputs.thegent.packages.${system}.thegent; };
#
# programs.thegent = {
#   enable = true;
#   package = thegent;  # optional - puts thegent on PATH; omit if installed via pip/uv
#   installTargets = [ "claude-code" "cursor" "envrc" "shell" ];
#   installShims = true;
#   installShimsSystem = false;  # requires sudo
#   installLockCleanupService = true;
# };

{ config, lib, pkgs, ... }:

let
  cfg = config.programs.thegent;
  targetsStr = lib.concatStringsSep " " cfg.installTargets;
  thegentBin = if cfg.package != null then "${cfg.package}/bin/thegent" else "thegent";
  activationScript = ''
    if command -v thegent >/dev/null 2>&1; then
      thegent install -t ${targetsStr} --force
      ${lib.optionalString cfg.installShims "thegent install-shims"}
      ${lib.optionalString cfg.installShimsSystem "thegent install-shims --system 2>/dev/null || echo 'install-shims --system skipped (may need sudo)'"}
      ${lib.optionalString cfg.installLockCleanupService ''
        thegent git lock-cleanup service install 2>/dev/null || true
        thegent git lock-cleanup service start 2>/dev/null || true
      ''}
    else
      echo "thegent not in PATH. Set programs.thegent.package or install via: pip install thegent, uv tool install thegent."
    fi
  '';
in
{
  meta.maintainers = [ ];

  options.programs.thegent = {
    enable = lib.mkEnableOption "thegent agent orchestration";

    package = lib.mkOption {
      type = lib.types.nullOr lib.types.package;
      default = null;
      example = lib.literalExpression "inputs.thegent.packages.\${system}.thegent";
      description = ''
        thegent package (e.g. from flake: inputs.thegent.packages.''${system}.thegent).
        When set, adds thegent to PATH via home.packages. Omit if installed via pip/uv.
      '';
    };

    installTargets = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ "claude-code" "cursor" "envrc" "shell" ];
      example = lib.literalExpression ''[ "claude-code" "cursor" "codex" "droid" "envrc" "shell" ]'';
      description = ''
        Targets for `thegent install -t`. Options: claude-code, claude-desktop, cursor, codex, droid, envrc, shell.
      '';
    };

    installShims = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Run `thegent install-shims` (user shims in ~/.local/bin).";
    };

    installShimsSystem = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = ''
        Run `thegent install-shims --system` (git wrapper in /usr/local/bin for nix/direnv).
        Requires sudo. Set to true only if you run home-manager with appropriate permissions.
      '';
    };

    installLockCleanupService = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Install and start thegent git lock-cleanup daemon (launchd/systemd).";
    };
  };

  config = lib.mkIf cfg.enable {
    home.packages = lib.mkIf (cfg.package != null) [ cfg.package ];
    home.activation.thegentInstall = lib.hm.dag.entryAfter [ "writeBoundary" ] activationScript;

    # Ensure ~/.local/bin in PATH for shims
    home.sessionPath = lib.mkIf cfg.installShims [
      "${config.home.homeDirectory}/.local/bin"
    ];
  };
}
