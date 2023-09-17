import os
import tempfile
import shutil

if os.name == 'nt':

    class TempDirectory:

        _directory: str

        def __init__(self):
            self._directory = tempfile.mkdtemp()

        def __del__(self):
            shutil.rmtree(self._directory)

        @property
        def directory(self):
            return self._directory

elif os.name == 'posix':

    class TempDirectory:

        TEMP_DIRECTORY: str = "/dev/shm/firework-rating"

        _directory: str

        def __init__(self):
            self._directory = self.TEMP_DIRECTORY
            os.makedirs(self._directory, exist_ok=True)

        def __del__(self):
            shutil.rmtree(self._directory)

        @property
        def directory(self):
            return self._directory

else:
    raise OSError(f"OS {os.name} not supported.")
