#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    test_blackbox.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2025
# date:    [2025-03-19 Wed]
# edit:    [2025-08-12 Tue]

"""External pytest checks by pytest on datawarrior_clustersort.py.

Checks in this file probe the application as a whole from the outside
(blackbox tests) marked by `blackbox`.  It is complemented by checks
defined in file `test_with_imports.py` labelled by `imported`."""

import filecmp
import os
import shutil
import subprocess

import pytest

PRG = "src/datawarrior_clustersort/datawarrior_clustersort.py"


@pytest.mark.blackbox
def test_script_exists() -> None:
    """Check for the script's presence."""
    assert os.path.isfile(PRG), f"script {PRG} was not found"


@pytest.fixture
def prepare_input_file() -> None:
    """Provide a suitable input file to test and process."""
    dummy_in = "input_file.txt"
    dummy_out = "input_file_sort.txt"

    content = r"""Structure [idcode]	Cluster No	Is Representative	record_number
elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2
elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3
eo`TND@MCNO@dnkg`HbpHrJJIQGQIRJGQQKKQbQXzBAajef`XHX@HID	2	No	4
fmg@p@@HkvZ|bfbbbbfTT\TqtEXwfjAbJJjZfcFEjA`@	4	No	5
fbma`@@`PKHihdhdXdierWhirt@QPAE@`@@	3	No	11
fnsQ`@CE@cJSK\l{]kLeNCdkTA@PQTrD@@	3	No	12
fmwAR@KNBeXICHhddeDeDhXedTjLejNYj`HfjjjjAPZ^P@	4	No	14
eg`TN@@LD`DBjecklbbVbbTTrbrbTjvbcegfWSUTBQETuUSPhTHq@@	4	No	21
fak@r@HHe[qPAFRPjIJKJJI[QHRgAjuZ@Hjjjja\Zahe@@	4	No	25"""
    with open(dummy_in, mode="w", encoding="utf-8") as new:
        new.write(content)
    yield dummy_in

    os.remove(dummy_in)
    os.remove(dummy_out)


@pytest.mark.blackbox
def test_default_sort2file(prepare_input_file) -> None:
    """Check the results of the normal sort to file.

    By this logic, label `1` is assigned to the cluster containing the
    most structures.  Any cluster label higher than `1` is about a
    subsequent cluster with equal or less structures."""
    subprocess.run(f"python {PRG} input_file.txt", shell=True, check=True)

    output_file = "input_file_sort.txt"
    with open(output_file, mode="r", encoding="utf-8") as source:
        content = source.read()

    expected_content = r"""Structure [idcode]	Cluster No	Is Representative	record_number
fmg@p@@HkvZ|bfbbbbfTT\TqtEXwfjAbJJjZfcFEjA`@	1	No	5
fmwAR@KNBeXICHhddeDeDhXedTjLejNYj`HfjjjjAPZ^P@	1	No	14
eg`TN@@LD`DBjecklbbVbbTTrbrbTjvbcegfWSUTBQETuUSPhTHq@@	1	No	21
fak@r@HHe[qPAFRPjIJKJJI[QHRgAjuZ@Hjjjja\Zahe@@	1	No	25
elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	2	No	3
fbma`@@`PKHihdhdXdierWhirt@QPAE@`@@	2	No	11
fnsQ`@CE@cJSK\l{]kLeNCdkTA@PQTrD@@	2	No	12
elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	3	No	2
eo`TND@MCNO@dnkg`HbpHrJJIQGQIRJGQQKKQbQXzBAajef`XHX@HID	3	No	4
"""

    assert content == expected_content


def test_default_sort2CLI(prepare_input_file, capfd) -> None:
    """Check the results of the normal sort to the CLI."""
    subprocess.run(f"python {PRG} input_file.txt", shell=True, check=True)
    out, err = capfd.readouterr()

    expected_content = r"""
DataWarrior's assignment of clusters:
cluster:        2 molecules:        2
cluster:        3 molecules:        3
cluster:        4 molecules:        4

clusters newly sorted and labeled:
cluster:        1 molecules:        4
cluster:        2 molecules:        3
cluster:        3 molecules:        2
"""

    # acount for different definitions of line ending
    #
    # In the report to the CLI of e.g., xfce4-terminal in Debian 13 and
    # by cmd.exe of Windows, the different advance to the next line can
    # be an issue.  Since this script is written in Debian, the check
    # `assert out == expected_content` set up with the multiline string
    # without reformat into a list otherwise would pass in Debian, but
    # fail in Windows.
    out = out.splitlines()
    expected_content = expected_content.splitlines()

    assert out == expected_content


def test_reverse_sort2file(prepare_input_file) -> None:
    """Check the results of the reversed sort.

    By this logic, label `1` is assigned to the cluster with the lowest
    number of structures.  Then, the higher the label (`2`, `3`, etc.),
    either the same, or a higher number of structures are in this
    particular cluster."""
    subprocess.run(f"python {PRG} input_file.txt -r", shell=True, check=True)

    output_file = "input_file_sort.txt"
    with open(output_file, mode="r", encoding="utf-8") as source:
        content = source.read()

    expected_content = r"""Structure [idcode]	Cluster No	Is Representative	record_number
elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	1	No	2
eo`TND@MCNO@dnkg`HbpHrJJIQGQIRJGQQKKQbQXzBAajef`XHX@HID	1	No	4
elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	2	No	3
fbma`@@`PKHihdhdXdierWhirt@QPAE@`@@	2	No	11
fnsQ`@CE@cJSK\l{]kLeNCdkTA@PQTrD@@	2	No	12
fmg@p@@HkvZ|bfbbbbfTT\TqtEXwfjAbJJjZfcFEjA`@	3	No	5
fmwAR@KNBeXICHhddeDeDhXedTjLejNYj`HfjjjjAPZ^P@	3	No	14
eg`TN@@LD`DBjecklbbVbbTTrbrbTjvbcegfWSUTBQETuUSPhTHq@@	3	No	21
fak@r@HHe[qPAFRPjIJKJJI[QHRgAjuZ@Hjjjja\Zahe@@	3	No	25
"""

    assert content == expected_content


def test_reverse_sort2CLI(prepare_input_file, capfd) -> None:
    """Check the results of the reverse sort to the CLI."""
    subprocess.run(f"python {PRG} -r input_file.txt", shell=True, check=True)
    out, err = capfd.readouterr()

    expected_content = r"""
DataWarrior's assignment of clusters:
cluster:        2 molecules:        2
cluster:        3 molecules:        3
cluster:        4 molecules:        4

clusters newly sorted and labeled:
cluster:        1 molecules:        2
cluster:        2 molecules:        3
cluster:        3 molecules:        4
"""

    # account for different line endings (cf. analogue check above)
    out = out.splitlines()
    expected_content = expected_content.splitlines()

    assert out == expected_content
