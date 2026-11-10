# Wirth

## [catches_incomplete_contracts] I run `wirth validate`, and it fails when a contract is incomplete or its evidence does not point at a test that exists.
Issue: https://github.com/chalkbadger/wirth/issues/1
Tests: [tests/catches_incomplete_contracts/](../tests/catches_incomplete_contracts/)

- I run it from my project root, and it checks the contracts in `contracts/`. `test_current_contract_set.py::test_command_finds_contracts_in_the_project_contracts_folder`
- I have several contracts, and every one is checked. `test_current_contract_set.py::test_every_current_contract_is_checked`
- I run it in a subfolder of a repository, and it does not use the contracts of a parent folder. `test_current_contract_set.py::test_parent_contracts_are_not_discovered`
- I keep a README and a nested `contracts/` folder in my project, and neither is read as a contract. `test_current_contract_set.py::test_root_readme_and_nested_contracts_are_not_discovered`
- I edit a committed contract without committing, and the result follows the edited text. `test_current_contract_set.py::test_uncommitted_edits_follow_current_content_in_both_directions`
- I add a contract without committing it, and it is checked. `test_current_contract_set.py::test_untracked_invalid_contract_is_checked`
- I delete my only contract, and it reports that no contracts were found. `test_current_contract_set.py::test_deleting_last_committed_contract_reports_empty`
- I write several claims, each with its Issue, Tests and evidence lines, and it passes. `test_content.py::test_multiple_claims_and_evidence`
- I leave out the title, a claim, its text, an Issue URL, a Tests link or a result, and it fails at that line. `test_content.py::test_required_content`
- I leave a claim without evidence before the next claim, and it fails at the empty claim. `test_content.py::test_empty_claim_before_another_claim_fails`
- I save a contract with Windows or old Mac line endings, or without a final newline, and it passes. `test_content.py::test_byte_written_line_endings_and_no_final_newline_pass`
- I reuse a claim ID in another contract file, and it fails, naming where the ID was first used, because each claim has its own tests folder. `test_claim_ids.py::test_same_id_in_different_contracts_fails`
- I repeat a claim ID within one contract, even with another claim between, and it fails at the repeat. `test_claim_ids.py::test_duplicate_ids_fail_even_when_separated_by_another_claim`
- I leave a claim ID empty, or use anything but lowercase letters, digits, `_` and `-` after a letter or digit, and it fails. `test_claim_ids.py::test_missing_invalid_and_uppercase_claim_ids_fail`
- I start a claim ID with a digit, and it passes. `test_claim_ids.py::test_digit_initial_claim_id_passes`
- I put an `Issue:` line and then a `Tests:` line directly under each claim heading, citing a different issue per claim, and it passes. `test_issue_links.py::test_each_claim_cites_its_own_issue`
- I leave out either line, swap them or move one lower, and it fails at the claim heading. `test_issue_links.py::test_issue_then_tests_lines_directly_follow_each_claim_heading`
- I keep a single `Issue:` line at the top of the file, and it tells me Issue lines now go under each claim heading and shows the shape. `test_issue_links.py::test_file_level_issue_line_shows_the_new_shape`
- I write an Issue line that is not an `https://github.com/<owner>/<repo>/issues/<positive integer>` URL, and it fails. `test_issue_links.py::test_issue_url_format`
- I link an issue in a repository with capitals or dots in its name, and it passes. `test_issue_links.py::test_mixed_case_dotted_repository_and_multiple_digits_pass`
- I link a tests folder that does not exist, or a file, and it fails at the Tests line. `test_check_references.py::test_tests_folder_must_be_an_existing_directory`
- I write a tests folder link whose target is not `../` followed by the displayed path, and it fails. `test_check_references.py::test_tests_folder_link_target_is_exactly_parent_then_displayed_path`
- I write the tests folder path without a final `/`, and it fails. `test_check_references.py::test_tests_folder_path_ends_with_a_slash`
- I name the tests folder after the claim ID under any parent folder, and it passes; I name it anything else, even a name that only starts or ends with the ID, and it fails, naming both. `test_check_references.py::test_tests_folder_is_named_after_the_claim_id`
- I put the tests folder under a hidden folder or one whose name breaks the naming rule, and it fails, naming that folder. `test_check_references.py::test_tests_folder_path_follows_the_naming_rule`
- I link a tests folder that is a symlink or sits under one, and it fails. `test_check_references.py::test_tests_folder_must_not_be_or_pass_through_symlinks`
- I end each result with `file::test_name`, the file relative to the tests folder, and it passes. `test_evidence_items.py::test_items_name_a_file_in_the_tests_folder_and_a_test`
- I end a result without a test in a code span, and it fails at that line. `test_evidence_items.py::test_item_must_end_with_a_test_code_span`
- I give a test name without its file, and it tells me to write `file::test_name`. `test_evidence_items.py::test_test_must_name_its_file_and_test`
- I give a test name that does not match `[A-Za-z_][A-Za-z0-9_]*`, and it fails, showing that rule. `test_evidence_items.py::test_test_name_must_be_an_identifier`
- I paste a test with its class, as pytest prints it, and it tells me to drop the class. `test_evidence_items.py::test_test_name_without_its_class`
- I cite one test for two results under a claim, and it passes, because one test can check several results. `test_evidence_items.py::test_one_test_may_prove_several_results`
- I keep an evidence line in the old one-link-per-line format, and it tells me the format changed and shows the new shape. `test_evidence_items.py::test_old_one_link_per_line_format_shows_the_new_shape`
- I keep a test file link on its own line, as in the grouped format, and it tells me the format changed and shows the new shape. `test_evidence_items.py::test_grouped_file_line_format_shows_the_new_shape`
- I point a test file outside the tests folder with `..` or an absolute path, and it fails. `test_evidence_items.py::test_item_file_stays_inside_the_tests_folder`
- I break a claim's tests folder link, and I see only that error, even when an earlier claim's folder holds the cited file; a missing test file gives only its own error. `test_evidence_items.py::test_items_under_a_failed_tests_folder_report_only_its_error`
- I cite a test file that does not exist, or a folder, and it fails at that line. `test_check_references.py::test_references_require_existing_regular_files`
- I cite a test file that is a symlink or sits under one, and it fails. `test_check_references.py::test_evidence_must_not_be_or_pass_through_symlinks`
- I cite a named pipe, and it fails without waiting on the pipe. `test_check_references.py::test_check_fifo_fails_without_blocking`
- I cite a test file nested several folders deep, and it passes. `test_check_references.py::test_nested_regular_evidence_file_passes`
- I write a path that treats a file as a folder, and it fails. `test_check_references.py::test_regular_file_cannot_be_a_directory_component`
- I name each path segment to match `[A-Za-z0-9]+([._-][A-Za-z0-9]+)*`, and it passes. `test_names.py::test_evidence_segments_accept_ascii_alphanumerics_and_single_internal_separators`
- I name contract files by the same rule, and they pass. `test_names.py::test_contract_filenames_accept_ascii_alphanumerics_and_single_internal_separators`
- I use a path segment that breaks the rule, such as `.github` or `.gitignore`, and it fails, naming that segment. `test_names.py::test_evidence_rejects_invalid_segments_and_names_each_segment`
- I write an empty, `.` or `..` path segment, or an absolute path, and it fails. `test_names.py::test_evidence_rejects_empty_and_dot_segments`
- I give a contract file a name that breaks the rule, and it fails, naming the file. `test_names.py::test_contract_filenames_reject_invalid_names_and_identify_them`
- I cite `.gitignore`, and the command fails without reporting success. `test_names.py::test_invalid_name_has_command_failure_without_false_success`
- On a filesystem that ignores case, I spell a test path in the wrong case, and it fails. `test_path_spelling.py::test_wrong_case_is_rejected_on_a_filesystem_that_accepts_it`
- On a filesystem that ignores case, I name the folder `Contracts`, and it fails. `test_path_spelling.py::test_discovery_directory_spelling_is_exact_when_filesystem_ignores_case`
- I spell a path differently from the entry its folder lists, and it fails, naming that entry. `test_path_spelling.py::test_exact_membership_with_controlled_directory_listings`
- I cite a Python test that has a `def` or `async def` line, at any indentation, and it passes. `test_test_names.py::test_python_test_needs_a_def_at_any_indentation`
- I cite a Python test that is only called, commented out, assigned or a prefix of another name, and it fails. `test_test_names.py::test_python_test_without_its_def_fails`
- I cite a test in a file that is not Python, and it passes only if the name appears there as a whole word. `test_test_names.py::test_other_files_need_the_name_as_a_whole_word`
- I cite tests in two files, and each name is looked up in its own file. `test_test_names.py::test_each_item_is_checked_against_its_own_file`
- I run `wirth validate` on a contract whose test was renamed, and it names the missing test and its line. `test_test_names.py::test_renamed_test_is_named_with_its_line`
- I write titles, claims and results using ASCII letters, digits, spaces, `. , ; : ' " ( ) ? ! -` and nonempty printable ASCII code spans, and they pass. `test_plain_text.py::test_ascii_words_punctuation_and_code_spans_pass`
- I use any other character outside a code span, an unpaired backtick, no letter or digit at all, or `www.` outside a code span, and it fails at that line. `test_plain_text.py::test_title_claim_and_result_follow_the_ascii_rule`
- I write a claim heading with only its ID, and it reports that the claim is blank. `test_plain_text.py::test_bare_claim_heading_reports_blank_text_cleanly`

