```bash
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

2. Lastly, you are missing some elements on the top of the Git commit message box:
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
You are missing:
- top and bottom stylistic quote icons (` ` ` `)
- Referencing an abbreviated version of the commit hash in the header.
- Use of the curvey corner `╰` in the tree line art
- custom file icons. You are using the python icon for files the do not end in .py.


## Important BIG FIX
It seems like you are missing some core functionality. Despite numerous files having 5 or 6 hunks, I have only ever seen a maximum of 1 group. While it is possible for that to happen, the scope of their recent changes leads me to beleive the there should be multiple groups for some of these files.

As a refresher, my intent for a hunk is a changed portion of the file that is scoped to is logical relevancy. For example, If I write a function that calculates the sum of three numbers in one file, then in that same file, I built out some doc strings for some functions that were written years ago... then I want to be able to push both of those changes in their own respective commits. Therefore, a hunk is a portion of the file that is scoped to the logic that changed. The sensitivity for what is in scope is determined by the command line argument `--chunk-level` ... For example, at its highest level, A chunk level of 3 would result in git commits scoped to, AT MOST, individual functions (so a very narrow scope and baseically everything gets its own commit.)

Therefore, I should be seeing multiple commit messages per file (which would involve interpreting the hunks, determining that changes between two hunks are logically separate, then making a group for each logical division.)


## Additional things:


## Final Request

Below is an updated and fully corrected output of the program. There are a number of areas I am looking for you to get creatively involved and implement a solution however you see fit. In regards to the bottom section, the summary and stats, do your best and try and implement some interesting things, But don't let this fun little feature disrupt from the quality and organization of the project. I'm happy to get rid of this stats thing if it's an issue.


```bash
╭────────────────────╮
│     AutoCommit    │
├────────────────────╯
│
├─── autocommit/cli/cli.py                                                 3     2
│   ├──  Found 2 Hunks                                                            2
│   │   ├──    Analyzing...
│   │   │   ├──    [{CHUNKING_LEVEL}]    →   1      2   =   Similar
│   │   │   ├──    Tagged Similar:  1,  2
│   │   │   ╰──     Combining Similar
│   │   ╰──   1 Group(s)
│   │
│   ╰──  Group 1 / 1                                                              2
│       ├──    1 / 2
│       ├──    2 / 2
│       │
│       ╰─╮   {$HASH} ──────────────  Message    ───────────────────────────╮
│          │                                                                  │
│          │   [Documentation] Update help text for commit atomicity argument  │
│          │                                                                   │
│          │   - Clarified the description of the standard commit level        │
│          │   - Added information about grouping logically related Hunks      │
│          │   - Enhances user understanding of commit atomicity options       │
│          │                                                                   │
│          ╰────────────────────────────────────────────────────────────────  ╯
│
│
╰──  autocommit/core/processor.py                                          301   203
    │
    ├──  Found 6 Hunks                                                            6
    ├──  Group 1 / 2                                                              2
    │   ├──    1 / 6
    │   ├──    2 / 6
    │   ╰─╮   {$HASH} ──────────────  Message    ───────────────────────────╮
    │      │                                                                  │
    │      │   [Documentation] Update help text for commit atomicity argument  │
    │      │                                                                   │
    │      │   - Clarified the description of the standard commit level        │
    │      │   - Added information about grouping logically related Hunks      │
    │      │   - Enhances user understanding of commit atomicity options       │
    │      │                                                                   │
    │      ╰────────────────────────────────────────────────────────────────  ╯
    │
    ╰──  Group 2 / 2                                                              4
        ├──    3 / 6
        ├──    4 / 6
        ├──    5 / 6
        ├──    6 / 6
        ╰─╮   {$HASH} ──────────────  Message    ───────────────────────────╮
           │                                                                  │
           │   [Documentation] Update help text for commit atomicity argument  │
           │                                                                   │
           │   - Clarified the description of the standard commit level        │
           │   - Added information about grouping logically related Hunks      │
           │   - Enhances user understanding of commit atomicity options       │
           │                                                                   │
           ╰────────────────────────────────────────────────────────────────  ╯


# If `--test` the show
    ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        TEST MODE ACTIVE
        No Changes Made
    ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔
# Else, show
Applying commits (placeholder)...

╭─────────────────────────────────────────────────────────╮
│    Config                                              │
│─────────────────────────────────────────────────────────│
│                                                         │
│    - Chunk level: 2 (logical units)                     │
│    - Parallelism: auto                                  │
│    - TODO: Include any other helpful                    │
│        config data. Perhaps info about the repo?        │
│                                                         │
╭─────────────────────────────────────────────────────────╮
│    Stats                                               │
│─────────────────────────────────────────────────────────│
│                                                         │
│   - TODO: Come up with interesting stats                │
│   - TODO: Come up with interesting stats                │
│   - TODO: Come up with interesting stats                │
│   - TODO: Come up with interesting stats                │
│    TODO: maybe number of stars the repo hash           │
│     How long the repo has been alive                   │
│                                                         │
│                                                         │
│    391   lines added                                   │
│    391   lines removed                                 │
│    3     files added                                   │
│    0     files deleted                                 │
│    1061  lines of code changed                         │
│                                                         │
╭─────────────────────────────────────────────────────────╮
│    Summary                                             │
│─────────────────────────────────────────────────────────│
│                                                         │
│       TODO: count the number of feature commits        │
│       TODO: count the number of refactor commits       │
│       TODO: count the number of chore commits          │
│       TODO: count the number of bug fix commits        │
│                                                         │
│                                                         │
│     TODO: idk, maybe look at their commit              │
│      Find a way to do a very very rough estimate       │
│        of how much time this tool has saved the user    │
│      How long the repo has been alive                  │
│      6/6 files tracked                                 │
│      6/17 changes committed                            │
│                                                         │
│     14614 TODO: lines of code tracked                  │
│     30    TODO: number of files tracked                │
│                                                         │
│    391   lines added                                   │
│    391   lines removed                                 │
│    3     files added                                   │
│    0     files deleted                                 │
│    1061  lines of code changed                         │
│                                                         │
╰─────────────────────────────────────────────────────────╯
```
