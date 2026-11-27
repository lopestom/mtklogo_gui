"""Prepares mtklogo-gui/git: bash.exe + the few coreutils the script needs (Git for Windows runtime)."""
import os, shutil, subprocess, sys, urllib.request
from pathlib import Path

URL = ("https://github.com/git-for-windows/git/releases/download/"
       "v2.56.0.windows.2/PortableGit-2.56.0.2-64-bit.7z.exe")
here = Path(__file__).resolve().parent
dest = here.parent / "mtklogo-gui" / "git"
work = here / "build_tmp"
TOOLS = ("bash sh basename cat chmod cp cut date dirname du env expr false file find grep head ls mkdir "
         "mktemp mv printf readlink realpath rm rmdir sed sha256sum sleep sort stat tail tee touch tr true "
         "uname uniq wc xargs awk gawk id tty stty ln echo test").split()


def source_tree() -> Path:
    for var in ("ProgramFiles", "ProgramFiles(x86)"):
        base = Path(os.environ.get(var, "."))
        if (base / "Git" / "usr" / "bin" / "bash.exe").is_file():
            print("Using installed Git for Windows:", base / "Git")
            return base / "Git"
    work.mkdir(exist_ok=True)
    exe, out = work / "PortableGit.7z.exe", work / "pgit"
    if not (out / "usr" / "bin" / "bash.exe").is_file():
        if not exe.is_file():
            print("Downloading PortableGit (~60 MB)...")
            urllib.request.urlretrieve(URL, exe)
        print("Extracting...")
        subprocess.run([str(exe), "-y", f"-o{out}"], check=True)
    return out


def main():
    if (dest / "usr" / "bin" / "bash.exe").is_file():
        print("git/ already prepared."); return
    src = source_tree()
    for d in ("usr/bin", "usr/share/misc", "etc", "tmp"):
        (dest / d).mkdir(parents=True, exist_ok=True)
    (dest / "tmp" / ".keep").write_text("")
    sb = src / "usr" / "bin"
    for f in sb.glob("*.dll"):
        shutil.copy2(f, dest / "usr" / "bin")
    for t in TOOLS:
        if (sb / f"{t}.exe").is_file():
            shutil.copy2(sb / f"{t}.exe", dest / "usr" / "bin")
    for rel in ("usr/share/misc/magic.mgc", "etc/nsswitch.conf", "etc/fstab"):
        if (src / rel).is_file():
            shutil.copy2(src / rel, dest / rel)
    env = {"PATH": str(dest / "usr" / "bin"), "MSYSTEM": "MSYS", "SYSTEMROOT": os.environ.get("SYSTEMROOT", r"C:\Windows")}
    r = subprocess.run([str(dest / "usr" / "bin" / "bash.exe"), "-c",
        'x=$(echo ok); echo "$x" | cat; readlink -f . >/dev/null; sha256sum --version >/dev/null; '
        'find . -maxdepth 0 >/dev/null; mktemp -u >/dev/null; du -s . >/dev/null; date >/dev/null && echo TOOLS_OK'],
        env=env, capture_output=True, text=True, timeout=60)
    print(r.stdout.strip(), r.stderr.strip())
    if "TOOLS_OK" not in r.stdout:
        sys.exit("BASH SELF-TEST FAILED - send this output for analysis.")
    print("git/ ready.")


main()
