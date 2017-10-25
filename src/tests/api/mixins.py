import jwt
import os
import time
from monumenten import settings


class JWTMixin(object):
    secret = settings.DATAPUNT_AUTHZ['JWT_SECRET_KEY']
    algorithm = settings.DATAPUNT_AUTHZ['JWT_ALGORITHM']

    assert(secret is not None)
    assert(algorithm is not None)

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

        return jwt.encode(payload, self.secret, algorithm=self.algorithm).decode("utf-8")

