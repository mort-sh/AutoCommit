# Notes

Here is the output of a previous run:
```bash
Analyzing changes and generating messages...
Message generation complete.



╭────────────────────╮
│    AutoCommit     │
╰────────────────────╯
├──  autocommit/cli/cli.py    34   17
│   ├──  Found 4 Hunks
│   └──  Group 1 / 1    4
│       └── ╭─  {SHORT_HASH} ────────────── Message  ────────────────────────────────────────────────────────────╮
│           │    [Refactor] Update console handling in CLI for improved consistency                                │
│           │                                                                                                      │
│           │ - Replace shared console object with local instance for error messages                               │
│           │ - Introduce a dedicated console for summary output to enhance clarity                                │
│           │ - Ensure safety checks for file processing to prevent potential errors                               │
│           │                                                                                                      │
│           │ This change improves the consistency of console output in the CLI by using                           │
│           │ a local console instance for error messages and summary printing, which enhances user                │
│           │ experience and reduces confusion.                                                                    │
│           ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
├──  autocommit/core/ai.py    73   1
│   ├──  Found 3 Hunks
│   └──  Group 1 / 1    3
│       └── ╭─  {SHORT_HASH} ────────────── Message  ────────────────────────────────────────────────────────────╮
│           │    [Feature] Add hunk classification functionality for commit message generation                     │
│           │                                                                                                      │
│           │ - Implemented `classify_hunks` function to group related hunks using OpenAI API                      │
│           │ - Enhanced commit message generation by logically organizing hunks                                   │
│           │ - Improves the accuracy of commit messages by ensuring related changes are grouped together          │
│           ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
└──  UI_Upgrade.md    383   0
    └──  Group 1 / 1    1
        └── ╭─  {SHORT_HASH} ────────────── Message  ────────────────────────────────────────────────────────────╮
            │    [Feature] Add UI Upgrade documentation for CLI visualization improvements                         │
            │                                                                                                      │
            │ - Introduced a new file `UI_Upgrade.md` to document changes                                          │
            │ - Refactored CLI output to use line art for hierarchical representation                              │
            │ - Enhances user experience by improving visual cues for file relationships                           │
            ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯

Applying commits (placeholder)...
Simulated 6 commits.

Summary:
        - 6/6 files tracked
        - 6/17 changes committed
        - 1061 lines of code changed
        - Chunk level: 2 (logical units)
        - Parallelism: auto

```




1. Fix the righthand indentation, so that this:
```
└──  UI_Upgrade.md    383   0
    └──  Group 1 / 1    1
```
turns to:
```
└──  UI_Upgrade.md                                                               383   0
    └──  Group 1 / 1                                                                    1
```

2. The Projects is missing some elements on the top of the Git commit message box as well as the bullet point indent:
```
        └── ╭─  {SHORT_HASH} ────────────── Message  ────────────────────────────────────────────────────────────╮
            │    [Feature] Add UI Upgrade documentation for CLI visualization improvements                         │
            │                                                                                                      │
            │ - Introduced a new file `UI_Upgrade.md` to document changes                                          │
            │ - Refactored CLI output to use line art for hierarchical representation                              │
            │ - Enhances user experience by improving visual cues for file relationships                           │
            ╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
Should be:
```
         ╰─╮  a2584435... ──────────────  Message    ───────────────────────────────────────────────────────────╮
            │                                                                                                     │
            │    [Feature] Add UI Upgrade documentation for CLI visualization improvements                         │
            │                                                                                                      │
            │    - Introduced a new file `UI_Upgrade.md` to document changes                                       │
            │    - Refactored CLI output to use line art for hierarchical representation                           │
            │    - Enhances user experience by improving visual cues for file relationships                        │
            │                                                                                                      │
            ╰───────────────────────────────────────────────────────────────────────────────────────────────────  ╯
```

3. Implement a slightly more detailed view in place of "Analyzing changes and generating messages..."


4. Final polishes! Please Implemnt:
- top and bottom stylistic quote icons (` ` ` `)
- Referencing an abbreviated version of the commit hash in the header.
- Use of the curvey corner `╰` in the tree line art
- custom file icons. You are using the python icon for files the do not end in .py.
