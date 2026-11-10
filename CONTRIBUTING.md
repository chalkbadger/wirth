# Contributing to Wirth

Follow the [shared participation policy](docs/participation.md) for use, feedback,
and upstream changes.

## Share feedback

Open a [Wirth issue](https://github.com/chalkbadger/wirth/issues/new) for a bug,
question, review, or challenge. You can also use an issue to link findings
published elsewhere.

## Propose a change

Open or identify the originating issue before implementing a change to Wirth.
Use the [implementation workflow](docs/workflow.md#claims-and-evidence) for scope
readiness, claims, and evidence, and [development and review](#development-and-review)
for the check commands and published-revision verification record.

The [review passes](docs/workflow.md#review-passes) guide review. The
[publication rules](docs/workflow.md#5-process) govern attribution and corrections.
[@weiks](https://github.com/weiks) is Wirth's accepting owner;
[acceptance](docs/product.md#acceptance) defines what the merge accepts.

## Development and review

Follow [the workflow](docs/workflow.md). Git is needed for the development tests. Run:

```sh
python3 -m unittest discover -s tests
```

For Wirth's own PRs, a passing [check](.github/workflows/checks.yml) on the PR's
latest push replaces the
[verification procedure](docs/workflow.md#record-execution-results); link that run
in the PR. Follow the procedure when no check ran on the latest push, for example
while a fork PR waits for approval. In Wirth's own checkout, the procedure's
commands are the tests above and `python3 -m wirth validate`.

References to an *archived* issue or PR point to the private repository that holds this project's earlier working history.
