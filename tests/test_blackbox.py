#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    test_blackbox.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2025
# date:    [2025-03-19 Wed]
# edit:    [2025-08-01 Fri]

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
INPUT_FILE = "100Random_Molecules.txt"
OUTPUT_FILE = "100Random_Molecules_sort.txt"
REFERENCE_SORT = "tests/100Random_Molecules_sort_ref.txt"
REFERENCE_REVERSE_SORT = "tests/100Random_Molecules_rev_sort_ref.txt"


def test_script_exists() -> None:
    """Check for the script's presence."""
    assert os.path.isfile(PRG), f"script {PRG} was not found"


@pytest.mark.blackbox
def test_get_test_data() -> None:
    """Check copy/paste of test input data to the script."""
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

    assert os.path.isfile(INPUT_FILE)


@pytest.mark.blackbox
def test_default_sort() -> None:
    """Check the results of the normal sort.

    By this logic, label `1` is assigned to the cluster containing the
    most structures.  Any cluster label higher than `1` is about a subsequent
    cluster with equal or less structures."""
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


@pytest.mark.blackbox
def test_reverse_sort() -> None:
    """Check the results of the reversed sort.

    By this logic, label `1` is for the cluster with the lowest number of
    structures.  The higher the label (`2`, `3`, etc.), either the same, or
    a higher number of structures are in this particular cluster."""
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


@pytest.mark.blackbox
def test_space_cleaning() -> None:
    """Check the removal of the local copy of the input file."""
    if os.path.exists(INPUT_FILE):
        try:
            os.remove(INPUT_FILE)
        except OSError as e:
            print(f"failed to remove old '{INPUT_FILE}' after the test; {e}")
