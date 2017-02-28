
Structure for the jenkins scripts:
.jenkins/test   : scripts for ci testing
.jenkins/import : scripts for ci importing
.jenkins        : common scripts, used by test, import and deploy (e.g. docker-wait.sh, docker-migrate.sh)

This structure prevents that web/ contains CI related scripts.


NOOT:
In the main Dockerfile, the following are copied for backwards compatability reasons.
 * .jenkins/import is copied into .jenkins-improt
 * .jenkins/docker-migrate.sh into web/docker-migrate.sh
 In future CI should point to .jenkins-import and .jenkins/docker-migrate.sh
