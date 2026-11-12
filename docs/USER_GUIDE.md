# CTF HUNTER X - User Guide

## 1. Creating and Managing Challenges
1. Click **New Challenge** in the navigation sidebar or press `Ctrl+K` and select *Create New Challenge*.
2. Enter the challenge title, category (Forensics, Steganography, Cryptography, Reverse Engineering, Web, OSINT, or Misc), and an optional flag format regex (e.g. `ctf\{[a-z0-9_]+\}`).
3. Drag and drop challenge files into the file intake area. The engine streams files into the vault, calculates SHA-256 hashes, true magic-byte formats, Shannon entropy, and marks files as read-only.

## 2. Using the 3-Panel Workspace
- **Left Panel (Artifacts)**: Displays all ingested files, nested unpacked archives, and quick links to the evidence graph and module cards.
- **Center Panel (Inspector & Hex View)**:
  - *Hex Viewer*: Interactive 16-byte grid showing hexadecimal bytes and ASCII representations.
  - *Metadata*: Detailed file header information, detected anomalies (e.g., trailing bytes beyond PNG IEND).
  - *Evidence Graph*: Interactive provenance tree showing transitions from root file to discovered flag.
  - *Analysis Modules*: Structured output summaries from domain-specific analyzers.
- **Right Panel (Candidate & Provenance Inspector)**:
  - Lists all discovered flag candidates with status badges and decoy detection indicators.
  - Clicking any candidate deep-links to its exact byte offset in the Hex Viewer.
  - Provides one-click buttons for authoritative validation (*Accept* or *Reject*).
  - Offers *Copy Evidence Chain* and *Export Repro Script*.

## 3. Keyboard Shortcuts
- `Ctrl+K`: Toggle Command Palette.
- `/`: Quick Search when not typing in an input field.
- `g` then `h`: Jump to Hex Viewer.
- `g` then `e`: Jump to Evidence Graph.
- `g` then `r`: Open Reports page.
