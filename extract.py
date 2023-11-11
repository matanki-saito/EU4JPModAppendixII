import os
import re
import shutil
from os.path import join
from pathlib import Path

_ = join

def en_filter(src, dst):
	if re.search(r"l_english.yml$", src):
		shutil.copy2(src, dst)


def main():
	extract_path = Path("./resource/gamedir")
	shutil.rmtree(extract_path, ignore_errors=True)
	os.makedirs(extract_path, exist_ok=True)

	base_path = Path("./tmp/game")

	shutil.copytree(base_path.joinpath(Path("common")), extract_path.joinpath(Path("common")), copy_function=en_filter)
	shutil.copytree(base_path.joinpath(Path("customizable_localization")), extract_path.joinpath(Path("customizable_localization")), copy_function=en_filter)
	shutil.copytree(base_path.joinpath(Path("decisions")), extract_path.joinpath(Path("decisions")), copy_function=en_filter)
	shutil.copytree(base_path.joinpath(Path("events")), extract_path.joinpath(Path("events")), copy_function=en_filter)
	shutil.copytree(base_path.joinpath(Path("hints")), extract_path.joinpath(Path("hints")), copy_function=en_filter)
	shutil.copytree(base_path.joinpath(Path("history")), extract_path.joinpath(Path("history")), copy_function=en_filter)
	shutil.copytree(base_path.joinpath(Path("missions")), extract_path.joinpath(Path("missions")), copy_function=en_filter)

if __name__ == "__main__":
	# execute only if run as a script
	main()
