{
  description = "Declarative ansible environments for VBC";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs.pyproject-nix.follows = "pyproject-nix";
      inputs.uv2nix.follows = "uv2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      nixpkgs,
      pyproject-nix,
      uv2nix,
      pyproject-build-systems,
      ...
    }:
    let
      inherit (nixpkgs) lib;
      forAllSystems = lib.genAttrs lib.systems.flakeExposed;

      profiles = {
        old = {
          workspaceRoot = ./nix/ansible-2_15;
          pythonAttr = "python311";
          virtualEnvName = "ansible-2_15-env";
        };
        new = {
          workspaceRoot = ./nix/ansible-2_20;
          pythonAttr = "python312";
          virtualEnvName = "ansible-2_20-env";
        };
      };

      workspaces = lib.mapAttrs (
        _: profile:
        uv2nix.lib.workspace.loadWorkspace {
          inherit (profile) workspaceRoot;
        }
      ) profiles;

      overlays = lib.mapAttrs (
        _: workspace:
        workspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        }
      ) workspaces;

      editableOverlays = lib.mapAttrs (
        _: workspace:
        workspace.mkEditablePyprojectOverlay {
          root = "$REPO_ROOT";
        }
      ) workspaces;

      pythonSets = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        lib.mapAttrs (
          name: profile:
          let
            python = pkgs.${profile.pythonAttr};
          in
          (pkgs.callPackage pyproject-nix.build.packages {
            inherit python;
          }).overrideScope
            (
              lib.composeManyExtensions [
                pyproject-build-systems.overlays.wheel
                overlays.${name}
              ]
            )
        ) profiles
      );

    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs {          # <-- replace nixpkgs.legacyPackages.${system}
            inherit system;
            config.allowUnfreePredicate = pkg: builtins.elem (lib.getName pkg) [
              "vagrant"
            ];
          };
          generated = lib.mapAttrs (
            name: profile:
            let
              pythonSet = pythonSets.${system}.${name}.overrideScope editableOverlays.${name};
              virtualenv = pythonSet.mkVirtualEnv profile.virtualEnvName workspaces.${name}.deps.all;
            in
            pkgs.mkShell {
              packages = [
                virtualenv
                pkgs.uv
                pkgs.vagrant
              ];
              env = {
                UV_NO_SYNC = "1";
                UV_PYTHON = pythonSet.python.interpreter;
                UV_PYTHON_DOWNLOADS = "never";
              };
              shellHook = ''
                unset PYTHONPATH
                export REPO_ROOT=$(git rev-parse --show-toplevel)
              '' + lib.optionalString (profile.virtualEnvName == "ansible-2_20-env") ''
                export PYTHON_LIB_PATH="$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"
                export ANSIBLE_FILTER_PLUGINS="''${PYTHON_LIB_PATH}/molecule/provisioner/ansible/plugins/filter:''${HOME}/.ansible/plugins/filter:/usr/share/ansible/plugins/filter"
                export ANSIBLE_LIBRARY="''${PYTHON_LIB_PATH}/molecule/provisioner/ansible/plugins/modules:''${PYTHON_LIB_PATH}/molecule_plugins/vagrant/modules:''${HOME}/.ansible/plugins/modules:/usr/share/ansible/plugins/modules"
                export ANSIBLE_ROLES_PATH="$(pwd)/roles:''${HOME}/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles"
              ''
              ;
            }
          ) profiles;
        in
        generated
        // {
          default = generated.new;
        }
      );

    };
}
