# WildWard Listen

**Offline bat-call review for Southeast Asian surveys**, by [WildWard](https://wildward.github.io).

Point it at a folder of bat-detector recordings. It finds every bat pass, measures every call, groups calls that sound alike, and lets an expert label whole groups at once. It learns from each label and exports spreadsheets plus a survey report. Everything runs on your own computer. Nothing is uploaded.

## What it does

- **Finds bat passes** in full-spectrum recordings (192 kHz and up) or time-expanded files (10x or 16x).
- **Measures every call** the way ecologists do by hand: start, end, peak and characteristic frequency, duration, bandwidth, slope and call shape (CF, CF-FM, FM, QCF). Exported as `calls.csv`, ready for discriminant-function analysis or call-library work.
- **Names the sound type with zero labels**, e.g. *"short constant tone, about 118 kHz, typical of leaf-nosed bats"*. These are broad textbook patterns, meant as a starting point, never an identification.
- **Groups similar passes** using Google's Perch 2.0 bioacoustics model on time-expanded audio, so an expert can confirm many passes with one click.
- **Learns from your reference library**: point it at your own folder of identified calls (one sub-folder per species) and it suggests species with a confidence score from the first minute, before you label anything. Cached, so it only learns once.
- **Learns from your labels**: every group you confirm retrains it in seconds, and your labels from this survey count more than the library. While it knows fewer than five species it only says which known species is closest, never a fake confidence score.
- **Orders the review** so the groups that teach it the most come first.
- **Flags unusual frequencies.** A horseshoe or leaf-nosed bat calling at least 5% away from every frequency your known species use gets marked *unusual*: it may be a species missing from your library, or one worth a closer look. Several cryptic Southeast Asian bats were first noticed this way. Tested on 49 species ([batlab Test 8](https://github.com/WildWard/batlab/blob/main/FINDINGS.md)): it flags about 4% of known-species passes recorded at new sites, and about half the passes of a hidden species that calls at its own distinct frequency. A newcomer calling close to a known species won't be flagged. Shown in the review, in `passes.csv` (`unusual_frequency`) and in the report.
- **Shows bat activity through the night**, with times read from file names like `20261024_213000.wav` (AudioMoth, Song Meter and similar).
- **Says the genus when the species is unsure.** If it isn't 70% sure of the species but is of the genus, it shows "probably *Hipposideros* (genus)" instead of a likely-wrong species. At recording sites the model had never heard, confident species calls were 80% right and genus fallbacks 94% right ([batlab Test 9](https://github.com/WildWard/batlab/blob/main/FINDINGS.md)).
- **Reads detector metadata.** GPS position, time and device from GUANO (Song Meter, Pettersson and others) and AudioMoth's own comments, so times don't depend on file names.
- **Sites & nights.** An offline map of detector positions and activity night by night across a whole survey.
- **Wind-site view.** Activity of open-air foragers by hour and night: the bats found flying at turbine height in Southeast Asia (free-tailed, sheath-tailed, house bats and relatives).
- **Speaks your language.** English, Bahasa Indonesia, Bahasa Melayu, Tiếng Việt, ไทย and Filipino (first-draft translations, corrections welcome).
- **Exports** `passes.csv`, `calls.csv`, `report.html` and `occurrences.csv` into the survey folder. `occurrences.csv` is Darwin Core, ready to publish to GBIF, and holds only passes an expert reviewed.

## How well does it work? (honest numbers)

Tested on 237 identified recordings of 21 Malaysian bat species from the [ChiroVox](https://www.chirovox.org) library:

| Check | Result |
|---|---|
| Recordings where at least one bat pass is found | 60 of 60 in a sample, at the species' known call frequencies |
| Sound type points to the right bat family, no labels at all | **78%** overall (184 of 237): leaf-nosed 85%, woolly 83%, horseshoe 73%, vesper 92%, free-tailed 75% |
| Slit-faced bats (*Nycteris*) | 0 of 12, there is no rule for their faint calls yet |
| Species, with labels (see [batlab](https://github.com/WildWard/batlab)) | 81% species / 92% genus; 53% / 84% on recording sites never seen in training |
| Species from a reference library only, zero labels, on a 48-recording test night (125 passes, no overlap with the library) | 53% species / 71% genus; when it says 80% or more, it is right 82% of the time |

Measured call frequencies match published values, for example *Hipposideros cervinus* about 118 kHz, *Rhinolophus affinis* 73.5 kHz with 36 ms calls, *R. borneensis* 82.5 kHz, *Kerivoula* 2 ms steep sweeps.

**Known limits:** apart from the unusual-frequency flag for constant-frequency bats, it can't tell when a bat is a species missing from your library, so it suggests the closest species it knows; a messy reference library (other bats in the background of reference files) can hide a newcomer from the flag; use the **Not in my library** button and it learns to route similar passes to Unknown; faint passes are marked "unclear" rather than guessed (about a quarter of the weaker passes in a test night); stray fragments that survive filtering are flagged `main_bat = no` in `calls.csv`; grouping mixes some similar species, so always listen before labelling; no pre-trained species model ships yet (see below).

## Install on Windows (no Python needed)

1. On the [GitHub page](https://github.com/WildWard/listen), click **Code → Download ZIP** and unzip it somewhere permanent, e.g. `Documents\WildWard Listen`.
2. Double-click **`Install WildWard Listen.bat`**. It sets up a private copy of Python and everything Listen needs inside that folder, then downloads the Perch 2.0 sound model. No admin rights, nothing installed system-wide. It needs internet once, about 1 GB, and takes 5-15 minutes.
3. Double-click **WildWard Listen** on your desktop. It opens in your browser. From then on it works fully offline.

To uninstall, delete the folder and the desktop shortcut.

## Install on a Mac (Apple Silicon, M1 or newer)

1. Download the ZIP as above and unzip it.
2. Right-click **`install-mac.command`** and choose **Open** (the first time macOS asks you to confirm a downloaded script). It installs everything inside that folder, like the Windows installer.
3. Double-click **`WildWard Listen.command`** to start.

Not yet tested on a real Mac: if anything goes wrong, email wildward.org@gmail.com. Intel Macs aren't supported, because TensorFlow (which runs the Perch model) only ships Mac builds for Apple Silicon.

## Run it (Python users)

Python 3.12, works on a normal laptop CPU.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python run.py
```

Your browser opens at `http://127.0.0.1:8790`. Type the folder with your recordings and press **Scan recordings**. Perch 2.0 is downloaded once on the first scan (about 400 MB); after that everything works offline. Results are saved in a `.wildward` folder inside your survey folder, so you can close and reopen any time.

Command line options: `python run.py <folder> --te 16` opens a folder directly, `--rescan` scans again, `--port` changes the port.

## Your data stays yours

The app only listens on your own computer (127.0.0.1). Recordings, labels and results never leave the machine. There is no account, no tracking and no upload.

## Reference libraries and the species model

Use your own reference library: a folder with one sub-folder per species, named the way the species should appear (for example `My calls\Hipposideros larvatus\*.wav`). Set the time-expansion factor for the library, or put a `te.txt` containing `10` or `16` in any species folder that is time-expanded. Listen only ever learns from data on your own computer.

A ready-made regional model trained on ChiroVox recordings would help everyone start faster. ChiroVox recordings are mostly CC BY-NC-ND, so we won't distribute such a model until the recordings' rights holders agree.

## Licence and credits

MIT licence. Perch 2.0 by Google DeepMind. Validation recordings: Görföl T. et al. (2022) *ChiroVox: a public library of bat calls*, PeerJ 10:e12445, used locally for non-commercial research and not redistributed.

Questions, recordings to test with, or ideas: **wildward.org@gmail.com**
