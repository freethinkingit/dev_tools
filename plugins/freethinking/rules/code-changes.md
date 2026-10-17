# Code changes

How to change code in any repository this handbook applies to.

- **Read before you write.** Look at the repository's README and contributing guide, then the surrounding code, the existing patterns, the tests and the configuration the change has to fit. Write code the way the file around it is written.
- **Match the project.** Use the languages, libraries, naming and formatting the repository already uses. Do not add a dependency, framework or tool without asking the author first.
- **Make the smallest change that does the job.** Do not refactor unrelated code, tidy nearby files, rename for taste or add features that were not asked for. If you find anything else worth doing on the way, say what it is and roughly how much work it would add to the branch, and let the author choose between keeping it in the branch and filing an issue; do not make it unasked.
- **Every behaviour change comes with a test.** Write it in the project's test framework, the way the project writes tests. A bug-fix test fails before the fix and passes after. If the repository has no test framework, say so and record a manual check instead; do not add a framework unless the author asks. A task from a spec's `tasks.md` is the one exception: there, tests are tasks of their own, so build only what the task says and prove it with an ephemeral check, a scratch script or call that exercises the new code and is deleted before the change is done, plus the existing tests for what you touched.
- **Run what you touched.** Run the tests you added or changed, the existing tests that cover what you touched, and any ephemeral check, before saying the change is done. Report the result as it is, including failures and anything you could not run.
- **Leave no investigation behind.** Remove debug output, commented-out code, temporary scripts, scratch files and stubs added while working out the change.
- **Say what you are unsure of.** Mark anything inferred rather than observed, and do not present a guess about the code's behaviour as fact.
