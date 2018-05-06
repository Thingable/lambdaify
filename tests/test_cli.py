import pytest
import os
import subprocess
from click.testing import CliRunner
from lambdaify_my_py import cli


@pytest.fixture
def runner():
    return CliRunner()

def test_startify(runner):
    result = runner.invoke(cli.main, ['startify', '-p', 'test_project', '-v', './test_project/'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == ''
    subprocess.call('rm -r test_project', shell=True)

def test_virtualify(runner):
    result = runner.invoke(cli.main, ['virtualify'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == 'Virtual environment created at ./'

def test_lambdaify(runner):
    result = runner.invoke(cli.main, ['lambdaify'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == 'lambdaify'

def test_zipify(runner):
    result = runner.invoke(cli.main, ['zipify'])
    assert not result.exception
    assert result.exit_code == 0
    assert result.output.strip() == 'zipify'

