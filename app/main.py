import sys
import os
import zlib
import hashlib
import stat
import time
from datetime import datetime

def entry_from_path(entry_path: str) -> str:
    return entry_path.split(os.sep)[-1]

def entry_mode(dir_or_file: str) -> int:
    mode = os.stat(dir_or_file).st_mode
    if stat.S_ISDIR(mode):
        return 40000
    if stat.S_ISLNK(mode):
        return 120000
    return 100755 if os.access(dir_or_file, os.X_OK) else 100644

def create_blob_object(file_path: str) -> dict:
    # Create Git blob object and compress it
    file_fd = open(file_path, "rb")
    file_contents = file_fd.read()
    file_size = len(file_contents)
    blob_contents_bytes = f"blob {file_size}\0".encode() + file_contents
    blob_contents_compressed_bytes = zlib.compress(blob_contents_bytes)
    file_fd.close()

    # Write compressed Git blob object to file
    file_hash = hashlib.sha1(blob_contents_bytes).hexdigest()
    blob_dir = file_hash[:2]
    blob_name = file_hash[2:]
    blob_dir_path = f".{os.sep}.git{os.sep}objects{os.sep}{blob_dir}"
    blob_file_path = f"{blob_dir_path}{os.sep}{blob_name}"
    if not os.path.exists(blob_dir_path):
        os.mkdir(blob_dir_path)
    if not os.path.exists(blob_file_path):
        blob_fd = open(f"{blob_dir_path}{os.sep}{blob_name}", "wb")
        blob_fd.write(blob_contents_compressed_bytes)
        blob_fd.close()

    return {
        "mode": entry_mode(file_path),
        "name": entry_from_path(file_path),
        "hashlib_sha1_obj": hashlib.sha1(blob_contents_bytes)
    }

def dir_contents(dir_path: str) -> list:
    if not os.path.isdir(dir_path):
        return []

    def is_valid_entry(entry: str) -> bool:
        if entry == ".git":
            return False
        entry = f"{dir_path}{os.sep}{entry}"
        if os.path.isfile(entry):
            return True
        return os.path.isdir(entry) and len(os.listdir(entry)) > 0
        
    return sorted(filter(is_valid_entry, os.listdir(dir_path)))

def write_tree_object(dir_path: str) -> dict:
    contents = dir_contents(dir_path)
    if len(contents) == 0:
        return {}

    root_dir_size = 0
    entries = []
    for dir_or_file in contents:
        res_object = None
        entry = None
        dir_or_file_path = f"{dir_path}{os.sep}{dir_or_file}"
        if os.path.isfile(dir_or_file_path):
            res_object = create_blob_object(dir_or_file_path)
        else: # is dir
            res_object = write_tree_object(dir_or_file_path)
        if len(res_object.keys()) == 0:
            continue
        entry = f"{res_object["mode"]} {res_object["name"]}\0".encode()
        entry += res_object["hashlib_sha1_obj"].digest()
        root_dir_size += len(entry)
        entries.append(entry)

    tree_contents_bytes = f"tree {root_dir_size}\0".encode()
    for entry in entries:
        tree_contents_bytes += entry
    tree_hash = hashlib.sha1(tree_contents_bytes).hexdigest()
    tree_contents_compressed_bytes = zlib.compress(tree_contents_bytes)
    tree_dir = tree_hash[:2]
    tree_name = tree_hash[2:]
    tree_path = f".git{os.sep}objects{os.sep}{tree_dir}"
    if not os.path.exists(tree_path):
        os.mkdir(tree_path)
    with open(f"{tree_path}{os.sep}{tree_name}", "wb") as tree_fd:
        tree_fd.write(tree_contents_compressed_bytes)
    
    return {
        "mode": entry_mode(dir_path),
        "name": entry_from_path(dir_path),
        "hashlib_sha1_obj": hashlib.sha1(tree_contents_bytes)
    }

def does_object_exist(sha1_hash: str, object_type: str = "") -> bool:
    # `sha1_hash` should be a 40-char SHA-1 hexadecimal hash string
    if len(sha1_hash) != 40:
        return False
    object_path = f".git{os.sep}objects{os.sep}{sha1_hash[:2]}{os.sep}{sha1_hash[2:]}"
    if not os.path.exists(object_path):
        return False
    if object_type == "":
        return True
    object_fd = open(object_path, "rb")
    object_contents_uncompressed_bytes = zlib.decompress(object_fd.read())
    object_fd.close()
    return object_type.encode() == object_contents_uncompressed_bytes[:len(object_type)]

def create_commit_object(tree_sha: str, message: str, commit_sha: str = "") -> str:
    # Create Git commit object contents
    timestamp = round(time.time())
    timezone_offset = datetime.now().astimezone().strftime("%z")
    name = "John Doe"
    email = "john@example.com"
    commit_contents_str = (
        f"author {name} <{email}> {timestamp} {timezone_offset}\n" +
        f"committer {name} <{email}> {timestamp} {timezone_offset}\n" +
        f"\n{message}\n"
    )
    if commit_sha:
        commit_contents_str = f"parent {commit_sha}\n" + commit_contents_str
    commit_contents_str = f"tree {tree_sha}\n" + commit_contents_str
    commit_contents_uncompressed_bytes = commit_contents_str.encode()
    commit_size = len(commit_contents_uncompressed_bytes)
    commit_contents_uncompressed_bytes = (
        f"commit {commit_size}\0".encode() + commit_contents_uncompressed_bytes
    )

    # Compress Git Commit object contents + write to file
    new_commit_sha = hashlib.sha1(commit_contents_uncompressed_bytes).hexdigest()
    commit_dir_path = f".git{os.sep}objects{os.sep}{new_commit_sha[:2]}"
    if not os.path.exists(commit_dir_path):
        os.mkdir(commit_dir_path)
    commit_file_path = f"{commit_dir_path}{os.sep}{new_commit_sha[2:]}"
    with open(commit_file_path, "wb") as commit_fd:
        commit_fd.write(zlib.compress(commit_contents_uncompressed_bytes))

    return new_commit_sha

