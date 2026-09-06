"""
patch_L288_1_studio_live_card.py -- Gallery Studio creates INTERACTIVE
cards (a card that opens a live scene, no figure file). Three files in
tools/, all-or-nothing.

Tony's ruling, 2026-09-06: Studio is where exhibits are authored, so
Studio authors these too; the card lands in STORAGE and moving it is the
editor's job. No still picture: the lobby settled on the phone that a
live card is a placard with an Interactive tag.

What changes:
- tools/json_converter.py gains live_scene_urls() (MOVED here from the
  editor so both tools read one list -- one pipeline) and
  add_live_card(): writes a schema-v2 card with `live` set and no file
  slots into storage; refuses if the config is not v2, if the title is
  empty, or if another card already opens that scene.
- tools/gallery_studio.py gains a "New Interactive Card..." button and a
  dialog: scene URL picker (read from interactive.html), title, placard
  sentence, sources one per line. Create -> add_live_card -> the card is
  in storage; a message says so and names it.
- tools/gallery_editor.py imports live_scene_urls from json_converter
  instead of defining its own copy.

RUN: save at the GALLERY repo root (the script edits tools/*.py by
relative path), open in VS Code, Run. Then run Studio, open the dialog,
create a test card, see it in the editor's storage room; commit, push.

Guards on the LF-normalized md5 of all three files at gallery fc8d9fb3
and writes NOTHING unless all three match and every anchor is found.
CRLF working copies pass and are written back as CRLF per file. Refuses
a second run. All inserted text is ASCII. No .bak.

Pre-tested here: py_compile on all three; headless (xvfb) launch of
Studio and the editor on throwaway copies; add_live_card exercised on a
copy of the real metadata (create, duplicate refusal, non-v2 refusal).

Written September 6, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery fc8d9fb3ecb2 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-288. Archive to documentation/ once run.
"""
import hashlib, os, sys

FILES = {
    "tools/json_converter.py": "940f64332a8e7cd6a502c6c5050bbdd9",
    "tools/gallery_studio.py": "71da322be5bb90e69b570fdcb4148812",
    "tools/gallery_editor.py": "c23b8302fccbe08ce24893c7346833df",
}

CONVERTER_FUNCS = b'''

def live_scene_urls(repo_root):
    """The ?exhibit= values interactive.html serves, read from its source.

    Returns a list of (url, note). The default exhibit comes from the
    `.get("exhibit") || "..."` fallback; the rest from `EXHIBIT === "..."`.
    Moved here from gallery_editor.py on 2026-09-06 (L-288) so Studio and
    the editor read one list.
    """
    path = os.path.join(repo_root, 'interactive.html')
    urls = []
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            src = f.read()
    except OSError:
        return urls
    m = re.search(r'get\\(["\\']exhibit["\\']\\)\\s*\\|\\|\\s*["\\']([a-z0-9_-]+)["\\']', src)
    if m:
        urls.append(('interactive.html', f'default exhibit: {m.group(1)}'))
    for key in sorted(set(re.findall(r'EXHIBIT\\s*===?\\s*["\\']([a-z0-9_-]+)["\\']', src))):
        if m and key == m.group(1):
            continue
        urls.append((f'interactive.html?exhibit={key}', key))
    return urls


def add_live_card(repo_root, url, title, description="", sources=None):
    """Write a schema-v2 INTERACTIVE card into storage (L-288).

    A live card opens a scene in interactive.html; it has no figure file,
    so nothing is converted. The card lands in room "other" (storage) and
    is placed in the editor, like every other new card. Refuses when the
    metadata is not schema v2, when the title is empty, or when another
    card already opens the same scene (edit that one in the editor).
    Returns the new entry. Raises ValueError with a plain message.
    """
    title = (title or "").strip()
    url = (url or "").strip()
    if not title:
        raise ValueError("The card needs a title.")
    if not url:
        raise ValueError("Pick the scene the card should open.")
    metadata_path = os.path.join(repo_root, DEFAULT_OUTPUT_FOLDER, METADATA_FILE)
    if not os.path.exists(metadata_path):
        raise ValueError(f"{metadata_path} not found.")
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    if metadata.get("version") != 2:
        raise ValueError("gallery_metadata.json is not schema version 2; "
                         "run the L-287 migration first.")
    viz_list = metadata.get("visualizations", [])
    for v in viz_list:
        if (v.get("live") or "").strip() == url:
            raise ValueError(f"'{v.get('title', v.get('id'))}' already opens "
                             f"{url}. Edit that card in the editor instead.")
    base = re.sub(r'[^\\w\\-]', '_', title.lower()).strip('_') or "interactive"
    safe_name = base
    n = 2
    ids = {v.get("id") for v in viz_list}
    while safe_name in ids:
        safe_name = f"{base}_{n}"
        n += 1
    entry = {
        "id": safe_name,
        "title": title,
        "description": (description or "").strip(),
        "room": "other",
        "shape": "16:9",
        "files": {},
        "live": url,
        "featured": False,
        "sources": [s.strip() for s in (sources or []) if s and s.strip()],
        "converted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "size_kb": {},
    }
    viz_list.append(entry)
    metadata["visualizations"] = viz_list
    metadata["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    metadata["total_count"] = len(viz_list)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"  metadata: new INTERACTIVE card {safe_name} -> {url} in Storage; place it in the editor")
    return entry
'''

