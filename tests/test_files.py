import unittest
import tempfile
from pathlib import Path
from scan_and_hash import retrieve_md_filenames, hash_md_file
from build import IGNORE_DIRS

class TestRetrieveMdFilenames(unittest.TestCase):
	def setUp(self):
		# create a temporary directory for testing
		self.temp_dir = tempfile.TemporaryDirectory()
		self.test_base = Path(self.temp_dir.name)

		# create some test files and directories
		(self.test_base / "file1.md").write_text("# file1")
		(self.test_base / "file2.txt").write_text("not markdown")
		
		# ignored directory
		ignored_dir = self.test_base / ".git"
		ignored_dir.mkdir()
		(ignored_dir / "ignored.md").write_text("should be ignored")
		
		# nested markdown file
		nested_dir = self.test_base / "docs"
		nested_dir.mkdir()
		(nested_dir / "nested.md").write_text("nested file")
	
	def tearDown(self):
		# clean up temp directory
		self.temp_dir.cleanup()

	def test_retrieve_md_filenames(self):
		md_files = retrieve_md_filenames(self.test_base, IGNORE_DIRS)
		md_files_set = set(f.name for f in md_files)

		# assert we found the correct markdown files
		self.assertIn("file1.md", md_files_set)
		self.assertIn("nested.md", md_files_set)
		# ignored files should NOT be included
		self.assertNotIn("ignored.md", md_files_set)
		# non-md files should NOT be included
		self.assertNotIn("file2.txt", md_files_set)
		# total count
		self.assertEqual(len(md_files_set), 2)

class TestHashMdFile(unittest.TestCase):
	def setUp(self):
		self.tmp_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".md", delete=False)
		self.tmp_file.write("# markdown content")
		# must close to read later
		self.tmp_file.close()
		self.tmp_path = Path(self.tmp_file.name)

	def tearDown(self):
		self.tmp_path.unlink()

	# test that same content returns same hash
	def test_hash_md_file(self):
		h1 = hash_md_file(self.tmp_path)
		h2 = hash_md_file(self.tmp_path)
		assert h1 == h2

if __name__ == "__main__":
	unittest.main()
