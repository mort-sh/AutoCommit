# Significant UI  Changes

Below is an updated and fully corrected output of the program. There are a number of areas I am looking for you to get creatively involved and implement a solution however you see fit. In regards to the bottom section, the summary and stats, do your best and try and implement some interesting things, But don't let this fun little feature disrupt from the quality and organization of the project. I'm happy to get rid of this stats thing if it's an issue.


## Repo Preview

Start by offering the user a preview of the repository. Would be cool if you could offer some sort of live updating on that preview while you check files.
```bash
╭────────────────────────────────────────────────────────────────╮
   PREVIEW                                           REPOSITORY
    ╭◉
    │
    │     scripts
    │      ├──  build.py............................  Added
    │      ├──  processor.py........................
    │      ├──  list_scripts.py.....................
    │      ├── 󰂺  README.md..........................  Changed
    │      └──  release.py..........................
    │     tests
    │       ├──  test_autocommit.py.................  Removed
    │       └──  test_commit_lock.py................
    │
    ╰◉
╰────────────────────────────────────────────────────────────────╯
```

## File Changes
Once you have files ready, present the user with this view, to view the commit and changes of file. This is the view of a single file after its hunks have been calculated and determined to be ready for a commit.
- `1/1` shows how many groups there are for this file.
- ` 5` shows how many hunks there are for this file.
- `  ` communicates to the user that this is the Git commit message.
- `{7_CHAR_HASH}` Please populate this and fill it in. It is an abbreviated or the prefix of a git commit hash.
- ` 4` tells the user how many new changes there are in this file.
- ` 2` tells the user how many deletions there are.
- ` processor.py` file name and Dynamic icon based on the file type.
  - The list of things underneath the file are just extra information, things that are useful for the user.
  - Similar idea with under the commit message. The only thing that's definitely there is listing the hunks that are associated or relevant to this commit.
```
╭──────────────────────────────────────────────────╮
│  processor.py             5  │     4  │    2 │
╰──────────────────────────────────────────────────╯
      ╰──╮
         ├─    autocommit/core/
         ├─    Change categories (fix, feat, etc.)
         ╰─    Found 10  Hunks

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
  │ │    ├─    Change categories (fix, feat, etc.)
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


## Results / Summary

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
