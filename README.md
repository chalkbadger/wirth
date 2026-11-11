# Wirth

**Agents write tests that pass and prove nothing. Wirth makes every claim name a test that could fail.**

An agent created a PR in stay-safe and all 123 existing and new tests passed. Because Wirth insists on claims, review started from the new claim — "never report a setup as clear when it couldn't check it" — asked where else Codex loads hooks, and found `hooks.json`, which stay-safe never read. A new test failed on that code and passed once the report flagged the file.

Wirth is two skills for Claude Code and Codex:

- **Refine** turns an issue into one small change with claims you can test.
- **Review** checks a pull request against those claims: it plants bugs to see whether
  the tests catch them, cuts tests that back no claim, and flags behavior no claim needs.

You merge code, tests and claims together; merging is acceptance.

## Try it

In your repository, with the `gh` CLI signed in, paste into Claude Code or Codex:

> Use Wirth from https://github.com/chalkbadger/wirth on this repository.

The install also adds `wirth validate`, which checks contract structure only;
`wirth check`, which would run your checks, [isn't built yet](docs/product.md#verification).

To start Wirth with a plain request, add this line to your repository's AGENTS.md
(and CLAUDE.md, if it has one):

```text
This repository uses Wirth: https://github.com/chalkbadger/wirth
```

Then ask "refine #12" before building, or "review PR #34" after.
[Usage](docs/usage.md) has install commands, approval advice, and how to name a skill directly.

## Why Wirth exists

Wirth is the refine and review tool in [chalkbadger](https://github.com/chalkbadger), whose
mission is to promote AI safety using adversarial peer review.

Loosely inspired by [Niklaus Wirth](https://en.wikipedia.org/wiki/Niklaus_Wirth) and
his "A Plea for Lean Software".

## Contribute

Share feedback or propose a change through [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
