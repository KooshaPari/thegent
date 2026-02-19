{
  description: "thegent: Agentic orchestration & governance platform";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
        pythonPackages = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python
            pythonPackages.pip
            pythonPackages.venvShellHook
            uv
            nodejs_20
            nodePackages.npm
            ripgrep
            fd
            jaq
            git
            tmux
          ];

          shellHook = ''
            # Virtualenv setup
            if [ ! -d .venv ]; then
              uv venv
            fi
            source .venv/bin/activate

            # Environment variables
            export PYTHONPATH=$PYTHONPATH:$(pwd)/src
            export PATH=$PATH:$(pwd)/.venv/bin:$HOME/.local/bin
            export THGENT_NOTIFY_ENABLE=1
            export THGENT_NOTIFY_VOICE_MODE=all
            export THGENT_NOTIFY_VOICE_NAME="Samantha"
            export THGENT_NOTIFY_COOLDOWN_SEC=8
            export THGENT_ZEN_BASE_URL="https://api.opencode.ai"

            echo "=== thegent dev environment ==="
            echo "Python: $(python --version)"
            echo "Node:   $(node --version)"
            echo "uv:     $(uv --version)"
            echo "==============================="
          '';
        };
      }
    );
}
