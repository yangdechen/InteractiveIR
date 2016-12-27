#!/bin/bash

WVDIR=/home/ydchen/tools/word2vec/word2vec/

$WVDIR/word2vec -train $1 -min-count 1 -output $2 -size 64 -window 3
