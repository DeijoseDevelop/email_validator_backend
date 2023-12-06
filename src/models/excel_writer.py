from io import BytesIO

import pandas as pd


class ExcelWriter(object):

    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data
        self.valid_emails = []
        self.invalid_emails = []
        self.valid_excel_file = BytesIO()
        self.invalid_excel_file = BytesIO()

    def set_seeks(self):
        self.valid_excel_file.seek(0)
        self.invalid_excel_file.seek(0)

    def add_valid_email(self, email) -> None:
        self.valid_emails.append(email)

    def add_invalid_email(self, email) -> None:
        self.invalid_emails.append(email)

    def make_dataframe(self, data: list[dict]) -> pd.DataFrame:
        return pd.DataFrame(data)

    def make_excel(self, excel_file: BytesIO, df: pd.DataFrame) -> None:
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Hoja1', index=False)