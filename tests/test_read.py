import unittest
import tempfile
from pathlib import Path
from scan_and_hash import read_md_file

class TestReadingFiles(unittest.TestCase):
	def setUp(self):
		"""
		Create temporary files for testing. This runs before each test method.
		"""
		# Normal file
		self.normal_file = tempfile.NamedTemporaryFile(mode='w+', suffix=".md", delete=False)
		self.normal_file.write("# Hello World\nThis is a test.")
		self.normal_file.flush()
		self.normal_path = Path(self.normal_file.name)

		# Empty file
		self.empty_file = tempfile.NamedTemporaryFile(mode='w+', suffix=".md", delete=False)
		self.empty_file.flush()
		self.empty_path = Path(self.empty_file.name)

		# Nonexistent file path
		self.fake_path = Path("this_file_does_not_exist.md")

	def tearDown(self):
		"""
		Clean up temporary files. This runs after each test method.
		"""
		for path in [self.normal_path, self.empty_path]:
			try:
				path.unlink()
			except FileNotFoundError:
				pass

	def test_read_normal_file(self):
		content = read_md_file(self.normal_path)
		self.assertTrue(content.startswith("# Hello World"))
		self.assertIn("This is a test.", content)

	def test_read_empty_file(self):
		content = read_md_file(self.empty_path)
		self.assertEqual(content, "")

	def test_read_nonexistent_file(self):
		with self.assertLogs(level='ERROR') as log:
			content = read_md_file(self.fake_path)
			self.assertEqual(content, "")
			self.assertIn("Error reading", log.output[0])

if __name__ == "__main__":
	unittest.main()
