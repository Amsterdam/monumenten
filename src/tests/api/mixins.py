import jwt
import time
from monumenten import settings

from authorization_django.config import settings as middleware_settings


class JWTMixin(object):

    # The following JWKS data was obtained in the authz project :  jwkgen -create -alg ES256
    # This is a test private/public key pair.
    settings.DATAPUNT_AUTHZ['JWKS'] = """
    {
        "keys": [
            {
                "kty": "EC",
                "key_ops": [
                    "verify",
                    "sign"
                ],
                "kid": "2aedafba-8170-4064-b704-ce92b7c89cc6",
                "crv": "P-256",
                "x": "6r8PYwqfZbq_QzoMA4tzJJsYUIIXdeyPA27qTgEJCDw=",
                "y": "Cf2clfAfFuuCB06NMfIat9ultkMyrMQO9Hd2H7O9ZVE=",
                "d": "N1vu0UQUp0vLfaNeM0EDbl4quvvL6m_ltjoAXXzkI3U="
            }
        ]
    }
"""
    jwks = middleware_settings()['JWKS'].signers

    assert len(jwks) > 0
    (kid, key), = jwks.items()

    def employee_credentials(self, scope=None):
        return dict(HTTP_AUTHORIZATION=('Bearer ' + self.jwt_token(scope)))

    def jwt_token(self, scope):
        now = int(time.time())
        scopes = [ scope ] if isinstance(scope, str) else []
        payload = {
            'iat': now,
            'exp': now + 300,
            'scopes': scopes
        }
        headers = {
            'kid': self.kid
        }

        return jwt.encode(payload, self.key.key, algorithm=self.key.alg, headers=headers).decode("utf-8")

