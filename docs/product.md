# Wirth

**Build software with verifiable contracts.**

This is the user-provided product direction. The README describes the current
implementation and the contracts state what is built and verified; proposals and
outstanding verification are tracked in the PR.

Wirth runs inside the developer’s existing coding agent. It helps refine an issue,
review the implementation against an explicit contract, and preserve the decisions
behind the change in GitHub. Wirth needs no hosted service of its own and no GitHub workflow.

**Refine the issue. Build the change. Review and accept code and contract together.**

## Refine the issue

The refinement skill reads the issue, its discussion, and the repository context.
It helps the developer define a clear, coherent problem and the simplest change that
addresses it.

Refinement cuts scope to the core: cut so much that you have to add back 10%.
Trimming obvious excess is not enough. Refinement identifies the first independently
useful outcome, splits off work that can come later, and says what was deferred.

Wirth identifies contradictions. It asks a human only about choices that change what
the software does, what is in scope, a claim or a principle, and names which. It
decides other technical choices itself and records them as findings in the issue or
PR. It does not invent requirements or treat its recommendations as human decisions.

Detail or stronger evidence implied by settled behavior needs no new question.
If a required change or principle conflicts with an adopted rule or a human choice,
ask the human under this rule during refinement or review before requesting an
implementation change.

Refinement produces an updated issue and a shared account of consequential decisions.
It does not produce a formal contract or require a separate approval step.

The [workflow guidance](workflow.md) describes how to carry out refinement and review.

## Build and review

Developers implement the change using their usual tools. The refined issue guides the
work without freezing the agreement.

The review skill reads the issue, recorded decisions, pull-request discussion,
proposed changes, and existing contracts. It drafts or updates the contract in the
implementation pull request.

The contract describes the intended behavior established through refinement and
review—not merely whatever the implementation happens to do. Differences between the
issue, implementation, and contract become review findings.

A finding can be resolved by changing the implementation, improving the evidence, or
revising the contract. Code, checks, and contract revisions remain in the same pull
request.

Wirth identifies changed or removed claims and records the reasons for those
changes. Revising a claim is a deliberate decision, not evidence that the previous
claim held.

Review stays focused on the intended behavior, adequate evidence, preservation or
explicit revision of existing claims, and removal of unnecessary implementation
complexity.

## Contracts

Contracts are readable files in `contracts/`. Each claim links its originating issue.

Contracts contain observable **claims** and their **evidence obligations**. The
claim and its evidence remain distinct.

For example, this obligation checks the stored-items part of the claim:

```markdown
## [deleting_a_missing_item_changes_nothing] I delete an item that is already gone, and the request succeeds without changing my stored items.
Issue: https://github.com/example/store/issues/7
Tests: [tests/deleting_a_missing_item_changes_nothing/](../tests/deleting_a_missing_item_changes_nothing/)

- I read the collection after deleting an absent ID, and I see the same IDs and values as before. `delete-missing-item.test.ts::keepsStoredItems`
```

Write claims and evidence in the first person, as the software's user narrating:
what I do, then what I see. A claim is one short sentence stating what the user
observes, written for the person deciding whether to accept it and readable without
the code. It names no file, function or mechanism unless the issue makes that detail
part of the interface. All detail that qualifies the claim (rules, edge
cases, error handling, examples) belongs in its evidence obligations; each
obligation states, in one sentence, one concrete result its named test must show,
something that could fail. Use the fewest claims that still cover the issue's
required behavior. Guarantees that together define one behavior belong in one
claim. Split claims only where they could be accepted or rejected independently.

A project keeps its claims in one file, `contracts/claims.md`, read top to bottom;
split it into one file per capability only when it gets long. Each claim's ID is a
short gist of the claim in underscores, such as `failures_say_what_to_fix`, unique
across all contract files, and is also the name of the claim's test folder. Each test lives in the folder of the claim
it proves; a test that would serve two claims moves or splits.

Contract revisions update the associated evidence obligations.

Contracts make claims only about behavior that executable checks can show. Guidance and skill
behavior is stated in the documents on main and accepted through review: an observed
agent run is published in its PR with its prompt, result and pinned links, and merging
accepts it.

## Fail loudly

Wirth reports success only for what it has actually checked. Ambiguous, missing,
unexpected, or unchecked input or work prevents a success result; Wirth names the
problem and what remains unresolved. A result's scope is always explicit: structural
validation does not imply test execution, adequate evidence, successful publication,
or human acceptance.

## Shared decisions

**A developer can understand and continue the work from the documents on main:
contracts, README, specification and guidance.** They state every decision in force,
each in one place. Text outside a rule's home links to the rule rather than restating
it. It may carry the rule's wording only as a link's label; any other restatement
needs the owner's approval first. Issues and pull requests also show how the rules
came to be.

The contracts state the claims, the README and its [usage guide](usage.md) the
current interface and usage, this specification the product principles and
direction, and the workflow the process.

Issues and pull requests hold proposals and history. The issue description has five
sections: Now, the relevant current system; Change, one
independently useful outcome; After, a first-time user's experience, narrated;
Success, the observable claims and how each will be shown; and Not included.
The issue explains the user's problem, not merely a desired feature or output.
Now is its normal home; a problem clearly stated elsewhere in the issue satisfies
this requirement.
The requested implementation must fit that outcome. Each implementation PR builds
from one originating issue. A separate outcome needs its own refined issue and PR.
The description reads on its own, without disclaimers, and
refinement answers its open questions before implementation. Reasons and history go in
comments. Once a pull request exists, further choices, review findings, resolutions,
and verification results live there, linked back to the issue.

Explain each behavior's actor, action, conditions and result before shortening
the explanation. Use active verbs, state expected behavior directly, and replace
double negatives and compressed abstractions. Cut repetition while preserving the
detail needed to follow each behavior.

For example:

- Compressed: "Failure of a subset of uploads must not suppress visibility of
  successful uploads."
- Concrete: "I upload three files. Two succeed and one fails. The page lists the
  two successful uploads."

The rewrite names the user's action, states the condition and shows the visible
result.

The description states the current proposal, including the latest human answer.
Comments preserve material choices, their reasons, the affected behavior, scope, claim
or principle, and any previous choice or meaningful alternative they replace, not how
the text was drafted. Link to the original discussion when it is on GitHub. Follow the
workflow's [publication rules](workflow.md#5-process) for attribution and corrections.

Exploratory conversation and routine tool output remain local. Changes to intended
behavior, scope, verification, or what reviewers must accept are shared.

Each skill invocation reads the documents on main and the latest discussion for
the work in progress. Teammates participate through ordinary GitHub comments;
their replies are incorporated on the next invocation. Unresolved disagreement
remains visible.

Skills prepare concise updates for developer review, publish approved updates, and
return their links. Failed or deferred publication remains explicitly marked as a
local draft.

## Acceptance

A human merges the reviewed implementation, contract, and checks together. That merge
accepts the combined change.

The merged contract becomes the baseline for subsequent work. Later changes preserve
its claims or explicitly revise them through the same review process.

Wirth does not approve on behalf of a human, accept its own recommendations, or merge
changes.

