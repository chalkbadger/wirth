import os
from pathlib import Path
import re
import stat


# The rules enforced here are specified in contracts/claims.md.
ISSUE_URL = re.compile(
    r"https://github\.com/[A-Za-z0-9_-]+/(?!\.{1,2}/)[A-Za-z0-9_.-]+/issues/[1-9][0-9]*"
)
CLAIM_ID = re.compile(r"[a-z0-9][a-z0-9_-]*")
NAME = re.compile(r"[A-Za-z0-9]+([._-][A-Za-z0-9]+)*")
TEST_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TESTS_LINE = re.compile(r"Tests: \[(.*?)\]\((.*?)\)")
# The greedy result leaves the last code span as the test.
ITEM = re.compile(r"- (.*) `([^`]*)`")
ISSUE_SHAPE = "Issue: https://github.com/<owner>/<repo>/issues/<positive integer>"
TESTS_SHAPE = "Tests: [tests/<claim_id>/](../tests/<claim_id>/)"
ITEM_SHAPE = "- <result> `file::test_name`"


def _validate_name(name, kind):
    if NAME.fullmatch(name) is None:
        raise ValueError(f"invalid {kind} {name!r}")


def _resolve_local(root, reference, kind="regular file"):
    current = root
    for component in reference.split("/"):
        # Windows reports a file used as a directory as missing, so check it here.
        if current is not root and not stat.S_ISDIR(mode):
            raise ValueError("path requires a directory component")
        candidate = current / component
        mode = candidate.lstat().st_mode
        # A case-insensitive filesystem resolves wrong spellings; require the exact entry name.
        if component not in os.listdir(current):
            raise ValueError(f"path spelling does not match an existing entry: {component!r}")
        current = candidate
    predicate = {"directory": stat.S_ISDIR, "regular file": stat.S_ISREG}[kind]
    if not predicate(mode):
        raise ValueError(f"must resolve to a {kind}")
    return current


def _path_error(exc):
    if isinstance(exc, FileNotFoundError):
        return "path does not exist"
    return str(exc)


def _validate_path(path):
    for component in path.split("/"):
        _validate_name(component, "evidence-path segment")


def _tests_folder(root, label, link, claim_id):
    if not label.endswith("/"):
        raise ValueError("tests folder path must end with '/'")
    path = label[:-1]
    _validate_path(path)
    if link != "../" + label:
        raise ValueError("link target must be exactly '../' followed by the displayed path")
    _resolve_local(root, path, kind="directory")
    if claim_id is not None and path.split("/")[-1] != claim_id:
        raise ValueError(f"folder {path.split('/')[-1]!r} must be named after the claim ID {claim_id!r}")
    return path


def _defines(label, content, name):
    if label.endswith(".py"):
        pattern = rb"(?:^|(?<=[\r\n]))[ \t]*(?:async[ \t]+)?def[ \t]+" + name.encode() + rb"[ \t]*\("
    else:
        pattern = rb"(?<![A-Za-z0-9_])" + name.encode() + rb"(?![A-Za-z0-9_])"
    return re.search(pattern, content) is not None


def _text_error(text):
    if not text.strip(" \t"):
        return "must be nonblank"
    parts = text.split("`")
    prose_spans = parts[::2]
    code_spans = parts[1::2]
    if len(parts) % 2 == 0 or any(not code for code in code_spans):
        return "must use nonempty, paired single-backtick code spans"
    if any(re.fullmatch(r"[A-Za-z0-9 .,;:'\"()?!-]*", prose) is None for prose in prose_spans) or any(
            re.fullmatch(r"[ -~]+", code) is None for code in code_spans):
        return "must contain only ASCII letters, digits, spaces, allowed punctuation or printable ASCII code spans"
    if re.search(r"[A-Za-z0-9]", text) is None:
        return "must contain at least one ASCII letter or digit"
    for prose in prose_spans:
        if re.search(r"www\.", prose, re.IGNORECASE):
            return "must not contain www. outside code spans"
    return None


