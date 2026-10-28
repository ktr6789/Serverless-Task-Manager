import sys
from pathlib import Path
import regex as re

path = Path(sys.argv[1])

path_text = path.read_text()
path_newtext = re.sub(r'\bapp\b', 'app_old', path_text)
path.write_text(path_newtext)