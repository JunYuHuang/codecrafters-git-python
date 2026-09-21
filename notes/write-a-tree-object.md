# Notes:

- PEDAC: Problem
    - input:
        - `command`: string in format `write-tree`
    - output:
        - N/A
    - side effects:
        - recursively creates all the tree and object objects at the root directory of the Git repo
        - prints the 40-char SHA1 hexadecimal string of the root tree object
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
        - TODO
- PEDAC: Examples
    - ex.1
        ```
        $ echo "hello world" > test_file_1.txt
        $ mkdir test_dir_1
        $ echo "hello world" > test_dir_1/test_file_2.txt
        $ mkdir test_dir_2
        $ echo "hello world" > test_dir_2/test_file_3.txt
        $ /path/to/your_program.sh write-tree
        4b825dc642cb6eb9a060e54bf8d69288fbee4904
        ```
    - ex.2: empty dir
        - ??
- PEDAC: Data Structures And Algorithms
    - set string array `entries` to `list_dir_contents("./")`
    - set string `root_dir_hash` to `create_dir_object("./", entries)`
    - print `root_dir_hash`
    - helper functions:
        - `create_blob_object(file_path: string) -> dict`:
            - creates a file that represents a Git object at `.git/objects/`
            - returns dictionary / hashmap object `res`
            - `res` = {
                - `size`: int size of file; length of contents in file
                - `mode`: 5 or 6 digits as a string that represents the file's type and permissions
                - `name`: the file name in `file_path` minus any prefixed path
                - `hash_bytes`: SHA-1 hash of the file as 20 raw bytes
            }
        - `dir_contents(dir_path: string) -> string[]`:
            - if `dir_path` is not a valid directory,
                - return empty array
            - return a string array of the names of all the files and directories
            in `dir_path` sorted in ascending alphabetical order
                - exclude empty directories and the `.git` dir
        - `create_tree_object(root_path: string) -> dict`:
            - set string array `dir_contents` to `dir_contents(root_path)`
            - if `dir_contents` is empty,
                - return dictionary / hashmap object `res`
                - `res` = 
                    ```
                    {
                        size: 0
                        mode: "INVALID_MODE",
                        name: "INVALID_NAME",
                        hash_bytes: b"INVALID_HASH"
                    }
                    ```
            - set int `root_dir_size` to 0
            - set `entries` to an empty array of `bytesarray` objects
            - loop for string `dir_or_file` in `dir_contents`,
                - set `res_object` to null
                - set `entry` to null
                - if `dir_or_file` is a file,
                    - set `res_object` to `create_blob_object(dir_or_file)`
                - else (`dir_or_file` is a dir),
                    - set `res_object` to `create_tree_object(dir_or_file)`
                - add `res_object[size]` to `root_dir_size`
                - set bytes object `entry` from string:
                    - `<res_object[mode]> <res_object[name]>\0<res_object[hash_bytes]>`
                - push `entry` to `entries`
            - set `tree_content_bytes` to bytearray from string `tree <root_dir_size>\0`
            - loop for bytesarray `entry` in `entries`,
                - append `entry` to `tree_content_bytes`
            - set `tree_hash` to SHA-1 40-char hash as hexadecimal string of `tree_content_bytes`
            - if dir `.git/objects/<tree_hash[:2]>` doesn't exist,
                - create the dir
            - set file object / descriptor `tree_object` at path `.git/objects/<tree_hash[:2]>/<tree_hash[2:]>` opened in binary write mode
            - set `tree_contents_compressed_bytes` to `tree_content_bytes` compressed via zlib compression method
            - write `tree_contents_compressed_bytes` to `tree_object`
            - close file `tree_object`
            - return dictionary / hashmap object `res`
                - `res` = 
                    ```
                    {
                        size: `root_dir_size`
                        mode: "40000",
                        name: dir name extracted from `root_path`,
                        hash_bytes: `tree_content_bytes` converted to SHA1 hash as 20-bytes
                    }
                    ```
    - TODO: test with real Git `write-tree` and `ls-tree` commands to find how it handle these edge cases:
        - Git project with an empty folder
            - Git doesn't create tree objects for empty folders
        - Git project with a single file
        - Git project with a folder that has a nested folder
            - does the Git tree object's content stored the nested folder's relative path up to the folder, or just the folder name with no prefixed path?
                - just the dir name with no prefixed path before it