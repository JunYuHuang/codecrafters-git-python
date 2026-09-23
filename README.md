[![progress-banner](https://backend.codecrafters.io/progress/git/c0c392c0-e0af-4ab5-8092-e04f82a57e85)](https://app.codecrafters.io/users/JunYuHuang?r=2qF)

This is a starting point for Python solutions to the
["Build Your Own Git" Challenge](https://codecrafters.io/challenges/git).

In this challenge, you'll build a small Git implementation that's capable of
initializing a repository, creating commits and cloning a public repository.
Along the way we'll learn about the `.git` directory, Git objects (blobs,
commits, trees etc.), Git's transfer protocols and more.

**Note**: If you're viewing this repo on GitHub, head over to
[codecrafters.io](https://codecrafters.io) to try the challenge.

# Passing the first stage

The entry point for your Git implementation is in `app/main.py`. Study and
uncomment the relevant code, and then run the command below to execute the tests
on our servers:

```sh
codecrafters submit
```

That's all!

# Stage 2 & beyond

Note: This section is for stages 2 and beyond.

1. Ensure you have `uv` installed locally
1. Run `./your_program.sh` to run your Git implementation, which is implemented
   in `app/main.py`.
1. Run `codecrafters submit` to submit your solution to CodeCrafters. Test
   output will be streamed to your terminal.

# Testing locally

The `your_program.sh` script is expected to operate on the `.git` folder inside
the current working directory. If you're running this inside the root of this
repository, you might end up accidentally damaging your repository's `.git`
folder.

We suggest executing `your_program.sh` in a different folder when testing
locally. For example:

```sh
mkdir -p /tmp/testing && cd /tmp/testing
/path/to/your/repo/your_program.sh init
```

To make this easier to type out, you could add a
[shell alias](https://shapeshed.com/unix-alias/):

```sh
alias mygit=/path/to/your/repo/your_program.sh

mkdir -p /tmp/testing && cd /tmp/testing
mygit init
```

Alternative:
```sh
python {path to '/app/main.py'} {your Git command arguments}

# Example:
mkdir test_git_repo
cd test_git_repo
python ../app/main.py init
```

# Supported Git commands

```
python app/main.py init
python app/main.py cat-file -p {object_sha_hash}
python app/main.py hash-object -w {path_to_file}
python app/main.py ls-tree [--name-only] {tree_sha_hash}
python app/main.py write-tree
```
