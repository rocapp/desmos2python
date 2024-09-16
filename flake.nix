{
  description = "desmos2python package";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable"; # Adjust to your preferred channel
  };

  outputs = { self, nixpkgs, lib }: {
    packages.x86_64-linux = with nixpkgs.legacyPackages.x86_64-linux; {
      desmos2python = python3Packages.buildPythonPackage {
        pname = "desmos2python";
        version = builtins.readFile (builtins.fetchurl {
          url = "file://${builtins.toString ./.git/refs/tags/$(git describe --tags --abbrev=0)}";
          sha256 = builtins.hashFile "sha256" "${builtins.toString ./.git/refs/tags/$(git describe --tags --abbrev=0)}";
        });

        src = ./.;

        buildInputs = [
          python3Packages.pandoc
          python3Packages.selenium
          # Add other dependencies as needed
        ];

        meta = with lib; {
          description = "Convert Desmos equations to executable Python code.";
          license = licenses.mit; # Update with the correct license
          maintainers = [ "Robert Capps <rocapp@gmail.com>" ]; # Replace with your name
        };
      };
    };
  };
}