## [failures_say_what_to_fix] When validation fails, I see every problem with its file and line, and the command exits unsuccessfully.
Issue: https://github.com/chalkbadger/wirth/issues/1
Tests: [tests/failures_say_what_to_fix/](../tests/failures_say_what_to_fix/)

- I run `wirth validate` on a broken contract, and it exits nonzero, prints each problem with its line and prints no success message. `test_command_errors.py::test_invalid_content_reports_lines_without_success`
- I run it with no command, another command or an extra option, and it prints usage and exits nonzero. `test_command_errors.py::test_only_validate_command`
- I break two contracts, and I see the errors of both. `test_input_errors.py::test_errors_are_preserved_across_fields_and_contracts`
- I break the title, and I still see the errors after it. `test_input_errors.py::test_bad_title_does_not_hide_later_errors`
- I leave out a claim's Issue line, and I still see the claim and its errors. `test_input_errors.py::test_missing_issue_does_not_hide_claim_or_its_errors`
- I give a contract an invalid file name, and I still see the errors inside it and in other contracts. `test_input_errors.py::test_invalid_contract_filename_preserves_content_errors`
- I cite a test path with a colon and parentheses next to a bad result, and I see an error for each. `test_input_errors.py::test_evidence_name_delimiters_do_not_hide_independent_result_errors`
- I cite an invalid test path next to a blank result, and I see both errors and no missing-evidence error. `test_input_errors.py::test_invalid_evidence_name_preserves_result_error_without_missing_evidence`
- I break a test reference and its result, and I still see a later claim's errors. `test_input_errors.py::test_evidence_errors_retain_later_claim_errors`
- I write a result without a test, and I still see a later claim's errors. `test_input_errors.py::test_malformed_evidence_retains_later_claim_and_reference_errors`
- I save a contract that is not UTF-8, and the error names that file. `test_input_errors.py::test_invalid_utf8_names_contract`
- I run it when one contract cannot be read, and I see that file named while the others are still checked. `test_input_errors.py::test_unreadable_contract_names_file_and_other_contract_is_checked`
- I run it when a cited test file cannot be read, and I see the line that cites it while the other contracts are still checked. `test_input_errors.py::test_unreadable_evidence_file_names_its_line_and_other_contract_is_checked`
- I run it when a folder on a test path cannot be listed, and I see that at its line along with other contracts' errors. `test_input_errors.py::test_denied_evidence_listing_retains_other_contract_error`
- I put an unexpected entry in `contracts/`, and I still see the errors in the next contract. `test_input_errors.py::test_entry_failures_retain_later_contract_errors`
- I have no contracts, or no `contracts/` folder, and it reports that none were found instead of passing. `test_input_errors.py::test_no_contracts_missing_or_empty_directory`
- I run it when `contracts/` cannot be read, and it says it cannot discover the folder. `test_input_errors.py::test_unreadable_contracts_directory_is_reported`
- I leave out the title, and I see one error, at the first claim in its place. `test_recovery.py::test_missing_title_reports_only_title_at_first_claim`
- I start with a blank claim, and I also see that the claim is blank. `test_recovery.py::test_first_blank_claim_retains_its_own_error`
- I start with a top-level Issue line where the title belongs, and I see both errors and the claim's own. `test_recovery.py::test_file_level_issue_in_title_position_is_reported`
- I write a malformed claim heading, and I see one format error, without missing-evidence, Issue or Tests errors. `test_recovery.py::test_malformed_heading_has_no_missing_evidence_or_issue_cascade`
- I write a malformed heading, and I still see the errors before it. `test_recovery.py::test_malformed_heading_keeps_earlier_errors`
- I write evidence right after a malformed heading, and I still see the evidence errors. `test_recovery.py::test_evidence_directly_after_malformed_heading_keeps_its_errors`
- I leave a well-formed claim without evidence after a malformed one, and I see that it has no evidence. `test_recovery.py::test_missing_evidence_is_retained_for_parsed_claims`
- I leave out the title and leave the first of two claims without evidence, and I see both. `test_recovery.py::test_nonfinal_claim_without_evidence_is_reported_after_missing_title`
- I leave out the opening lines before a claim without evidence, and I still see that it has no evidence. `test_recovery.py::test_missing_evidence_survives_each_opening_recovery`
- I start with a claim and leave blank lines, and I still see the later claim and result errors. `test_recovery.py::test_later_errors_survive_first_claim_recovery_and_blank_lines`
- I write a malformed heading and blank lines, and I still see the later errors. `test_recovery.py::test_later_errors_survive_malformed_heading_and_blank_lines`
- I run `wirth validate` on a contract missing its title, and it prints the later errors too. `test_recovery.py::test_command_retains_later_errors_after_missing_title`
- I leave blank lines between every part of a valid contract, and it passes. `test_recovery.py::test_valid_contract_with_blank_lines_passes`

