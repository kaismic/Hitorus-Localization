import os
import json
from pathlib import Path
from datetime import datetime

script_path = Path(__file__).resolve()
script_dir = script_path.parent
os.chdir(script_dir)

projectNames = ["Hitorus.Api", "Hitorus.Web"]
inputSrcPath = Path("src")
outputSrcPath = Path.joinpath(Path.cwd().parent, "src")
templateResxPath = Path("resx-template.resx")
lastUpdateTimeRecordPath = Path("last-update-time.json")

print("Choose the project resource to generate:")
print(f"{projectNames[0]} - 1, {projectNames[1]} - 2, Both - 3")

try:
    generateOption = int(input("Select an options: "))
except ValueError:
    print('Enter a valid number between 1 - 3')
    exit()
if generateOption < 1 or generateOption > 3:
    print('Enter a number between 1 - 3')
    exit()

selectedDirs = []

if generateOption & 0b01:
    selectedDirs.append(projectNames[0])
if generateOption & 0b10:
    selectedDirs.append(projectNames[1])

resxTemplateContentFront: str
resxTemplateContentBack: str
with open(templateResxPath, "r") as f:
    resxTemplateContent = f.read()
    resxTemplateContentFront = resxTemplateContent[:-8]
    resxTemplateContentBack = resxTemplateContent[-8:]

resxKeyValueTemplate = """  <data name="{key}" xml:space="preserve">
    <value>{value}</value>
  </data>"""

# gotta use divide and conquer algorithm
def generateResx(dirPath: Path, data: dict, lang: str):
    outputKeys: list[str] = []
    for key in data.keys():
        if isinstance(data[key], str):
            outputKeys.append(key)
        else:
            generateResx(Path.joinpath(dirPath, key), data[key], lang)
    if (len(outputKeys) > 0):
        outputContent = '\n'.join([resxKeyValueTemplate.format(key = key,value = data[key]) for key in outputKeys])
        dirPath.parent.mkdir(parents = True, exist_ok = True)
        outputFilePath = Path.joinpath(dirPath.parent, dirPath.stem + (".resx" if lang == "en" else f".{lang}.resx"))
        with open(outputFilePath, "w") as f:
            f.write(resxTemplateContentFront + outputContent + resxTemplateContentBack)

for d in selectedDirs:
    inputPath = Path.joinpath(inputSrcPath, d)
    outputPath = Path.joinpath(outputSrcPath, d, "Localization")
    for filePath in inputPath.iterdir():
        lang = filePath.stem
        with open(filePath) as file:
            data: dict = json.load(file)
            generateResx(outputPath, data, lang)

with open(lastUpdateTimeRecordPath, "r+") as f:
    data = json.load(f)
    if generateOption & 0b01:
        data[projectNames[0]] = datetime.now().isoformat()
    if generateOption & 0b10:
        data[projectNames[1]] = datetime.now().isoformat()
    f.seek(0)
    json.dump(data, f, indent = 2)

