# gameControl

A specialized keyboard macro for rune farming in Elden Ring.

## Overview

This project automates repetitive tasks in Elden Ring to optimize rune farming. It uses Python to simulate keyboard inputs, capture screenshots, and perform OCR (Optical Character Recognition) to monitor progress and reset sequences when necessary.

## Features

- Automated keyboard macros for rune farming.
- Image comparison to detect changes in the game state.
- OCR-based number extraction to track rune counts.
- Sequence reset logic for efficient farming.

## Requirements

- Python 3.8 or higher
- Required Python libraries:
  - `pynput`
  - `pytesseract`
  - `Pillow`
  - `Quartz` (macOS-specific)
- Tesseract OCR installed on your system.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gameControl.git

## Notes

This macro is designed specifically for rune farming and may not work for other tasks in Elden Ring.
Ensure the game window is visible and accessible for the macro to function correctly.


## Disclaimer
This project is intended for educational purposes only. Use at your own risk.