# devenv module for thegent - add thegent to dev environment
# Usage: imports = [ (inputs.thegent.devenvModules.thegent inputs.thegent) ];
#
# Options (optional):
#   thegent.enable = true;   # default: true
#   thegent.installOnEnter = true;  # run thegent install -t all on shell enter

self: { config, pkgs, lib, ... }:

let
  thegentPkg = (pkgs.callPackage ./thegent-package.nix { python3 = pkgs.python312; }) { src = self; };
  cfg = config.thegent or {};
in
{
  options.thegent = lib.mkOption {
    type = lib.types.submodule {
      options = {
        enable = lib.mkEnableOption "thegent in devenv";
        installOnEnter = lib.mkOption {
          type = lib.types.bool;
          default = false;
          description = "Run thegent install -t all on shell enter";
        };
      };
    };
    default = {};
  };

  config = lib.mkIf (cfg.enable or false) {
    packages = [ thegentPkg ];
    enterShell = lib.mkIf (cfg.installOnEnter or false) ''
      if command -v thegent >/dev/null 2>&1; then
        thegent install -t all --force 2>/dev/null || true
      fi
    '';
  };
}
