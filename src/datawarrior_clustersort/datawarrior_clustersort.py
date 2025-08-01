#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2022, 2023
# date:    [2022-04-22 Fri]
# edit:    [2025-08-01 Fri]
"""Provide a sort on DataWarrior clusters by popularity of the cluster.

DataWarrior can recognize structure similarity in a set of molecules.  The
more similar molecules are then grouped in clusters labeled by integers, a
result DataWarrior can store as .dwar, or export as .sdf file.  However so
far, the program however does not provide to report the molecules in a sort
based on the popularity of their corresponding clusters.
For context and motivation, see DataWarrior's discussion board after mcmc's
post 'Assign cluster name based on cluster size' by April 7, 2022
(https://openmolecules.org/forum/index.php?t=msg&th=586&goto=1587&#msg_1587).

The script uses only functions of the standard library, for instance of
Python version 3.11.2."""

import argparse
import csv
import logging
import os
import re
import sys
from typing import List, Tuple, Dict, TextIO

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("error.log"), logging.StreamHandler(sys.stderr)],
)


def get_args(arg_list) -> argparse.Namespace:
    """collect the arguments from the command line"""
    parser = argparse.ArgumentParser(
        description="""Sort DataWarrior's cluster list based on the number of
        molecules per cluster.  The triage by frequency reports the cluster
        most populous first.  After processing input file `example.txt`, the
        newly written record `example_sort.txt` can be accessed directly by
        DataWarrior by the short cut `Ctrl + O`.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        metavar="file",
        type=argparse.FileType("rt"),
        help="DataWarrior's cluster list which was exported as .txt file",
    )

    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="""override the default sort sequence; i.e. assign the least
        populous cluster the lowest label""",
    )

    args = parser.parse_args(arg_list)
    return args


def file_reader(input_file: TextIO) -> Tuple[str, List[str], int]:
    """
    access the data as provided by DataWarrior's .txt file

    :param input_file: DataWarrior's exported .txt list of clusters
    :type input_file: TextIO
    :return: table header, table body, and column of cluster labels
    :rtype: Tuple[str, List[str], int]
    """
    try:
        raw_table = input_file.read().splitlines()
        raw_table = [i.strip() for i in raw_table if len(i) > 1]
        if len(raw_table) < 3:
            logging.error(
                "Only %s non-empty line(s) instead of 3 in the input file.",
                len(raw_table),
            )
            sys.exit(1)

        headline = raw_table[0]
        table_body = raw_table[1:]
        old_cluster_label = identify_cluster_column(headline)

        return headline, table_body, old_cluster_label
    except OSError as e:
        logging.error("Error while reading %s: %s", input_file.name, e)
        sys.exit(1)


def identify_cluster_column(headline: str) -> int:
    """
    identify the column with DW's assigned cluster labels

    The first occurrence of 'Cluster No' identified by a regular
    expression is assumed to indicate the column of interest.

    :return: index of the column of cluster labels
    :rtype: int
    """
    column_heads = headline.split("\t")
    list_of_matches = [
        i for i, item in enumerate(column_heads) if re.search("Cluster No", item)
    ]
    old_cluster_label = int(list_of_matches[0])

    return old_cluster_label


def read_dw_list(table_body: List[str], old_cluster_label: int) -> Dict[str, int]:
    """
    query current cluster labels' popularity

    Query currently assigned cluster labels DataWarrior assigned,
    and how many molecules each represents.

    :param table_body: the data table except its headline
    :type table_body: List[str]
    :param old_cluster_label: data table's column of cluster labels
    :type old_cluster_label: int
    :return: dictionary of cluster labels (key) and popularity (value)
    :rtype: Dict[str, int]
    """
    dw_cluster_labels = []

    source = csv.reader(table_body, delimiter="\t")
    for row in source:
        cluster_label_on_molecule = row[old_cluster_label]
        dw_cluster_labels.append(cluster_label_on_molecule)

    # build and report a dictionary:
    count: Dict[str, int] = {}
    for label in dw_cluster_labels:
        count.setdefault(label, 0)
        count[label] = count[label] + 1

    #    print("\nDataWarrior's assignment of clusters:")
    for key, value in count.items():
        print(f"cluster: {key:>8} molecules: {value:>8}")

    return count


def label_sorter(count: Dict[str, int], reversed_order: bool) -> Dict[str, int]:
    """
    relate DW assigned cluster labels with the new ones to be used

    First sort the old cluster labels by number of molecules per
    cluster (i.e., by popularity).  Then assign how old labels by
    DW are going to be updated

    :param count: dictionary (k = cluster label, v = times it is used)
    :type count: Dict[str, int]
    :param reversed_order: sort either by as/descending popularity
    :type reversed_order: bool
    :return: sorted cluster dictionary (k = old DW, v = new label)
    :rtype: Dict[str, int]
    """
    if reversed_order:
        sorted_list = sorted(count, key=count.__getitem__, reverse=False)
    else:
        sorted_list = sorted(count, key=count.__getitem__, reverse=True)

    # create the dictionary by dictionary comprehension, `+ 1`accounts
    # for Python's zero-based indexing
    label_dictionary = {
        old_label: new_label + 1 for new_label, old_label in enumerate(sorted_list)
    }

    return label_dictionary


def update_cluster_labels(
    table_body: List[str], old_cluster_label: int, label_dictionary: Dict[str, int]
) -> List[str]:
    """
    update the molecules' labels by cluster popularity

    With the dictionary which relates original cluster labels
    (assigned by DataWarrior) and the new ones (based on cluster
    popularity and sort), each molecule's record is updated.

    :param table_body: data table except headline
    :type table_body: List[str]
    :param old_cluster_label: DataWarrior cluster label (prior to sort)
    :type old_cluster_label: int
    :param label_dictionary: dictionary (k = old DW, v = new label)
    :type label_dictionary: Dict[str, int]
    :return: body of table (no headline) with updated cluster labels
    :rtype: List[str]
    """
    reporter_list = []

    for record in table_body:
        record_data = []
        record_data = record.split("\t")

        old_label = record_data[old_cluster_label]
        new_label = label_dictionary.get(old_label)

        # update of the cluster label
        record_data[old_cluster_label] = str(new_label)

        new_record = "\t".join(record_data)
        reporter_list.append(new_record)

    reporter_list = sorted(reporter_list, key=sort_by_cluster_label)

    return reporter_list


def sort_by_cluster_label(s: str) -> int:
    """return a key to sort records in `table_body` by cluster label"""
    return int(s.split("\t")[1])


def permanent_report(input_file: str, headline: str, listing: List[str]) -> str:
    """
    provide a permanent record DW may access

    :param input_file: file name of the input file
    :type input_file: str
    :param headline: headline of the data table
    :type headline: str
    :param listing: data table except headline
    :type listing: List[str]
    :return: complete data table (headline and table body)
    :rtype: str
    """ """Provide a permanent record DW may access."""
    stem_input_file = os.path.splitext(input_file)[0]
    report_file = "".join([stem_input_file, str("_sort.txt")])

    try:
        with open(report_file, encoding="utf-8", mode="w") as newfile:
            newfile.write("".join([headline, "\n"]))
            for entry in listing:
                newfile.write("".join([entry, "\n"]))
    except OSError as e:
        logging.error("Error to export record into %s (%s).  Exit.", report_file, e)
        sys.exit()

    return report_file


def main(arg_list=None) -> None:
    """join the functions"""
    args = get_args(arg_list)
    headline, table_body, old_cluster_label = file_reader(args.file)

    print("\nDataWarrior's assignment of clusters:")
    popularity = read_dw_list(table_body, old_cluster_label)

    # reorganize the data:
    label_dictionary = label_sorter(popularity, args.reverse)
    report_list = update_cluster_labels(table_body, old_cluster_label, label_dictionary)
    permanent_report(args.file.name, headline, report_list)

    # read the new data:
    print("\nclusters newly sorted and labeled:")
    read_dw_list(report_list, old_cluster_label)


if __name__ == "__main__":  # pragma: no cover
    main()
