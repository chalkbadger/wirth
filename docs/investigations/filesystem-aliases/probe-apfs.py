#!/usr/bin/env python3
"""Bounded macOS native observations for #6; not a validator test or Windows run."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True

MAIN = "1079e7dda120253dfaa41798aaba2186b4a09fab"
BLOBS = {
    "wirth/validate.py": "3c679b4f2329896144812751740e5f606bd0d0db",
    "contracts/local-validation.md": "e58e3a01c846b996948da543fa0ae74ce02efa3c",
}
# A lexical exclusion is not evidence of native alias resolution.
CANDIDATES = [
    ("case-final", "checks/Report.py", "checks/report.py"),
    ("case-directory", "Checks/result.py", "checks/result.py"),
    ("unicode-nfc-request", "checks/cafe\u0301.py", "checks/caf\u00e9.py"),
    ("unicode-nfd-request", "checks/caf\u00e9.py", "checks/cafe\u0301.py"),
    ("unicode-kelvin-ascii-request", "checks/\u212a.py", "checks/K.py"),
    ("unicode-longs-ascii-request", "checks/\u017f.py", "checks/s.py"),
    ("trailing-dot-request", "checks/report.py", "checks/report.py."),
    ("trailing-dots-request", "checks/report.py", "checks/report.py..."),
    ("trailing-dot-directory", "checks/report.py", "checks./report.py"),
    ("trailing-dot-stored", "checks/report.py.", "checks/report.py"),
    ("trailing-space-request", "checks/report.py", "checks/report.py "),
    ("short-name-tilde", "checks/LongFilename.py", "checks/LONGFI~1.PY"),
    ("short-name-without-tilde", "checks/LongFilename.py", "checks/SHORT.PY"),
    ("reserved-NUL", "checks/NUL", "checks/NUL"),
    ("reserved-CON-extension", "checks/CON.txt", "checks/CON.txt"),
    ("reserved-COM1", "checks/COM1", "checks/COM1"),
    ("reserved-LPT1", "checks/LPT1", "checks/LPT1"),
    ("alternate-data-stream", "checks/report.py", "checks/report.py:stream"),
    ("alternate-data-default-stream", "checks/report.py", "checks/report.py::$DATA"),
    ("git-case", ".git/config", ".GIT/config"),
    ("git-trailing-dot", ".git/config", ".git./config"),
    ("git-trailing-dots", ".git/config", ".git.../config"),
    ("git-short-tilde", ".git/config", "GIT~1/config"),
    ("git-short-without-tilde", ".git/config", "GITDIR/config"),
    ("git-ignorable-request", ".git/config", ".g\u200cit/config"),
    ("hidden-exact-main-control", ".github/check.py", ".github/check.py"),
]

def command(args, cwd=None, env=None, timeout=10):
    start = time.monotonic()
    try:
        p = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout)
        return {"argv": args, "exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr,
                "timeout_seconds": timeout, "timed_out": False,
                "elapsed_seconds": round(time.monotonic() - start, 4)}
    except subprocess.TimeoutExpired as e:
        return {"argv": args, "exit": None, "stdout": str(e.stdout or ""),
                "stderr": str(e.stderr or ""), "timeout_seconds": timeout, "timed_out": True}

def git_blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def load_validator(source, name):
    spec = importlib.util.spec_from_file_location(name, source / "wirth/validate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def lexical_gate(module, label):
    """Controlled resolver stub isolates the published pre-filesystem rules."""
    saved = module._resolve_local
    called = []
    module._resolve_local = lambda *args, **kwargs: called.append(True)
    try:
        module._validate_reference(Path("."), label, "../" + label)
        return {"allowed_to_reach_filesystem": bool(called), "diagnostic": None,
                "method": "controlled resolver stub; no filesystem observation"}
    except ValueError as e:
        return {"allowed_to_reach_filesystem": False, "diagnostic": str(e),
                "method": "controlled resolver stub; no filesystem observation"}
    finally:
        module._resolve_local = saved

def identity(path):
    try:
        s = path.lstat()
        return {"exists": True, "device": s.st_dev, "inode": s.st_ino, "mode": oct(s.st_mode),
                "size": s.st_size}
    except OSError as e:
        return {"exists": False, "errno": e.errno, "error_type": type(e).__name__, "message": str(e)}

def listing_walk(root, label):
    current = root
    rows = []
    for part in label.split("/"):
        try:
            names = sorted(os.listdir(current))
            rows.append({"parent": str(current.relative_to(root)), "requested_component": part,
                         "names": names, "exact_member": part in names})
        except OSError as e:
            rows.append({"parent": str(current.relative_to(root)), "requested_component": part,
                         "error_type": type(e).__name__, "errno": e.errno})
            break
        current /= part
    return rows

def write_contract(root, label, directory="contracts"):
    target = root / directory
    target.mkdir(exist_ok=True)
    (target / "one.md").write_text(
        "# Alias observation\nIssue: https://github.com/chalkbadger/wirth/issues/6\n\n"
        "## [alias] The reference names the file.\n"
        "- [" + label + "](../" + label + "): The file is present.\n", encoding="utf-8")

def validate_command(source, root):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(source)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return command([sys.executable, "-m", "wirth", "validate"], cwd=root, env=env)

def native_case(source, module, parent, case_id, actual, requested):
    with tempfile.TemporaryDirectory(prefix=case_id + "-", dir=parent) as dirname:
        root = Path(dirname)
        p = root / actual
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("probe marker for " + case_id + "\n", encoding="utf-8")
        observed = {"requested": requested, "created": actual,
                    "directory_walk": listing_walk(root, requested),
                    "requested_object": identity(root / requested), "created_object": identity(p)}
        try:
            observed["same_object"] = os.path.samefile(root / requested, p)
        except OSError:
            observed["same_object"] = False
        write_contract(root, requested)
        observed["validator"] = validate_command(source, root)
        write_contract(root, actual)
        observed["exact_spelling_control"] = {
            "requested": actual, "directory_walk": listing_walk(root, actual),
            "object": identity(p), "lexical_gate": lexical_gate(module, actual),
            "validator": validate_command(source, root)}
        return observed

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="exact selected main checkout")
    parser.add_argument("--probe-parent", type=Path, required=True, help="existing writable APFS directory")
    parser.add_argument("--proposed-source", type=Path, help="optional issue-65 source for separate #5 rule analysis")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.error("This recorded native probe is macOS-only; it does not establish NTFS behavior.")
    source = args.source.resolve()
    parent = args.probe_parent.resolve()
    hashes = {p: git_blob(source / p) for p in BLOBS}
    if hashes != BLOBS:
        parser.error("source validator/contract do not match selected main " + MAIN)
    v = load_validator(source, "selected_main")
    proposed = load_validator(args.proposed_source.resolve(), "unmerged_proposal") if args.proposed_source else None
    metadata = {
        "selected_main_commit": MAIN, "selected_blob_hashes": hashes,
        "python": sys.version, "platform": platform.platform(), "machine": platform.machine(),
        "filesystem_path": str(parent), "os_release": command(["sw_vers"]),
        "df": command(["df", "-P", str(parent)]),
        "diskutil": command(["diskutil", "info", "-plist", str(parent)]),
        "native_scope": "one local macOS filesystem; Windows/NTFS not executed",
    }
    mounts = command(["mount"])
    df_lines = metadata["df"]["stdout"].splitlines()
    device = df_lines[-1].split()[0] if len(df_lines) > 1 else ""
    metadata["selected_mount"] = [line for line in mounts["stdout"].splitlines() if line.startswith(device + " on ")]
    rows = []
    for case_id, actual, requested in CANDIDATES:
        gate = lexical_gate(v, requested)
        row = {"case": case_id, "requested": requested, "created_candidate": actual, "main_rule_gate": gate}
        if proposed:
            row["unmerged_57_rule_analysis"] = lexical_gate(proposed, requested)
        if gate["allowed_to_reach_filesystem"]:
            row["native"] = native_case(source, v, parent, case_id, actual, requested)
        else:
            row["native"] = None
            row["native_disposition"] = "not executed; requested label excluded before filesystem lookup"
        rows.append(row)
    with tempfile.TemporaryDirectory(prefix="discovery-case-", dir=parent) as dirname:
        root = Path(dirname)
        (root / "check.py").write_text("control\n")
        write_contract(root, "check.py", directory="Contracts")
        discovery = {"requested": "contracts", "created": "Contracts", "directory_walk": listing_walk(root, "contracts"),
                     "requested_object": identity(root / "contracts"), "created_object": identity(root / "Contracts"),
                     "same_object": os.path.samefile(root / "contracts", root / "Contracts"),
                     "validator": validate_command(source, root)}
        # Rename through an unrelated name so the case change reaches the directory entry.
        (root / "Contracts").rename(root / "temporary")
        (root / "temporary").rename(root / "contracts")
        discovery["exact_spelling_control"] = {"requested": "contracts",
            "directory_walk": listing_walk(root, "contracts"), "validator": validate_command(source, root)}
    output = {"metadata": metadata, "cases": rows, "discovery": discovery,
              "final_selected_blob_hashes": {p: git_blob(source / p) for p in BLOBS},
              "limits": ["Rule-gate stubs are only lexical observations.",
                         "No Windows/NTFS native result is supplied.",
                         "No production mutation, Git-index or GitHub-link test is performed.",
                         "Only the enumerated fixtures on the recorded configuration are covered."]}
    print(json.dumps(output, indent=2, ensure_ascii=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

