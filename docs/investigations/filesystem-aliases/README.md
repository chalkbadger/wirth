# Filesystem alias investigation

[Issue #6](https://github.com/chalkbadger/wirth/issues/6) asks whether an allowed spelling can reach a differently named file and pass validation. On the recorded case-insensitive APFS configuration, all five demonstrated spelling aliases fail validation. No incorrect pass was demonstrated. No Windows execution environment was available; the NTFS investigation moved to [#7](https://github.com/chalkbadger/wirth/issues/7).

## Revisions and scope

| Role | Exact revision |
|---|---|
| Implementation and contract selected from live main at investigation start | `1079e7dda120253dfaa41798aaba2186b4a09fab` |
| Selected validator blob | `3c679b4f2329896144812751740e5f606bd0d0db` |
| Selected contract blob | `e58e3a01c846b996948da543fa0ae74ce02efa3c` |

Every native observation below runs the selected **main** validator. Its [contract](https://github.com/chalkbadger/wirth-archive/blob/1079e7dda120253dfaa41798aaba2186b4a09fab/contracts/local-validation.md) and [pre-filesystem path checks](https://github.com/chalkbadger/wirth-archive/blob/1079e7dda120253dfaa41798aaba2186b4a09fab/wirth/validate.py#L38) govern the investigation. The [unmerged #5 implementation](https://github.com/chalkbadger/wirth-archive/blob/b9ffb00549411e89ad10a221ff2fd392b63c2505/wirth/validate.py#L52) is separately classified; it is not presented as main behavior. Main remained at the selected revision during the initial run.

No validator, test or contract is changed. The two deliverables are this bounded report and [the observation script](probe-apfs.py). Full raw observations, source inventories and execution logs are published in the originating PR. The script records observations; exit zero means the collection finished, not that all platforms or aliases were verified.

## Recorded native configuration

- macOS 26.6, build 25G72; Darwin 25.6.0; arm64.
- CPython `3.15.0 (main, Oct 9 2026, 11:16:41) [Clang 21.0.0 (clang-2100.3.34.2)]`.
- The temporary fixtures are on `/dev/disk3s5`, mounted at `/System/Volumes/Data` as `apfs, local, journaled, nobrowse, protect, root data`.
- Case insensitivity is established by equal device/inode identities and `samefile` for the differently cased requests, while directory listings retain their original spelling.
- `diskutil info -plist` fails because the DiskManagement framework is unavailable. The record retains that error. `df`, the selected mount line, and actual alias behavior establish the configuration used; no unavailable volume-option result is invented.
- No Windows host, native NTFS mount or Windows execution tool was available. No NTFS case-sensitivity setting, short-name setting or validator result was observed.

## Candidate dispositions

The script first isolates the selected revision's path checks with a controlled resolver stub. This is **lexical classification only**, not a native alias experiment. Excluded requests receive no native fixture. For allowed requests, unmodified filesystem APIs and an unmodified validator subprocess produce the native record. Every native row includes requested and created paths, each parent listing, exact membership, object identity, validator exit/stdout/stderr, and an exact-spelling control.

| Candidate family and concrete samples | Selected main path rules | Native APFS result | Windows NTFS disposition |
|---|---|---|---|
| Final/intermediate/discovery case: `checks/report.py` vs `checks/Report.py`; `checks/result.py` vs `Checks/result.py`; `contracts` vs `Contracts` | Evidence requests allowed; discovery uses its required literal | All resolve to the differently spelled entry and are rejected by exact directory membership. Exact ASCII controls pass. | Native run missing. |
| Non-ASCII requested normalization forms: NFC `café.py`, NFD `cafe\u0301.py` | Excluded before filesystem lookup | Not probed; exclusion is not proof of filesystem behavior. | Excluded by the same selected lexical rule; native behavior unclaimed. |
| ASCII request reaching Unicode storage: `K.py` vs U+212A Kelvin sign; `s.py` vs U+017F long s | ASCII requests allowed | Both reach the stored Unicode file; listing preserves its Unicode spelling; validator rejects the ASCII spelling. Exact Unicode labels are rejected by the character rule. | Native result missing for allowed ASCII requests. |
| Trailing dots: `report.py.`, `report.py...`, `checks./report.py`; reverse case of stored `report.py.` requested as `report.py` | Allowed | No alias resolves in these fixtures; validator reports missing path. Exact stored-spelling controls pass. | Gap: selected Windows API normalization and actual identities must be observed. |
| Trailing ASCII space: `checks/report.py ` | Excluded | Not probed. | Excluded request; no filesystem observation claimed. |
| Typical tilde short name: `LONGFI~1.PY` | Excluded | Not probed. | This spelling is excluded; this does not exclude every possible short name. |
| Non-tilde short-name candidate: `SHORT.PY` for `LongFilename.py` | Allowed | No alias in APFS fixture; missing-path failure. Exact long-name control passes. | Gap: query real short names/settings; a legal short name need not contain a tilde. |
| Reserved names: `NUL`, `CON.txt`, `COM1`, `LPT1` | Allowed | These are exact regular filenames here and pass. They do not demonstrate Windows device behavior. | Gap: native device-name resolution, type and membership remain untested. |
| Alternate streams: `report.py:stream`, `report.py::$DATA` | Excluded | Not probed. | Stream syntax is excluded; no stream access performed. |
| Git metadata spellings: `.GIT/config`, `.git./config`, `.git.../config` | Excluded by the selected Git-directory check | Not probed. | These requests are excluded independently of Windows resolution. |
| Git short/ignorable variants: `GIT~1/config`, `.g\u200cit/config` | Excluded | Not probed. | These particular requests are excluded. |
| Non-tilde Git short-name candidate: `GITDIR/config` for `.git/config` | Allowed | No alias in APFS fixture; missing-path failure. Exact `.git/config` control is intentionally rejected by the Git-directory rule. | Gap: a native assigned/discovered short name without a tilde must be checked; no universal Git-alias conclusion. |

The ASCII-to-Unicode cases matter: rejecting non-ASCII **requests** does not by itself prevent an ASCII request from reaching a Unicode-named entry. The native membership checks, not the lexical filter, reject those two demonstrated aliases.

Twenty-six evidence labels were classified: 11 lexical exclusions and 15 native fixtures. A separate discovery-directory alias/control makes 16 native fixture groups. Four evidence aliases plus the discovery alias actually resolve under a different spelling; all five fail with nonzero exit and empty stdout. Five other native groups are exact-name controls rather than aliases (the four reserved-looking filenames and `.github/check.py`). Six allowed mismatch candidates do not resolve here. No mock or skipped test is counted as a resolving alias.

## Demonstrated alias observations

| Request | Actual listing entry | Requested and stored object identity | Validator result |
|---|---|---|---|
| `checks/report.py` | `Report.py` in `checks/` | Equal device/inode; `samefile=True` | Exit 1; line 5 names `report.py` spelling mismatch. |
| `checks/result.py` | `Checks` in project root | Equal device/inode; `samefile=True` | Exit 1; line 5 names `checks` spelling mismatch. |
| `checks/K.py` | `\u212a.py` in `checks/` | Equal device/inode; `samefile=True` | Exit 1; line 5 names `K.py` spelling mismatch. |
| `checks/s.py` | `\u017f.py` in `checks/` | Equal device/inode; `samefile=True` | Exit 1; line 5 names `s.py` spelling mismatch. |
| `contracts` | `Contracts` in project root | Equal device/inode; `samefile=True` | Exit 1; discovery diagnostic names `contracts` spelling mismatch. |

Raw device/inode values and complete messages are in the PR's JSON observations. They are run-specific identifiers, not expected constants. Positive exact ASCII controls return the structural-only message. Exact Unicode and Git-directory controls intentionally fail their own lexical rules; those failures are recorded rather than treated as unexpected alias results.

## Sources and their limits

- Apple's [current filesystem overview](https://developer.apple.com/documentation/technologyoverviews/files-and-directories) describes configurable APFS case sensitivity. Its [archived APFS filename FAQ](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html) explains case/normalization preservation and normalization-insensitive lookup in the versions it covers. The FAQ is retired; this report's current conclusions come from the recorded native observations, not an assumption that every detail of the old document applies to macOS 26.6.
- Python documents [directory-name enumeration](https://docs.python.org/3.15/library/os.html#os.listdir), [lstat](https://docs.python.org/3.15/library/pathlib.html#pathlib.Path.lstat), and [samefile identity comparison](https://docs.python.org/3.15/library/os.path.html#os.path.samefile). The probe records both listing and object identity before running validation.
- Microsoft's [naming documentation](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file) identifies case behavior, reserved device names, trailing-dot/space restrictions, and short-name variability. These source facts motivate the outstanding NTFS probes; they are not observations from a Windows run.
- [GetShortPathNameW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getshortpathnamew), [fsutil 8dot3name](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-8dot3name), and [fsutil file setshortname](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-file) support querying the configuration and actual short name rather than assuming a tilde alias.
- Microsoft's [stream naming documentation](https://learn.microsoft.com/en-us/windows/win32/fileio/file-streams) supplies the colon-delimited candidates. Their selected-rule exclusion is source/lexical analysis, not a native stream result.

Sources were inspected on November 6, 2026. No third-party question or message was sent.

## Separate unmerged rule analysis

The optional `--proposed-source` column observes only the pre-filesystem rules from the stacked `issue-65` revision. Under that unmerged #5 implementation, trailing-dot requests and hidden paths are rejected earlier. Case variants, ASCII requests for Unicode-stored names, non-tilde short-name candidates and ASCII reserved-device names still require filesystem handling. Both revisions exclude the sampled non-ASCII requests, tilde short names, spaces and stream syntax. This comparison supplies no native result for the unmerged validator and makes no change to #5's rules.

## Reproduction

Obtain an exact checkout of selected main `1079e7dda120253dfaa41798aaba2186b4a09fab` and an exact checkout of the PR head recorded in its verification comment. The script refuses a selected source whose validator/contract blob hashes differ. From the PR checkout on macOS, use an existing writable directory on the APFS volume being assessed:

```sh
python3 docs/investigations/filesystem-aliases/probe-apfs.py \
  --source /absolute/path/to/selected-main \
  --probe-parent /absolute/path/on/apfs \
  --proposed-source /absolute/path/to/pr-checkout > apfs-observations.json
```

Each validation subprocess has a 10-second timeout; the recorded outer run also had a 60-second timeout. Temporary fixtures are created beneath the chosen probe parent and removed afterward. The native probe rejects non-macOS use; it is not an untested Windows harness. It does not change volume settings, send network traffic or modify the selected source.

To finish NTFS work, use one native Windows configuration, record OS/Python, volume identity and NTFS format, directory case-sensitivity and 8dot3 settings, then filter requested names through the same pinned main rules. Query real short names instead of fabricating them. For every remaining case record requested spelling, full parent listing, native object identity/type, validator exit/output and exact-spelling control. Include ASCII-to-Unicode possibilities, trailing-dot behavior, non-tilde short names, reserved devices and Git metadata aliases. Run potentially blocking operations in timed child processes; setup failures or absent aliases remain gaps. This is outstanding work, tracked in [#7](https://github.com/chalkbadger/wirth/issues/7), not an executed Windows procedure.

## Verification and open work

The selected-main suite passes 42/42 tests with zero skips on the recorded macOS run. Structural validation passes, and all tracked source hashes remain unchanged. The PR records final published-head checks separately.

This investigation changes no executable product behavior, so a test-first failing implementation stage and an author production-mutation list are inapplicable. All four existing contract IDs are kept. Earlier implementation/evidence findings remain open and are not repaired by this report.

No demonstrated incorrect pass needs a product-fix follow-up from this run. The native NTFS configuration is tracked in [#7](https://github.com/chalkbadger/wirth/issues/7). Conclusions cover only the listed requests, selected main revision and recorded APFS configuration; they do not establish exhaustive alias rejection, future OS behavior, Git-index agreement or GitHub-link correctness.
