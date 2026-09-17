"""
mirror_constants.py -- write the orrery's exported numbers into
data/objects_config.json, and name every link it cannot serve yet.

WHAT THIS IS

    The page reads data/objects_config.json at boot. Until now the
    numbers in that file were typed by hand from the orrery's store, and
    a live check (Store drift) reported when one fell out of step. This
    tool writes them instead, from data/constants_export.json, which the
    orrery generates from constants_new.py and the gallery pulls at a
    recorded SHA.

    Tony's ruling, 2026-09-17: "a tool reading and writing is not
    creating a second store, it is just transmitting." The numbers stay
    in the config because that is the file the page reads; they are put
    there by this tool, never by hand, and a hand edit fails the next
    maintenance run.

RUN COMMAND

    python tools/mirror_constants.py              report only, writes nothing
    python tools/mirror_constants.py --write      writes the config
    python tools/mirror_constants.py --write --accept-relabel NAME
                                                 writes a named relabel too

    Open it in VS Code and click Run for the report. The maintenance run
    calls it with --write as a generator, after the pull.

WHAT IT WRITES, PER LINK

    SERVED     the export has the row: value, unit and figures are
               written into the slot the link governs. Nothing else on
               the entry is touched -- not the source, not the
               description, not the presentation.
    FALLBACK   the export names the row in not_exported (no unit line
               yet, or a retired token). The hand-typed value stays, and
               the link is named with the export's reason. Store drift
               still watches these.
    ABSENT     the link points outside the store (the four planet_poles
               entries and the galactic tide default). Named, untouched.

IT EDITS IN PLACE, AND WHY

    The config is hand-formatted: some entries sit on one line, some
    across several, and the file carries long sources and descriptions a
    person maintains. Rewriting it with a JSON dump would reformat all
    900 lines and bury three changed numbers in a diff nobody can read.
    So this tool parses the file with its own scanner, which records
    where each value sits, and replaces only those characters. Every
    other byte, including the spacing, survives.

IT CONVERTS NOTHING, AND TELLS TWO KINDS OF CHANGE APART

    A change of SPELLING is ordinary: the config writes R_earth, nPa,
    nT, per_nT where the export's tokens are r_earth, npa, nt, per_nt,
    and the page moved to the token spelling in the same build. Those
    are written without ceremony.

    When the token is a different token, the mirror looks at the NUMBER
    to decide which of two things is happening (Tony's decision of
    2026-09-17):

    TOKEN CHANGE, a relabel. The number is the same; only the name of
    the unit moved. The four magnetosphere coefficients are this case:
    the store retires "dimensionless" and gives them a token that names
    what they are, and 0.58 stays 0.58. The page asserts the old name by
    hand in four places, so the relabel and those edits belong in one
    commit. The mirror refuses it by default and writes it when the run
    names the link with --accept-relabel.

    UNIT CONFLICT, a conversion. The number is different too. The Sun's
    core sits in the config as 0.2 R_sun, and the store holds CORE_AU in
    AU; mirroring it blindly would write 0.00093 AU into a slot the
    renderer draws in solar radii, and the shell would silently
    collapse. This is refused and --accept-relabel does not reach it. No
    conversion is done here, because a factor typed into this file would
    be a second copy of the store's own. A person decides: take the
    store's unit at that site, or add the row the page draws.

    Refusal is per link. Every other link is still written, so one
    blocked transmission does not hold back sixteen good ones, and the
    run exits non-zero so the maintenance run shows it.

A LINK TO THE ROW THAT DEFINES ITS OWN UNIT IS EXACTLY ONE

    Earth's crust is 1.0 R_earth and points at
    EARTH_EQUATORIAL_RADIUS_KM, which is the row the token table names
    as the definition of one r_earth. There is no number to transmit:
    copying 6378.1366 into that slot would draw the crust at 6,378 Earth
    radii. The value is 1, exactly, by definition.

    So when a link points at a token's defining constant and its slot is
    measured in that token, the mirror writes 1 with figures "exact".
    The rule reads the token table the export already carries, so no
    factor is typed here either, and the 1.0 becomes a number with a
    source rather than an assertion. (Fable's proposal, Tony's decision,
    2026-09-17.)

Role: devtool
Domain: gallery

Module created: September 17, 2026 with Anthropic's Claude Opus 5
(L-322, the gallery half: piece 1 of
documentation/BUILD_MANIFEST_L322_gallery_half_20260917.md).
"""

