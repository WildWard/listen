# WildWard Listen: MVP spec

Offline desktop tool that turns a folder of bat-detector recordings into reviewed species identifications and a survey report.

## Who it's for
A field ecologist or student in Southeast Asia, back from a survey with SD cards full of ultrasonic recordings (AudioMoth, Pettersson, Batlogger, Song Meter). No coding, often no reliable internet, little time.

## The core loop (MVP)
1. **Open a survey:** pick a folder of WAV files (any sample rate ≥ 192 kHz, or time-expanded files with a declared factor).
2. **Find calls:** an energy detector in the 12-192 kHz band marks every call sequence. Each file becomes a list of "passes" (a few seconds of calls).
3. **Listen like Perch:** each pass is time-expanded 12x and embedded with Perch 2.0 (the method from batlab, 74% species / 88% genus on 21 species).
4. **Group:** passes are clustered by sound, so similar calls sit together.
5. **Suggest:** if a regional model is loaded, each pass and cluster gets a species or genus suggestion with a confidence score. Without a model, clusters are simply unlabelled.
6. **Review in the browser:** each cluster is a card with a spectrogram and a slowed-down audio player. The expert confirms or renames a whole cluster with one click, or splits out wrong passes.
7. **Learn:** confirmed labels retrain a small local classifier in seconds, so suggestions improve on that site.
8. **Export:** a CSV (file, time, species, confidence, reviewed yes/no) and a one-page HTML survey report (species list, pass counts, activity by night hour).

## Non-negotiables
- **Offline** after the first install. Nothing leaves the laptop.
- **The expert stays in charge:** the AI suggests, a human confirms. Unreviewed results are always marked as unreviewed.
- **Their data stays theirs:** no upload, no telemetry.
- **Honest confidence:** show how sure the model is, and say clearly when a species is outside what it was trained on.

## Out of scope for the MVP
Cloud sync, multi-user, mobile, live field monitoring, non-bat taxa, a packaged installer (MVP runs from Python; installer comes after the first pilot).

## Tech
- Python 3.12 engine: detection (numpy/scipy), Perch 2.0 CPU (TensorFlow), clustering + classifier (scikit-learn).
- Local web UI: a tiny Python server (standard library) serving one HTML page; opens in the user's browser at localhost.
- Survey state saved as JSON next to the recordings, so work is never lost.

## Licence note (important)
The regional starter model would be trained on ChiroVox recordings, which are mostly CC BY-NC-ND. **We do not distribute a model trained on that data until the rights holders agree**. Until then the app works fully without a pre-trained model: clustering + the user's own labels.

## Done means
Point it at a folder of real recordings → calls found → clusters shown with spectrograms and audio → label two clusters → suggestions appear for the rest → CSV + report exported. Works with the network cable unplugged.
