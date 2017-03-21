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

    def employee_credentials(self):
        return dict(HTTP_AUTHORIZATION=('Bearer ' + self.jwt_token(self.LEVEL_EMPLOYEE)))

    def jwt_token(self, level):
        now = int(time.time())
        payload = {
            'iat': now,
            'exp': now + 300,
            'authz': level
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm).decode("utf-8")

