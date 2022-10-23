# Civ 5 Automation + Log Harvesting
A utility for running repeated iterations of civ 5 games

## Prerequisites
### Python and Packages
Install python3+ (tested with 3.9), and the following packages:
```
pywinauto
pandas
```

### Modpack
VP is ran with a modpack for the following two reasons: speeding up time between games, and reducing the amount of menu automation needed to be done.
Use a provided modpack or follow the steps at https://civ-5-cbp.fandom.com/wiki/Creating_a_Modpack to create one and place it in `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\Assets\DLC` (or your DLC location)

### Steam Options
Properties -> General -> Launch Options
must be set to
```
"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\CivilizationV.exe" %command%
```
(or your executable location)

### Game Options
The following options must be set in-game:

Game Options:
* Skip Intro Video Enabled
* Single Player Quick Combat
* Single Player Quick Movement
* Advisor Level: No Advice
* Optional: Turns Between Autosaves:1 and max autosaves kept:999

Video Options:
* Screen Resolution: 1024x768
* Fullscreen: Disabled

### Game Config Options
`C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\config.ini`:
```
EnableTuner = 1
...
MessageLog = 1
AILog = 1
AIPerfLog = 1
BuilderAILog = 1
PlayerAndCityAILogSplit = 1
LoggingEnabled = 1
```

### Game Setup:
On the main menu under "Set Up Game" select the options you want - most of these are saved and applied every game


### Script Options
Fill out `options.py` downloaded from this repo if installed in a non-standard location

### Windows Options
This script requires a desktop environment with a resolution of 1920x1080

## Running the Script
```
python3 main.py
```
from the root of the repo.

Will save completed games to the `complete` directory in the civ 5 documents location (adjacent to `MODS`)