
Structure for the jenkins scripts:
.jenkins/test   : scripts for ci testing
.jenkins/import : scripts for ci importing
.jenkins        : common scripts, used by test, import and deploy (e.g. docker-wait.sh, docker-migrate.sh)

This structure prevents that web/ contains CI related scripts.


NOOT:
In the main Dockerfile, the following are copied for backwards compatability reasons.
 * .jenkins/import copied into /.jenkins-import
 * .jenkins/docker-migrate.sh copied into /app/docker-migrate.sh
 In future CI can be switched over to point to /app/.jenkins/import and /app/.jenkins/docker-migrate.sh
