
# CLI UI Upgrade

Please look at the tree visualization below.
```bash
 .
├──  LICENSE
├──  logo.png
├──  main.py
├──  pyproject.toml
├──  pytest.ini
├── 󰂺 README.md
├──  uv.lock
├──  autocommit
│   ├──  main.py
│   ├──  cli
│   ├──  core
│   └──  utils
├──  scripts
│   ├──  build.py
│   ├──  clean.py
│   ├──  list_scripts.py
│   ├── 󰂺 README.md
│   └──  release.py
└──  tests
    ├──  test_autocommit.py
    └──  test_commit_lock.py
```

Take inspiration from the use of icons and the line art -- Specifically, the hierarchical nature. I would like you to refactor the project and rework how the indentation and CLI display is shown. Please move away from indentation and use line art as the new visual cue for the parent child relationship between the file, the hunks and the commit messages.

Here is a before and after example output of what i'd like the CLI to look like...

After:
```
Results:


git:            [ , 󰊢, , , , , , , , , , ,  ]

file changes:   [                           ]
     files  :   [                       ]


util-solid :    [                               ]
state-solid:    [                    ]

round-hollow :  [                               ]
round-solid  :  [                  ]
square-solid :  [                           ]
square-hollow:  [                           ]
letters:        [                               ]
 arrows:        [ ←, ↑, →, ↓, ↖, ↗, ↘, ↙ ]
shapes:         [ ◉, ◎, ◈, ◆, ◇, ○, ●, □, ■ ]
weather:        [ ☀, ☁, ☂, ☃, ⛅, ⚡, ❄ ]


TODO, ADD THIS JUNK IN! [                                ]

                


╭────────────────────╮
│     AutoCommit    │
├────────────────────╯
│
├─── autocommit/cli/cli.py                                                 3     2
│   ├──  processor.py   =    2 Hunks
│   ╰──  Group 1                                                                  2
│       ├──    1 / 2
│       ├──    2 / 2
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
╰▣─  autocommit/core/processor.py                                          301   203
    │
    ├──  processor.py   =    6 Hunks
    ├──  Group 1                                                                  2
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
    ╰──  Group 2                                                                    4
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
































│
├──  autocommit/cli/cli.py                                               3   2
│   ╰──   2 Hunks Found
│       ├──  Group 1
│       │   ├──    1 / 2
│       │   ├──    2 / 2
│       │   ╰  
│       │
│       │   ╭  Message   ─────────────────────────────────────────────────────╮
│       │   │                                                                   │
│       │   │                                                                   │
│       │   │   [Documentation] Update help text for commit atomicity argument  │
│       │   │                                                                   │
│       │   │   - Clarified the description of the standard commit level        │
│       │   │   - Added information about grouping logically related Hunks      │
│       │   │   - Enhances user understanding of commit atomicity options       │
│       │   │                                                                   │
│       │   │                                                                   │
│       │   ╰────────────────────────────────────────────────────────────────  ╯
│       │
│       ├──  Group 2
│       │   ├──    1 / 2
│       │   ├──    2 / 2
│       │   ╰  
│       │












├──  autocommit/cli/cli.py ▪─────────────────────────▪  3 /  2 ├─
│   ╰──   2 Hunks Found
│       ╰──  Group 1
│           ├──    1 / 2
│           ├──    2 / 2
│           ╰  
│
│              Commit   ───╮
│           │                 ╰─────────────────────────────────────────────────╮
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           ╰────────────────────────────────────────────────────────────────  ╯
│











├▣──  autocommit/cli/cli.py                                              3   2
│   ╰──   2 Hunks Found
│       ╰──  Group 1
│           ├──    1 / 2
│           ├──    2 / 2
│           ╰  
│
│           ╭  Message   ─────────────────────────────────────────────────────╮
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           │                                                                   │
│           ╰────────────────────────────────────────────────────────────────  ╯
│
│







                                [Documentation] Update help text for commit atomicity argument

                                - Clarified the description of the standard commit level
                                - Added information about grouping logically related hunks
                                - Enhances user understanding of commit atomicity options



├──  autocommit/core/ai.py ──────────────────────────  3 /  2
│   └──   2 Hunks Found
│       ├──  Group 1
│       │   ├──   1 / 2
│       │   ├──   2 / 2
│       │   ├── ✔
│       │    Commited
│       
│       └── ✔
├──  logo.png


     autocommit/cli/cli.py ····································································································································· +3 / -2
 Found 2 hunks in autocommit/cli/cli.py
     autocommit/core/ai.py ···································································································································· +73 / -1
     autocommit/core/constants.py ····························································································································· +25 / -0
 Found 3 hunks in autocommit/core/ai.py
 Found 2 hunks in autocommit/core/constants.py
     autocommit/core/processor.py ·························································································································· +188 / -110
 Found 6 hunks in autocommit/core/processor.py
Grouped into 1 logical groups

 Processing hunk group 1/1 for autocommit/cli/cli.py
Grouped into 1 logical groups

 Processing hunk group 1/1 for autocommit/core/ai.py
Grouped into 1 logical groups

 Processing hunk group 1/1 for autocommit/core/constants.py
                     Commit Message ······························································································································
                        {
                                [Documentation] Update help text for commit atomicity argument

                                - Clarified the description of the standard commit level
                                - Added information about grouping logically related hunks
                                - Enhances user understanding of commit atomicity options
                        }

```








```
    Results:
        autocommit/cli/cli.py ····································································································································· +3 / -2
    Found 2 hunks in autocommit/cli/cli.py
        autocommit/core/ai.py ···································································································································· +73 / -1
        autocommit/core/constants.py ····························································································································· +25 / -0
    Found 3 hunks in autocommit/core/ai.py
    Found 2 hunks in autocommit/core/constants.py
        autocommit/core/processor.py ·························································································································· +188 / -110
    Found 6 hunks in autocommit/core/processor.py
    Grouped into 1 logical groups

    Processing hunk group 1/1 for autocommit/cli/cli.py
    Grouped into 1 logical groups

    Processing hunk group 1/1 for autocommit/core/ai.py
    Grouped into 1 logical groups

    Processing hunk group 1/1 for autocommit/core/constants.py
                        Commit Message ······························································································································
                            {
                                    [Documentation] Update help text for commit atomicity argument

                                    - Clarified the description of the standard commit level
                                    - Added information about grouping logically related hunks
                                    - Enhances user understanding of commit atomicity options
                            }

```



               




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
