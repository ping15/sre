from cryptography.fernet import Fernet


class Cipher:
    def __init__(self, key=None):
        self.key = key
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data: str) -> str:
        return self.cipher_suite.encrypt(bytes(data, "utf-8")).decode("utf-8")

    def decrypt(self, data: str) -> str:
        return self.cipher_suite.decrypt(bytes(data, "utf-8")).decode("utf-8")


cipher = Cipher(b"1i54T4vwS3a7ltiL3j0Yod6Iix4T3KnKpP0xxB54W8E=")
