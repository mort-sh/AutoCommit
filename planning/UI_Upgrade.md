
# CLI UI Upgrade

Start by offering the user a preview of the repository.
```bash
╭────────────────────────────────────────────────────────────────╮
   PREVIEW                                           REPOSITORY
    ╭◉
    │
    │     scripts
    │      ├──  build.py
    │      ├──  processor.py
    │      ├──  list_scripts.py
    │      ├── 󰂺  README.md
    │      └──  release.py
    │     tests
    │       ├──  test_autocommit.py
    │       └──  test_commit_lock.py
    │
    ╰◉
╰────────────────────────────────────────────────────────────────╯
```

would be cool if you could offer some sort of live updating on that preview while you check files.

Once you have files ready, present the user with this view, to view the commit and changes of file. This is the view of a single file after its hunks have been calculated and determined to be ready for a commit.
- `1/1` shows how many groups there are for this file.
- ` 5` shows how many hunks there are for this file.
- `  ` communicates to the user that this is the Git commit message.
- `{7_CHAR_HASH}` Please populate this and fill it in. It is an abbreviated or the prefix of a git commit hash.
- ` 4` tells the user how many new changes there are in this file.
- `  2` tells the user how many deletions there are.
- ` processor.py` file name and Dynamic icon based on the file type.
  - The list of things underneath the file are just extra information, things that are useful for the user.
  - Similar idea with under the commit message. The only thing that's definitely there is listing the hunks that are associated or relevant to this commit.
```
╭──────────────────────────────────────────────────╮
│  processor.py             5  │     4  │    2 │
╰──────────────────────────────────────────────────╯
      ╰──╮
         ├─    autocommit/core/
         ├─    idk
         ╰─    Found 10  Hunks
                                                                                                                   .
         ╭───┤ 1/1▕   5 ▕    ├───────────────────────────────────────────────────────────────┤   {7_CHAR_HASH} ├──╮
         │                                                                                                          │
         │    [Fix] Improve debug output and console messages in processor.py                                        │
         │                                                                                                           │
         │      - Added debug output to show classification of hunks into groups                                     │
         │      - Updated console messages for clarity on simulated commits and test mode                            │
         │      - Enhances user understanding of the processing flow and results                                     │
         │     ◉───────────────────◉                         ◉────────────────────────────────────────────────────  ╯
         │              2 / 10                                   Debug Information
         │              3 / 10                                   Debug Information
         │              5 / 10                                   Debug Information
         │              1 / 10                                   Extra Information
         │           ...                                        ...
         ╰─◉

```


This is another view for a file change, but this is when there are two or more groups associated with the file. The lock bar on the left is added to make it easier for the user to determine what are child elements.

```
╭──────────────────────────────────────────────────╮
│   build.py             5  │     28  │    8   │
╰──────────────────────────────────────────────────╯
  ╭╮ ╰──╮
  │ │    ├─    autocommit/core/
  │ │    ├─    idk
  │ │    ╰─    Found 10  Hunks
  │ │                                                                                                                  .
  │ │    ╭───┤ 1/2▕   5 ▕    ├───────────────────────────────────────────────────────────────┤   {7_CHAR_HASH} ├──╮
  │ │    │                                                                                                          │
  │ │    │    [Fix] Improve regex and processing logic for hunk classification                                       │
  │ │    │                                                                                                           │
  │ │    │      - Update regex to capture content inside brackets more accurately                                    │
  │ │    │      - Enhance logic to prevent duplicate hunk assignments across groups                                  │
  │ │    │      - Add warnings for ungrouped hunks and failed classifications to improve user feedback               │
  │ │    │                                                                                                           │
  │ │    │      This change addresses issues with the previous implementation, ensuring more reliable                │
  │ │    │      classification of hunks and better handling of edge cases.                                           │
  │ │    │                                                                                                           │
  │ │    │     ◉───────────────────◉                         ◉────────────────────────────────────────────────────  ╯
  │ │    │             2 / 10                                   Debug Information
  │ │    │             3 / 10                                   Debug Information
  │ │    │             5 / 10                                   Debug Information
  │ │    │             1 / 10                                   Extra Information
  │ │    │          ...                                        ...
  │ │    ╰─◉
  ││                                                                                                                 .
  │ │    ╭───┤ 2/2▕   5 ▕    ├───────────────────────────────────────────────────────────────┤   {7_CHAR_HASH} ├──╮
  │ │    │                                                                                                          │
  │ │    │    [Chore] Add debug print statement for classify_hunks response                                          │
  │ │    │                                                                                                           │
  │ │    │      - Introduced a debug print statement to output the raw response from classify_hunks.                 │
  │ │    │      - This change aids in testing and troubleshooting by providing visibility into the function's output.│
  │ │    │      - Future improvements needed to handle debug flag properly or integrate with logging configuration.  │
  │ │    │                                                                                                           │
  │ │    │     ◉───────────────────◉                         ◉────────────────────────────────────────────────────  ╯
  │ │    │             2 / 10                                   Debug Information
  │ │    │             3 / 10                                   Debug Information
  │ │    │             5 / 10                                   Debug Information
  │ │    │             1 / 10                                   Extra Information
  │ │    │          ...                                        ...
  │ │    ╰─◉
  ││
  ╰─╯

```


This is what the end of the script looks like. You commit the files, have them be shown in a file tree for their project and have them pushed upstream optionally. the users then presented with a summary dashboard, as well as a small config dashboard, just so they can see some data about the flow.
```

╭───────────────────────────────────────────────────────────╮
│             Commiting Files...                          │
╰───────────────────────────────────────────────────────────╯
          scripts.....................................   
           ├──  build.py................................ 
           ├──  clean.py................................ 
           ├──  list_scripts.py......................... 
           ├── 󰂺  README.md.............................. 
           └──  release.py.............................. 
          tests.......................................   
            ├──  test_autocommit.py..................... 
            └──  test_commit_lock.py.................... 

    ╭◉
    │    N Files Comitted ............................... 
    │    Pushing updtream ............................... 
    │    Pushed! ........................................ 
    ╰◉

╭────────────────────────┤    Summary  ├───────────────────────────────╮
    ╭◉
    │     TODO:   count the number of feature commits
    │     TODO:   count the number of refactor commits
    │     TODO:   count the number of chore commits
    │     TODO:   count the number of bug fix commits
    │
    │    391       lines added
    │    391       lines removed
    │    3         files added
    │    0         files deleted
    │    1061      lines of code changed
    ╰◉

    ╭◉
    │     TODO:    How long the repo has been alive
    │     6/6      files tracked
    │     6/17     changes committed
    │
    │    14614     TODO: lines of code tracked
    │    30        TODO: number of files tracked
    ╰◉

├─────────────────────────────────────────────────────────────────────├
    Config                                         {REPO_REMOTE_URL}
    ╭◉
    │ - Chunk level: 2 (logical units)
    │ - Parallelism: auto
    │ - TODO: Include any other helpful
    │       config data. Perhaps info about the repo?
    ╰◉
╰─────────────────────────────────────────────────────────────────────╯
```



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
