from pathlib import Path
import os

BASE_DIR = Path("../")
IGNORE_DIRS = {".git", ".github", ".DS_Store"}

def retrieve_md_filenames():
	md_files = []
	for root, dirs, files in os.walk(BASE_DIR):
		# remove ignored dirs from traversal
		print(f"{root}, {dirs}, {files}")
		dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
		for file in files:
			if file.endswith(".md"):
				md_files.append(Path(root) / file)
	return md_files

def main():
	retrieve_md_filenames()

# --- entry point ---
if __name__ == "__main__":
	main()
