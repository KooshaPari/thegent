# nix-darwin module for thegent - MCP service + lock-cleanup timer
# Usage: imports = [ inputs.thegent.nixDarwinModules.thegent ];
#
# Uses launchd.user.agents (per-user agents). Structure matches nix-darwin's
# launchd module: each agent has serviceConfig with ProgramArguments, etc.
#
# thegent = {
#   enable = true;
#   enableMcpService = true;   # launchd for MCP server
#   enableLockCleanup = true;  # launchd timer for git lock-cleanup
# };

{ config, lib, pkgs, ... }:

let
  cfg = config.thegent or {};
in
{
  options.thegent = lib.mkOption {
    type = lib.types.submodule {
      options = {
        enable = lib.mkEnableOption "thegent system services";
        enableMcpService = lib.mkOption {
          type = lib.types.bool;
          default = true;
          description = "Run thegent MCP as launchd service at login";
        };
        enableLockCleanup = lib.mkOption {
          type = lib.types.bool;
          default = true;
          description = "Run thegent git lock-cleanup every 5 min via launchd";
        };
        package = lib.mkOption {
          type = lib.types.nullOr lib.types.package;
          default = null;
          description = "thegent package (from flake). When null, uses thegent from PATH.";
        };
      };
    };
    default = {};
  };

  config = lib.mkIf (cfg.enable or false) (lib.mkMerge [
    (lib.mkIf cfg.enableMcpService {
      launchd.user.agents.thegent-mcp = {
        serviceConfig = {
          ProgramArguments = [
            (if cfg.package != null then "${cfg.package}/bin/thegent" else "thegent")
            "serve"
          ];
          RunAtLoad = true;
          KeepAlive = true;
          StandardOutPath = "/tmp/thegent-mcp.log";
          StandardErrorPath = "/tmp/thegent-mcp.err";
        };
      };
    })
    (lib.mkIf cfg.enableLockCleanup {
      launchd.user.agents.thegent-lock-cleanup = {
        serviceConfig = {
          ProgramArguments = [
            (if cfg.package != null then "${cfg.package}/bin/thegent" else "thegent")
            "git" "lock-cleanup"
          ];
          StartInterval = 300;
          RunAtLoad = false;
          StandardOutPath = "/tmp/thegent-lock-cleanup.log";
          StandardErrorPath = "/tmp/thegent-lock-cleanup.err";
        };
      };
    })
  ]);
}
