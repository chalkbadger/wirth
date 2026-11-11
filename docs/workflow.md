# Wirth workflow

## Refinement

Read the issue and relevant repository context under
[Shared decisions](product.md#shared-decisions).

Apply the specification's [scope and decision rules](product.md#refine-the-issue).
Use the scope cut to propose the first useful delivery and identify deferrals.

State observable success at the user's level. Each item an
[adequate test](#adequate-tests) can show becomes a contract claim; each other item
names the observation its PR will publish, under the
[contract rule](product.md#contracts). Test details belong in the contract. Update
the issue using the specification's [issue requirements](product.md#shared-decisions).

## Claims and evidence

Before editing files, identify and read the originating issue and its discussion.
If no originating issue can be identified, or the issue cannot be read, explain
the missing issue or access problem and stop before editing.

Check the requested work against the [issue requirements](product.md#shared-decisions).
Do not invent missing decisions from the requested implementation. If a requirement
is unmet or the request falls outside the issue, name exactly what needs settling
and ask the owner to invoke refinement. Do not begin implementation or start
refinement automatically.

When the issue is ready and covers the request, begin the agreed change. If a
separate outcome emerges while building, apply the
[outcome rule](product.md#shared-decisions): set that outcome aside and continue
work already covered by the original issue.

Apply the [claim rule](product.md#contracts) to the proposed change.
One result means **per evidence item**, not per test case. Do not restate the claim
or list cases: the named test carries the individual cases, and its name accurately
describes what it shows.
Prefer cutting an unnecessary claim to building evidence for it. A claim that
something never happens needs its own trap; make it only when the issue asks.

Lay out test folders as the [claim rule](product.md#contracts) says; shared setup
stays in an uncited helper. Account for every test, preserve discovery when moving
files and report removed cases. A test that fits no claim is unnecessary or exposes
a missing claim.

### Before implementation

For new or changed behavior with executable checks, write the checks first and run
them on the unchanged implementation. They must fail because the behavior is
missing, not because of a setup or import error. Record that failure in the PR,
opening a draft PR first if none exists, then implement and record the same checks
passing.

### Adequate tests

- Each test can fail for the reason its claim states; expected results are
  independent of the implementation under test. Expected results copied from the
  implementation's output are not independent, even after review. When code
  interprets an external system, its expected results cite that system's
  documentation or source.
- A bug aimed at an evidence item must be caught by its cited file, not by chance
  elsewhere in the suite.
- Harmless refactoring keeps tests green. Check behavior, not source structure or
  the test's own setup.
- A claim that behavior is unchanged requires existing tests to pass without edits
  to those tests or their expected results; deleting a test counts as an edit, but
  moving one unchanged does not. New tests are allowed when they also pass on the
  base commit.
- Isolate tests from network access and other uncontrolled environment behavior,
  for example with an audit hook that makes forbidden access observable.
- Establish the needed conditions: testing uncommitted edits requires a committed
  baseline and an uncommitted change.
- A skipped test supplies no evidence. For platform-specific behavior, record a
  run on a platform where the check executes.
- Assert actual results or messages, not only their count.
- Run a case that could block through a subprocess with a timeout.
- Show command exit status, output and absence of false success once per relevant
  claim. Check individual inputs in-process unless they need distinct command-level
  observations, such as timeouts. Avoid duplicated assertions across both levels.

### Worked example

One evidence item of a claim in Wirth's own [contract](../contracts/claims.md):

```markdown
## [failures_say_what_to_fix] When validation fails, I see every problem with its file and line, and the command exits unsuccessfully.
Issue: https://github.com/chalkbadger/wirth/issues/1
Tests: [tests/failures_say_what_to_fix/](../tests/failures_say_what_to_fix/)

- I leave out a claim's Issue line, and I still see the claim and its errors. `test_input_errors.py::test_missing_issue_does_not_hide_claim_or_its_errors`
```

The [test](../tests/failures_say_what_to_fix/test_input_errors.py) writes a
contract whose claim lacks its Issue line, once alone and once with a blank claim, and compares
the returned diagnostics with an exact expected list. An implementation that stopped
at the missing Issue line would fail that comparison, so the obligation isolates
error preservation.

## Review passes

Read the proposed changes and their issue and PR discussion against the documents
on main, under [Shared decisions](product.md#shared-decisions). If a required
document or the current proposal's records cannot be read, report the affected
review as not performed and stop short of judging scope.

Brief each reviewer on one pass only. If one reviewer runs all passes, run them one
at a time, re-reading only that pass's section. Start with claim level. Each finding
names its location, affected claim or principle, mismatch and resolution type:
**implementation, evidence or contract**. Implementation includes documentation
changes. Report inapplicable checks with their reason.

Resolve findings through the specification's [build-and-review process](product.md#build-and-review).
Apply the [decision rule](product.md#refine-the-issue) to conflicts and the
[claim rule](product.md#contracts) to added detail or separate claims. Record the
resolution against the finding so another reviewer can see what changed and why.

A finding or recommendation that depends on how an external system behaves cites
that system's documentation or source at a pinned revision, or a recorded run with
the system's version, inputs and result. Without that it is marked **unverified**;
an unverified statement cannot block a PR or be the reason for a change.

### 1. Claim level

Compare claims with the proposed change and user-facing documentation using the
[claim rule](product.md#contracts). Flag claims in that documentation without
supporting evidence.
Judge claim and result text as rendered on GitHub, including hidden content and
unchecked links.

Compare claims and evidence items with the issue's Success items and report each
difference. For a claim wider than the issue asked, recommend the issue's
wording; for a Success item left unmet, name it.

Flag detailed rules repeated from contracts or reference sources, including claim
text, evidence descriptions and reference-table entries. Name both the copy and
authoritative source, and request replacing the duplicated detail with a source
link before recommending acceptance. Keep examples.

Compare with the merged contract. Record each existing claim as kept, revised or
removed, with the reason.
If a kept claim's earlier evidence was inadequate, record **kept; earlier evidence
inadequate**, name the missed failure and explain the repair.

### 2. Evidence

For each obligation, look for a concrete wrong implementation that would still
pass its tests. If one exists, the evidence is inadequate: name the missed failure
and the observation needed. Apply the adequate-test rules and check test mapping
and discovery. Flag duplicated, tautological or unnecessary tests.

Inspect the [before-and-after record](#before-implementation); a passing result
alone does not supply it.

A planted-bug check deliberately changes the implementation to see whether tests
catch the error. Plant only mistakes an honest implementer could plausibly make;
deliberate sabotage is outside this pass's scope.
If run, publish the bugs, revision, reproduction steps, timeouts
and outcomes with the findings; explain acceptable survivors. Distinguish a
hypothetical missed failure from an executed check.
The reviewer chooses independent bugs before reading the author's bug list, then
checks both sets. For each condition a claim depends on, plant one bug that makes it
hold when it should not and one that makes it fail when it should hold.

### 3. Fail loudly

Apply the [product principle](product.md#fail-loudly).
Look for success on ambiguous, missing, unexpected, external or skipped input.
Report only inputs an honest author could plausibly write. Deliberate obfuscation
is outside this pass's scope.
Prefer allow-lists that define accepted input over lists of forbidden cases.

### 4. Simplicity

Apply the specification's [scope rule](product.md#refine-the-issue) to the entire
change: code, tests, fixtures, documentation and records. Judge readability and
necessity. For every added file, ask what would be lost by deleting it or
replacing it with a pinned link; request concrete cuts before recommending
acceptance and name what must remain. Superseded material leaves the tree. Request
no unrelated improvements. A reviewer may recommend cutting built behavior the
issue did not require.
Recommend accepting new behavior only if it is required for a claim to be true.

### 5. Process

Check the [shared-decision requirements](product.md#shared-decisions) and published
results against the procedure below.
Name a human as the author or reviewer of text only when they wrote or reviewed
that exact text.
Never edit old comments; append corrections as new comments.
Once the PR exists, publish earlier local review findings with their locations,
mismatches, resolutions and reasons; identify any review that was local and
unrecorded.

## Record execution results

For observed runs that compare files, publish the raw before-and-after inventories
with the comparison output in the PR as each run finishes, unless the run's
procedure requires holding it.

Before publishing results, push the commit and put exactly that commit in a new,
empty directory by any method, such as a Git clone, an archive, an API or a
connector. The directory must match the published tree: every path with its
contents, file type and mode, and nothing else. Confirm through authenticated
repository access that the commit's full ID is the head of its branch. Run the
project's own checks and `wirth validate` there, with any Git metadata a check
needs. Record the repository, branch, commit, method, how the source and head were
checked, commands, results and platform in the PR. Missing or mismatched source,
or an unconfirmed head, leaves verification incomplete. Repeat after revisions.
State failures, skips and limits.