import json
import os
import sys

CONFIG = os.path.join("data", "objects_config.json")
EXPORT = os.path.join("data", "constants_export.json")
STORE_FILE = "constants_new.py"
FIELDS = ("value", "unit", "figures")
REFUSALS = ("UNIT CONFLICT", "TOKEN CHANGE", "NO SLOT")


# ------------------------------------------------------------------
# A JSON scanner that remembers where every value sits.
# ------------------------------------------------------------------

class Node(object):
    """One parsed value: its Python form, and its span in the text."""

    __slots__ = ("value", "start", "end", "members", "items")

    def __init__(self, value, start, end):
        self.value = value
        self.start = start
        self.end = end
        self.members = {}      # key -> (Node, key_start)
        self.items = []        # [Node]


class Scanner(object):
    WHITESPACE = " \t\r\n"

    def __init__(self, text):
        self.text = text
        self.index = 0

    def parse(self):
        node = self.value()
        self.skip()
        if self.index != len(self.text):
            raise ValueError("trailing text at %d" % self.index)
        return node

    def skip(self):
        while (self.index < len(self.text)
               and self.text[self.index] in self.WHITESPACE):
            self.index += 1

    def expect(self, char):
        if self.text[self.index] != char:
            raise ValueError("expected %r at %d, found %r"
                             % (char, self.index, self.text[self.index]))
        self.index += 1

    def value(self):
        self.skip()
        start = self.index
        char = self.text[start]
        if char == "{":
            return self.obj(start)
        if char == "[":
            return self.arr(start)
        if char == '"':
            text = self.string()
            return Node(text, start, self.index)
        for word, parsed in (("true", True), ("false", False),
                             ("null", None)):
            if self.text.startswith(word, start):
                self.index = start + len(word)
                return Node(parsed, start, self.index)
        return self.number(start)

    def obj(self, start):
        self.expect("{")
        node = Node({}, start, None)
        self.skip()
        if self.text[self.index] == "}":
            self.index += 1
            node.end = self.index
            return node
        while True:
            self.skip()
            key_start = self.index
            key = self.string()
            self.skip()
            self.expect(":")
            child = self.value()
            node.value[key] = child.value
            node.members[key] = (child, key_start)
            self.skip()
            if self.text[self.index] == ",":
                self.index += 1
                continue
            self.expect("}")
            node.end = self.index
            return node

    def arr(self, start):
        self.expect("[")
        node = Node([], start, None)
        self.skip()
        if self.text[self.index] == "]":
            self.index += 1
            node.end = self.index
            return node
        while True:
            child = self.value()
            node.value.append(child.value)
            node.items.append(child)
            self.skip()
            if self.text[self.index] == ",":
                self.index += 1
                continue
            self.expect("]")
            node.end = self.index
            return node

    def string(self):
        self.expect('"')
        out = []
        while True:
            char = self.text[self.index]
            if char == "\\":
                pair = self.text[self.index:self.index + 2]
                self.index += 2
                if pair[1] == "u":
                    out.append(chr(int(self.text[self.index:self.index + 4],
                                       16)))
                    self.index += 4
                else:
                    out.append({"n": "\n", "t": "\t", "r": "\r", "b": "\b",
                                "f": "\f", '"': '"', "\\": "\\",
                                "/": "/"}[pair[1]])
                continue
            if char == '"':
                self.index += 1
                return "".join(out)
            out.append(char)
            self.index += 1

    def number(self, start):
        index = start
        if self.text[index] in "+-":
            index += 1
        while index < len(self.text) and self.text[index] in "0123456789.eE+-":
            index += 1
        raw = self.text[start:index]
        self.index = index
        try:
            parsed = int(raw)
        except ValueError:
            parsed = float(raw)
        return Node(parsed, start, index)


def parse_with_spans(text):
    """(Node, python value). Raises ValueError on anything it cannot read."""
    node = Scanner(text).parse()
    if node.value != json.loads(text):
        raise ValueError("the scanner and json disagree about this file")
    return node


# ------------------------------------------------------------------
# Finding the links and their value slots.
# ------------------------------------------------------------------

