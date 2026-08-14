import hashlib
import hmac
import unittest

from webhook_security import verify_meta_signature


class WebhookSignatureTests(unittest.TestCase):
    def test_accepts_valid_sha256_signature(self):
        body = b'{"entry":[]}'
        secret = "test-app-secret-value"
        signature = "sha256=" + hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        self.assertTrue(verify_meta_signature(body, signature, secret))

    def test_rejects_missing_or_tampered_signature(self):
        self.assertFalse(verify_meta_signature(b"{}", None, "secret"))
        self.assertFalse(verify_meta_signature(b"tampered", "sha256=" + "0" * 64, "secret"))


if __name__ == "__main__":
    unittest.main()
