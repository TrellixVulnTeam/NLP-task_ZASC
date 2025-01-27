# !/usr/bin/env python
# -*- coding: utf-8 -*-

from skipgram import Skipgram
from dataset import Corpus, load_data
import argparse
parser = argparse.ArgumentParser(description='main.py')
parser.add_argument('-train', action='store_true',
                    default=False, help='train model')
parser.add_argument('-test', action='store_true',
                    default=False, help='test model')
args = parser.parse_args()


if __name__ == '__main__':

    data = list(load_data())
    corpus = Corpus(data)
    skipgram = Skipgram(corpus)

    if args.train:
        skipgram.train()
    elif args.test:
        word = input('Input word> ')
        print(skipgram.test(word))
