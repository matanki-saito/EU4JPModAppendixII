import os
import re
import shutil
from os.path import join
from pathlib import Path

_ = join

def main():
	extract_path = Path("./resource/gamedir")
	shutil.rmtree(extract_path, ignore_errors=True)
	os.makedirs(extract_path, exist_ok=True)

	base_path = Path("./tmp/game")

	shutil.copytree(base_path.joinpath(Path("common")), extract_path.joinpath(Path("common")))
	shutil.copytree(base_path.joinpath(Path("customizable_localization")), extract_path.joinpath(Path("customizable_localization")))
	shutil.copytree(base_path.joinpath(Path("decisions")), extract_path.joinpath(Path("decisions")))
	shutil.copytree(base_path.joinpath(Path("events")), extract_path.joinpath(Path("events")))
	shutil.copytree(base_path.joinpath(Path("hints")), extract_path.joinpath(Path("hints")))
	shutil.copytree(base_path.joinpath(Path("history")), extract_path.joinpath(Path("history")))
	shutil.copytree(base_path.joinpath(Path("missions")), extract_path.joinpath(Path("missions")))

if __name__ == "__main__":
	# execute only if run as a script
	main()
