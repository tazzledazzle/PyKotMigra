# FAANG Python service taxonomy — implementation plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Land the approved taxonomy design in-repo and surface it where roadmap readers look, without expanding PyKotMig MVP scope.

**Architecture:** One canonical design doc (`2026-05-14-faang-python-services-taxonomy-design.md`) stays the source of truth. The catalog and roadmap gain **short pointer paragraphs** so strangers see *why* MVP is HTTP-first and how later phases might grow—no new examples or manifest rows in this pass unless you explicitly extend scope later.

**Tech Stack:** Markdown only; repository layout per existing `catalog/README.md` and `.planning/ROADMAP.md`.

---

### Task 1: Confirm design artifact

**Files:**

- Read: `docs/plans/2026-05-14-faang-python-services-taxonomy-design.md`

**Step 1: Open the file**

Verify all sections render (headings, table): purpose/boundaries, archetype table, cross-cutting matrix, alignment with Phase 1.

**Step 2: Commit (if using git)**

Run:

```bash
cd /path/to/pykotmig
git add docs/plans/2026-05-14-faang-python-services-taxonomy-design.md
git status
```

Expected: file staged.

**Step 3: Commit message**

```bash
git commit -m "docs: add FAANG Python archetypes design for PyKotMig scope tags"
```

---

### Task 2: Roadmap pointer (single paragraph)

**Files:**

- Modify: `.planning/ROADMAP.md` (after **Overview** or under **Research inputs**)

**Step 1: Insert a 3–4 sentence block**

Content intent (paraphrase in your own words when editing):

- Large orgs run many Python **shapes**; PyKotMig Phase 1 intentionally targets **Must-hit** HTTP/JSON patterns first.
- Pattern-level map and tags: `docs/plans/2026-05-14-faang-python-services-taxonomy-design.md`.
- Catalog expansion for **Catalog-later** rows is **explicitly deferred** to later phases/research.

**Step 2: Commit**

```bash
git add .planning/ROADMAP.md
git commit -m "docs: link roadmap to FAANG Python taxonomy design"
```

---

### Task 3: Catalog glossary pointer

**Files:**

- Modify: `catalog/README.md` (after **Glossary** or end of intro)

**Step 1: Add one short subsection or bullet list**

- Link: `../docs/plans/2026-05-14-faang-python-services-taxonomy-design.md`
- Clarify: MVP rows map to **Must-hit**; v2 rows map toward **Catalog-later**; everything else in that doc is context only.

**Step 2: Commit**

```bash
git add catalog/README.md
git commit -m "docs: point catalog readers to FAANG taxonomy scope doc"
```

---

### Task 4: Optional root README one-liner (YAGNI default: skip)

**Files:**

- Modify: `README.md` — only if root README is the primary entry for external reviewers **and** it currently lacks any pointer to `.planning/`.

**Step 1: Decide**

If `README.md` already links ROADMAP/catalog, **skip** this task to avoid duplicate links.

**Step 2: If needed, add a single line** under the project blurb linking the taxonomy design.

---

## Verification

- Grep for broken relative links from `catalog/README.md` and `.planning/ROADMAP.md` to `docs/plans/2026-05-14-faang-python-services-taxonomy-design.md` (paths must resolve from each file’s directory).
- No changes to `catalog/manifest.json` or `examples/` in this plan unless you later promote a **Catalog-later** archetype to MVP.

---

## Handoff

Plan complete and saved to `docs/plans/2026-05-14-faang-python-services-taxonomy.md`. Two execution options:

**1. Subagent-Driven (this session)** — dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Parallel Session (separate)** — open a new session with superpowers:executing-plans, batch execution with checkpoints.

**Which approach?**

If Subagent-Driven: use superpowers:subagent-driven-development. If Parallel Session: new session uses superpowers:executing-plans.
