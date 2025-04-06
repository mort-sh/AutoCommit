# Notes

Here is the output of a previous run:
```bash
Analyzing changes and generating messages...
Message generation complete.



╭────────────────────╮
│    AutoCommit     │
╰────────────────────╯
└──  autocommit/cli/cli.py    6   1
    ├──  Found 2 Hunks
    └──  Group 1 / 1    2
        └── ╭─  {SHORT_HASH} ────────────── Message  ────────────────────────────────────────────────────────────────────────────────────────────────────────╮
            │    [Feature] Enhance test mode argument for better functionality                                                                                 │
            │                                                                                                                                                  │
            │ - Updated the `--test` argument to accept an optional integer value                                                                              │
            │ - Default behavior now processes 1 file if the flag is present without a value                                                                   │
            │ - Improves usability by automatically tracking untracked files in test mode                                                                      │
            ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


Test Mode: Would attempt 1 commits (limited to 1 file(s)).

Summary:
        - 1/3 files tracked
        - 1/7 changes committed
        - 25 lines of code changed
        - Chunk level: 2 (logical units)
        - Parallelism: auto

TESTING MODE WAS ON. NO CHANGES WERE MADE.
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
