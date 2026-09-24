# Notes:

- PEDAC: Problem
    - input:
        - `command`: string
            - in format `commit-tree <tree_sha> [-p <commit_sha>] -m <message>`
                - `<tree_sha>` = 40-char SHA-1 hexadecimal hash string of a Git tree object to commit
                - `<commit_sha>` = 40-char SHA-1 hexadecimal hash string of a Git commit object
                - `<message>` = double-quotes enclosed string that represents the Git commit message e.g., `"Initial commit"`
    - output:
        - N/A
    - side effects:
        - creates a Git commit object stored in a Git project root dir at:
            - `.git/objects/<new_commit_sha[0:2]>/<new_commit_sha[2:40]>`
                - where `<new_commit_sha?` is the 40-char SHA-1 hexadecimal string of the new Git commit object's contents
        - prints `<new_commit_sha>`
        - if called with `[-p <commit_sha>]` flag,
            - adds line `"parent <commit_sha>` right after commit header in commit object body content
    - commit object anatomy (after zlib decompression):
        - content format (if command called w/o optional `-p <commit_sha>` flag):
        ```
        commit <size>\0tree <tree_sha>
        author <name> <<email>> <timestamp> <timezone>
        committer <name> <<email>> <timestamp> <timezone>

        <commit message>
        ```
        - content format (if command called w/ optional `-p <commit_sha>` flag):
        ```
        commit <size>\0tree <tree_sha>
        parent <parent_sha>
        author <name> <<email>> <timestamp> <timezone>
        committer <name> <<email>> <timestamp> <timezone>

        <commit message>
        ```
        - all lines are binary-encoded given the plaintext content
        - each line ends with a newline `\n` char
        - line 6 is a blank line (i.e., just a newline char)
        - `<size>` = length (in bytes) of rest of plain text contents
        - `<tree_sha>` = content of commit object minus header as a 40-char hexadecimal SHA-1 hash string or optionally passed in `<commit_sha>` ?
        - `<parent_sha>` = 40-char hexadecimal SHA-1 hash string of a tree object to be committed
        - `<timestamp>` = seconds since epoch e.g., `1234567890`
        - `<timezone>` = timezone offset e.g., `+0000`
        - `<commit message>` = variable length commit message string
        - `author` and `committer` values can be hardcoded dummy values
    - questions:
        - how to get seconds since epoch in Python?
        - how to get timezone offset in Python?
        - in the commit object,
            - where does `<tree_sha>` in line 1 (commit header) come from?
                - from `<tree_sha>` argument when running command in form `commit-tree <tree_sha> [-p <commit_sha>] -m <message>`
            - where does `<parent_sha>` in line 2 come from?
                - from `<commit_sha>` argument when running command in form `commit-tree <tree_sha> -p <commit_sha> -m <message>`
                - this line only exists if command called and passes the optional flag `-p <commit_sha>`
        - can commit message `<message>` be empty?
            - let's assume it can't be
- PEDAC: Examples
    - ex.1
        ```
        $ mkdir test_dir && cd test_dir
        $ git init
        Initialized empty Git repository in /path/to/test_dir/.git/

        # Create a tree, get its SHA
        $ echo "hello world" > test.txt
        $ git add test.txt
        $ git write-tree
        4b825dc642cb6eb9a060e54bf8d69288fbee4904

        # Create the initial commit
        $ git commit-tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904 -m "Initial commit"
        3b18e512dba79e4c8300dd08aeb37f8e728b8dad

        # Write some changes, get another tree SHA
        $ echo "hello world 2" > test.txt
        $ git add test.txt
        $ git write-tree
        5b825dc642cb6eb9a060e54bf8d69288fbee4904

        # Create a new commit with the new tree SHA and parent
        $ git commit-tree 5b825dc642cb6eb9a060e54bf8d69288fbee4904 -p 3b18e512dba79e4c8300dd08aeb37f8e728b8dad -m "Second commit"
        6c18e512dba79e4c8300dd08aeb37f8e728b8dad
        ```
- PEDAC: Data Structures And Algorithms
    - if command not called in form `commit-tree <tree_sha> [-p <commit_sha>] -m <message>`,
        - exit and print error
    - if command called in form `commit-tree <tree_sha> -m <message>`,
        - exit and print error if `<tree_sha>`'s tree object file doesn't exist
        - exit and print error if `<tree_sha>` is not a tree object
        - exit and print error if `<message>` is not enclosed with double quotes
    - set bool `has_commit_sha` to false
    - if command called in form `commit-tree <tree_sha> -p <commit_sha> -m <message>`,
        - exit and print error if `<commit_sha>`'s tree object file doesn't exist
        - exit and print error if `<commit_sha>` is not a commit object
        - exit and print error if `<message>` is not enclosed with double quotes
        - set `has_commit_sha` to true
    - set int `timestamp` to seconds since epoch time
    - set string `timezone` to timezone offset
    - set bytes `commit_contents_uncompressed_bytes` from string:
        ```
        "author John Doe <john@example.com> <timestamp> <timezone>\n" +
        "committer John Doe <john@example.com> <timestamp> <timezone>\n" +
        "\n" +
        "<message[1:-1]\n>
        ```
    - set bytes `new_commit_sha` to bytes from empty string
    - if `has_commit_sha`,
        - prepend bytes `"parent <commit_sha>"` to `commit_contents_uncompressed_bytes`
    - prepend bytes `"tree <tree_sha>\n"` to `commit_contents_uncompressed_bytes`
    - set int `commit_size` to length of `commit_contents_uncompressed_bytes`
    - prepend bytes `commit <commit_size>\0>` to `commit_contents_uncompressed_bytes`
    - set string `new_commit_sha` from `commit_contents_uncompressed_bytes` as 40-char SHA-1 hexadecimal hash string
    - create dir at `.git/objects/<new_commit_sha[0:2]>` if needed
    - open file `commit_fd` at `.git/objects/<new_commit_sha[0:2]>/<new_commit_sha[2:]>` with write permissions in bytes mode
    - write zlib-compressed `commit_contents_uncompressed_bytes` to `commit_fd`
    - close file `commit_fd`
    - return `new_commit_sha`
    - helper functions:
        - `does_object_exist(sha1_hash: string, object_type: string = "") -> boolean`:
            - returns true if:
                - there exists a file in `./git/objects` associated with the 40-char SHA-1 hexadecimal hash string `sha1_hash`
                - the file associated with `sha1_hash` matches the Git object type `object_type` if `object_type` is not an empty string
            - else returns false
