# Advanced CLI UI Enhancement

Start by showcasing a dynamic, real-time preview of the repository's structure and status, with live updates as files are checked:

```bash
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
```

Enable live updates on this preview during file checks.

Once files are ready, present a detailed view of the commit and file changes. This view displays a single file after its hunks are calculated and ready for commit:
- `1/1` indicates the number of groups for this file.
- ` 5` shows the number of hunks for this file.
- `  ` indicates the Git commit message.
- `{7_CHAR_HASH}` is an abbreviated Git commit hash.
- ` 4` shows new changes in this file.
- `  2` shows deletions.
- ` processor.py` is the file name with a dynamic icon based on file type.

```bash
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

For files with multiple groups, a lock bar on the left helps identify child elements:

```bash
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

Upon script completion, commit files, display them in a project file tree, and optionally push upstream. Present a summary dashboard and a config dashboard for flow insights:

```bash
╭───────────────────────────────────────────────────────────╮
│             Committing Files...                          │
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
    │    N Files Committed ............................... 
    │    Pushing upstream ............................... 
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
