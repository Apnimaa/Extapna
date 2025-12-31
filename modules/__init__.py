import glob
from os.path import basename, dirname, isfile, join

def __list_all_modules():
    mod_paths = glob.glob(join(dirname(__file__), "*.py"))
    all_modules = [
        basename(f)[:-3]
        for f in mod_paths
        if isfile(f)
        and f.endswith(".py")
        and not f.endswith("__init__.py")
    ]
    return sorted(all_modules)

ALL_MODULES = __list_all_modules()

__all__ = ALL_MODULES + ["ALL_MODULES"]
