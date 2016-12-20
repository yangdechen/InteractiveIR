#!/bin/bash

dtype=transcripts
outdir=retrieval
docdir=corpus/docs/$dtype

if [ ! -d "$outdir/index/" ]; then
    mkdir -p $outdir/index
fi
if [ ! -d "$outdir/bglm/" ]; then
    mkdir -p $outdir/bglm
fi
if [ ! -d "$outdir/doclen/" ]; then
    mkdir -p $outdir/doclen
fi

python src/create_inverted_index.py $docdir $outdir/index/${dtype}.index
python src/create_bg_lm.py $docdir $outdir/bglm/${dtype}.bglm
python src/calc_doc_len.py $docdir $outdir/doclen/${dtype}.doclen
