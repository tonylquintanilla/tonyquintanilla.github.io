"""
patch_L267_4_info_panel_links.py -- Stage C of the Sun exhibit GUI (L-267):
the i panel follows the focus and carries the link out.

Built on gallery 197fd96340722192f8f58ced7ea5cee62ca074f8 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

WHAT IT DOES

  Before this patch the i button opens a panel holding one fixed
  description of the exhibit. It does not know which shell is focused.
  The 22 curated links (L-265) sit in the served config and reach the
  page inside the assembler's feature report, and nothing reads them.

  After it, the panel has two parts. The top part follows the focus
  the same way the drawer handle does: the focused shell's swatch and
  name, and one "Read more" link out to its NASA or Wikipedia page. When
  nothing is focused, that part reads "Focus a shell to see its link"
  and the exhibit description below is all there is, as today. A shell
  with no link on file says so in words rather than showing nothing --
  a blind spot announces (protocol: A Check That Cannot Fail).

  The panel carries no radius and no citation. The cross marker's hover
  already does (L-267: the panel is not a second copy of the hover).
  The i button keeps one job: open and close the panel. It does not move
  the camera and it does not draw anything.

  DELIBERATELY LEFT OUT: the mockup's hover-seize workaround (hovermode
  off while the panel is open). Stage B found that exact relayout throws
  inside Plotly and takes viewInitial with it (gallery-assembler 1.2,
  Mode 5 rule 3), and the seize itself was most likely the L-278 click
  re-entry, fixed in patch_L267_3. If the seize recurs it is a separate
  finding, not a reason to reintroduce that call.

HOW THE LINK GETS INTO THE PAGE

  feature_renderers.js already builds the drawer's group label
  ("Sun: Core") from the shell config. Rather than rebuild that label a
  second time in interactive.html to look the link up, renderShellSet
  stamps each shell's link onto the traces it makes, in Plotly's own
  `meta` field ({info_url} or {info_urls}). buildSunDrawer reads it off
  the trace when it builds the group. One source, no parallel formula.

  Only renderShellSet is stamped. That covers every Sun shell (all
  eighteen are shell-set members, streamer belt and Oort shapes
  included). Earth's belts carry `info_urls` through renderBelts, which
  is not on this rung of the ladder and is not touched here; the reader
  side already accepts the array form so that rung needs only the stamp.

TWO FILES, SIX EDITS

  gallery/feature_renderers.js
    1. header: Module updated line (Stamp What You Change)
    2. a stampLink helper before renderShellSet
    3. renderShellSet: streamer, Oort and sphere branches stamp their
       traces (three anchors, one edit each)
  interactive.html
    4. header: Updated line
    5. CSS for the focus block in the panel
    6. SUN_INFO_HTML gains the focus block; buildSunDrawer records the
       link per group; renderSunDrawer calls renderSunInfo; renderSunInfo
       and sunLinkOf are new

HOW TO RUN
  Save this file into the GALLERY repo root (the folder holding
  interactive.html), open it in VS Code and press Run. It takes no
  arguments. Then commit and push in GitHub Desktop.

  Mode 5 after, on the live page (conditions stated, per
  gallery-assembler 1.2):
    1. Fresh load, nothing focused. Tap i. The panel opens on "Focus a
       shell to see its link" over the exhibit description. Tap i
       again; it closes.
    2. Click the Core cross marker (drawer open or closed, either).
       Tap i. The top of the panel shows the Core swatch and name and
       one "Read more at Wikipedia" link. Tap the link: Solar_core
       opens in a new tab; the exhibit page is still there and still
       responds.
    3. With the panel OPEN, click a different marker (the Alfven
       surface). The panel's top block changes to the Alfven surface
       and "Read more at NASA" without the panel closing.
    4. With the panel open, hover a few markers and rotate the scene.
       Nothing seizes. (This is the trial the mockup's open defect
       needs; report what you did, not only whether it hung.)
    5. Open the drawer, untick the focused shell. The label reads
       "(not drawn)" as before; the panel's top block keeps the name
       and link.

GUARDS
  Both files are fingerprinted (MD5 over LF-normalised content), every
  anchor must match exactly once, and nothing is written unless all
  checks pass. The two files are written together or not at all. No
  .bak (safe-file-editing 1.10); undo is Discard Changes in GitHub
  Desktop.

Module created: September 3, 2026 with Anthropic's Claude Fable 5.1.
"""

import hashlib
import os
import sys

MARKER = 'L-267 Stage C'

FILES = {
    'gallery/feature_renderers.js': 'e26d917a6d4c319ed373fd669598876b',
    'interactive.html':             '86ac834b7aa368a9383742d510e48928',
}

