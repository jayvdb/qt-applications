import os
import pathlib
import subprocess
import sys
import sysconfig
import tempfile

import pytest

import build

fspath = getattr(os, "fspath", str)

os.environ.setdefault("QT_VERSION", "5.15.1")


def create_configuration(env=os.environ):
    build_base_path = pathlib.Path(tempfile.mkdtemp())
    build_base_path.mkdir(parents=True, exist_ok=True)
    # Prevent .resolve() later causing problems
    build_base_path = build_base_path.resolve()

    package_path = tempfile.mkdtemp(
        dir=fspath(build_base_path),
    )
    build_path = pathlib.Path(
        tempfile.mkdtemp(
            prefix="qt5_applications-",
            dir=fspath(build_base_path),
        )
    )

    configuration = build.Configuration.build(
        environment=env,
        build_path=build_path,
        package_path=package_path,
    )
    return configuration


def test_configuration_create():
    configuration = create_configuration()
    assert configuration.download_path
    assert not configuration.download_path.exists()

    configuration.create_directories()
    assert configuration.download_path.exists()
    assert configuration.download_path == configuration.download_path.resolve()


def test_install_qt():
    configuration = create_configuration()
    build.install_qt(configuration)

    qt_paths = build.QtPaths.build(
        base=configuration.qt_path,
        version=configuration.qt_version,
        compiler=configuration.qt_compiler,
        platform_=configuration.platform,
    )
    assert qt_paths.bin.exists()
    assert os.listdir(qt_paths.bin)
    assert qt_paths.compiler.exists()
    assert qt_paths.qmake.exists()

    assert qt_paths.applications

    assert any(
        str(exe.original_path).endswith("Designer.app")
        or str(exe.original_path).endswith("qtdesigner")
        for exe in qt_paths.applications
    )

    for exe in qt_paths.applications:
        print(exe.original_path)
    assert any(
        str(exe.original_path).endswith("qmlscene") for exe in qt_paths.applications
    )
