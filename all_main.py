import argparse
from config import setup_logger

# this will be the entry point. based on arguments passed it will either call the build or query flow
def main():
	parser = argparse.ArgumentParser(
		formatter_class=argparse.RawTextHelpFormatter,
		usage="python all_main.py {build,query} [--debug] [-h]"
	)

	parser.add_argument("mode", choices=["build", "query"])
	parser.add_argument("--debug", action="store_true", help="Enable debug logging")
	args = parser.parse_args()

	logger = setup_logger(debug=args.debug)
	logger.debug("Debug mode enabled.")

	if args.mode == "build":
		import build
		build.main(logger)
	elif args.mode == "query":
		import query
		query.main(logger)

# --- entry point ---
if __name__ == "__main__":
	main()
