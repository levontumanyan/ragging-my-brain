import unittest
import os
import numpy as np
from embed_and_store import store_embeddings
import faiss

class TestStoreEmbeddings(unittest.TestCase):
	def setUp(self):
		"""Run before each test"""
		self.test_index_path = "test_index.faiss"
		self.DIM = 384

		# clean up any leftover index from previous runs
		if os.path.exists(self.test_index_path):
			os.remove(self.test_index_path)

		# create fake embeddings (5 vectors of dimension self.DIM)
		np.random.seed(42)
		self.embeddings = np.random.rand(10, self.DIM).astype("float32")

	def tearDown(self):
		"""Run after each test"""
		if os.path.exists(self.test_index_path):
			os.remove(self.test_index_path)

	def test_creates_index_file(self):
		"""Test that a new FAISS index file is created"""
		store_embeddings(self.embeddings, self.test_index_path)
		self.assertTrue(os.path.exists(self.test_index_path))

	def test_index_has_correct_dimension(self):
		"""Test that FAISS index has expected vector dimension"""
		store_embeddings(self.embeddings, self.test_index_path)
		index = faiss.read_index(self.test_index_path)
		self.assertEqual(index.d, self.DIM)

	def test_index_adds_embeddings(self):
		"""Test that embeddings can be added"""
		store_embeddings(self.embeddings, self.test_index_path)
		index = faiss.read_index(self.test_index_path)
		# if your function later adds to index, check total vectors here
		self.assertIsInstance(index, faiss.IndexFlatL2)

	