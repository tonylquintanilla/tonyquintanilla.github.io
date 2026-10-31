"""
test_pull_failures.py -- a pull that cannot fetch fails by name, writes
nothing, and the mirror after it does not run; and proof that this check
can fail.

WHY THIS EXISTS

    Until 2026-10-15 each of the three pulls printed N-A and exited 0
    when it could not reach the orrery. The maintenance run read that as
    PASS "no change", and the Config mirror then wrote
    data/objects_config.json from the old export: in a sandbox that could
    not reach GitHub, 36 fields written backwards (L-388). The pulls now
    fail by name, and the Daily Run stops before the cache builder when
    one does (L-446, Tony's option A of 2026-10-15). A network that is
    down is rare on Tony's machine, so this is the check that exercises
    those branches every day instead of only on that day.

RUN COMMAND

    Open this file in VS Code and click Run. It takes no arguments.
        python tools/test_pull_failures.py
    The gallery maintenance run runs it as the gating checker "Pull
    failures"; its last line starts "PULL FAILURES:".

WHAT IT DOES (it edits nothing in the repository)

    It copies the three pulls and the data they read into a throwaway
    folder, and runs each pull there with its network replaced by a
    stand-in that fails in one of three ways: the orrery's HEAD cannot be
    read, HEAD's answer is unreadable, or the file cannot be fetched at
    HEAD. Each time the pull must exit 1, print one line starting "FAIL:"
    that names the address it tried, and leave every file in the folder
    byte for byte as it was.

    Then it runs gallery_maintenance_run.py's run_generators with the
    tools replaced by stand-ins: the constants pull fails and the objects
    pull passes. The Config mirror must not run and its row must be red,
    naming the pull; the Objects mirror must run; --pull's summary must
    exit 1 and name the failed rows on its "=== PULLS:" line; and with
    every pull passing it must exit 0.

PROOF THAT IT CAN FAIL

    Before the real checks it plants three faults, each of which must be
    caught: a pull that prints N-A and exits 0 (the old behaviour), a
    pull that writes a file before it fails, and a run whose mirror is
    no longer held back after its pull failed.

THE RUN'S TOKEN (L-485, October 31, 2026)

    On GitHub's computers the pulls ask GitHub's REST interface with the
    run's GITHUB_TOKEN, since an unsigned question is limited by an
    address GitHub's runners share (pull_constants_export.py, SIGNED IN
    ON GITHUB'S COMPUTERS). It checks request_headers: the token goes to
    api.github.com when the environment carries one, never to
    raw.githubusercontent.com, and no header is sent without one. Two
    more planted faults: a pull that never sends it, and one that sends
    it to every address.

Role: devtool
Domain: gallery

Module created: October 15, 2026 with Anthropic's Claude Opus 5.5 (L-446,
with L-388).
Module updated: October 31, 2026 with Anthropic's Claude Opus 5.5 (L-485,
the gallery half: the run's token, and two planted faults.)
"""

import contextlib
import hashlib
import importlib.util
import io
import os
import shutil
import stat
import sys
import tempfile

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)

PULLS = ["pull_constants_export", "pull_objects_export", "pull_drawings"]
DATA = [os.path.join("data", "objects_config.json"),
        os.path.join("data", "constants_export.json"),
        os.path.join("data", "constants_export.sha"),
        os.path.join("data", "objects_export.json"),
        os.path.join("data", "objects_export.sha"),
        os.path.join("data", "drawings")]

HEAD_JSON = b'{"sha": "0123456789abcdef0123456789abcdef01234567"}'


# ---- stand-ins for the network ---------------------------------------

def no_head(url):
    return None, b"", "planted: the network is down"


def bad_head(url):
    if "api.github.com" in url:
        return 200, b"this is not JSON", None
    return no_head(url)


def no_file(url):
    if "api.github.com" in url:
        return 200, HEAD_JSON, None
    return 404, b"", None


WAYS = [("HEAD cannot be read", no_head),
        ("HEAD's answer is unreadable", bad_head),
        ("the file cannot be fetched at HEAD", no_file)]


# ---- the throwaway folder --------------------------------------------

def make_tree():
    """A throwaway copy of the pulls and the data they read."""
    tree = tempfile.mkdtemp(prefix="test_pull_failures_")
    os.makedirs(os.path.join(tree, "tools"))
    for name in PULLS:
        shutil.copyfile(os.path.join(TOOLS, name + ".py"),
                        os.path.join(tree, "tools", name + ".py"))
    os.makedirs(os.path.join(tree, "data"))
    # Plain file copies only: copytree and copy2 carry the read-only mark
    # OneDrive sets on the folders under data/, and Windows then refuses
    # to delete the copy (gallery-cache-builder, Never shutil.rmtree).
    for rel in DATA:
        src = os.path.join(ROOT, rel)
        if os.path.isdir(src):
            for folder, _dirs, files in os.walk(src):
                into = os.path.join(tree, rel, os.path.relpath(folder, src))
                os.makedirs(into, exist_ok=True)
                for name in files:
                    shutil.copyfile(os.path.join(folder, name),
                                    os.path.join(into, name))
        elif os.path.exists(src):
            shutil.copyfile(src, os.path.join(tree, rel))
    return tree


