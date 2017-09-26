import jwt
import os
import time
from monumenten import settings


class JWTMixin(object):
    #LEVEL_DEFAULT = 0b0
    LEVEL_EMPLOYEE = 0b1
    #LEVEL_EMPLOYEE_PLUS = 0b11

    secret = settings.DATAPUNT_AUTHZ['JWT_SECRET_KEY']
    algorithm = settings.DATAPUNT_AUTHZ['JWT_ALGORITHM']

    assert(secret is not None)
    assert(algorithm is not None)

    def employee_credentials(self, scope=None):
        return dict(HTTP_AUTHORIZATION=('Bearer ' + self.jwt_token(scope if scope else self.LEVEL_EMPLOYEE)))

    def jwt_token(self, level_or_scope):
        now = int(time.time())
        if isinstance(level_or_scope, str):
            payload = {
                'iat': now,
                'exp': now + 300,
                'scopes': [ level_or_scope ]
            }
        else:
            payload = {
                'iat': now,
                'exp': now + 300,
                'authz': level_or_scope

            }

        return jwt.encode(payload, self.secret, algorithm=self.algorithm).decode("utf-8")

