# Optional repository organization

Read only if the user also requests a full repository scaffold. The early question
and textual audit can be complete without this layout. Creating folders or plans
is not permission to implement or run scientific work.

## Workflow

1. Reuse an existing benchmark rather than initializing it again. Preserve its
   research stage and review history.
2. For a new paper-derived full scaffold, the existing creation CLI requires real
   reviewed paper IDs. Use its [metadata schema](metadata-schema.md) and scaffold
   assets; never invent papers to satisfy the script.
3. Direct questions/transcripts can use the schema's direct-problem provenance
   with empty paper_ids and hashed supplied source files. A lightweight candidate
   does not need metadata or a catalog entry until it becomes a full workspace.
4. Populate the clear problem statement and prospective metadata. Leave unsupported
   results absent. Only include wiki, frontier, and lab design when requested;
   a first lab or completed reference solution is not an early acceptance gate.
5. Run the structural validator only for a full scaffold it is designed to check.
   Missing research infrastructure in a lightweight candidate is not a problem
   with the scientific question.

## Existing tools

From the repository root, the paper-driven CLI is:

```bash
python3 skills/create-benchmark/scripts/create_benchmark.py \
  <benchmark-id> --title "<title>" --paper-id <paper-id> \
  --summary "<objective>" --idea "<direction>"

python3 skills/create-benchmark/scripts/validate_benchmark.py benchmarks/<benchmark-id>
```

Never overwrite an existing benchmark. Newly initialized full workspaces use
`stage: problem-opened` and `expert_review: pending`; editorial screening does not
impersonate a human review. Detailed research, idea evolution, labs, and reference
evidence belong to [later research design](../../auto-research/references/research-workspace.md)
when that work is separately requested.