def collect_links(node, path=""):
    """[(path, entry node)] for every object carrying an orrery_constant.

    The same walk gallery_maintenance_run.py's collect_pointers makes,
    over the span-carrying tree.
    """
    found = []
    if isinstance(node.value, dict):
        if "orrery_constant" in node.value:
            found.append((path, node))
        for key, (child, _key_start) in node.members.items():
            found.extend(collect_links(child, path + "/" + key))
    elif isinstance(node.value, list):
        for index, child in enumerate(node.items):
            found.extend(collect_links(child, path + "/%d" % index))
    return found


def value_slot(entry):
    """The node holding this link's number, or None.

    The entry itself when it carries a value; otherwise the sub-entry
    that does (radius, standoff, and so on). This is the rule
    config_value() already applies in the maintenance runner, so the
    mirror and Store drift always mean the same slot.
    """
    if "value" in entry.value:
        return entry
    for _key, (child, _start) in entry.members.items():
        if isinstance(child.value, dict) and "value" in child.value:
            return child
    return None


def store_name(entry):
    pointer = entry.value["orrery_constant"]
    file_part, _, name = pointer.partition("::")
    return file_part, name


# ------------------------------------------------------------------
# The plan: what would change, and what is refused.
# ------------------------------------------------------------------

class Change(object):
    __slots__ = ("field", "old", "new", "start", "end", "insert_after")

    def __init__(self, field, old, new, start, end, insert_after=False):
        self.field = field
        self.old = old
        self.new = new
        self.start = start
        self.end = end
        self.insert_after = insert_after


class Link(object):
    __slots__ = ("path", "name", "verdict", "detail", "changes")

    def __init__(self, path, name, verdict, detail):
        self.path = path
        self.name = name
        self.verdict = verdict
        self.detail = detail
        self.changes = []


def render(value):
    """A JSON literal, the way this file already writes numbers."""
    return json.dumps(value, ensure_ascii=True)


def spelling_change(entry, export):
    """A unit written in another case than the token table's, or None.

    A link the export cannot serve yet still holds a unit in the config,
    and the page reads ONE vocabulary. Without this, switching the page
    to the store's tokens would drop every feature whose row has not
    been walked yet -- measured: every Sun shell. Normalising the
    SPELLING is not transmitting a value and says nothing about which
    unit the row will declare; if the store later declares a different
    unit, that is a UNIT CONFLICT exactly as it would have been.
    """
    slot = value_slot(entry)
    if slot is None:
        return None
    held = slot.value.get("unit")
    if not isinstance(held, str):
        return None
    for token in export.get("tokens", {}):
        if held != token and held.lower() == token.lower():
            node, _key_start = slot.members["unit"]
            return Change("unit", held, token, node.start, node.end)
    return None


def defined_token(name, export):
    """The token this store row defines, or None.

    The export's token table names, for r_earth and r_sun and au, the
    row whose value is ONE of that token. A link pointing at such a row,
    in a slot measured in that token, transmits exactly 1.
    """
    for token, spec in export.get("tokens", {}).items():
        if spec.get("defining_constant") == name:
            return token
    return None


def same_token(held, token):
    return str(held or "").lower() == str(token or "").lower()


def same_number(held, exported, figures):
    """Is the config's number the export's, allowing for rounding?

    The export rounds to the row's declared figures; the config may hold
    the unrounded hand copy. Without this allowance the first
    "# Figures:" line on a served row would turn a routine transmission
    into a false conflict.
    """
    if not isinstance(held, (int, float)) or isinstance(held, bool):
        return False
    if not isinstance(exported, (int, float)) or isinstance(exported, bool):
        return False
    if held == exported:
        return True
    if isinstance(figures, int):
        return float("%.*g" % (figures, held)) == exported
    return False


