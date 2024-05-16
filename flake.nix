# based off https://git.belanyi.fr/ambroisie/advent-of-code/src/commit/d35e1d43d664403d1de330d40e7a865eb3554533/flake.nix
{
  description = "Z3 lab";

  inputs = {
    flake-utils = {
      type = "github";
      owner = "numtide";
      repo = "flake-utils";
    };

    nixpkgs = {
      type = "github";
      owner = "NixOS";
      repo = "nixpkgs";
      ref = "nixos-unstable";
    };
  };

  outputs =
    {
      self,
      flake-utils,
      nixpkgs,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };

        run = pkgs.writeShellScriptBin "python-run" ''
          clear 
          python3 example.py
        '';

        watch = pkgs.writeShellScriptBin "python-watch" ''
          ${pkgs.fswatch}/bin/fswatch -o . | xargs -n1 ${run}/bin/python-run
        '';
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            run
            watch
            (python312.withPackages (
              ps: with ps; [
                black
                pyright
                z3
              ]
            ))
          ];
        };
      }
    );
}
