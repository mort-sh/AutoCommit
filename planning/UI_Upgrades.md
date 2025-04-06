# Significant UI  Changes

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
