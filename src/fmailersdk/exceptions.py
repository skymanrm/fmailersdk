class FmailerSdkException(Exception):
    msg = "Unhandled exception"

    def __init__(self, msg: str, *args):
        super().__init__(*args)
        self.msg = msg

    def __str__(self):
        return f"FmailerSdkException: {self.msg}"
