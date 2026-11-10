# Using Wirth

## Install

Paste [the README's prompt](../README.md#use-wirth-in-claude-code-or-codex) into
Claude Code or Codex, and the agent installs the two skills and the `wirth`
validator. Approve each install command once; don't choose "don't ask again". In
Claude Code's auto mode, the installs may run without asking.

- **Claude Code:** the agent runs `claude plugin install wirth --marketplace chalkbadger/wirth`;
  then you type `/reload-plugins` to load the skills.
- **Codex:** use the built-in `$skill-installer` to install `skills/wirth-refinement`
  and `skills/wirth-review` from `chalkbadger/wirth`. They load on the next turn.
- **Both:** install the validator as in [Local contract validation](#local-contract-validation).

## Name a skill

Naming a skill works in any repository, with or without the README's opt-in line:

- **Claude Code:** `/wirth:wirth-refinement refine #12`
- **Codex:** `Use $wirth-refinement to refine #12`

## Local contract validation

Python 3.11 or newer is required. Install Wirth with [pipx](https://pipx.pypa.io/):

```sh
pipx install git+https://github.com/chalkbadger/wirth
```

Then, from your project's root, run:

```sh
wirth validate
```

[No Git repository or runner configuration is required.](../contracts/claims.md)

Put Markdown contracts directly in `contracts/`, for example
`contracts/claims.md`:

```markdown
# Delivery service

## [one_receipt_per_order] I place an order and receive exactly one receipt.
Issue: https://github.com/example/service/issues/1
Tests: [tests/one_receipt_per_order/](../tests/one_receipt_per_order/)

- I complete an order, and one receipt arrives. `test_delivery.py::test_completed_order_sends_one_receipt`
- I retry a declined payment until it succeeds, and still only one receipt arrives. `test_delivery.py::test_retried_payment_sends_one_receipt`
```

The [claim rule](product.md#contracts) says how to write claims and evidence and
how to lay out contracts and test folders. [What validation checks and what a pass
means](../contracts/claims.md) are stated as claims in Wirth's own contract.
