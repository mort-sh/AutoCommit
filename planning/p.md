Please help me redesign this terminal CLI line art. Currently, it is not obvious to me visually when two groups are linked together. It feels like there's a lot of lines going on. Please propose three to five different designs that focus on highlighting the parent-child relationship between the file and the group. For example, if you were to respond with this answer, that would have been a phenomenal redesign.

Example:
```

╭────────────────────────────────────────────────────────────────╮
   REPO PREVIEW                                       GIT STATUS
    ╭◉
    │
    │    scripts.....................................   
    │     ├──  build.py................................ 
    │     ├──  clean.py................................ 
    │     ├──  list_scripts.py......................... 
    │     ├── 󰂺  README.md.............................. 
    │     └──  release.py.............................. 
    │    tests.......................................   
    │      ├──  test_autocommit.py..................... 
    │      └──  test_commit_lock.py.................... 
    │
    ╰◉
╰────────────────────────────────────────────────────────────────╯


╭──────────────────────────────────────────────────╮
│  processor.py             5  │     4  │    2 │
╰──────────────────────────────────────────────────╯
      ╰──╮
         ├─    autocommit/core/
         ├─    idk
         ╰─    Found 10  Hunks
                                                                                                                   .
         ╭───┤ 2/2▕   5 ▕    ├───────────────────────────────────────────────────────────────┤   {7_CHAR_HASH} ├──╮
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

╭───────────────────────────────────────────────────────────────────────╮
    COMMITTING

          scripts...........................   
           ├──  build.py...................... 
           ├──  clean.py...................... 
           ├──  list_scripts.py............... 
           ├── 󰂺  README.md.................... 
           └──  release.py.................... 
          tests.............................   
            ├──  test_autocommit.py............ 
            └──  test_commit_lock.py........... 

    ╭◉
    │   N Files Comitted
    │   Pushing updtream
    │   Pushed!
    ╰◉

╰───────────────────────────────────────────────────────────────────────╯
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

╭──────────────────────────────────────────────────╮
│  processor.py             5  │     4  │    2 │
╰──────────────────────────────────────────────────╯
      ╰──╮
         ├─    autocommit/core/
         ├─    idk
         ╰─    Found 10  Hunks
                                                                                                                   .
         ╭───┤ 2/2▕   5 ▕    ├───────────────────────────────────────────────────────────────┤   {7_CHAR_HASH} ├──╮
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







 TODO:     idk, maybe look at their commit
  TODO:     Find a way to do a very very rough estimate
of how much time this tool has saved the user












╭░
│░
│░
│░
│░
│░
│░
╰░


















    ╭◉  processor.py
    │
    │
    │
    │
    │
    │
   ─╯
    5
   ─╮
    │
    │
    │
    │
    │
    │
    ╰◉  processor.py


    ╭◉  processor.py
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    ╰◉  processor.py





╭◉
│
│
│
│
│
│
│
│
│
│
│
│
│
│
╰◉






























▕
         



◉────────────────────◉
▢────────────────────▢
  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
      TEST MODE ACTIVE
      No Changes Made

  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔


▢────────────────────────◉








╭────────────────────────────────────────────────────────────────╮
   AutoCommit                           5  │    28  │    8

    ╭◉ 2/2▕   5 ▕  
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    ╰◉


╰────────────────────────────────────────────────────────────────╯






    ╭─
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    │
    ╰─










╭─
│
│
│
│
│
│
│
│
│
│
╰─


├─────┤        ▐─────▌        ■─────■        □─────□        ▢─────▢
▣─────▣        ▤─────▤        ▥─────▥        ▦─────▦        ▧─────▧
▪─────▪        ▫─────▫        ◆─────◆        ◇─────◇        ◈─────◈
◉─────◉        ○─────○        ●─────●        ☀─────☀        ─────

░░░░
░░░░
░░░░
░░░░
░░░░
░░░░

▒

▓



▥
▥













├──  autocommit
▌  ╰──  core
│       ╰──  ai.py
│   ├──  TODO.md
│   ├──  UI_Upgrade.md
│   └──  UI_Upgrades.md
 scripts
├──  build.py
├──  clean.py
├──  list_scripts.py
├── 󰂺  README.md
└──  release.py

Content you should redesign:
```


◉ ────── ◉ ──────
▢ ────────────────────▢───
  ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁


╭────────────────────╮
│    AutoCommit     │
╰────────────────────╯
 ai.py                                              28   8
╰──╮
   ├─  Found 10  Hunks
   ├─  Found 10  Hunks
   ╰─  Found 10  Hunks

╭◉   28    8    10
│
│
│
╰◉






╭──────────────────────────────────────────────────╮
│  AutoCommit             5  │     28  │    8   │
╰──────────────────────────────────────────────────╯

    ╭◉ 2/2▕   5 ▕  
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    │                                              .
    ╰◉  {7_CHAR_HASH}