def plan(text, export, accept=()):
    """(links, failures). Refused links are named; the rest still write."""
    root = parse_with_spans(text)
    rows = export.get("rows", {})
    skipped = export.get("not_exported", {})
    links = []
    failures = []

    for path, entry in collect_links(root):
        file_part, name = store_name(entry)
        if file_part != STORE_FILE or name not in rows:
            if file_part != STORE_FILE or name not in skipped:
                link = Link(path, name, "ABSENT",
                            "points outside %s" % STORE_FILE
                            if file_part != STORE_FILE
                            else "not a row in %s" % STORE_FILE)
            else:
                link = Link(path, name, "FALLBACK", skipped[name])
            spell = spelling_change(entry, export)
            if spell is not None:
                link.changes.append(spell)
                link.detail += ("; unit spelling normalised to %s"
                                % render(spell.new))
            links.append(link)
            continue

        row = rows[name]
        link = Link(path, name, "SERVED", "")
        slot = value_slot(entry)
        if slot is None:
            link.verdict = "NO SLOT"
            link.detail = ("the export serves this row, but the entry has "
                           "no value to write it into")
            failures.append(link)
            links.append(link)
            continue

        held_unit = slot.value.get("unit")
        held_value = slot.value.get("value")
        wanted = dict((field, row[field]) for field in FIELDS)

        defines = defined_token(name, export)
        if defines is not None and same_token(held_unit, defines):
            # The row that defines this slot's own unit: one of it, exactly.
            link.detail = ("1 %s by definition: this row is what the token "
                           "table calls one %s" % (defines, defines))
            wanted = {"value": 1.0, "unit": defines, "figures": "exact"}
        elif held_unit is not None and not same_token(held_unit, row["unit"]):
            if same_number(held_value, row["value"], row["figures"]):
                link.verdict = "TOKEN CHANGE"
                link.detail = ("the number is unchanged (%s); this is a "
                               "relabel from %s to %s. Move the page's "
                               "asserts for this feature in the same "
                               "commit, and run with --accept-relabel %s"
                               % (render(row["value"]), render(held_unit),
                                  render(row["unit"]), name))
                if name not in accept:
                    failures.append(link)
                    links.append(link)
                    continue
                link.verdict = "SERVED"
                link.detail = ("relabel accepted: %s to %s, number "
                               "unchanged" % (render(held_unit),
                                              render(row["unit"])))
            else:
                link.verdict = "UNIT CONFLICT"
                link.detail = ("the config holds %s %s and the store "
                               "declares %s %s. The number changes too, so "
                               "this is a conversion, and nothing here "
                               "converts. Either the page takes the store's "
                               "unit at this site, or the store gains the "
                               "row the page draws"
                               % (render(held_value), render(held_unit),
                                  render(row["value"]), render(row["unit"])))
                failures.append(link)
                links.append(link)
                continue

        for field in FIELDS:
            new = wanted[field]
            if field in slot.value:
                child, _key_start = slot.members[field]
                if child.value != new:
                    link.changes.append(Change(field, child.value, new,
                                               child.start, child.end))
            elif field == "figures" or new is not None:
                anchor = slot.members.get("unit") or slot.members.get("value")
                if anchor is None:
                    continue
                node, _key_start = anchor
                link.changes.append(Change(field, None, new, node.end,
                                           node.end, insert_after=True))
        links.append(link)

    return links, failures


def member_separator(text, slot_start):
    """How this object separates its members: same line, or a new one."""
    line_end = text.find("\n", slot_start)
    close = text.find("}", slot_start)
    if line_end == -1 or (close != -1 and close < line_end):
        return ", "
    line_start = text.rfind("\n", 0, slot_start) + 1
    indent = ""
    probe = text.find("\n", slot_start) + 1
    while probe < len(text) and text[probe] in " \t":
        indent += text[probe]
        probe += 1
    if not indent:
        indent = text[line_start:slot_start].split('"')[0] + "  "
    return ",\n" + indent


def apply_changes(text, links):
    """The config with every change made, bottom-up so offsets hold."""
    edits = []
    for link in links:
        if link.verdict in REFUSALS:
            continue
        for change in link.changes:
            edits.append((change, link))
    edits.sort(key=lambda pair: pair[0].start, reverse=True)
    for change, link in edits:
        if change.insert_after:
            separator = member_separator(text, change.start)
            piece = '%s"%s": %s' % (separator, change.field,
                                    render(change.new))
            text = text[:change.start] + piece + text[change.start:]
        else:
            text = (text[:change.start] + render(change.new)
                    + text[change.end:])
    return text


# ------------------------------------------------------------------
# Output
# ------------------------------------------------------------------

