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
        - if file `tree_fd` linked to `<tree_sha>` exists and flag `--name-only` is present,
            - prints a list of tree and blob object entries in `tree_fd` in ASC order by file name
                - list has 3 columns: `<mode> <object_type> <object_sha>`
        - if file `tree_fd` linked to `<tree_sha>` exists and flag `--name-only` is NOT present,
            - prints a list of tree and blob object entries in `tree_fd` in ASC order by file name
                - list only has 1 column: `<file_name>`
    - TODO: figure out how to test and imitate the real `git ls-tree` command
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
        - for string `tree_content` that represents the UTF8-encoded text content of the file linked to `file_content`:
            - let `first_null_pos` = index of 1st null byte `\0` in `tree_content`
            - object header:
                - `tree <size>\0` = `file_content[:first_null_pos]`
            - for each Git object entry:
                - int `null_pos` = index of current null byte char pos in `tree_content`
                - int `space_pos` = index of current space char in `tree_content` between the previous null byte char and the current null byte char
                - `<mode>` =
                    - if entry is a file object:
                        - `tree_content[space_pos - 6:space_pos]`
                    - if entry is a directory object:
                        - `tree_content[space_pos - 5:space_pos]`
                - `<name>` = `tree_content[space_pos + 1:null_pos]`
                - `<20_byte_sha>` = `tree_content[null_pos + 1:null_pos + 21]`
    - questions
        - does file size of 20 bytes == string of 20 chars?
            - yes
        - how to check if an entry in a tree object represents:
            - a regular file?
            - an executable file?
            - a symbolic link?
            - a directory?
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
    - if file at `./.git/objects/<tree_sha[:2]>/<tree_sha[2:]>` doesn't exist,
        - throw error
    - set bool `is_name_only` to true if `--name-only` is present, else to false
    - open file `./.git/objects/<tree_sha[:2]>/<tree_sha[2:]` as `tree_file`
    - decompress file `tree_file` via `zlib` compression as `tree_decompressed_bytes` bytes
    - set string `tree_decompressed_str` to `tree_decompressed_bytes` converted to a string
    - set int `space_pos` to index of 2nd space char in `tree_decompressed_str`
    - set int `null_pos` to index of 2nd null byte char in `tree_decompressed_str`
    - while both `space_pos` and `null_pos` are not -1,
        - set string `mode` =
            - if entry is a file object:
                - `tree_content[space_pos - 6:space_pos]`
            - if entry is a directory object:
                - `tree_content[space_pos - 5:space_pos]`
        - set string `name` = `tree_content[space_pos + 1:null_pos]`
        - set string `sha_20_bytes` = `tree_content[null_pos + 1:null_pos + 21]`
        - if `is_name_only`,
            - print `name`
        - set `space_pos` = index of next space char in `tree_decompressed_str`
        - set `null_pos` = index of next null byte char in `tree_decompressed_str`
    - helper functions:
        - `is_tree_type(object_decompressed_str: string) -> bool`:
            - set `first_space_pos` = index of first ` ` space char in `object_decompressed_str`
            - return `object_decompressed_str[:first_space_pos]` == "tree"
        - `is_blob_type(object_decompressed_str: string) -> bool`:
            - set `first_space_pos` = index of first ` ` space char in `object_decompressed_str`
            - return `object_decompressed_str[:first_space_pos]` == "blob"
