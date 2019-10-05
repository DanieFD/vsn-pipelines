#!/usr/bin/env python3

import argparse
import glob
import loompy as lp
import ntpath
import os
import pandas as pd
from pyscenic.genesig import GeneSignature
from pyscenic.aucell import aucell, derive_auc_threshold, enrichment, create_rankings
import sys
from typing import List
import utils
import warnings

################################################################################
################################################################################

parser_grn = argparse.ArgumentParser(description='Run AUCell on gene signatures saved as TSV in folder.')

parser_grn.add_argument('expression_mtx_fname',
                        type=argparse.FileType('r'),
                        help='The name of the file that contains the expression matrix for the single cell experiment.'
                        ' Two file formats are supported: csv (rows=cells x columns=genes) or loom (rows=genes x columns=cells).')
parser_grn.add_argument('signatures_fname',
                        help='The name of the folder containing the signatures as TSV files.')
parser_grn.add_argument('-o', '--output',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help='Output file/stream, i.e. a table of TF-target genes (CSV).')
parser_grn.add_argument('--auc-threshold',
                        type=float, default=0.05,
                        dest="auc_threshold",
                        help='The auc threshold used for calculating the AUC of a feature as fraction of ranked genes (default: {}).'.format(0.05))
parser_grn.add_argument('--percentile-threshold',
                        type=float,
                        dest="percentile_threshold",
                        help='This option override --auc-threshold!. The percentile to get the auc threshold used for calculating the AUC of a feature as fraction of ranked genes (default: {}).'.format(0.05))
parser_grn.add_argument('--gene-occurence-threshold',
                        type=int, default=5,
                        dest="gene_occurence_threshold",
                        help='The threshold used for filtering the genes bases on their occurence (default: {}).'.format(5))
parser_grn.add_argument('--num-workers',
                        type=int, default=1,
                        dest="num_workers",
                        help='The number of workers to use. (default: {}).'.format(1))
parser_grn.add_argument('--cell-id-attribute',
                        type=str, default='CellID',
                        dest="cell_id_attribute",
                        help='The name of the column attribute that specifies the identifiers of the cells in the loom file.')
parser_grn.add_argument('--gene-attribute',
                        type=str, default='Gene',
                        dest="gene_attribute",
                        help='The name of the row attribute that specifies the gene symbols in the loom file.')

args = parser_grn.parse_args()

# Do stuff

ex_matrix_df = utils.get_matrix(loom_file_path=args.expression_mtx_fname.name,
                                gene_attribute=args.gene_attribute,
                                cell_id_attribute=args.cell_id_attribute)
signatures = utils.read_signatures_from_tsv_dir(dpath=args.signatures_fname, noweights=False, weight_threshold=args.gene_occurence_threshold)
auc_threshold = args.auc_threshold

if args.percentile_threshold is not None:
    percentiles = derive_auc_threshold(ex_matrix_df)
    auc_threshold = percentiles[args.percentile_threshold]

aucs_mtx = aucell(ex_matrix_df, signatures, auc_threshold=auc_threshold, num_workers=args.num_workers)
aucs_mtx.to_csv(path_or_buf=args.output, index=True, sep='\t')