STUDIO_METHOD = b'''    def _new_live_card(self):
        """New Interactive Card (L-288): a card that opens a scene in
        interactive.html. No figure, nothing to convert; Studio writes the
        card (title, placard, sources, scene URL) into storage through
        json_converter.add_live_card, and the editor places it."""
        import json_converter
        root = self._repo_root()
        scenes = json_converter.live_scene_urls(root)
        if not scenes:
            messagebox.showinfo("New Interactive Card",
                                "No scenes found in interactive.html.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("New Interactive Card")
        dlg.transient(self.root)
        dlg.grab_set()
        pad = {'padx': 8, 'pady': 4}

        tk.Label(dlg, text="Scene (read from interactive.html)").grid(
            row=0, column=0, sticky='w', **pad)
        labels = [f"{u}    ({note})" for u, note in scenes]
        var_scene = tk.StringVar(value=labels[0])
        tk.OptionMenu(dlg, var_scene, *labels).grid(
            row=0, column=1, sticky='ew', **pad)

        tk.Label(dlg, text="Title").grid(row=1, column=0, sticky='w', **pad)
        var_title = tk.StringVar()
        tk.Entry(dlg, textvariable=var_title, width=48).grid(
            row=1, column=1, sticky='ew', **pad)

        tk.Label(dlg, text="Placard (one or two sentences)").grid(
            row=2, column=0, sticky='nw', **pad)
        txt_desc = tk.Text(dlg, width=48, height=3, wrap='word')
        txt_desc.grid(row=2, column=1, sticky='ew', **pad)

        tk.Label(dlg, text="Sources (one per line)").grid(
            row=3, column=0, sticky='nw', **pad)
        txt_src = tk.Text(dlg, width=48, height=4, wrap='none')
        txt_src.grid(row=3, column=1, sticky='ew', **pad)

        tk.Label(dlg, fg='#555', justify='left',
                 text="The card lands in Storage; move it to its room in "
                      "the gallery editor.\\nNo picture: a live card is a "
                      "placard with an Interactive tag.").grid(
            row=4, column=0, columnspan=2, sticky='w', **pad)

        def create():
            url = var_scene.get().split('    (')[0].strip()
            title = var_title.get()
            desc = txt_desc.get('1.0', 'end').strip()
            sources = txt_src.get('1.0', 'end').splitlines()
            try:
                entry = json_converter.add_live_card(root, url, title, desc, sources)
            except (ValueError, OSError, json.JSONDecodeError) as e:
                messagebox.showerror("New Interactive Card", str(e), parent=dlg)
                return
            self._log_status(f"Interactive card created in Storage: {entry['id']} -> {url}")
            messagebox.showinfo(
                "New Interactive Card",
                f"Created '{entry['title']}' ({entry['id']}) in Storage, opening {url}.\\n\\n"
                "Open the gallery editor to move it to its room.", parent=dlg)
            dlg.destroy()

        btns = tk.Frame(dlg)
        btns.grid(row=5, column=0, columnspan=2, sticky='e', **pad)
        tk.Button(btns, text="Create", command=create, width=10,
                  fg='blue').pack(side='right', padx=3)
        tk.Button(btns, text="Cancel", command=dlg.destroy,
                  width=10).pack(side='right', padx=3)
        dlg.columnconfigure(1, weight=1)

'''

