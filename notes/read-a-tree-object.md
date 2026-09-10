# Notes:

- PEDAC: Problem
    - input:
        - `command`: string
            - format `ls-tree [--name-only] <tree_sha>` where `<tree_sha>`:
                - is a Git tree object in the local Git repo root dir
                - is a file at `<git-repo-root>/.git/objects/<tree_sha[:2]>/<tree_sha[2:]>`
    - output:
        - N/A
    - side effects:
        - TODO
    - TODO: figure out how to test and imitate the real `git ls-tree` command
- PEDAC: Examples
    - `ls-tree 3b18e512dba79e4c8300dd08aeb37f8e728b8dad`
        -
        ```
        $ git ls-tree <tree_sha>
        040000 tree <tree_sha_1>    dir1
        040000 tree <tree_sha_2>    dir2
        100644 blob <blob_sha_1>    file1
        ```
    - `ls-tree --name-only 3b18e512dba79e4c8300dd08aeb37f8e728b8dad`
        -
        ```
        $ git ls-tree --name-only <tree_sha>
        dir1
        dir2
        file1
        ```
- PEDAC: Data Structures And Algorithms
    - tree object anatomy (after zlib decompression):
        - content format (binary-encoded):
        ```
        tree <size>\0
        <mode> <name>\0<20_byte_sha>
        <mode> <name>\0<20_byte_sha>
        ```
        - no newline chars in actual contents
        - `<size>`: size in bytes of `<file>` before zlib compression
        - `\0`: a null byte
        - line 2: a Git blob or tree object entry
            - `<mode>`: mode of file or dir of values in the set:
                - 100644 (regular file)
                - 100755 (executable file)
                - 120000 (symbolic link)
                - 40000 (directories)
            - `<name>`: name of file or directory
            - `<20_byte_sha>`: SHA-1 hash as 20 raw bytes long (non-hexadecimal)
        - entries are sorted in ASC order by name
    - TODO