def _contract_errors(root, text, label, seen):
    # seen maps each claim ID to where it was first used, across all contract files.
    errors = []
    source_lines = text.split("\n")
    numbered_lines = enumerate(source_lines, start=1)
    nonblank_lines = [(number, line) for number, line in numbered_lines if line.strip(" \t")]
    missing_content_line = len(source_lines) if source_lines[-1] == "" else len(source_lines) + 1
    title_at, title = nonblank_lines[0] if nonblank_lines else (missing_content_line, "")
    if not title.startswith("# "):
        errors.append(f"{title_at}: expected '# <nonblank title>'")
    elif problem := _text_error(title[2:]):
        errors.append(f"{title_at}: title {problem}")
    # A missing title must not swallow an Issue line or claim in its place.
    body = nonblank_lines[0 if title.startswith(("Issue:", "## ")) else 1:]
    ids = set()
    claim_at = None
    needs_evidence = False
    # Lines still due directly under the current heading, and whether they are required.
    due, due_required = [], False
    claim_id = None
    folder = None

    def finish_claim():
        for name in due if due_required else []:
            shape = ISSUE_SHAPE if name == "Issue" else TESTS_SHAPE
            errors.append(f"{claim_at}: claim must be followed by {shape}")
        if needs_evidence:
            errors.append(f"{claim_at}: claim must have at least one evidence item")

    for number, line in body:
        if due and due[0] == "Issue":
            due.pop(0)
            if line.startswith("Issue:"):
                if not line.startswith("Issue: ") or ISSUE_URL.fullmatch(line[7:]) is None:
                    errors.append(f"{number}: expected {ISSUE_SHAPE}")
                continue
            if due_required:
                errors.append(f"{claim_at}: claim must be followed by {ISSUE_SHAPE}")
        if due and due[0] == "Tests":
            due.pop(0)
            if line.startswith("Tests:"):
                tests = TESTS_LINE.fullmatch(line)
                if tests is None:
                    errors.append(f"{number}: expected '{TESTS_SHAPE}'")
                    continue
                try:
                    folder = _tests_folder(root, *tests.groups(), claim_id)
                except (OSError, ValueError) as exc:
                    errors.append(f"{number}: tests folder: {_path_error(exc)}")
                continue
            if due_required:
                errors.append(f"{claim_at}: claim must be followed by {TESTS_SHAPE}")
        if line.startswith("## "):
            finish_claim()
            heading = re.fullmatch(r"## \[([^\]]*)\](?: (.*))?", line)
            claim_at, needs_evidence = number, heading is not None
            due, due_required, claim_id, folder = ["Issue", "Tests"], heading is not None, None, None
            if heading is None:
                errors.append(f"{number}: expected '## [id] <nonblank claim>'")
                continue
            identifier, claim = heading.groups(default="")
            if CLAIM_ID.fullmatch(identifier) is None:
                errors.append(f"{number}: claim ID must start with a lowercase ASCII letter or digit and contain only lowercase letters, digits, '_' or '-'")
            else:
                claim_id = identifier
                if identifier in ids:
                    errors.append(f"{number}: duplicate claim ID {identifier!r}")
                elif identifier in seen:
                    errors.append(f"{number}: duplicate claim ID {identifier!r}, first used at {seen[identifier]}")
                else:
                    seen[identifier] = f"{label}:{number}"
            ids.add(identifier)
            if problem := _text_error(claim):
                errors.append(f"{number}: claim {problem}")
        elif line.startswith("- "):
            needs_evidence = False
            if claim_at is None:
                errors.append(f"{number}: evidence must follow a claim heading")
            item = ITEM.fullmatch(line)
            if item is None:
                errors.append(f"{number}: expected '{ITEM_SHAPE}', ending with the test in a code span")
                continue
            result, test = item.groups()
            if problem := _text_error(result):
                errors.append(f"{number}: evidence result {problem}")
            path, separator, name = test.rpartition("::")
            if "::" in path:
                errors.append(f"{number}: test {test!r} includes a class; write `file::test_name` without it")
                continue
            if not separator:
                errors.append(f"{number}: test {test!r} must be written `file::test_name`, with the file relative to the claim's tests folder")
                continue
            if TEST_NAME.fullmatch(name) is None:
                errors.append(f"{number}: test name {name!r} must match `[A-Za-z_][A-Za-z0-9_]*`")
            try:
                _validate_path(path)
                if folder is None:
                    continue
                found = _resolve_local(root, f"{folder}/{path}")
            except (OSError, ValueError) as exc:
                errors.append(f"{number}: evidence reference: {_path_error(exc)}")
                continue
            try:
                content = found.read_bytes()
            except OSError as exc:
                errors.append(f"{number}: evidence reference: cannot read: {exc.strerror or exc}")
                continue
            if TEST_NAME.fullmatch(name) and not _defines(path, content, name):
                errors.append(f"{number}: test {name!r} is not defined in {folder}/{path}")
        else:
            errors.append(f"{number}: unexpected content; expected a claim heading or evidence item")
    finish_claim()
    if claim_at is None:
        errors.append(f"{missing_content_line}: contract must have at least one claim")
    return errors


def validate():
    contracts = []
    try:
        root = Path.cwd().resolve()
        if os.path.exists(root / "contracts"):
            directory = _resolve_local(root, "contracts", kind="directory")
            contracts = sorted(directory.iterdir(), key=lambda path: path.name)
    except (OSError, ValueError) as exc:
        return [f"cannot discover contracts/: {_path_error(exc)}"]
    if not contracts:
        return ["no contracts found in contracts/"]
    errors = []
    seen = {}
    for entry in contracts:
        label = f"contracts/{entry.name}"
        if not entry.name.endswith(".md"):
            errors.append(f"{label}: unexpected entry; expected a direct *.md regular file")
            continue
        # No continue: a bad filename must not hide the contract's other errors.
        try:
            _validate_name(entry.name, "contract filename")
        except ValueError as exc:
            errors.append(f"{label}: {exc}")
        try:
            path = _resolve_local(root, label)
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: {_path_error(exc)}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, ValueError) as exc:
            errors.append(f"{label}: cannot read Markdown: {exc}")
            continue
        errors.extend(f"{label}:{error}" for error in _contract_errors(root, text, label, seen))
    return errors
