#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    test_datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2025
# date:    [2025-03-19 Wed]
# edit:    [2025-04-01 Tue]

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

from datawarrior_clustersort import (
    file_reader,
    identify_cluster_column,
    read_dw_list,
    label_sorter,
    update_cluster_labels,
)

PRG = "datawarrior_clustersort/__init__.py"
INPUT_FILE = "100Random_Molecules.txt"
OUTPUT_FILE = "100Random_Molecules_sort.txt"
REFERENCE_SORT = "tests/100Random_Molecules_sort_ref.txt"
REFERENCE_REVERSE_SORT = "tests/100Random_Molecules_rev_sort_ref.txt"


def test_script_exists():
    """check for the script's presence"""
    assert os.path.isfile(PRG), f"script {PRG} was not found"


# section of black-box tests (the inner working doesn't matter):


@pytest.mark.blackbox
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


@pytest.mark.blackbox
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


@pytest.mark.blackbox
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


@pytest.mark.blackbox
def test_space_cleaning():
    """remove copy of the input file"""
    if os.path.exists(INPUT_FILE):
        try:
            os.remove(INPUT_FILE)
        except OSError as e:
            print(f"failed to remove old '{INPUT_FILE}' after the test; {e}")


# section of tests to check the inner of the python script:


@pytest.mark.imported
def test_file_reader():
    probe_data = r"""Structure [idcode]	Cluster No	Is Representative	record_number
edR\FD@KFncOLbji`HbHHrJIJYKJYSQRJiSIQITLRJ@pp@@DtuKMMP@@PARBj@	1	No	1
elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2
elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3
"""
    mock_file = io.StringIO(probe_data)
    head_line, table_body, old_cluster_label = file_reader(mock_file)
    assert (
        head_line == "Structure [idcode]\tCluster No\tIs Representative\trecord_number"
    )
    assert table_body == [
        r"edR\FD@KFncOLbji`HbHHrJIJYKJYSQRJiSIQITLRJ@pp@@DtuKMMP@@PARBj@	1	No	1",
        r"elRRF@@DLCH`FMLfilbbRbrTVtTTRbtqbRRJzAQZijfhHbbZBA@@@@	2	No	2",
        r"elZPE@@@DFACBeghT\bfbbfabRRvfbRbVaTdt\BfvZBHBBJf@Hii`@@@	3	No	3",
    ]
    # implicitly test function `identify_cluster_column`:
    assert old_cluster_label == 1


@pytest.mark.imported
def test_identify_cluster_column():
    """identification of the cluster column"""
    input_string = "Structure [idcode]	Cluster No	Is Representative	record_number"
    expected_column = 1
    test_column = identify_cluster_column(input_string)
    assert test_column == expected_column, "wrong column index"


@pytest.mark.imported
def test_read_dw_list():
    # some records of DW cluster 1, 5, and 8 of `100Random_Molecules.txt`
    mock_table_body = [
        r"fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6",
        r"ek`PLH@Fam`IAIfYf[fUUUWcQQpKjhz@H@@@jBJh@@@@	5	No	7",
        r"fmgq`@BRBAG\bfdrTRfabRaTRRT\vjjjhHHjjGFIqU`@	1	No	10",
        r"fco@H@@HXKsU{rJZJJZEIIJYJYZRUYu^mAD@AT@QS@@@@	5	No	17",
        r"ffmhP@DLxKpJJKdTRbfLrbbRtsUiZif```ACR@	8	Yes	18",
        r"e`\TJ@@BF`DDailbfbTRRRRRbabfQVWDfedUVqsP@@PHU@LAT@@PNP	5	No	19",
        r"ed\XK@@H`DFC@jfnimgoh\bfbbrRbaaTTTltrfPdegcPP@QCULsMMHPIP@	1	Yes	28",
        r"fde``@E@PdrrsmkbTYpXmTsUUKMBT@@	1	No	40",
        r"fasPR@B\XJS`XfQQQIQHqQKQYZIV}iZfhF@@@@HPx`	8	No	67",
    ]
    old_cluster_label = 1
    expected_dictionary = {
        "1": 4,
        "5": 3,
        "8": 2,
    }
    test_dictionary = read_dw_list(mock_table_body, old_cluster_label)
    assert test_dictionary == expected_dictionary


