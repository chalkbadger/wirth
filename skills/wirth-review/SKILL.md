---
name: wirth-review
description: Review a GitHub pull request, draft or revise its contract, and carry findings through correction with the existing coding agent and GitHub access (a GitHub connection or the signed-in `gh` CLI). Use when the owner names Wirth Review or wirth-review, or asks to review a PR in a repository whose AGENTS.md or CLAUDE.md links to https://github.com/chalkbadger/wirth, including follow-up requests to address its findings or review the revised work. In other repositories a plain review request does not invoke it.
---

# Wirth review

Use the existing coding agent and GitHub access (a GitHub connection or the signed-in `gh` CLI)
for the repository named in the request. Keep review and correction in the current conversation.

1. Resolve the PR identified by the owner or the current conversation. Ask for
   its number or URL if it is missing or ambiguous.
2. Read the current [README](https://github.com/chalkbadger/wirth/blob/main/README.md),
   [specification](https://github.com/chalkbadger/wirth/blob/main/docs/product.md),
   [workflow](https://github.com/chalkbadger/wirth/blob/main/docs/workflow.md), and every
   [contract](https://github.com/chalkbadger/wirth/tree/main/contracts) on `main`, and the
   named repository's README and contracts on its default branch.
   Read the PR's current description, complete discussion, changes and proposed
   contracts, plus its originating issue and all comments. Identify the reviewed
   head commit and recover prior decisions and unresolved findings.
3. Use one reviewer to carry out the
   [review passes](https://github.com/chalkbadger/wirth/blob/main/docs/workflow.md#review-passes)
   in order, one at a time. Draft or revise the contract in the implementation PR
   under [Build and review](https://github.com/chalkbadger/wirth/blob/main/docs/product.md#build-and-review).
   Keep each finding identifiable so corrections can refer back to it.
4. Prepare the findings and contract changes for publication under
   [Shared decisions](https://github.com/chalkbadger/wirth/blob/main/docs/product.md#shared-decisions)
   and its linked publication rules. Re-read the PR head and discussion before
   writing; reconcile intervening changes rather than overwriting them. Publish
   authorized updates and read back their content. Return their GitHub links.
5. When asked to address findings, give the existing coding agent the recorded
   findings, affected revision and current repository context directly. If you
   are that agent, continue with those records. Do not ask the owner to assemble
   a brief or copy findings. Resolve the requested work under the
   [decision rule](https://github.com/chalkbadger/wirth/blob/main/docs/product.md#refine-the-issue);
   record each resolution against its finding in the same PR.
6. After corrections, verify the published revision under the
   [CONTRIBUTING procedure](https://github.com/chalkbadger/wirth/blob/main/CONTRIBUTING.md#development-and-review).
   Re-read the current GitHub context and review the revised work through the
   passes above. Keep remaining findings, disagreements, owner decisions and
   the next step visible in the PR.
7. Apply [Fail loudly](https://github.com/chalkbadger/wirth/blob/main/docs/product.md#fail-loudly)
   to unavailable context, handoffs, checks or publication. Identify unperformed
   work and unpublished drafts. Follow
   [Acceptance](https://github.com/chalkbadger/wirth/blob/main/docs/product.md#acceptance);
   a review result is not human acceptance.
