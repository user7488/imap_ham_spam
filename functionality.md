# Functionality Overview

## Implemented Features

| ID | Name | File | Description | Status |
|----|------|------|-------------|--------|
| F01 | config_loader | config.py | Load IMAP credentials and category definitions | Done |
| F02 | imap_fetcher | imap_client.py | Connect to IMAP and fetch emails from category folders | Done |
| F03 | local_storage | storage.py | Store fetched emails locally per category | Done |
| F04 | trainer | trainer.py | Train SpamBayes classifiers per category | Done |
| F05 | classifier | classifier.py | Score incoming emails against trained models | Done |
| F06 | daemon | daemon.py | Background service to auto-classify new emails | Done |
| F07 | chunk_processing | daemon.py | Process INBOX in 50-email chunks | Done |
| F08 | run_once | daemon.py | --once flag to process all and exit | Done |
| F09 | no_match_folder | daemon.py | Move unmatched emails to _no_match | Done |

## CLI Scripts

| Script | Purpose |
|--------|---------|
| fetch_training_data.py | Fetch emails from IMAP folders to local storage |
| train.py | Train classifiers from local data |
| daemon.py | Run the auto-classification daemon |

## Tags Summary

| Tag | Meaning | Count |
|-----|---------|-------|
| `#TODOLLM` | Unfinished task requiring implementation | 1 |
| `#NOTELLM` | Note for future reference | 1 |
| `#LATERLLM` | Deferred work / low priority | 0 |

### Tag Locations

- `config.py`: `#TODOLLM` - Add .env file support for credentials
- `imap_client.py`: `#NOTELLM` - Gmail uses COPY+DELETE instead of MOVE for older IMAP

*Code is the source of truth for tag counts.*