@pytest.mark.imported
def test_label_sorter_default_sort():
    mock_dictionary = {"1": 4, "5": 3, "8": 2}
    reversed_order = False
    expected_dictionary = {"1": 1, "5": 2, "8": 3}
    test_dictionary = label_sorter(mock_dictionary, reversed_order)
    assert test_dictionary == expected_dictionary


@pytest.mark.imported
def test_label_sorter_reverse_sort():
    mock_dictionary = {"1": 4, "5": 3, "8": 2}
    reversed_order = True
    expected_dictionary = {"1": 3, "5": 2, "8": 1}
    test_dictionary = label_sorter(mock_dictionary, reversed_order)
    assert test_dictionary == expected_dictionary


@pytest.mark.imported
def test_update_cluster_labels():
    # some of DW clusters 1, 5, and 8
    mock_table_body = [
        r"fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6",
        r"ek`PLH@Fam`IAIfYf[fUUUWcQQpKjhz@H@@@jBJh@@@@	5	No	7",
        r"fmgq`@BRBAG\bfdrTRfabRaTRRT\vjjjhHHjjGFIqU`@	1	No	10",
        r"fco@H@@HXKsU{rJZJJZEIIJYJYZRUYu^mAD@AT@QS@@@@	5	No	17",
        r"ffmhP@DLxKpJJKdTRbfLrbbRtsUiZif```ACR@	8	Yes	18",
        r"e`\TJ@@BF`DDailbfbTRRRRRbabfQVWDfedUVqsP@@PHU@LAT@@PNP	5	No	19",
        r"ed\XK@@H`DFC@jfnimgoh\bfbbrRbaaTTTltrfPdegcPP@QCULsMMHPIP@	1	Yes	28",
        r"fde``@E@PdrrsmkbTYpXmTsUUKMBT@@	1	No	40",
        r"fasPR@B\XJS`XfQQQIQHqQKQYZIV}iZfhF@@@@HPx`	8	No	67",
    ]
    old_cluster_label = 1
    label_dictionary = {"1": 1, "5": 2, "8": 3}
    expected_reporter_list = [
        r"fko`H@D@yHsQ{OdTRbbbtRLLRTvRfoEjuTuUTAAUSPSBiAKL@@	1	No	6",
        r"fmgq`@BRBAG\bfdrTRfabRaTRRT\vjjjhHHjjGFIqU`@	1	No	10",
        r"ed\XK@@H`DFC@jfnimgoh\bfbbrRbaaTTTltrfPdegcPP@QCULsMMHPIP@	1	Yes	28",
        r"fde``@E@PdrrsmkbTYpXmTsUUKMBT@@	1	No	40",
        r"ek`PLH@Fam`IAIfYf[fUUUWcQQpKjhz@H@@@jBJh@@@@	2	No	7",
        r"fco@H@@HXKsU{rJZJJZEIIJYJYZRUYu^mAD@AT@QS@@@@	2	No	17",
        r"e`\TJ@@BF`DDailbfbTRRRRRbabfQVWDfedUVqsP@@PHU@LAT@@PNP	2	No	19",
        r"ffmhP@DLxKpJJKdTRbfLrbbRtsUiZif```ACR@	3	Yes	18",
        r"fasPR@B\XJS`XfQQQIQHqQKQYZIV}iZfhF@@@@HPx`	3	No	67",
    ]
    test_reporter_list = update_cluster_labels(
        mock_table_body, old_cluster_label, label_dictionary
    )
    assert test_reporter_list == expected_reporter_list