def main():
    # print("Logs from your program will appear here!", file=sys.stderr)
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "init":
        dirs = [".git", ".git/objects", ".git/refs"]
        for git_dir in dirs:
            if not os.path.exists(git_dir):
                os.mkdir(git_dir)
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file":
        if len(sys.argv) != 4 or sys.argv[2] != "-p" or len(sys.argv[3]) != 40:
            print("[Error] Usage: cat-file -p <blob_sha>")
            return
        blob_sha = sys.argv[3]
        blob_path = f".{os.sep}.git{os.sep}objects{os.sep}{blob_sha[:2]}{os.sep}{blob_sha[2:]}"
        if not os.path.exists(blob_path):
            print(f"[Error] Blob does not exist at '{blob_path}'")
            return
        blob_compressed_fd = open(blob_path, "rb")
        blob_uncompressed_bytes = zlib.decompress(blob_compressed_fd.read())
        blob_uncompressed_str = blob_uncompressed_bytes.decode()
        blob_compressed_fd.close()
        null_pos = blob_uncompressed_str.find("\0")

        print(blob_uncompressed_str[null_pos + 1:], end="")
    elif command == "hash-object":
        if len(sys.argv) != 4 or sys.argv[2] != "-w" or len(sys.argv[3]) < 1:
            print("[Error] Usage: hash-object -w <file>")
            return
        file = sys.argv[3]
        if not os.path.exists(file):
            print(f"[Error] File '{file}' does not exist")
            return

        file_dict = create_blob_object(file)
        print(file_dict["hashlib_sha1_obj"].hexdigest())
    elif command == "ls-tree":
        passed_args_count = len(sys.argv)
        if not (3 <= passed_args_count <= 4):
            print("[Error] Usage: ls-tree [--name-only] <tree_sha>")
            return
        tree_sha = sys.argv[-1]
        tree_path = f".{os.sep}.git{os.sep}objects{os.sep}{tree_sha[:2]}{os.sep}{tree_sha[2:]}"
        if not os.path.exists(tree_path):
            print(f"[Error] Tree object with hash '{tree_sha}' does not exist")
            return
        is_name_only = (len(sys.argv) == 4 and sys.argv[2] == "--name-only")

        # Read tree object contents
        tree_compressed_fd = open(tree_path, "rb")
        tree_uncompressed_bytes = zlib.decompress(tree_compressed_fd.read())
        tree_compressed_fd.close()
        
        # Traverse tree object contents
        pos = tree_uncompressed_bytes.find(b"\0") + 1
        max_pos = len(tree_uncompressed_bytes)

        while pos < max_pos:
            # Get Git object Unix mode and object type
            is_dir_mode = tree_uncompressed_bytes[pos:pos + 5] == b'40000'
            mode = "040000"
            if not is_dir_mode:
                mode = tree_uncompressed_bytes[pos:pos + 6].decode()
            object_type = "tree" if is_dir_mode else "blob"

            # Get Git object name
            pos += 5 if is_dir_mode else 6
            name_start_pos = pos + 1
            null_pos = tree_uncompressed_bytes.find(b"\0", name_start_pos)
            object_name = tree_uncompressed_bytes[name_start_pos:null_pos].decode()

            # Get Git object SHA1 hash
            object_hash = tree_uncompressed_bytes[null_pos + 1:null_pos + 21].hex()

            if is_name_only:
                print(object_name)
            else:
                print(f"{mode} {object_type} {object_hash}    {object_name}")

            pos = null_pos
            pos += 21
    elif command == "write-tree":
        tree_obj = write_tree_object(".")
        print(tree_obj["hashlib_sha1_obj"].hexdigest())
    elif command == "commit-tree":
        argv_len = len(sys.argv)
        proper_use = "[Error] Usage: commit-tree <tree_sha> [-p <commit_sha>] -m \"<message>\""
        if argv_len != 5 and argv_len != 7:
            print(proper_use)
            print("[Error] Invalid number of arguments passed")
            return
        if (argv_len == 7 and sys.argv[3] != "-p") or sys.argv[-2] != "-m":
            print(proper_use)
            print("[Error] Invalid flags passed")
            return
        if len(sys.argv[-1]) < 1:
            print(proper_use)
            print("[Error] Commit message must enclosed by double quotes and not empty")
            print(f"Commit message: '{sys.argv[-1]}'")
            return
        if not does_object_exist(sys.argv[2], "tree"):
            print(f"[Error] Tree object '{sys.argv[2]}' does not exist")
            return
        if argv_len == 7 and not does_object_exist(sys.argv[4], "commit"):
            print(f"[Error] Commit object '{sys.argv[4]}' does not exist")
            return

        has_commit_sha = argv_len == 7
        commit_sha = sys.argv[4] if has_commit_sha else ""
        new_commit_sha = create_commit_object(
            sys.argv[2], sys.argv[-1], commit_sha
        )

        print(new_commit_sha)
    else:
        raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
