# Civ 5 Automation + Log Harvesting
A utility for running repeated iterations of civ 5 games

## Prerequisites
### Python and Packages
Install python3+ (tested with 3.9), and the following packages:
```
pywinauto
pandas
numpy
```

### Modpack
VP is ran with a modpack so that the Civ 5 CLI automation can be used.

Use a provided modpack (https://drive.google.com/file/d/1nRFx276ZaUyccGBICBQigW6wDNBnZfpS) or follow the steps at https://civ-5-cbp.fandom.com/wiki/Creating_a_Modpack to create one (be sure to include the autoplay mod in this repo) and place it in `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\Assets\DLC` (or your DLC location)

### Automation Entrypoint
Copy `RunAutoplayGame.lua` from the root of this repo to `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\Assets\Automation`

### Maps
Copy `Community_79a.lua` to `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\Assets\Maps`

### Steam Options
Properties -> General -> Launch Options
must be set to
```
"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization V\CivilizationV.exe" %command% -Automation RunAutoplayGame.lua
```
(or your executable location)

### Game Options
The following options must be set in-game:

Game Options:
* Skip Intro Video Enabled
* Optional: Turns Between Autosaves:1 and max autosaves kept:999

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
...
[GAME]
...

; Force quick combat animations
QuickCombat = 1

...

; Worldsize options are WORLDSIZE_DUEL/WORLDSIZE_TINY/WORLDSIZE_SMALL/WORLDSIZE_STANDARD/WORLDSIZE_LARGE/WORLDSIZE_HUGE
WorldSize = WORLDSIZE_STANDARD

...

; Map Script file name
Map = Assets\Maps\Communitu_79a.lua

...

; Handicap for quick play
QuickHandicap = HANDICAP_EMPEROR

```

### Script Options
Fill out `config.py` downloaded from this repo with your install and local files locations

## Running the Script
```
python3 main.py
```
from the root of the repo.

Will save completed games to the `complete` directory in the civ 5 documents location (adjacent to `MODS`)