def remove_tree(tree):
    """Remove the throwaway folder, adding the write bit where Windows
    refuses, and say so if anything is left behind."""
    def again(function, path, _info):
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        function(path)
    if sys.version_info >= (3, 12):
        shutil.rmtree(tree, onexc=again)
    else:
        shutil.rmtree(tree, onerror=again)
    if os.path.exists(tree):
        print("note: the throwaway folder %s could not be removed" % tree)


def fingerprint(tree):
    """{relative path: md5} for every file under the tree's data/."""
    prints = {}
    base = os.path.join(tree, "data")
    for folder, _dirs, files in os.walk(base):
        for name in files:
            path = os.path.join(folder, name)
            with open(path, "rb") as handle:
                prints[os.path.relpath(path, tree)] = \
                    hashlib.md5(handle.read()).hexdigest()
    return prints


def load(tree, name):
    """Import tools/<name>.py from the tree, under a name of its own."""
    tools = os.path.join(tree, "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    sys.modules.pop("pull_constants_export", None)
    spec = importlib.util.spec_from_file_location(
        "planted_" + name, os.path.join(tools, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_main(main):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main()
    return code, out.getvalue()


# ---- the checks --------------------------------------------------------

def pull_problems(tree, main, way):
    """Why this run of a pull is wrong, as a list; empty when right."""
    before = fingerprint(tree)
    try:
        code, text = run_main(main)
    except Exception as exc:              # a pull must not crash
        return ["it raised %s: %s" % (type(exc).__name__, exc)]
    problems = []
    if code != 1:
        problems.append("it exited %r, not 1" % code)
    fails = [line for line in text.splitlines() if line.startswith("FAIL:")]
    if not fails:
        problems.append("it printed no line starting FAIL: (it printed %r)"
                        % text.strip()[:80])
    elif "https://" not in fails[0]:
        problems.append("its FAIL line names no address: %r" % fails[0][:80])
    after = fingerprint(tree)
    moved = sorted(path for path in set(before) | set(after)
                   if before.get(path) != after.get(path))
    if moved:
        problems.append("it changed %s" % ", ".join(moved))
    return problems


def check_pulls(tree, results):
    for name in PULLS:
        module = load(tree, name)
        for way, stub in WAYS:
            module.fetch = stub
            problems = pull_problems(tree, module.main, stub)
            results.append(("%s, %s" % (name, way), problems))


def header_problems(headers_of):
    """L-485: the run's token goes to GitHub's REST interface when the
    environment carries it, and nowhere else; with no token, no header.
    headers_of(url, environ) is pull_constants_export.request_headers."""
    api = "https://api.github.com/repos/o/r/commits/main"
    raw = "https://raw.githubusercontent.com/o/r/0123/data/x.json"
    problems = []
    got = headers_of(api, {"GITHUB_TOKEN": "planted-token"})
    if got.get("Authorization") != "Bearer planted-token":
        problems.append("the interface was asked without the run's token: %r"
                        % got.get("Authorization"))
    if "Authorization" in headers_of(raw, {"GITHUB_TOKEN": "planted-token"}):
        problems.append("the token was sent to raw.githubusercontent.com")
    if "Authorization" in headers_of(api, {}):
        problems.append("a token header was sent with no GITHUB_TOKEN set")
    return problems


def fake_tool(fail):
    """A run_tool stand-in. Records what ran; fails the labels' scripts
    named in `fail`."""
    ran = []

    def run_tool(root, runner, argv_tail, cwd):
        script = argv_tail[0]
        ran.append(script)
        if script in fail:
            return ("FAIL", 0.0, "FAIL: planted, could not fetch")
        return ("PASS", 0.0, "planted pass")
    return run_tool, ran


def runner_problems(gmr, hold_back=True):
    """Why the maintenance run's handling of a failed pull is wrong."""
    problems = []
    saved = gmr.run_tool, gmr.FED_BY
    if not hold_back:
        gmr.FED_BY = {}
    try:
        tool, ran = fake_tool({"tools/pull_constants_export.py"})
        gmr.run_tool = tool
        results = []
        with contextlib.redirect_stdout(io.StringIO()):
            gmr.run_generators(ROOT, results, only=gmr.PULL_ROWS)
        if "tools/mirror_constants.py" in ran:
            problems.append("the Config mirror ran after its pull failed")
        rows = dict((row[1], row) for row in results)
        mirror = rows.get("Config mirror")
        if mirror is None:
            problems.append("no Config mirror row was printed")
        elif mirror[0] != "FAIL" or "Constants export pull" not in mirror[3]:
            problems.append("the Config mirror row is %s %r, not FAIL naming "
                            "the pull" % (mirror[0], mirror[3]))
        if "tools/mirror_objects.py" not in ran:
            problems.append("the Objects mirror did not run, though its "
                            "pull passed")
        if "module_atlas.py" in ran:
            problems.append("--pull ran the Module atlas")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = gmr.summarize_pulls(results)
        last = out.getvalue().strip().splitlines()[-1]
        if code != 1:
            problems.append("--pull's summary exited %r with a failed pull"
                            % code)
        if not (last.startswith("=== PULLS:")
                and "Constants export pull" in last
                and "Config mirror" in last):
            problems.append("--pull's last line does not name both failed "
                            "rows: %r" % last)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            gen_code = gmr.summarize(results)
        if gen_code != 1 or "generator(s) FAILED" not in out.getvalue():
            problems.append("the offline summary does not fail and name a "
                            "failed generator")

        tool, ran = fake_tool(set())
        gmr.run_tool = tool
        results = []
        with contextlib.redirect_stdout(io.StringIO()):
            gmr.run_generators(ROOT, results, only=gmr.PULL_ROWS)
            code = gmr.summarize_pulls(results)
        if code != 0 or len(results) != len(gmr.PULL_ROWS):
            problems.append("with every pull passing, --pull exited %r over "
                            "%d rows" % (code, len(results)))
    finally:
        gmr.run_tool, gmr.FED_BY = saved
    return problems


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "planted_gallery_maintenance_run",
        os.path.join(ROOT, "gallery_maintenance_run.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---- planted faults ------------------------------------------------------

def planted(tree, gmr):
    """Each planted fault must be caught. Returns (label, caught)."""
    out = []

    def old_pull():
        print("N-A: could not read the orrery HEAD SHA (planted). The "
              "previous pull is left as it is.")
        return 0
    out.append(("a pull that prints N-A and exits 0",
                bool(pull_problems(tree, old_pull, no_head))))

    def writes_then_fails():
        path = os.path.join(tree, "data", "constants_export.sha")
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write("planted\n")
        print("FAIL: could not read https://planted (planted)")
        return 1
    saved = {}
    path = os.path.join(tree, "data", "constants_export.sha")
    if os.path.exists(path):
        with open(path, "rb") as handle:
            saved[path] = handle.read()
    out.append(("a pull that writes a file before it fails",
                bool(pull_problems(tree, writes_then_fails, no_head))))
    for p, data in saved.items():
        with open(p, "wb") as handle:
            handle.write(data)
    if not saved and os.path.exists(path):
        os.remove(path)

    out.append(("a mirror no longer held back after its pull failed",
                bool(runner_problems(gmr, hold_back=False))))

    # L-485: the token never sent, and the token sent everywhere.
    def never(url, environ=None):
        return {"User-Agent": "planted"}

    def everywhere(url, environ=None):
        env = {} if environ is None else environ
        h = {"User-Agent": "planted"}
        if env.get("GITHUB_TOKEN"):
            h["Authorization"] = "Bearer " + env["GITHUB_TOKEN"]
        return h
    out.append(("a pull that never sends the run's token",
                bool(header_problems(never))))
    out.append(("a pull that sends the token to every address",
                bool(header_problems(everywhere))))
    return out


def main():
    print("=" * 70)
    print("PULL FAILURES -- each pull with no network, and the run after it")
    print("=" * 70)
    tree = make_tree()
    failures = 0
    try:
        gmr = load_runner()
        print("Planted faults, each of which must be caught:")
        for label, caught in planted(tree, gmr):
            print("  %s   %s" % ("ok  " if caught else "FAIL", label))
            if not caught:
                failures += 1
        print("")
        results = []
        check_pulls(tree, results)
        results.append(("the maintenance run after a failed pull",
                        runner_problems(gmr)))
        results.append(("the run's token, to GitHub's interface only",
                        header_problems(
                            load(tree, "pull_constants_export").request_headers)))
        for label, problems in results:
            print("  %s   %s" % ("ok  " if not problems else "FAIL", label))
            for problem in problems:
                print("         %s" % problem)
            if problems:
                failures += 1
        total = len(results) + 5
    finally:
        remove_tree(tree)
    print("")
    if failures:
        print("PULL FAILURES: %d of %d checks FAILED" % (failures, total))
        return 1
    print("PULL FAILURES: all %d checks passed (3 pulls x 3 ways to fail, "
          "the run after a failed pull, the run's token to GitHub's "
          "interface only, and 5 planted faults caught)"
          % total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
