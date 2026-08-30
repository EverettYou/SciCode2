# Talk tick protocol

## Select work

1. Read `talk/README.md` and `skills/consult-human/SKILL.md` completely.
2. Run `python3 skills/consult-human/scripts/research_mailbox.py list .` from the project root.
3. Select at most three eligible open threads. Prioritize blocking and high-priority threads, then the oldest `updated_at` value.
4. A thread is eligible when either:
   - its latest active, materialized message is authored by `user`; or
   - its latest message is an unfinished agent message beginning with `[process-talk:working]`.
5. Immediately before claiming a thread, materialize it again. Skip it if another agent has replied or its status changed.

Ignore retracted content and superseded edit events. Do not process an unhandled agent question, an `[process-talk:blocked]` message, or an `[process-talk:done]` resolution.

## Claim and act

For a new user message, use the talk helper to append one concise `acknowledgment` beginning with `[process-talk:working]`. State the concrete interpretation and immediate next action. Do not add a second acknowledgment when resuming work already tagged `working`.

Read the thread context, related artifacts, and relevant project instructions. Carry out the requested work when it is safe, project-local, and authorized. Read-only source research is allowed when required by the request. Ask instead of guessing when an action requires new authority or a choice that materially changes the outcome.

## Persist an outcome

End processing for each claimed thread with exactly one state:

- `[process-talk:done]` in a `resolution`: summarize the result, project-relative artifact links, and checks performed.
- `[process-talk:blocked]` in a `question`, `checkpoint`, or `update`: explain the blocker and ask one focused question if user input is required.
- `[process-talk:working]` in an `update`: use only when bounded work remains and the next scheduled tick can resume safely.

Use `skills/consult-human/scripts/research_mailbox.py reply` for every reply. Never manually edit the thread log. If no thread is eligible, make no talk or project changes.

