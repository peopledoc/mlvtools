# Release Procedure

1. Update [`CHANGELOG`](CHANGELOG)
2. Set the new version in [`setup.cfg`](setup.cfg)
3. Add a commit with this changes, create a PR on GitHub, and merge
4. Create a source package and a wheel:
    ```shell
    rm -rf dist
    python setup.py sdist bdist_wheel
    ```
5. Push the source package and the wheel to pypi:
    ```shell
    twine upload --repository=pypi dist/*
    ```
6. Update `CHANGELOG` and `setup.cfg` again for the new development version