def report(links, failures, writing):
    served = [l for l in links if l.verdict == "SERVED"]
    changed = [l for l in served if l.changes]
    exact = [l for l in served if l.detail.startswith("1 ")]
    fallback = [l for l in links if l.verdict == "FALLBACK"]
    absent = [l for l in links if l.verdict == "ABSENT"]

    print("=" * 70)
    print("  CONFIG MIRROR -- %s -> %s"
          % (EXPORT.replace(os.sep, "/"), CONFIG.replace(os.sep, "/")))
    print("=" * 70)
    print("")
    print("%d link(s): %d served, %d fallback, %d outside the store."
          % (len(links), len(served), len(fallback), len(absent)))
    print("")

    if failures:
        print("REFUSED (%d) -- these links are left as they are; every "
              "other served link is still written:" % len(failures))
        for link in failures:
            print("  %-14s %s" % (link.verdict, link.name))
            print("                 %s" % link.path)
            print("                 %s" % link.detail)
        print("")

    if exact:
        print("DEFINITION, %d link(s) transmitted as exactly 1:" % len(exact))
        for link in exact:
            print("  %-34s %s" % (link.name, link.detail))
        print("")

    print("SERVED, %d with something to write:" % len(changed))
    for link in changed:
        for change in link.changes:
            print("  %-34s %-8s %s -> %s"
                  % (link.name, change.field,
                     "(absent)" if change.insert_after else render(change.old),
                     render(change.new)))
    if not changed:
        print("  every served link already holds the export's numbers")
    print("")

    print("FALLBACK, %d link(s) the export cannot serve yet:" % len(fallback))
    for link in sorted(fallback, key=lambda l: l.name):
        print("  %-34s %s" % (link.name, link.detail[:60]))
    print("")
    print("OUTSIDE THE STORE, %d link(s):" % len(absent))
    for link in sorted(absent, key=lambda l: l.name):
        print("  %-34s %s" % (link.name, link.detail))
    print("")

    total = sum(len(link.changes) for link in changed)
    if failures:
        kinds = {}
        for link in failures:
            kinds[link.verdict] = kinds.get(link.verdict, 0) + 1
        print("Refused %d link(s): %s. %s %d field(s) across %d other "
              "served link(s)."
              % (len(failures),
                 ", ".join("%d %s" % (n, k) for k, n in sorted(kinds.items())),
                 "Would write" if not writing else "Wrote",
                 total, len(changed)))
    elif not writing:
        print("Report only, nothing written: %d field(s) would change "
              "across %d served link(s); %d fallback, %d outside the store."
              % (total, len(changed), len(fallback), len(absent)))
    elif total:
        print("Wrote %d field(s) across %d served link(s); %d fallback "
              "left alone, %d outside the store."
              % (total, len(changed), len(fallback), len(absent)))
    else:
        print("Unchanged: all %d served link(s) already hold the export's "
              "numbers; %d fallback, %d outside the store."
              % (len(served), len(fallback), len(absent)))


def run(root, write, accept=()):
    config_path = os.path.join(root, CONFIG)
    export_path = os.path.join(root, EXPORT)
    for path in (config_path, export_path):
        if not os.path.exists(path):
            print("ERROR: %s does not exist. Run the maintenance run's "
                  "pull first." % path)
            return 1
    with open(config_path, "r", encoding="utf-8") as handle:
        text = handle.read()
    with open(export_path, "r", encoding="utf-8") as handle:
        export = json.load(handle)

    try:
        links, failures = plan(text, export, accept)
    except ValueError as exc:
        print("ERROR: %s could not be read: %s" % (CONFIG, exc))
        return 1

    report(links, failures, write)
    if failures:
        return 1
    if not write:
        return 0

    changed = apply_changes(text, links)
    if changed == text:
        return 0
    try:
        parse_with_spans(changed)
    except ValueError as exc:
        print("ERROR: the edited config would not parse (%s). Nothing "
              "written." % exc)
        return 1
    with open(config_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(changed)
    return 0


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    write = False
    accept = []
    expecting = False
    for argument in argv[1:]:
        if expecting:
            accept.append(argument)
            expecting = False
        elif argument == "--write":
            write = True
        elif argument == "--report":
            pass
        elif argument == "--accept-relabel":
            expecting = True
        elif argument.startswith("--accept-relabel="):
            accept.append(argument.split("=", 1)[1])
        else:
            print("ERROR: unknown option %s. Use --write, "
                  "--accept-relabel NAME, or nothing for a report."
                  % argument)
            return 1
    if expecting:
        print("ERROR: --accept-relabel needs the name of a store row.")
        return 1
    return run(root, write, tuple(accept))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
