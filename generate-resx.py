import os
import json
from pathlib import Path
from datetime import datetime

script_path = Path(__file__).resolve()
script_dir = script_path.parent
os.chdir(script_dir)

projects = ["Hitorus.Api", "Hitorus.Web"]
inputSrcPath = Path("src")
outputSrcPath = Path.joinpath(Path.cwd().parent, "src")
templateResxPath = Path("resx-template.resx")
lastUpdateTimeRecordPath = Path("last-update-time.json")

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

for p in projects:
    inputPath = Path.joinpath(inputSrcPath, p)
    outputPath = Path.joinpath(outputSrcPath, p, "Localization")
    for filePath in inputPath.iterdir():
        lang = filePath.stem
        with open(filePath) as file:
            data: dict = json.load(file)
            generateResx(outputPath, data, lang)
            print("Generated resource files in", outputPath)

with open(lastUpdateTimeRecordPath, "r+") as f:
    data = json.load(f)
    timeNow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.seek(0)
    f.truncate(0)
    json.dump(data, f, indent = 2)