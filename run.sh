#!/bin/bash

index=retrieval/index/transcripts.char_bichar.index
doclen=retrieval/doclen/transcripts.doclen
bglm=retrieval/bglm/transcripts.char_bichar.lm
key_dir=keyterm/transcripts/textrank_core_window2
doc_dir=corpus/docs/transcripts
sim_key=user_sim/keyword/related_keyword_list
python src/main.py corpus/PTV.query corpus/PTV.ans $index $doclen $bglm $key_dir $doc_dir $sim_key
