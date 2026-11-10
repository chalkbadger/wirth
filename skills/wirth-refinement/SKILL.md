---
name: wirth-refinement
description: Refine a GitHub issue with its owner and publish the agreed result through the existing GitHub access (a GitHub connection or the signed-in `gh` CLI). Use when the owner names Wirth Refinement or wirth-refinement, or asks to refine an issue in a repository whose AGENTS.md or CLAUDE.md links to https://github.com/chalkbadger/wirth. In other repositories a plain refine request does not invoke it; implementation requests never do.
---

# Wirth refinement

Use the existing GitHub access (a GitHub connection or the signed-in `gh` CLI) for the repository named in the request.
Keep this invocation to refinement in the current conversation.

1. Resolve the issue number or URL supplied by the owner. Ask for it if missing;
   do not choose an issue or another repository.
2. Read the current [README](https://github.com/chalkbadger/wirth/blob/main/README.md),
   [specification](https://github.com/chalkbadger/wirth/blob/main/docs/product.md),
   [workflow](https://github.com/chalkbadger/wirth/blob/main/docs/workflow.md), and every
   [contract](https://github.com/chalkbadger/wirth/tree/main/contracts) on `main` through
   GitHub, and the named repository's README and contracts on its default
   branch. Use these live sources, not bundled copies or conversation memory.
3. Read the issue's current description, all comments, and any linked
   implementation PR and its discussion. Recover the current proposal and prior
   decisions from those records; follow relevant repository references as needed.
4. Carry out [Refinement](https://github.com/chalkbadger/wirth/blob/main/docs/workflow.md#refinement)
   with the owner, applying
   [Shared decisions](https://github.com/chalkbadger/wirth/blob/main/docs/product.md#shared-decisions)
   and the linked decision and publication rules. Prepare the complete proposed
   issue update and decision comment for the owner's review.
5. Before publishing approved text, re-read the target issue and its discussion.
   Reconcile intervening changes and obtain approval for any revised text. Publish
   the approved update and decision comment using the existing GitHub access,
   at the location required by Shared decisions.
6. Read back the published result and return its GitHub links. Apply
   [Fail loudly](https://github.com/chalkbadger/wirth/blob/main/docs/product.md#fail-loudly)
   to unavailable reads, failed writes, or incomplete publication; identify each
   unpublished draft separately from any successful write.
