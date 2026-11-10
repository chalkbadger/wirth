# Continuation prompt

Fill the four inputs and give the text below to a fresh agent. Identify this
prompt by the Git revision containing it. Run setup and scoring are in the
[workflow](../workflow.md#continuation-runs).

```text
Repository: <owner/name>
Repository revision: <full commit SHA>
Owner-selected task: <issue or PR URL and the owner's requested work>
Local output directory: <isolated directory for this run>

You are joining this project with no prior conversation or other run's output.
Use only the named repository's files at the supplied revision and its live
GitHub issues, pull requests and discussions. Use GitHub access read-only.
Do not read an answer key, previous run, or other local context. Write only
local work for this run; do not post, edit, push, merge or change GitHub state.

If an input or required source is missing or ambiguous, identify it and the
work it prevents. Do not invent an owner decision or report that work complete.

1. Orient. Read the project's own guidance. Summarize its purpose, how work is
   done, and the decisions governing the supplied task. Cite repository paths
   with their revision and issue/PR comment URLs.
2. Find the remaining work for that task and who must do it. Distinguish
   adopted rules and owner decisions from proposals and historical results.
3. Perform the next permitted process step locally, following the project's
   rules. Do not select another task. If proceeding requires an owner choice,
   produce the questions or proposed text for that choice instead of making it.
4. Report missing, contradictory or ambiguous records and any inference you
   made. Give the source and the information needed to resolve each gap.

Write continuation.md in the local output directory with sections 1-4 and the
complete next-step output. Include start/end times, the repository revision,
and the model/settings and tool access you can identify; mark unavailable
details explicitly. Record tool calls before step 3 and total tool calls.
Count each underlying tool invocation once, including calls within a batch;
do not also count the batching wrapper. Record bytes read when measurable,
otherwise mark the measurement unavailable. Effort is descriptive, with no
pass threshold. Cite evidence for conclusions and label uncertainty. Report
any observed changes in the live discussion during this run.
```