# --------------------------------------------------------------------
# gallery/feature_renderers.js
# --------------------------------------------------------------------

FR_EDITS = [
    # 1. header stamp
    (""" * Module created: August 2026 with Anthropic's Claude Opus 5 (L-154).
 */
""",
     """ * Module created: August 2026 with Anthropic's Claude Opus 5 (L-154).
 * Module updated: September 3, 2026 with Anthropic's Claude Fable 5.1
 *   (L-267 Stage C: renderShellSet stamps each shell's info link onto
 *   its traces in `meta`, so the page's i panel can read it off the
 *   trace instead of rebuilding the label to look it up).
 */
"""),

    # 2. helper before renderShellSet
    ("""  function renderShellSet(slug, bodyName, featureKey, params, center,
                          basis, halfRangeAu, warn) {
""",
     """  /*
   * L-267 Stage C. Carry a shell's curated link (L-265) on its traces in
   * Plotly's `meta`, which Plotly ignores and passes through. The page
   * groups traces by legendgroup to build its drawer; reading the link
   * from the trace keeps ONE source for "which link belongs to this
   * group" instead of a second copy of the label formula in the page.
   * Two forms, matching the config: `info_url` (one page) and
   * `info_urls` (a list, used by Earth's belts). Neither present: no
   * meta, and the page says so in words.
   */
  function stampLink(traceList, cfg) {
    var meta = null;
    if (typeof cfg.info_url === "string" && cfg.info_url) {
      meta = { info_url: cfg.info_url };
    } else if (Array.isArray(cfg.info_urls) && cfg.info_urls.length) {
      meta = { info_urls: cfg.info_urls.slice() };
    }
    if (meta) {
      for (var i = 0; i < traceList.length; i++) {
        traceList[i].meta = meta;
      }
    }
    return traceList;
  }

  function renderShellSet(slug, bodyName, featureKey, params, center,
                          basis, halfRangeAu, warn) {
"""),

    # 3a. streamer branch
    ("""          traces = traces.concat(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn));
          drawn += 1;
""",
     """          traces = traces.concat(stampLink(renderStreamerBand(
            slug, bodyName, cfg, where + "/" + key, center, basis,
            starRadiusKm, warn), cfg));
          drawn += 1;
"""),

    # 3b. Oort branch
    ("""          traces = traces.concat(oortTraces);
          drawn += 1;
""",
     """          traces = traces.concat(stampLink(oortTraces, cfg));
          drawn += 1;
"""),

    # 3c. sphere branch: the geometry trace and its info marker
    ("""      if (beyondFrame) {
        built.trace.visible = "legendonly";
      }
      traces.push(built.trace);
""",
     """      if (beyondFrame) {
        built.trace.visible = "legendonly";
      }
      stampLink([built.trace], cfg);
      traces.push(built.trace);
"""),
    ("""        marker.visible = "legendonly";
      }
      traces.push(marker);
      drawn += 1;
""",
     """        marker.visible = "legendonly";
      }
      stampLink([marker], cfg);
      traces.push(marker);
      drawn += 1;
"""),
]

# --------------------------------------------------------------------
# interactive.html
# --------------------------------------------------------------------

