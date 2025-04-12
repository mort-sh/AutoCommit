# Multi-Stage Output Requirements for the Python Package UI Update

Your task is to modify the Python package’s output (both log rendering and file tree structure) so that it exactly matches the following specifications. The modifications should follow clean code standards, prioritize visually appealing CLI-based UI/UX, and be optimized for performance. Use clear structure, meaningful names, and code comments where appropriate.

---

## 1. Testing Mode Indicator

- **Objective:**
  Render a test-mode banner *only* when the command-line argument `--test` is passed. The banner should be rendered `yellow`. When `--test` is active, ensure that all extraneous test messages are removed from the output.

- **Expected Output (when `--test` is passed):**

  ```log
  ╭◉ 
  │
  │             TEST MODE: ON
  │       CHANGES ARE ONLY VISUAL 
  │
  ╰◉
  ```

- **Notes:**
  - When the flag is not provided, nothing should be printed for this section.
  - Ensure that this logic is robust against incorrect or missing input parameters.

---

## 2. Repository Preview Display

- **Objective:**
  Provide the user with a preview of the repository contents. Always list all folders, but include only those files that have been changed.

- **Expected Output:**
  ```log
  ╭───────────────────────────────────────────────────────────╮
  │   {REPOSITORY NAME}                                     │
  ╰───────────────────────────────────────────────────────────╯
       ./ ............................................... 
           scripts....................................... 
              ├──  build.py.............................. 
              ├──  clean.py.............................. 
              ├── 󰂺  README.md............................ 
              └──  release.py............................ 
           tests......................................... 
              └──  test_commit_lock.py................... 

  Analyzing changes and generating messages... Message generation complete!
  ```

- **Notes:**
  - Maintain the folder tree structure.
  - Ensure that only the files with modifications are showcased in detail.

---

## 3. File and Commit Message Format Update

- **Objective:**
  Update the UI for file changes and commit messages. The new layout should have a wider project header, right-aligned file status indicators, and a neatly formatted commit message.

- **Comparison:**

  **Current Output:**
  ```log
  ╭────────────────────╮
  │    AutoCommit     │
  ╰────────────────────╯
  └──  dummy_test_data/    1   0
      └──  Group 1 / 1    1
          └── ╭─  {SHORT_HASH} ────────────── Message  ─────────────────────────────────────────────╮
              │    [Chore] Add new directory for dummy test data                                      │
              │                                                                                       │
              │ - Created a new directory named `dummy_test_data`                                     │
              │ - This directory will be used to store test data for development and testing purposes │
              │ - Helps in organizing test resources and improving project structure                  │
              ╰───────────────────────────────────────────────────────────────────────────────────────╯
  ```

  **Desired Output:**
  ```log
  ╭───────────────────────────────────────────────────────────╮
  │   {REPOSITORY NAME}                                      │
  ╰───────────────────────────────────────────────────────────╯
  └──  dummy_test_data/                                                                   1   0
      └──  Group 1 / 1                                                                         1
          └── ╭─  ─────────────────────────── Message  ─────────────────────────────────────────╮
              │    [Chore] Add new directory for dummy test data                                  │
              │                                                                                   │
              │       - Created a new directory named `dummy_test_data`                           │
              │       - This directory will be used to store test data for development and        │
              │         testing purposes.                                                         │
              │       - Helps in organizing test resources and improving project structure        │
              ╰───────────────────────────────────────────────────────────────────────────────────╯
  ```

- **Required Changes:**
  - **Project Header:**
    - Increase the width and include the repository name.
  - **File Status Counters:**
    - Right-align the status counters (` 1   0` for files and ` 1` for groups).
  - **Message Body Formatting:**
    - Allocate 3/4 of the screen width for the commit message body.
    - Indent the commit message content uniformly.
    - Implement word-wrapping for any line longer than 100 characters.
  - **Commit Message Contents:**
    - Remove the `{SHORT_HASH}` from the commit message.

- **Notes:**
  - The UI should strictly match the desired output styling.
  - Validate string lengths and ensure consistent alignment across various terminal sizes if applicable.

---

## 4. Final Results / Summary Display

- **Objective:**
  At the end of the script, display a summarized results section that shows the committed files in a file tree format along with an optional push status message.

- **Expected Output:**

  ```log
  ╭───────────────────────────────────────────────────────────╮
  │  Commiting Files...                                     │
  ╰───────────────────────────────────────────────────────────╯
       ./ ................................................ 
           scripts........................................ 
              ├──  build.py............................... 
              ├──  clean.py............................... 
              ├──  list_scripts.py........................ 
              ├── 󰂺  README.md............................. 
              └──  release.py............................. 
           tests.......................................... 
              ├──  test_autocommit.py..................... 
              └──  test_commit_lock.py.................... 

      ╭◉
      │     N Files Comitted ............................. 
      │     Pushing updtream ............................. 
      │     Pushed! ...................................... 
      ╰◉
  ```

- **Notes:**
  - Ensure that the file tree layout is clear and accurately reflects the repository structure.
  - Optionally, include a push status if the files are being pushed upstream.
  - Use dynamic counters (e.g., replace `N` with the actual number of committed files) by validating the number of modified files.

---

## Implementation Guidelines

- **Maintainability & Clean Code:**
  - Refactor common log-rendering operations into helper functions or classes.
  - Use clear, descriptive variable/function names.
  - Ensure modular design to allow future UI improvements with minimal changes.

- **Security & Robustness:**
  - Validate command-line arguments to prevent unexpected behavior.
  - Ensure output formatting logic handles edge cases (e.g., long file names, zero changes).

- **Performance:**
  - Optimize file tree generation by processing only necessary directories.
  - Use efficient string manipulation and alignment algorithms.

- **Testing:**
  - Write tests to ensure that:
    - The `--test` flag correctly toggles the test mode output.
    - The repository preview only shows the intended files.
    - The commit message UI matches the desired output exactly.
