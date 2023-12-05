import io

import pandas as pd

# from .email import Email


class ExcelReader(object):

    def __init__(self, file) -> None:#, Email: Email):
        # self.Email = Email
        self.data = self._make_dataframe(file)
        self._make_header_lowercase()

    @classmethod
    def _make_dataframe(self, file) -> pd.DataFrame:
        file_bytes = file.read()
        memmory_file = io.BytesIO(file_bytes)

        return pd.read_excel(memmory_file)

    def _make_header_lowercase(self) -> None:
        self.data.columns = self.data.columns.str.lower()

    def is_header_valid(self) -> bool:
        if "email" in list(self.data.columns):
            return True

        return False

