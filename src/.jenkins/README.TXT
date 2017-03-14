
Structure for the jenkins scripts:
.jenkins/test   : scripts for ci testing
.jenkins/import : scripts for ci importing
.jenkins        : common scripts, used by test and import (e.g. docker-wait.sh)

This structure prevents that web/ contains CI related scripts.


NOOT:
For backwards compatability reasons:
 * the directory .jenkins-import is created:
this directory is currently actually  being called by CI. In future CI should point to the .jenkins/import/import.sh.
 * web/docker-migrate.sh
 this is being called by CI. In future CI should point to .jenkins/docker-migrate.sh
