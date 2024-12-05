from pathlib import Path


def check_directory(directory: Path, create: bool = True, parents: bool = False):
    if not directory.exists():
        if create:
            directory.mkdir(parents=parents)
        else:
            raise FileNotFoundError(f'The directory "{directory}" doesn\'t exist.')
    elif not directory.is_dir():
        raise NotADirectoryError(f'"{directory}" is not a directory.')
