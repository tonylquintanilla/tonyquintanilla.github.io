<!-- Doc-Kind: hand | The door into the protocol for a Claude Code session in the gallery repository: it points at the orrery's PROJECT_INSTRUCTIONS.md and skills in the sibling folder, and states what a Code session writes. -->
# Paloma's Orrery website: how a Claude Code session works here

This is the gallery repository (palomasorrery.com, served from GitHub
Pages). The project's rules live in the ORRERY repository, the sibling
folder `..\palomas_orrery_for_github\`: the protocol is its
PROJECT_INSTRUCTIONS.md and the skills are its `skills/<name>/SKILL.md`.
This file points there; it does not repeat them. If a sentence here
disagrees with the protocol or a skill, the protocol or the skill wins,
and this file gets corrected. Added October 27, 2026, modelled on the
orrery's CLAUDE.md of October 26.

@../palomas_orrery_for_github/PROJECT_INSTRUCTIONS.md

Reading the sibling folder needs your approval once; Tony says yes.
If the import above cannot be read, stop and say so before any work:
the session has no rules without it.

## Who you are working for

Tony is in the protocol's Roles section. Read it. He is not a
programmer. He runs Python with VS Code's Run button and uses GitHub
Desktop's buttons for commit and push. Explain any step outside that
in plain words before asking him to do it.

## The skills

They live in the orrery folder at
`..\palomas_orrery_for_github\skills\<name>\SKILL.md`. The Skill
Manifest in the protocol says which fires on which work; for this
repository that is usually interactive-exhibit, gallery-cache-builder,
gallery-assembler, gallery-pipeline, ledger-and-session-records,
safe-file-editing and agentic-pre-test. Read each one the job fires,
in full, before the work, and open your first report by naming the
skills you read and the version line each carries. Compare that
version with the manifest's row; if they disagree, stop and say so.

## At the start of a session

1. Read `..\palomas_orrery_for_github\documentation\WHERE_WE_ARE.md`.
   Its "Do next" line names the job, and a brief it names
   (`documentation\COORD_*.md` in the orrery folder) carries the
   details. Records live in the orrery's documentation folder, by
   Tony's practice; the gallery's documentation folder holds spent
   patches and the maintenance run's inputs.
2. Record the base: `git rev-parse HEAD` and `git ls-remote origin
   HEAD`, both read-only. If they differ, or `git status` shows edits
   already waiting, say so and stop.
3. Say what you are about to do, in one sentence, and wait for his
   go-ahead.

## What a Code session writes, and what it does not

- You edit the files in this folder directly; no patch file. The
  change list in GitHub Desktop is Tony's review; the records are his
  summary.
- Commit and push are Tony's, always. Never run git commit, git push,
  git add, or anything that discards work (reset, checkout, restore,
  clean, stash). `.claude\settings.json` forbids the important ones.
- Never edit the served cache under `data/solar-system/` by hand, nor
  `data/objects_config.json` except through the tools the
  gallery-cache-builder and interactive-exhibit skills name.
- Run the tests yourself and read the result: `gallery_maintenance_run.py`
  (offline) from this folder. The Daily Run and the live run after a
  push are Tony's, from the dashboard. "All green" is a line you read
  from the output, never a prediction; a red checker is fixed or
  reported, never left for the close.
- The orrery folder is read, not edited, from a gallery session,
  except its ledger and Where We Are for the records.
- ASCII only, LF line endings: the safe-file-editing skill.

## At the end of a session

- Records per the ledger-and-session-records skill, in the orrery
  folder: the ledger item, and WHERE_WE_ARE.md edited section by
  section, its box carrying a plain-word summary of what changed and
  why. Nothing below the page's run-record marker is touched.
- The run-record zone below that marker is empty by design. Tony's
  record is his timestamped copy of the page
  (`WHERE_WE_ARE_<m-d-yy>_<hhmm>_run_record.md`), one session per
  copy, and he writes only there (his ruling of Oct 28, 2026). An
  empty zone is not a missing record: read his latest copy instead.
- Your final report lists every file changed with the number of
  edits, in both folders, the way a patch prints "ok <file> (n
  edits)"; then his run order; then the Tony-action rollup.

## How to report to Tony

Tony reads your reports on his phone, between other things. He is not
a programmer and cannot follow compressed language (the protocol's
Register Rule, Part 2). So every report to him:
- Leads with the claim in one plain sentence; detail after.
- Says the thing, not the name of the thing: a ledger handle always
  carries its short label in parentheses, "L-497 (left-aligned
  text)", and a file is named with what it is for.
- Puts one question to him per report. A finding, a recommendation,
  an uncertainty and a question are four things; send the one that is
  due and put the rest in the records.
- Ends with the file list for his run record, his run order, and the
  Tony-action rollup, in that order.
