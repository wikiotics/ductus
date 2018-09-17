# https://vaibhavsagar.com/blog/2018/05/27/quick-easy-nixpkgs-pinning/
#
# See also https://nixos.wiki/wiki/FAQ/Pinning_Nixpkgs (though I found
# it less useful).
#
# Also useful: https://nixos.org/nixpkgs/manual/#python especially
# "Overriding Python packages"
with import (builtins.fetchGit {
  # Descriptive name to make the store path easier to identify
  name = "nixos-unstable-2018-09";
  url = "https://github.com/NixOS/nixpkgs";
  # see https://github.com/NixOS/nix/issues/1923#issuecomment-382581096
  rev = "57ee1416965e3675857aa8c0856d36e3ba0b30c3";
}) {};

stdenv.mkDerivation {
  name = "impurePythonEnv";
  buildInputs = [
    # To help with development
    gitFull
    less
    which
    nano
    # Python and packages
    python27Packages.virtualenv
    python27Packages.pip
    (python27.withPackages (ps:
      [
        ps.pillow
        ps.lxml
      ]
    ))
  ];
  src = null;
  # From https://nixos.org/nixpkgs/manual/#how-to-consume-python-modules-using-pip-in-a-virtualenv-like-i-am-used-to-on-other-operating-systems
  shellHook = ''
  #rm -rf $PWD/venv
  # set SOURCE_DATE_EPOCH so that we can use python wheels
  SOURCE_DATE_EPOCH=$(date +%s)
  virtualenv --system-site-packages $PWD/venv >$PWD/virtualenv.log
  source $PWD/venv/bin/activate
  pip install -r $PWD/requirements.txt >$PWD/pip.log
  export EDITOR=nano
  '';
}
