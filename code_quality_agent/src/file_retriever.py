import os


class FileRetriever:
    """
    A class designed to manage and organize file retrieval from a specified directory.

    This class, FileRetriever, facilitates the retrieval and organization of files within a given directory. It supports operations such as initializing with a specific directory, recursively searching for files while ignoring specified files and directories, creating mappings of file extensions to file paths, and retrieving these mappings. It also provides a string representation of the current state of file retrieval and organization.

    Attributes:
        directory (str): The path to the directory from which files are retrieved.
        ignored_dirs (list): Directories that are ignored during the file search.
        ignored_files (list): Files that are ignored during the file search.
        file_list (list): List of files found in the directory and its subdirectories.
        file_map (dict): Dictionary mapping file extensions to lists of file paths.

    Methods:
        __init__(self, directory): Initializes the FileRetriever object with the specified directory.
        _find_files(self): Recursively searches and populates the file_list with files from the directory.
        _file_mapping(self): Organizes files into a dictionary based on their file extensions.
        get_mapping(self): Returns the dictionary mapping file extensions to file paths.
        __str__(self): Returns a string representation of the FileRetriever object.
    """

    def __init__(self, directory):
        """
        Initialize the FileRetriever object with a specified directory.

        This constructor sets up the initial directory to search for files, initializes lists
        for ignored directories and files, and prepares structures to hold the list of files
        and their mappings based on file extensions. It also triggers the file finding and
        mapping processes.

        Parameters:
            directory (str): The path to the directory where files will be retrieved.
        """
        self.directory = directory
        self.ignored_dirs = ['__pycache__', 'venv', 'node_modules', 'dist',
            'build', 'out', 'target', 'bin', 'obj', 'lib', 'include', 'logs']
        self.ignored_files = ['__init__.py', 'Thumbs.db', 'desktop.ini']
        self.file_list = []
        self.file_mapping = {}
        self._find_files()
        self._file_mapping()

    def _find_files(self):
        """
        Recursively searches for files in the specified directory while ignoring certain directories and files.

        This method populates the `file_list` attribute with the absolute paths of files found in the given directory,
        excluding those that start with a dot ('.') or are listed in `ignored_files`. It also skips directories listed
        in `ignored_dirs` and any hidden directories (those starting with a dot '.').
        """
        file_list = []
        for root, dirs, files in os.walk(self.directory):
            dirs[:] = [d for d in dirs if not d[0] == '.' and not d in self
                .ignored_dirs]
            for file in files:
                if not file[0] == '.' and not file in self.ignored_files:
                    file_list.append(os.path.abspath(os.path.join(root, file)))
        self.file_list = file_list

    def _file_mapping(self):
        """
        Creates a mapping of file extensions to lists of file paths within the specified directory.

        This method iterates over all files found in the directory and its subdirectories, excluding
        those in ignored directories or with ignored filenames. It then categorizes these files based
        on their extensions into a dictionary where each key is a file extension and each value is a
        list of paths to files with that extension.
        """
        mapping = {}
        for file in self.file_list:
            _, extension = os.path.splitext(file)
            extension = extension[1:]
            if extension in mapping:
                mapping[extension].append(file)
            else:
                mapping[extension] = [file]
        self.file_mapping = mapping

    def get_mapping(self):
        """
        Retrieves the mapping of file extensions to file paths.

        This method returns a dictionary where the keys are file extensions (without the dot),
        and the values are lists of file paths that have that extension.

        Returns:
            dict: A dictionary mapping file extensions to lists of file paths.
        """
        return self.file_mapping

    def __str__(self):
        """
        Return a string representation of the FileRetriever object, detailing the directory being scanned and the files organized by their extensions.

        Returns:
            str: A formatted string that lists the directory followed by each file type and its associated files.
        """
        ret = 'Directory: ' + self.directory + '\n'
        for key, value in self.file_mapping.items():
            ret += key + ':\n'
            for file in value:
                ret += '  ' + file + '\n'
        return ret