IH_EDITS = [
    # 4. header stamp
    ("""     Created: July 6, 2026 with Anthropic's Claude Opus 4.6
""",
     """     Created: July 6, 2026 with Anthropic's Claude Opus 4.6
     Updated: September 3, 2026 with Anthropic's Claude Fable 5.1
       (L-267 Stage C: the Sun exhibit's i panel follows the focus and
        carries the focused shell's link out)
"""),

    # 5. CSS after the info-note rule
    ("""        .info-panel .info-note {
            font-size: 11px;
            color: var(--text-dim);
            font-style: italic;
            line-height: 1.5;
            padding-top: 12px;
            border-top: 1px solid var(--border);
        }
""",
     """        .info-panel .info-note {
            font-size: 11px;
            color: var(--text-dim);
            font-style: italic;
            line-height: 1.5;
            padding-top: 12px;
            border-top: 1px solid var(--border);
        }
        /* L-267 Stage C. The block at the top of the Sun panel that
           follows the focus: swatch, name, link out. Same swatch as the
           drawer handle so the two readouts visibly agree. */
        .info-focus {
            padding-bottom: 12px;
            margin-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }
        .info-focus .info-focus-name {
            display: flex; align-items: center; gap: 8px;
            font-family: 'Cormorant Garamond', serif;
            font-size: 18px; font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 6px;
        }
        .info-focus .info-focus-swatch {
            width: 12px; height: 12px; border-radius: 50%;
            flex-shrink: 0;
        }
        .info-focus .info-focus-empty {
            font-size: 13px; color: var(--text-dim); font-style: italic;
        }
        .info-focus a {
            display: inline-block;
            font-size: 13px;
            color: var(--accent);
            text-decoration: none;
            border-bottom: 1px solid var(--accent-dim);
            margin-right: 12px;
        }
        .info-focus a:hover { color: var(--text-primary); }
"""),

    # 6a. the focus block leads the Sun panel
    ("""const SUN_INFO_HTML = [
    "<h3>The Sun</h3>",
""",
     """const SUN_INFO_HTML = [
    // L-267 Stage C. Filled by renderSunInfo on every focus change.
    "<div class=\\"info-focus\\" id=\\"sun-info-focus\\"></div>",
    "<h3>The Sun</h3>",
"""),

    # 6b. buildSunDrawer: record the link when the group is created ...
    ("""            byName[g] = {
                name: t.name || g,
                color: sunSwatchColor(t),
                indices: [],
                shown: t.visible !== SUN_HIDDEN && t.visible !== false,
            };
""",
     """            byName[g] = {
                name: t.name || g,
                color: sunSwatchColor(t),
                link: sunLinkOf(t),
                indices: [],
                shown: t.visible !== SUN_HIDDEN && t.visible !== false,
            };
"""),

    # 6c. ... and refresh it from the legend-bearing trace
    ("""        if (t.showlegend === true) {
            byName[g].name = t.name || g;
            byName[g].color = sunSwatchColor(t);
        }
""",
     """        if (t.showlegend === true) {
            byName[g].name = t.name || g;
            byName[g].color = sunSwatchColor(t);
            byName[g].link = sunLinkOf(t) || byName[g].link;
        }
"""),

    # 6d. renderSunDrawer ends by refreshing the panel
    ("""    document.getElementById("sun-drawer-label").textContent =
        grp ? (grp.name + (hiddenFocus ? " (not drawn)" : ""))
            : "Nothing drawn";
}
""",
     """    document.getElementById("sun-drawer-label").textContent =
        grp ? (grp.name + (hiddenFocus ? " (not drawn)" : ""))
            : "Nothing drawn";

    renderSunInfo(grp);
}

// L-267 Stage C. The link a shell carries, read off its trace. The
// renderer stamps it in `meta` (feature_renderers.js, stampLink); this
// side accepts both forms the config uses. Returns a list of URLs, or
// null when the trace carries none.
function sunLinkOf(trace) {
    const m = trace && trace.meta;
    if (!m) { return null; }
    if (typeof m.info_url === "string" && m.info_url) {
        return [m.info_url];
    }
    if (Array.isArray(m.info_urls) && m.info_urls.length) {
        return m.info_urls.slice();
    }
    return null;
}

// Wording for a link, from its host. NASA and Wikipedia are the two
// sources L-265 allows; anything else is named by its host so a stray
// link is visible rather than mislabelled.
function sunLinkLabel(url) {
    let host = "";
    try { host = new URL(url).hostname; } catch (e) { host = ""; }
    if (/(^|\\.)nasa\\.gov$/.test(host)) { return "Read more at NASA"; }
    if (/(^|\\.)wikipedia\\.org$/.test(host)) { return "Read more at Wikipedia"; }
    return "Read more at " + (host || url);
}

// L-267 Stage C. The i panel's top block follows the focus, the same
// way the drawer handle does. It carries the name and the link OUT and
// nothing else: the cross marker's hover already has the radius and
// the citation, and the panel is not a second copy of it. The i button
// keeps one job -- open and close -- so this never opens the panel
// itself; it only keeps the contents current for when it is opened.
function renderSunInfo(grp) {
    const box = document.getElementById("sun-info-focus");
    if (!box) { return; }
    box.innerHTML = "";
    if (!grp) {
        const empty = document.createElement("div");
        empty.className = "info-focus-empty";
        empty.textContent = "Focus a shell to see its link.";
        box.appendChild(empty);
        return;
    }
    const head = document.createElement("div");
    head.className = "info-focus-name";
    const sw = document.createElement("span");
    sw.className = "info-focus-swatch";
    sw.style.background = grp.color;
    sw.style.opacity = grp.shown ? "1" : "0.3";
    head.appendChild(sw);
    head.appendChild(document.createTextNode(grp.name));
    box.appendChild(head);

    if (!grp.link) {
        // A blind spot announces. A shell with no link on file says so
        // rather than leaving an empty block that reads as "nothing to
        // say" -- the served config should carry one for every shell
        // (L-265 asserts zero placeholders), so seeing this is a finding.
        const none = document.createElement("div");
        none.className = "info-focus-empty";
        none.textContent = "No link on file for this shell.";
        box.appendChild(none);
        return;
    }
    for (let i = 0; i < grp.link.length; i++) {
        const a = document.createElement("a");
        a.href = grp.link[i];
        a.target = "_blank";
        a.rel = "noopener";
        a.textContent = sunLinkLabel(grp.link[i]);
        box.appendChild(a);
    }
}
"""),
]


