#!/bin/bash -eux

pushd $(dirname $0)
GIT_DIR=$(git rev-parse --show-toplevel)
popd

pushd /tmp
export PATH=$PATH:$HOME/.local/bin
pip install --user $GIT_DIR/package/mlvtools-*.whl
pip install --user mlvtools[dev]
pytest -s $GIT_DIR/tests/large
popd
