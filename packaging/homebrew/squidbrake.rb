# Homebrew formula for Squidbrake. It lives in the tap repo github.com/batrapulkit/homebrew-tap as
# Formula/squidbrake.rb, so people install with:
#   brew install batrapulkit/tap/squidbrake
# On every release: update url and sha256 (the sdist on PyPI) and copy this file to the tap.
class Squidbrake < Formula
  desc "Change control for AI agents: agents propose, people approve"
  homepage "https://squidbrake.com"
  url "https://files.pythonhosted.org/packages/74/95/7e4b173a602a6646ef67d4ae4cd81529c68cf88ca9068ae1661983274f8d/squidbrake-0.14.2.tar.gz"
  sha256 "c62287cf3c54aea654bc0a40f387f198424755af1718e1dd26bc8da4e76e895d"
  license "Apache-2.0"

  depends_on "python@3.12"

  def install
    # shortcut: dependencies come from PyPI at install time, not pinned resource blocks; fine for our own tap,
    # run `brew update-python-resources` and pin them before submitting to homebrew-core
    system Formula["python@3.12"].opt_bin/"python3.12", "-m", "venv", libexec
    system libexec/"bin/python", "-m", "pip", "install", "--no-cache-dir", buildpath
    bin.install_symlink libexec/"bin/squidbrake"
  end

  def caveats
    <<~EOS
      Start it and connect every agent on this computer:
        squidbrake setup
      Or connect to your team's gateway:
        squidbrake connect all --url https://gateway.yourcompany.com --key gw_YOUR_AGENT_KEY
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/squidbrake --version")
  end
end
