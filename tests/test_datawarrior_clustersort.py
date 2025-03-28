#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    test_datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2025
# date:    [2025-03-19 Wed]
# edit:    [2025-03-27 Thu]

"""pytest script of datawarrior_clustersort.py

Instead of a sequential import of functions of the parental script
of `datawarrior_clustersort.py`, this pytest based script provides
a couple of _black box tests_ to check only the results default and
reverse sort provide.
"""

import filecmp
import io
import os
import shutil
import subprocess

import pytest

from datawarrior_clustersort import file_reader


PRG = "datawarrior_clustersort/__init__.py"
INPUT_FILE = "100Random_Molecules.txt"
OUTPUT_FILE = "100Random_Molecules_sort.txt"
REFERENCE_SORT = "tests/100Random_Molecules_sort_ref.txt"
REFERENCE_REVERSE_SORT = "tests/100Random_Molecules_rev_sort_ref.txt"


def test_script_exists():
    """check for the script's presence"""
    assert os.path.isfile(PRG), f"script {PRG} was not found"


# section of black-box tests (the inner working doesn't matter):


def test_get_test_data():
    """get a copy of the test's input data"""
    source = os.path.join("tests", INPUT_FILE)
    target = os.path.join(os.getcwd(), INPUT_FILE)

    if os.path.exists(INPUT_FILE):
        try:
            os.remove(INPUT_FILE)
        except OSError as e:
            print(f"failed to remove old '{INPUT_FILE}' prior to the test; {e}")

    try:
        shutil.copy(source, target)
    except OSError as e:
        print(f"failed to copy '{INPUT_FILE}' for the test; {e}")


def test_default_sort():
    """check the results of the normal sort"""
    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
        except OSError as e:
            print(f"failed to remove '{OUTPUT_FILE}' prior to the test; {e}")

    subprocess.run(f"python {PRG} {INPUT_FILE}", shell=True, check=True)
    assert os.path.exists(OUTPUT_FILE), f"file '{OUTPUT_FILE}' was not written"
    assert filecmp.cmp(
        OUTPUT_FILE, REFERENCE_SORT, shallow=False
    ), "mismatch of expected/reference content"

    try:
        os.remove(OUTPUT_FILE)
    except OSError as e:
        print(f"removal of '{OUTPUT_FILE}' after the test failed; {e}")


def test_reverse_sort():
    """check the results of the normal sort"""
    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
        except OSError as e:
            print(f"failed to remove '{OUTPUT_FILE}' prior to the test; {e}")

    subprocess.run(f"python {PRG} {INPUT_FILE} -r", shell=True, check=True)
    assert os.path.exists(OUTPUT_FILE), f"file '{OUTPUT_FILE}' was not written"
    assert filecmp.cmp(
        OUTPUT_FILE, REFERENCE_REVERSE_SORT, shallow=False
    ), "mismatch of expected/reference content"

    try:
        os.remove(OUTPUT_FILE)
    except OSError as e:
        print(f"removal of '{OUTPUT_FILE}' after the test failed; {e}")


def test_space_cleaning():
    """remove copy of the input file"""
    if os.path.exists(INPUT_FILE):
        try:
            os.remove(INPUT_FILE)
        except OSError as e:
            print(f"failed to remove old '{INPUT_FILE}' after the test; {e}")


# section of tests to check the inner of the python script:


probe_data = r"""Structure [idcode]	Cluster No	Is Representative	record_number
edR\FD@KFncOLbji`HbHHrJIJYKJYSQRJiSIQITLRJ@pp@@DtuKMMP@@PARBj@	1	No	1
elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2
elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3
eo`TND@MCNO@dnkg`HbpHrJJIQGQIRJGQQKKQbQXzBAajef`XHX@HID	2	No	4
fmg@p@@HkvZ|bfbbbbfTT\TqtEXwfjAbJJjZfcFEjA`@	4	No	5
fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6
"""


def test_file_reader():
    mock_file = io.StringIO(probe_data)
    head_line, table_body, old_cluster_label = file_reader(mock_file)
    assert (
        head_line == "Structure [idcode]\tCluster No\tIs Representative\trecord_number"
    )
    assert table_body == [
        r"edR\FD@KFncOLbji`HbHHrJIJYKJYSQRJiSIQITLRJ@pp@@DtuKMMP@@PARBj@	1	No	1",
        r"elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2",
        r"elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3",
        r"eo`TND@MCNO@dnkg`HbpHrJJIQGQIRJGQQKKQbQXzBAajef`XHX@HID	2	No	4",
        r"fmg@p@@HkvZ|bfbbbbfTT\TqtEXwfjAbJJjZfcFEjA`@	4	No	5",
        r"fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6",
    ]
    # implicitly test function `identify_cluster_column`:
    assert old_cluster_label == 1