EDITS = {
    "tools/json_converter.py": [
        (b"the category prompt is skipped when gallery_config.json is version 2.\n",
         b"the category prompt is skipped when gallery_config.json is version 2.\n"
         b"Module updated: September 6, 2026 with Anthropic's Claude Fable 5.1 (L-288):\n"
         b"live_scene_urls() moved here from the editor; add_live_card() writes an\n"
         b"INTERACTIVE card (live scene, no file) into storage for Gallery Studio.\n", 1),
        (b"    return entry, None\n\n\n# ============================================================================\n# HTML -> JSON EXTRACTION\n",
         b"    return entry, None\n" + CONVERTER_FUNCS +
         b"\n\n# ============================================================================\n# HTML -> JSON EXTRACTION\n", 1),
    ],
    "tools/gallery_studio.py": [
        (b"  gallery/_studio_preview.json -> ?preview= in the genuine gallery), so the\n"
         b"  GE button / link icon appear exactly as the live gallery will show them.\n",
         b"  gallery/_studio_preview.json -> ?preview= in the genuine gallery), so the\n"
         b"  GE button / link icon appear exactly as the live gallery will show them.\n"
         b"\n"
         b"Module updated: September 6, 2026 with Anthropic's Claude Fable 5.1 (L-288)\n"
         b"- New Interactive Card: a card that opens a scene in interactive.html\n"
         b"  (title, placard, sources, scene URL from a picker); no figure, nothing\n"
         b"  converted; lands in Storage via json_converter.add_live_card.\n", 1),
        (b'                "Output: a .py file to paste into spacecraft_encounters.py.")\n'
         b"\n"
         b"        # Spacer to push status bar down and give tooltip room\n",
         b'                "Output: a .py file to paste into spacecraft_encounters.py.")\n'
         b"\n"
         b"        live_btn = tk.Button(action_frame, text=\"New Interactive Card...\",\n"
         b"                             command=self._new_live_card, width=20,\n"
         b"                             fg='#7a4a9a')\n"
         b"        live_btn.pack(side='left', padx=3)\n"
         b"        ToolTip(live_btn,\n"
         b"                \"Create a card that opens a live scene in interactive.html\\n\"\n"
         b"                \"(the Sun today; Earth when its exhibit exists).\\n\\n\"\n"
         b"                \"No figure and nothing to convert: you write the title,\\n\"\n"
         b"                \"the placard and the sources, and pick the scene. The card\\n\"\n"
         b"                \"lands in Storage; move it to its room in the editor.\")\n"
         b"\n"
         b"        # Spacer to push status bar down and give tooltip room\n", 1),
        (b"    def _export(self):\n        \"\"\"Export the tailored HTML to a user-chosen location.\"\"\"\n",
         STUDIO_METHOD + b"    def _export(self):\n        \"\"\"Export the tailored HTML to a user-chosen location.\"\"\"\n", 1),
    ],
    "tools/gallery_editor.py": [
        (b"Module updated: September 5, 2026 (L-287): Apply button removed, fields\n"
         b"apply on focus-out; a live card may have no file; Copy to Room.\n",
         b"Module updated: September 5, 2026 (L-287): Apply button removed, fields\n"
         b"apply on focus-out; a live card may have no file; Copy to Room.\n"
         b"Module updated: September 6, 2026 (L-288): live_scene_urls() now lives in\n"
         b"json_converter.py and is imported; Studio reads the same list.\n", 1),
        (b"def live_scene_urls(repo_root):\n"
         b"    \"\"\"The ?exhibit= values interactive.html serves, read from its source.\n"
         b"\n"
         b"    Returns a list of (url, note). The default exhibit comes from the\n"
         b"    `.get(\"exhibit\") || \"...\"` fallback; the rest from `EXHIBIT === \"...\"`.\n"
         b"    \"\"\"\n"
         b"    path = os.path.join(repo_root, 'interactive.html')\n"
         b"    urls = []\n"
         b"    try:\n"
         b"        with open(path, 'r', encoding='utf-8', errors='replace') as f:\n"
         b"            src = f.read()\n"
         b"    except OSError:\n"
         b"        return urls\n"
         b"    m = re.search(r'get\\([\"\\']exhibit[\"\\']\\)\\s*\\|\\|\\s*[\"\\']([a-z0-9_-]+)[\"\\']', src)\n"
         b"    if m:\n"
         b"        urls.append(('interactive.html', f'default exhibit: {m.group(1)}'))\n"
         b"    for key in sorted(set(re.findall(r'EXHIBIT\\s*===?\\s*[\"\\']([a-z0-9_-]+)[\"\\']', src))):\n"
         b"        if m and key == m.group(1):\n"
         b"            continue\n"
         b"        urls.append((f'interactive.html?exhibit={key}', key))\n"
         b"    return urls\n",
         b"# live_scene_urls() moved to json_converter.py on 2026-09-06 (L-288) so\n"
         b"# Studio and the editor read one list. Same signature, same result.\n"
         b"from json_converter import live_scene_urls  # noqa: E402\n", 1),
    ],
}


