# pazel - generate Bazel BUILD files for Python

[![Build Status](https://travis-ci.org/tuomasr/pazel.svg?branch=master)](https://travis-ci.org/tuomasr/pazel)

## Requirements

### pazel
No requirements. Tested on Python 2.7 and 3.6 on Ubuntu 16.04 and macOS High Sierra.

### Bazel
Tested on Bazel 0.11.1. All recent versions are expected to work.

## Installation

```
> git clone https://github.com/tuomasr/pazel.git
> cd pazel
> python setup.py install
```

## Usage

### Default usage

The following example generates all BUILD files for the sample Python project in `sample_app`.

```
> cd sample_app   # Assumes that you are in the pazel root directory containing setup.py.
> pazel
Generated BUILD files for <pazel_install_dir>/sample_app.
```

Now, we can build, test, and run the sample project using the invocations below, respectively.

```
> bazel build
> bazel test ...
> bazel run foo:bar3
```

### Command-line options

`pazel -h` shows a summary of the command-line options. Each of them is explained below.

By default, BUILD files are generated recursively for the current working directory.
Use `pazel <some_path>` to generate BUILD file(s) recursively for another directory
or for a single Python file.

All imports are assumed to be relative to the current working directory. For example,
`sample_app/foo/bar2.py` imports from `sample_app/foo/bar1.py` using `from foo.bar1 import sample`.
Use `pazel -r <some_path>` to override the path to which the imports are relative.

By default, `pazel` adds rules to install all external Python packages. If your environment has
pre-installed packages for which these rules are not required, then use `pazel -p`.


### Ignoring rules in existing BUILD files

The tag `# pazel-ignore` causes `pazel` to ignore the rule that immediately follows the tag in an
existing BUILD file. In particular, the tag can be used to skip custom rules that `pazel` does not 
handle. `pazel` places the ignored rules at the bottom of the BUILD file. See `sample_app/foo/BUILD`
for an example using the tag.


### Customizing and extending pazel

`pazel` can be programmed using a `.pazelrc` Python file that should be located in the project root
(defaults to the current working directory but can be changed with the flag `pazel -r <some_path>`).

The user can define variables `HEADER` and `FOOTER` to add custom header and footer to
all BUILD files, respectively. See `sample_app/.pazelrc` and `sample_app/BUILD` for an example that
adds the same `visibility` to all BUILD files.

If some pip package has different install name than import name, then the user
should define `EXTRA_IMPORT_NAME_TO_PIP_NAME` dictionary accordingly. `sample_app/.pazelrc` has
`{'yaml': 'pyyaml'}` as an example. In addition, the user can specify local packages and their
corresponding Bazel dependencies using the `EXTRA_LOCAL_IMPORT_NAME_TO_DEP` dictionary.

The user can define custom Bazel rules by defining a new `Rule` class and by
adding the class to `EXTRA_RULES` list in `.pazelrc`. `sample_app/.pazelrc` defines a custom
`PyDoctestRule` class that identifies all doctests and generates custom `py_doctest` Bazel rules for
them as defined in `sample_app/custom_rules.bzl`. Custom `Rule` classes must follow the interface in
`pazel/bazel_rules.py`.
