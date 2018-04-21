"""Parse imports in Python files and infer what is being imported from which package."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast
import os

from pazel.helpers import contains_python_file
from pazel.helpers import is_installed


def get_imports(script_source):
    """Parse imported packages and objects imported from packages.

    Args:
        script_source (str): The source code of a Python script.

    Returns:
        packages (list of tuple): List of (package name, None) tuples.
        from_imports (list of tuple): List of (package/module name, some object) tuples. Note that
        some object can be a function, object, module, or package.
    """
    packages = []
    from_imports = []
    ast_of_source = ast.parse(script_source)

    for node in ast_of_source.body:
        # Parse expressions of the form "from X import Y".
        if isinstance(node, ast.ImportFrom):
            module = node.module

            for name in node.names:
                from_imports.append((module, name.name))
        # Parse expressions of the form "import X".
        elif isinstance(node, ast.Import):
            for package in node.names:
                packages.append((package.name, None))

    return packages, from_imports


def infer_import_type(all_imports, project_root, contains_pre_installed_packages):
    """Infer what is being imported.

    Given a list of tuples (package/module, some object) infer whether the first element is a
    package or a module and whether it is installed. Also, infer the type of the second element.

    Args:
        all_imports (list of tuple): All imports in a Python script.
        project_root (str): Local imports are assumed to be relative to this path.
        contains_pre_installed_packages (bool): Whether the environment contains external packages
        or not.

    Returns:
        packages: Set of package names that are imported.
        modules: Set of module names that are imported.
    """
    modules = []
    packages = []

    # Base is package/module and the type of unknown is inferred below.
    for base, unknown in all_imports:
        # Early exit if base is in the installed modules of the current environment.
        if is_installed(base, unknown, contains_pre_installed_packages):
            continue

        # By default, assume that 'base' is a module and 'unknown' is function, variable or any
        # other object in that module.
        module_path = os.path.join(project_root, base.replace('.', '/') + '.py')
        if os.path.exists(module_path):
            modules.append(base)
            continue

        # Check if 'unknown' is actually a package or a module.
        dotted_path = base + '.%s' % unknown
        package_path = os.path.join(project_root, dotted_path.replace('.', '/'))
        module_path = os.path.join(project_root, dotted_path.replace('.', '/') + '.py')

        unknown_is_package = os.path.isdir(package_path) and contains_python_file(package_path)
        unknown_is_module = os.path.isfile(module_path)

        if unknown_is_package:
            # Assume that for package //foo, there exists rule //foo:foo.
            # TODO: Relax this assumption.
            dotted_path += '.%s' % unknown
            modules.append(dotted_path)
            continue

        if unknown_is_module:
            modules.append(dotted_path)
            continue

        # Finally, assume that base is either a pip installable or a local package.
        packages.append(base)

    return set(packages), set(modules)