import jwt
import time

from authorization_django.config import settings as middleware_settings


class JWTMixin(object):

    # VERY NEW STYLE AUTH. JWKS public/private keys are defined in settings
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

