#!/bin/bash -eux

pushd $(dirname $0)
GIT_DIR=$(git rev-parse --show-toplevel)
popd

pushd /tmp
export PATH=$PATH:$HOME/.local/bin
pip install --user $GIT_DIR/package/ml_versioning_tools-*.whl pytest
pytest $GIT_DIR/tests/large
popd
