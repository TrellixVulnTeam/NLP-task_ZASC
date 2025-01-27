# !/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(description='main.py')
parser.add_argument('-train', action='store_true', default=False, help='train model')
parser.add_argument('-retrain', action='store_true', default=False, help='train model')
parser.add_argument('-test', action='store_true', default=False, help='test model')
args = parser.parse_args()

import const
import numpy as np
import torch
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable

from dataset import Corpus, load_data
from cbow import Cbow
from utils import Utils

def test(word, corpus, k=10):
	vocab = corpus.vocab
	model,_ = Utils.load_previous_model('model')
	target_V = model.pred(Variable(torch.LongTensor(corpus.var_word(word))))
	scores=[]
	for i in range(len(vocab)):
		if vocab[i] == word or vocab[i] == const.U_TOKEN: 
			continue
		vector = model.pred(Variable(torch.LongTensor(corpus.var_word(list(vocab)[i]))))
		cosine_sim = F.cosine_similarity(target_V, vector).data.tolist()[0] 
		scores.append([vocab[i],cosine_sim])
	return sorted(scores, key=lambda x: x[1], reverse=True)[:k] # sort by similarity

def train(corpus):
	if args.retrain:
		Utils.remove_models('model')

	losses = []

	start_epoch = 0
	model, start_epoch = Utils.load_previous_model('model')
	if model == None:
		model = Cbow(corpus.n_words, const.EMBEDDING_SIZE)

	if torch.cuda.is_available():
		model.cuda()
	optimizer = optim.Adam(model.parameters(), const.LR_RATE)

	for epoch in range(start_epoch, const.EPOCH):
		inputs, targets = corpus.batch_data()


		inputs = Variable(torch.from_numpy(inputs).long())
		targets = Variable(torch.from_numpy(targets).long())

		negs = corpus.negative_sampling(targets)
		#print(inputs.size(), targets.size(), vocabs.size())
		#exit()
		model.zero_grad()
		loss = model(inputs, targets, negs)
		loss.backward()
		optimizer.step()

		losses.append(loss.data.tolist()[0])
		if epoch % 100 == 0:
			print("Epoch : %d, mean_loss : %.02f" % (epoch , np.mean(losses)))
			Utils.save_model(model, epoch, 'model')
			losses = []
	Utils.save_model(model, epoch, 'model')

data = list(load_data())
corpus = Corpus(data)
if args.train or args.retrain:
	train(corpus)
elif args.test:
	word = input('Input word> ')
	print(test(word, corpus))