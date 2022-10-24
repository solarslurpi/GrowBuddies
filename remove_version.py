
# The requirements.txt file included versioning.  The versioning conflicts made it next to impossible to build on ReadTheDocs
# This script removes the versioning from requirements.txt.
replacement = ""

def strip_version(line):
    substring = line.find("=")
    return line[0:substring]


with open("requirements.txt") as f:
    for line in f:
        substring = line.find("=")
        line = line[0:substring]
        replacement = replacement + line + "\n"


with open("requirements.txt", "w") as f:
    f.write(replacement)
