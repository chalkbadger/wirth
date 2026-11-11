# Wirth

**Build Lean Software with Verifiable Contracts**

Wirth adds two skills to Claude Code and Codex:
[refine](skills/wirth-refinement/SKILL.md) and [review](skills/wirth-review/SKILL.md).
Refine helps produce lean, coherent issues with well-defined claims. Review
helps produce [claims, tests](docs/product.md#contracts) and code that you
understand. Here's what a Wirth review of an agent's pull request turned up:

> **Claim:** stay-safe never reports a setup as clear when it couldn't check it.
>
> The report read Codex's `config.toml`, and all 123 tests passed. Working from the claim instead of the code, a Wirth review asked where else Codex loads hooks from, and found `hooks.json`. stay-safe never looked there, yet the report showed no gaps. A new test turns red on that code and green once the report flags the file.

Because the claim is written down, review can check it against the real system, not
just the code.

## Use Wirth in Claude Code or Codex

In your repository, with the `gh` CLI signed in, paste:

> Use Wirth from https://github.com/chalkbadger/wirth on this repository.

The agent installs the two skills and the `wirth` validator without changing your
repository's files. [Usage](docs/usage.md) has each agent's install commands and
approval advice.

To start Wirth with a plain request, add this line to your repository's AGENTS.md,
and to its CLAUDE.md if it has one:

```text
This repository uses Wirth: https://github.com/chalkbadger/wirth
```

Then ask "refine #12" before building, or "review PR #34" once the agent has opened a
pull request. Without the line, these requests get the agent's ordinary help;
[Usage](docs/usage.md#name-a-skill) shows how to name a skill instead. [Merging the
reviewed PR accepts the change](docs/product.md#acceptance).

## What works today

- The [refine](skills/wirth-refinement/SKILL.md) and
  [review](skills/wirth-review/SKILL.md) skills.
- `wirth validate`, which [checks contract structure only](contracts/claims.md);
  [Usage](docs/usage.md#local-contract-validation) shows how to run it.
- `wirth check` [is not built yet](https://github.com/chalkbadger/wirth/issues/17).

## Why Wirth exists

Wirth is the review tool in [chalkbadger](https://github.com/chalkbadger), whose
mission is to promote AI safety using adversarial peer review.

In Wirth, owners use [refine](skills/wirth-refinement/SKILL.md) to make sure every
issue is coherent and [names one small change to implement](docs/product.md#refine-the-issue)
before coding begins. After coding produces a candidate,
[review](skills/wirth-review/SKILL.md) makes sure [each claim names a test that could
fail](docs/product.md#contracts), and also [plants bugs to see whether the tests catch
them](docs/workflow.md#2-evidence). Tests that prove nothing don't count, so [tests
without a claim are cut](docs/workflow.md#claims-and-evidence), and [expected results
copied from the code's own output aren't evidence](docs/workflow.md#adequate-tests).
Review also [recommends accepting new behavior only if it is required for a claim to
be true](docs/workflow.md#4-simplicity). When owners are satisfied
that the contract expresses their intent and the tests properly define that behavior,
[they merge code, tests and contract together](docs/product.md#acceptance). Wirth is
built with Wirth; its own claims are in [`contracts/claims.md`](contracts/claims.md).

Loosely inspired by [Niklaus Wirth](https://en.wikipedia.org/wiki/Niklaus_Wirth) and
his "A Plea for Lean Software".

## Contribute

Share feedback or propose a change through [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
