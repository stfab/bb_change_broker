"""This module contains functions for executing command line commands."""

import subprocess
import shlex


def check_output(command) -> str:
    """Port of commands.getoutput in python2.

    :param command (str): The command to execute.
    :return (str): The output of the command.
    """
    command = shlex.split(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout
