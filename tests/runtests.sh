#!/bin/bash

set -e

# Run pytest on the tests directory,
# which is assumed to be mounted somewhere in the docker image.

here=$(dirname $0)
testvenv=/tmp/testsvenv 

python3.8 /usr/local/share/virtualenv.pyz -p python3 $testvenv
$testvenv/bin/pip install pytest
$testvenv/bin/pytest $here "$@"
