# Homebrew formula for Squidbrake. It lives in the tap repo github.com/batrapulkit/homebrew-tap as
# Formula/squidbrake.rb, so people install with:
#   brew install batrapulkit/tap/squidbrake
# On every release: update url and sha256 (the sdist on PyPI) and copy this file to the tap.
class Squidbrake < Formula
  desc "Change control for AI agents: agents propose, people approve"
  homepage "https://squidbrake.com"
  url "https://files.pythonhosted.org/packages/57/44/e8fd98cf2324f81005ebf300cdbe361ab51ef7e380e5c5e9758dbb1ffa86/squidbrake-0.14.7.tar.gz"
  sha256 "a7f8af96a441429413c813d0890615552ac74d65cf698336da6c38b323cc656f"
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
