#!/usr/bin/env bash
#
# Copyright (c) 2016-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.
#

myshuf() {
  perl -MList::Util=shuffle -e 'print shuffle(<>);' "$@";
}

#normalize_text() {
#  tr '[:upper:]' '[:lower:]' | sed -e "s/<.*>//g" | \
#	sed -e "s/-+//g" | \
#	sed -e "s/'//g" -e 's/"//g' -e 's/\.//g' -e 's/<br \/>/ /g' \
#       -e 's/,//g' -e 's/~/ , /g' -e 's/(//g' -e 's/)//g' -e 's/\!//g' \  # note comma sequence
#       -e 's/\?//g' -e 's/\;/ /g' -e 's/\:/ /g' | tr -s " " | myshuf
#}

normalize_text() {
  tr '[:upper:]' '[:lower:]' | sed -e 's/-+//g' -e 's/<.*>//g' | \
    sed -e "s/'//g" -e 's/"//g' -e 's/\.//g' -e 's/<br \/>/ /g' \
        -e 's/,//g' -e 's/~/ , /g' -e 's/(/ ( /g' -e 's/)/ ) /g' -e 's/\!/ \! /g' \
        -e 's/\?/ \? /g' -e 's/\;/ /g' -e 's/\:/ /g' | tr -s " " | myshuf
}


RESULTDIR=result
DATADIR=data

TRAIN="movielines.train"
TEST="movielines.test"
TRAINSET="train.csv"
TESTSET="test.csv"

cat "${DATADIR}/${TRAIN}" | normalize_text > "${DATADIR}/${TRAINSET}"
cat "${DATADIR}/${TEST}" | normalize_text > "${DATADIR}/${TESTSET}"

iconv -f utf-8 -t utf-8 -c "${DATADIR}/${TRAINSET}"
iconv -f utf-8 -t utf-8 -c "${DATADIR}/${TESTSET}"

#make

#./fasttext supervised -input "${DATADIR}/${TRAINSET}" -output "${RESULTDIR}/movielines" -dim 10 -lr 0.1 -wordNgrams 2 -minCount 1 -bucket 10000000 -epoch 5 -thread 4

#./fasttext test "${RESULTDIR}/movielines.bin" "${DATADIR}/${TESTSET}"

#./fasttext predict "${RESULTDIR}/dbpedia.bin" "${DATADIR}/dbpedia.test" > "${RESULTDIR}/dbpedia.test.predict"
