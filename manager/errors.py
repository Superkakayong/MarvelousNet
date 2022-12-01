class BaseErrorData:
    def __init__(self, code: int, reason: str):
        self._code = code
        self._reason = reason

    @property
    def error_code(self):
        return self._code

    @property
    def error_reason(self):
        return self._reason


SuccessCode = BaseErrorData(100, "Command executed successfully")
ApiTaskFailNoFileField = BaseErrorData(201, "/task must have a file field, using Form Data.")
ApiTaskFailFileIsEmpty = BaseErrorData(202, "file is empty.")
