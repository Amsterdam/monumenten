import time

from jwcrypto.jwt import JWT
from authorization_django.jwks import get_keyset


class JWTMixin(object):

    jwks = get_keyset()

    assert len(jwks['keys']) > 0
    key = next(iter(jwks['keys']))
    kid = key.key_id

    def employee_credentials(self, scope=None):
        return dict(HTTP_AUTHORIZATION=('Bearer ' + self.jwt_token(scope)))

    def jwt_token(self, scope):
        now = int(time.time())
        scopes = [scope] if isinstance(scope, str) else []
        payload = {
            'iat': now,
            'exp': now + 300,
            'scopes': scopes
        }
        headers = {
            'alg': 'ES256',  # algorithm of the test key
            'kid': self.kid
        }

        token = JWT(header=headers, claims=payload)
        token.make_signed_token(self.key)
        return token.serialize()
