class Thegent < Formula
  include Language::Python::Virtualenv

  desc "Unified agent orchestration CLI for Factory skills, droids, and multi-agent workflows"
  homepage "https://github.com/kooshapari/thegent"
  url "https://github.com/kooshapari/thegent/archive/refs/tags/v{{VERSION}}.tar.gz"
  sha256 "{{SHA256}}"
  license "MIT"

  depends_on "python@3.12"
  depends_on "ripgrep"
  depends_on "fd"
  depends_on "jq"
  depends_on "git"
  depends_on "node"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/thegent", "--version"
  end
end
