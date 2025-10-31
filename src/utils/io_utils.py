from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)

# create data dir
def create_data_dir() -> Path:
	data_dir = Path("data/")
	data_dir.mkdir(exist_ok=True)
	return data_dir

# this is where we store the hashes of files, in order to not run the pipeline on those files for which the content hasn't changed.
def create_metadata_file(data_dir: Path, name: str) -> Path:
	metadata_file = data_dir / name

	if not metadata_file.exists():
		logger.info(f"Metadata file doesn't exist")
		# create an empty JSON file
		metadata_file.write_text("")
		logger.info(f"{metadata_file} created with empty json.")

	return metadata_file

def read_file(file: Path) -> str:
	"""
	Read a markdown file and return its content as a string.
	"""
	content = ""
	logger.debug(f"Starting to read file, received {file.name} file to read.")

	try:
		with file.open("r", encoding="utf-8") as f:
			content = f.read()
	except Exception as e:
		logger.error(f"Error reading {file}: {e}")

	return content

# load json text into a dict
def json_to_dict(text) -> dict:
	if not text:
		return {}

	return json.loads(text)

def save_dict_to_json(metadata_file: Path, metadata: dict) -> None:
	"""
	Take a dictionary and save to a file as json.
	"""
	try:
		with metadata_file.open("w", encoding="utf-8") as f:
			json.dump(metadata, f, indent=2)
			logger.info(f"Wrote dict with hashes to metadata.json")
	except (OSError, json.JSONDecodeError) as e:
		logger.error(f"Error saving metadata to {metadata_file}: {e}")

def save_jsonl(metadata: list[dict], metadata_jsonl_file: Path):
	"""
	metadata: is a list of dictionaries(each a json like dict)
	metadata_jsonl_file: jsonl file to write metadata into
	"""
	with open(metadata_jsonl_file, "w", encoding="utf-8") as f:
		for entry in metadata:
			f.write(json.dumps(entry) + "\n")

def load_jsonl_metadata(content: str) -> list[dict]:
	"""
		Parse JSON Lines (JSONL) content into a list of dictionaries.

		Each line in the input string `content` is expected to be a valid JSON object.
		Empty lines are ignored. Lines that fail to parse as JSON will be skipped,
		and a warning will be logged for each invalid line.

		Args:
			content (str): The JSONL content as a string, where each line is a JSON object.

		Returns:
			List[Dict]: A list of dictionaries parsed from the JSONL content.
			Returns an empty list if no valid JSON lines are present.
	"""

	metadata = []
	for line in content.splitlines():
		# splits on \n efficiently
		line = line.strip()
		if not line:
			# skip empty lines
			continue
		try:
			metadata.append(json.loads(line))
		except json.JSONDecodeError as e:
			logger.warning(f"Skipping invalid JSON line: {line[:50]}... ({e})")

	return metadata
