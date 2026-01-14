# Usage Guide

## Purpose

This tool automatically categorizes incoming emails in your Gmail inbox using machine learning (Naive Bayes classification). It connects to your email via IMAP, analyzes each message, and moves it to the appropriate folder based on trained models.

**Use cases:**
- Automatically sort billing emails, newsletters, delivery notifications, etc.
- Keep your inbox at zero by moving all emails to categorized folders
- Review classifier decisions with debug labels for human verification

## Setup

### 1. Environment Variables

Set your Gmail credentials (use an App Password if 2FA is enabled):

```bash
export IMAP_USER="you@gmail.com"
export IMAP_PASS="your-app-password"
```

### 2. Prepare Training Data

Manually sort some emails into the category folders defined in `categories.md` (under `_auto_categorization/`). You need ~50-100 emails per category for good results.

### 3. Fetch Training Data

Download the training emails from IMAP to local storage:

```bash
python fetch_training_data.py
```

### 4. Train Classifiers

Build the Naive Bayes models from local data:

```bash
python train.py
```

## Running the Daemon

### Basic Usage

Run continuously, checking for new emails every 60 seconds:

```bash
python daemon.py
```

### One-Time Processing

Process all unseen emails and exit:

```bash
python daemon.py --once
```

### Process All Emails (Including Read)

```bash
python daemon.py --once --all
```

### Debug Mode with Tagging

Process slowly in small chunks and tag moved emails for human review:

```bash
python daemon.py --once --all --chunk-size=10 --interval=5 --tag-moved='testrun-26-01-13'
```

## Command-Line Options

| Option | Description |
|--------|-------------|
| `--once` | Process all matching emails and exit (don't run as daemon) |
| `--all` | Process all emails, not just unseen/unread |
| `--chunk-size=N` | Process N emails per batch (default: 50) |
| `--interval=N` | Wait N seconds between batches (default: 60) |
| `--tag-moved=LABEL` | Copy processed emails to this label for review |

## Folder Structure

Emails are moved to folders under `_auto_categorization/`:
- `_auto_categorization/billing`
- `_auto_categorization/newsletters`
- `_auto_categorization/_no_match` (emails that don't match any category)