def fail(msg):
    print('')
    print('FAILURE: %s' % msg)
    print('NOTHING was written. No file on disk has changed.')
    print('If a previous run did write, undo is Discard Changes in GitHub Desktop.')
    sys.exit(1)


def read_lf(path):
    raw = open(path, 'rb').read()
    was_crlf = b'\r\n' in raw
    return (raw.replace(b'\r\n', b'\n') if was_crlf else raw), was_crlf


def prepare(path, edits):
    """Verify and apply in memory. Returns (bytes_out, was_crlf)."""
    if not os.path.exists(path):
        fail('%s not found. Run this from the GALLERY repo root.' % path)
    content, was_crlf = read_lf(path)
    actual = hashlib.md5(content).hexdigest()
    if actual != FILES[path]:
        fail('BASE MOVED for %s.\n  expected %s\n  found    %s\n'
             '  Built against gallery 197fd963. A size delta of about one\n'
             '  byte per line is CRLF, not content.'
             % (path, FILES[path], actual))
    print('  %-32s fingerprint matches%s'
          % (path, ' [CRLF]' if was_crlf else ''))
    if MARKER.encode('ascii') in content:
        fail('%s already carries "%s". This patch has run.' % (path, MARKER))
    for i, (old, new) in enumerate(edits, 1):
        try:
            new.encode('ascii')
        except UnicodeEncodeError as exc:
            fail('%s edit %d: non-ASCII in replacement: %s' % (path, i, exc))
        a = old.encode('ascii')
        n = content.count(a)
        if n != 1:
            fail('%s edit %d: anchor matched %d times (expected 1):\n  %r'
                 % (path, i, n, old[:70]))
        content = content.replace(a, new.encode('ascii'))
        print('  %-32s edit %d anchor verified' % ('', i))
    return content, was_crlf


def main():
    print('patch_L267_4 -- Stage C: the i panel follows the focus')
    print('=' * 62)

    staged = {}
    for path, edits in [('gallery/feature_renderers.js', FR_EDITS),
                        ('interactive.html', IH_EDITS)]:
        staged[path] = prepare(path, edits)

    # All checks passed on both files; only now does anything get written.
    for path, (out, was_crlf) in staged.items():
        with open(path, 'wb') as f:
            f.write(out.replace(b'\n', b'\r\n') if was_crlf else out)
        print('  wrote %s' % path)
    print('  stamped: feature_renderers.js header, interactive.html header')

    # --- Post-conditions, read back from disk ------------------------
    print('')
    print('Post-conditions (read back from disk):')
    ok = True
    fr = read_lf('gallery/feature_renderers.js')[0].decode('utf-8', 'replace')
    ih = read_lf('interactive.html')[0].decode('utf-8', 'replace')
    checks = [
        ('fr: stampLink declared',    fr.count('function stampLink(traceList, cfg)'), 1),
        ('fr: stampLink call sites',  fr.count('stampLink('), 5),  # decl + 4
        ('fr: header stamped',        fr.count('Module updated: September 3, 2026'), 1),
        ('ih: focus block in panel',  ih.count('id=\\"sun-info-focus\\"'), 1),
        ('ih: renderSunInfo declared', ih.count('function renderSunInfo(grp)'), 1),
        ('ih: renderSunInfo called',  ih.count('renderSunInfo(grp);'), 1),
        ('ih: sunLinkOf declared',    ih.count('function sunLinkOf(trace)'), 1),
        ('ih: sunLinkOf call sites',  ih.count('sunLinkOf(t)'), 2),
        ('ih: no hovermode toggle',   ih.count('hovermode: false'), 0),
        ('ih: header stamped',        ih.count('Updated: September 3, 2026'), 1),
    ]
    for label, got, want in checks:
        print('  %-28s %d (want %d) %s' % (label, got, want,
                                          'ok' if got == want else 'FAIL'))
        if got != want:
            ok = False
    if not ok:
        print('')
        print('POST-CONDITION FAILED. Undo is Discard Changes in GitHub Desktop.')
        sys.exit(1)

    print('')
    print('DONE. Commit and push, then Mode 5 on the live page -- the five')
    print('trials are in the docstring at the top of this file.')


if __name__ == '__main__':
    main()
