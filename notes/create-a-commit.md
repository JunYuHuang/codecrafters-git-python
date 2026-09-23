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
            - `.git/objects/<commit_sha[0:2]>/<commit_sha[2:40]>`
        - prints its created Git commit object's SHA-1 hexadecimal hash string
        - if called without `[-p <commit_sha>]` flag,
            - sets its created commit object's own SHA-1 hexadecimal hash as its own parent SHA-1 hash
        - if called with `[-p <commit_sha>]` flag,
            - uses `<commit_sha>` as the newly created commit object's parent SHA-1 hash
    - commit object anatomy (after zlib decompression):
        - content format:
        ```
        commit <size>\0tree <tree_sha>
        parent <parent_sha>
        author <name> <<email>> <timestamp> <timezone>
        committer <name> <<email>> <timestamp> <timezone>

        <commit message>
        ```
        - line 1 is binary-encoded, rest of lines are plain text
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
- PEDAC: Examples
    - ex.1
        ```
        # Create the initial commit
        $ git commit-tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904 -m "Initial commit"
        3b18e512dba79e4c8300dd08aeb37f8e728b8dad
        ```
    - ex.2
        ```
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
    - set string `body_lines_str` to:
        ```
        "parent <tree_sha>\n" +
        "author John Doe <john@example.com> <timestamp> <timezone>\n" +
        "committer John Doe <john@example.com> <timestamp> <timezone>\n" +
        "\n" +
        "<message[1:-1]\n>
        ```
    - set string `new_commit_sha` to empty string
    - if `has_commit_sha`,
        - set `new_commit_sha` to `<commit_sha>` 
    - if `tree_sha` is empty string,
        - set `new_commit_sha` to SHA-1 hexadecimal hash string of `body_lines_str` ?
    - set int `commit_size` to length of `body_lines_str`
    - set bytes `header_bytes` from string `commit <commit_size>\0tree <tree_sha>`
    - create dir at `".git/objects/<new_commit_sha[0:2]>` if needed
    - open file `commit_fd` with write permissions in bytes mode
    - write bytes `header_bytes` to `commit_fd`
    - close file `commit_fd`
    - open file `commit_fd` with permissions in plain-text mode (w/ UTF8 encoding)
    - write string TODO
    - helper functions:
        - `does_object_exist(sha1_hash: string, object_type: string = "") -> boolean`:
            - returns true if:
                - there exists a file in `./git/objects` associated with the 40-char SHA-1 hexadecimal hash string `sha1_hash`
                - the file associated with `sha1_hash` matches the Git object type `object_type` if `object_type` is not an empty string
            - else returns false
