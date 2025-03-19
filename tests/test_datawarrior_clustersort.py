#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    test_datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2025
# date:    [2025-03-19 Wed]
# edit:

"""pytest script of datawarrior_clustersort.py

Instead of a sequential import of functions of the parental script
of `datawarrior_clustersort.py`, this pytest based script provides
a couple of _black box tests_ to check only the results default and
reverse sort provide.
"""

import filecmp
import os
import shutil
import subprocess

import pytest

PRG = "datawarrior_clustersort.py"
INPUT_FILE = "100Random_Molecules.txt"
OUTPUT_FILE = "100Random_Molecules_sort.txt"
REFERENCE_SORT = "tests/100Random_Molecules_sort_ref.txt"
REFERENCE_REVERSE_SORT = "tests/100Random_Molecules_rev_sort_ref.txt"


def test_script_exists():
    """check for the script's presence"""
    assert os.path.isfile(PRG), f"script {PRG} was not found"


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
