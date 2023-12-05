class Email(object):

    def __init__(self, value: str):
        self._value = value

    def get_value(self):
        return self._value

    @classmethod
    def create_list_emails(cls, emails: list[dict]) -> list:
        return [cls.create_email(email) for email in emails]

    @classmethod
    def create_email(cls, value: str):
        return cls(value)