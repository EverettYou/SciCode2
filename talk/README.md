# Project research talk

`threads/` contains all user–agent supervision conversations for this SciCode2 project. The talk is project-wide; benchmarks do not contain their own talk copies.

Each thread carries free-text `context` pasted or written by the user or agent. It may include paper IDs, benchmark IDs, copied assessment items, excerpts, links, or working instructions. The dashboard does not require the user to classify the thread with a benchmark selector.

When a canonical benchmark ID appears in the context, the dashboard records it in derived `benchmark_ids` so the conversation also appears on that benchmark's detail page:

- an empty list means project-wide;
- one ID scopes the thread to one benchmark;
- multiple IDs represent a cross-benchmark discussion.

The last active message `author` determines who answers next. Users may edit or retract their own messages in an open thread; these actions append audit events while the dashboard materializes the current card in place. Retracted messages do not hand work to the agent. The agent reports completion with a `resolution` message; only the user closes or reopens a thread. Use `$consult-human` or the dashboard rather than editing thread files manually.

The reusable `$process-talk` skill checks the talk in both directions: it acts on eligible user messages, prepares durable agent replies, and can summarize open questions that are waiting on the user. Research loops should invoke it as part of their normal tick instead of relying on a separate talk automation.
