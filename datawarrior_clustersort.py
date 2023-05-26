#!/usr/bin/env python3

# name:    datawarrior_clustersort.py
# author:  nbehrnd@yahoo.com
# license: GPL v2, 2022.
# date:    <2022-04-22 Fri>
# edit:    <2023-05-26 Fri>
"""Provide a sort on DataWarrior clusters by popularity of the cluster.

DataWarrior can recognize structure similarity in a set of molecules.  The
more similar molecules are then grouped in clusters labeled by integers, a
result DataWarrior can store as .dwar, or export as .sdf file.  However so
far, the program however does not provide to report the molecules in a sort
based on the popularity of their corresponding clusters.
For context and motivation, see DataWarrior's discussion board after mcmc's
post 'Assign cluster name based on cluster size' by April 7, 2022
(https://openmolecules.org/forum/index.php?t=msg&th=586&goto=1587&#msg_1587).

The script uses only functions of Python's standard library."""

import argparse
import csv
import os
import re
import sys


def get_args():
    """Get the arguments from the command line."""
    parser = argparse.ArgumentParser(
        description="""Sort DataWarrior's cluster list based on the number of
        molecules per cluster.  The triage by frequency reports the cluster most
        populous first.  After processing input file `example.txt`, the newly
        written record `example_sort.txt` can be accessed directly by
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

    return parser.parse_args()


def file_reader(input_file=""):
    """access the data as provided by DataWarrior's .txt file

    Assuming DW's file is less than half of the (remaining) available
    RAM of the computer used, the whole content of input file is read."""
    raw_table = input_file.read().splitlines()

    head_line = raw_table[0]
    table_body = raw_table[1:]

    return head_line, table_body


#def access_raw_data(input_file=""):
#    """Access DW's exported cluster list."""
#    raw_data = []

#    try:
#        with open(input_file, encoding="utf-8", mode="r") as source:
#            raw_data = source.readlines()
#    except OSError:
#        print(f"Input file {input_file} was not accessible.  Exit.")
#        sys.exit()

#    return raw_data


#def read_header(raw_data=[]):
#    """Extract the headline of DW's table."""
#    table_header = ""
#    table_header = str(raw_data[0]).strip()

#    return table_header


def identify_cluster_column(table_header):
    """Identify the column with DW's assigned cluster labels.

    The first occurrence of 'Cluster No' identified by a regular expression is
    assumed to indicate the column of interest.  For this, the split has to be
    an explicit separator (tabulator)."""
    column_heads = table_header.split("\t")
    list_of_matches = [
        i for i, item in enumerate(column_heads) if re.search("Cluster No", item)
    ]
    column_number = int(list_of_matches[0])

    return column_number


def read_dw_list(raw_data, special_position):
    """Establish a frequency list based on DW's exported cluster list."""
    dw_cluster_labels = []

    source = csv.reader(raw_data, delimiter="\t")
    for row in source:
        cluster_label_on_molecule = row[special_position]
        dw_cluster_labels.append(cluster_label_on_molecule)
    del dw_cluster_labels[0]  # do not consider the table header

    # build and report a dictionary:
    count = {}
    for label in dw_cluster_labels:
        count.setdefault(label, 0)
        count[label] = count[label] + 1

    for key, value in count.items():
        print("cluster: ", key, "\t molecules: ", value)

    return count


def entry_sorter(count={}, reversed_order=False):
    """Sort the popularity of the clusters either way."""
    if reversed_order:
        sorted_list = sorted(count, key=count.__getitem__, reverse=True)
    else:
        sorted_list = sorted(count, key=count.__getitem__, reverse=False)
    return sorted_list


def scrutin_by_label(raw_data, population_list, special_position):
    """Update the molecules' labels according to the cluster popularity."""
    reporter_list = []
    new_cluster_label = 1

    for entry in population_list:
        source = csv.reader(raw_data, delimiter="\t")

        for row in source:
            if row[special_position] == entry:
                cell_entries = row
                del cell_entries[special_position]
                cell_entries.insert(special_position, str(new_cluster_label))
                retain = "\t".join(cell_entries)
                reporter_list.append(retain)

        new_cluster_label += 1

    return reporter_list


def permanent_report(input_file="", topline="", listing=[]):
    """Provide a permanent record DW may access."""
    stem_input_file = os.path.splitext(input_file)[0]
    report_file = "".join([stem_input_file, str("_sort.txt")])

    try:
        with open(report_file, encoding="utf-8", mode="w") as newfile:
            newfile.write("".join([topline, "\n"]))
            for entry in listing:
                newfile.write("".join([entry, "\n"]))
    except OSError:
        print(f"Error to export record into {report_file}.  Exit.")
        sys.exit()

    return report_file


def main():
    """Join the functions."""
    args = get_args()
    print(args)

    head_line, table_body = file_reader(args.file)

    print("echo")
    print(f"head_line: {head_line}")
    print(f"3 lines: {table_body[:3]}")
    print(f"There are {len(table_body)} entries.")
#    input_file = args.file
#    sort_option = args.reverse  # .true. == start by the least popular cluster

#    # work on old data:
#    print("Preview, sort by DataWarrior's cluster labels:")
#    raw_data = access_raw_data(input_file)
#    headline = read_header(raw_data)
    special_position = identify_cluster_column(head_line)
    print(f"The cluster label is in column {special_position}.")

#    popularity = read_dw_list(raw_data, special_position)

#    sorted_population_list = entry_sorter(popularity, sort_option)
#    report_list = scrutin_by_label(raw_data, sorted_population_list,
#                                   special_position)
#    report_file = permanent_report(input_file, headline, report_list)

#    # work on new data:
#    print("\nclusters newly sorted and labeled:")
#    raw_data = access_raw_data(report_file)
#    headline = read_header(raw_data)
#    special_position = identify_cluster_column(headline)
#    popularity = read_dw_list(raw_data, special_position)

if __name__ == "__main__":
    main()