## [a_pass_means_well_formed_only] When validation passes, I know my contracts are well formed and nothing more: no tests ran.
Issue: https://github.com/chalkbadger/wirth/issues/1
Tests: [tests/a_pass_means_well_formed_only/](../tests/a_pass_means_well_formed_only/)

- I cite a test file that would fail if run, in a folder with no runner configuration and no Git repository, and run `wirth validate`; it exits zero, says checks were not run and evidence adequacy was not assessed, and the test file never runs. `test_validation_result.py::test_valid_cli_is_structure_only_and_does_not_execute`
- I cite a file that is not a test, or not text, and it passes when the named test appears in it as a whole word. `test_validation_result.py::test_referenced_file_need_not_be_a_check_or_readable_text`

## [rejects_anything_unexpected] I put something validation does not recognize in a contract or in `contracts/`, and it fails instead of ignoring it.
Issue: https://github.com/chalkbadger/wirth/issues/1
Tests: [tests/rejects_anything_unexpected/](../tests/rejects_anything_unexpected/)

- I break the brackets of a Tests line, or add text after it, and it fails at that line. `test_markdown_structure.py::test_tests_line_delimiters_are_required`
- I add notes, another title, a stray Issue or Tests line, a code fence or another kind of bullet, and it fails at that line. `test_markdown_structure.py::test_unrecognized_content_is_not_silently_ignored`
- I indent a claim heading, Issue line, Tests line or result, and it fails. `test_markdown_structure.py::test_indented_headings_claim_lines_and_items_fail`
- I leave a line holding whitespace other than spaces and tabs, and it fails. `test_markdown_structure.py::test_only_spaces_and_tabs_are_blank_lines`
- I put evidence before any claim, and it fails. `test_markdown_structure.py::test_evidence_before_first_claim_fails`
- I put a symlink or folder with a hidden name in `contracts/`, and it fails without reading it. `test_contract_inputs.py::test_invalid_contract_name_does_not_allow_reading_symlink_or_directory`
- I put a named pipe with a hidden name in `contracts/`, and it fails without waiting on it. `test_contract_inputs.py::test_invalid_contract_name_does_not_allow_reading_fifo`
- I make a contract a symlink or a folder, and it fails. `test_contract_inputs.py::test_contract_files_must_not_be_symlinks`
- I put something other than a `.md` file in `contracts/`, and it fails. `test_contract_inputs.py::test_unexpected_entries_are_reported`
- I make `contracts/` a symlink or a file, and it fails. `test_contract_inputs.py::test_symlinked_discovery_directory_fails`
- I put a named pipe called `pipe.md` in `contracts/`, and it fails without waiting on it. `test_contract_inputs.py::test_contract_fifo_fails_without_blocking`
