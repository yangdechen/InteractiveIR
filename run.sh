#!/bin/bash

index=retrieval/index/transcripts.char_bichar.index
doclen=retrieval/doclen/transcripts.doclen
bglm=retrieval/bglm/transcripts.char_bichar.lm
key_dir=keyterm/transcripts/textrank_core_window2
doc_dir=corpus/docs/transcripts
sim_key=user_sim/keyword/related_keyword_list

for i in {1..5}; do
echo "======== train $i ========"
python src/main.py train \
                   corpus/5fold_cv/fold_${i}/query.train \
                   corpus/PTV.ans_new \
                   $index \
                   $doclen \
                   $bglm \
                   $key_dir \
                   $doc_dir \
                   $sim_key \
                   model.${i}

echo "======= test $i ========"
python src/main.py test \
                   corpus/5fold_cv/fold_${i}/query.test \
                   corpus/PTV.ans_new \
                   $index \
                   $doclen \
                   $bglm \
                   $key_dir \
                   $doc_dir \
                   $sim_key \
                   model.${i}
done
