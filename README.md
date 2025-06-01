# MLBModel

## Overview

This repository contains code for scraping, processing, and updating Major League Baseball (MLB) data, with a focus on player lineups and betting odds. The code interacts with various APIs and Google Sheets to automate data collection and reporting.

## How It Works

- **Data Collection:**  
  The scripts in this codebase scrape MLB lineup and odds data from public sources and APIs.

- **Google Sheets Integration:**  
  Data is pushed to private Google Sheets for further analysis and reporting.  
  **Note:** All sensitive calculations, formulas, and proprietary logic are performed within these private Google Sheets for privacy and security reasons. The code in this repository does not contain or expose those formulas.

- **Automation:**  
  The code is designed to automate the process of updating Google Sheets with the latest MLB data, making it easier to track and analyze trends.

## Important Notes

- **Privacy:**  
  All advanced calculations and formulas are kept private within Google Sheets and are not included in this repository.

- **Outdated Code:**  
  This codebase is out of date and does **not** reflect my current coding standards or best practices.  
  If you are reviewing this code, please be aware that it is not representative of how I would structure or write similar projects today.

## Getting Started

1. **Clone the repository**
2. **Set up your environment:**  
   - Place your Google API credentials in a `credentials.json` file.
   - Set required environment variables (e.g., `API_Key`, `Sheet_ID`).
3. **Run the scripts** as needed to update your Google Sheets.

## Disclaimer

This repository is for reference only. For up-to-date implementations or questions about the private calculations, please contact me directly.