def die(m):
    print("ERROR: " + m)
    print("NOTHING was written to any file.")
    sys.exit(1)


os.chdir(os.path.dirname(os.path.abspath(__file__)))
loaded = {}
for path, expect in FILES.items():
    if not os.path.exists(path):
        die("%s not found; save this script at the GALLERY repo root" % path)
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n") if crlf else raw
    got = hashlib.md5(s).hexdigest()
    if got != expect:
        if b"add_live_card" in s or b"_new_live_card" in s or b"from json_converter import live_scene_urls" in s:
            die("this patch has already been applied (%s)" % path)
        die("%s does not match gallery fc8d9fb3 (md5 %s, expected %s)" % (path, got, expect))
    loaded[path] = (s, crlf)
    print("ok  %s matches fc8d9fb3%s" % (path, " (CRLF)" if crlf else ""))

results = {}
for path, edits in EDITS.items():
    s, crlf = loaded[path]
    for old, new, n in edits:
        c = s.count(old)
        if c != n:
            die("%s: anchor expected %d time(s), found %d: %r" % (path, n, c, old[:60]))
        s = s.replace(old, new)
        if any(ch > 127 for ch in new):
            die("non-ASCII byte in inserted text for %s" % path)
    results[path] = (s, crlf)

for path, (s, crlf) in results.items():
    open(path, "wb").write(s.replace(b"\n", b"\r\n") if crlf else s)
    print("wrote %s" % path)

print("json_converter.py: live_scene_urls() (moved) + add_live_card(); docstring credit.")
print("gallery_studio.py: New Interactive Card button + dialog; docstring credit.")
print("gallery_editor.py: imports live_scene_urls from json_converter; docstring credit.")
print("Next: run Studio, New Interactive Card..., create a test card; see it in the editor's Storage;")
print("      commit the three files, push, report the gallery SHA.")
print("Undo is Discard Changes in GitHub Desktop.")
