import sys
import os
import zlib
import hashlib

def main():
    # print("Logs from your program will appear here!", file=sys.stderr)

    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
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

        # Create Gib blob object and compress it
        file_fd = open(file, "r")
        file_contents = file_fd.read()
        file_size = len(file_contents)
        blob_contents_str = f"blob {file_size}\0{file_contents}"
        blob_contents_compressed_bytes = zlib.compress(blob_contents_str.encode())
        file_fd.close()

        # Write compressed Git blob object to file
        file_hash = hashlib.sha1(blob_contents_str.encode()).hexdigest()
        blob_dir = file_hash[:2]
        blob_name = file_hash[2:]
        blob_path = f".{os.sep}.git{os.sep}objects{os.sep}{blob_dir}"
        if not os.path.exists(blob_path):
            os.mkdir(blob_path)
        with open(f"{blob_path}{os.sep}{blob_name}", "wb") as blob_fd:
            blob_fd.write(blob_contents_compressed_bytes)

        print(file_hash)
    # TODO: add non-`--name-only` flagged `ls-tree` functionality
    elif command == "ls-tree":
        if len(sys.argv) < 3:
            print("[Error] Usage: ls-tree [--name-only] <tree_sha>")
            return
        tree_sha = sys.argv[-1]
        tree_path = f".{os.sep}.git{os.sep}objects{os.sep}{tree_sha[:2]}{os.sep}{tree_sha[2:]}"
        if not os.path.exists(tree_path):
            print(f"[Error] Tree object with hash '{tree_sha}' does not exist")
            return
        is_name_only = (len(sys.argv) == 4 and sys.argv[2] == "--name-only")

        # Read the tree object contents
        tree_compressed_fd = open(blob_path, "rb")
        tree_uncompressed_bytes = zlib.decompress(tree_compressed_fd.read())
        tree_uncompressed_str = tree_uncompressed_bytes.decode()
        tree_compressed_fd.close()
        
        # Traverse tree object contents
        space_pos = tree_uncompressed_str.find(" ")
        space_pos = tree_uncompressed_str.find(" ", space_pos + 1)
        null_pos = tree_uncompressed_str.find("\0")
        null_pos = tree_uncompressed_str.find("\0", null_pos + 1)

        while space_pos != -1 and null_pos != -1:
            name = tree_uncompressed_str[space_pos + 1:null_pos]

            if is_name_only:
                print(name)

            space_pos = tree_uncompressed_str.find(" ", space_pos + 1)
            null_pos = tree_uncompressed_str.find("\0", null_pos + 1)
        
    else:
        raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
