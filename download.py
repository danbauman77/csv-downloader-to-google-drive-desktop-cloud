#!/usr/bin/env python3

import csv
import json
import logging
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import load_config


# --- logging ---

def setup_logging(cfg):
    log = logging.getLogger(cfg.get("monitor_name", "monitor"))
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    if not log.handlers:
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(fmt)
        log.addHandler(sh)
        if cfg.get("log_file"):
            fh = logging.FileHandler(cfg["log_file"])
            fh.setFormatter(fmt)
            log.addHandler(fh)
    return log


# --- state ---

def load_state(state_file):
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(state_file, state_dict):
    try:
        with open(state_file, "w") as f:
            json.dump(state_dict, f, indent=2)
    except IOError as e:
        logging.getLogger(__name__).error(f"Failed to save state: {e}")


# --- http ---

def create_session(cfg):
    session = requests.Session()
    session.headers.update({"User-Agent": cfg["user_agent"]})
    return session


# --- file I/O ---

def save_json(data, filepath, log):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        log.info(f"Saved to {filepath}")
    except IOError as e:
        log.error(f"Error saving JSON: {e}")


# --- file cleanup ---

def cleanup_old_files(directory, patterns, keep_count):
    if keep_count <= 0:
        return 0
    total_deleted = 0
    directory = Path(directory)
    for pattern in patterns:
        files_with_ts = []
        for fp in directory.glob(pattern):
            try:
                parts = fp.stem.split("_")
                if len(parts) >= 3:
                    ts_str = f"{parts[-2]}_{parts[-1]}"
                    ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
                    files_with_ts.append((fp, ts))
            except (ValueError, IndexError):
                continue
        files_with_ts.sort(key=lambda x: x[1], reverse=True)
        for fp, _ in files_with_ts[keep_count:]:
            try:
                fp.unlink()
                total_deleted += 1
            except Exception:
                continue
    return total_deleted


# --- output ---

def ensure_output_dir(path):
    d = Path(path)
    d.mkdir(exist_ok=True)
    return d


# --- run wrapper ---

def run_monitor(cfg, work_fn):
    log = setup_logging(cfg)
    start_time = datetime.now()

    log.info("=" * 60)
    log.info(f"{cfg['monitor_name']} started at {start_time}")
    log.info("=" * 60)

    state = load_state(cfg["state_file"])
    session = create_session(cfg)
    output_dir = ensure_output_dir(cfg["data_directory"]) if cfg.get("data_directory") else None

    new_state = work_fn(cfg, state, session, output_dir, log)

    if new_state:
        new_state["last_run"] = start_time.isoformat()
        save_state(cfg["state_file"], new_state)

    if output_dir and cfg.get("cleanup_patterns"):
        cleanup_old_files(output_dir, cfg["cleanup_patterns"], cfg.get("keep_files", 2))

    elapsed = datetime.now() - start_time
    log.info("=" * 60)
    log.info(f"Completed in {elapsed.total_seconds():.2f}s")
    log.info("=" * 60)


# --- google sheets push ---

def push_to_google_sheets(rows, cfg, log):
    creds_file = cfg.get("csv_credentials_file", "credentials.json")
    spreadsheet_id = cfg.get("csv_spreadsheet_id")
    sheet_name = cfg.get("csv_sheet_name", "importXML")

    if not spreadsheet_id:
        log.error("csv_spreadsheet_id not set in config")
        return False

    credentials = service_account.Credentials.from_service_account_file(
        creds_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    svc = build("sheets", "v4", credentials=credentials)

    svc.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'",
    ).execute()

    svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"'{sheet_name}'!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()

    log.info(f"Wrote {len(rows)} rows to {sheet_name}")
    return True


# --- work function ---

def csv_download_work(cfg, state, session, output_dir, log):
    file_url = cfg.get("csv_file_url")
    filename = cfg.get("csv_filename", os.path.basename(file_url))

    log.info(f"Downloading {filename}")
    tmp_path = os.path.join(tempfile.gettempdir(), filename)

    timeout = cfg.get("request_timeout", 120)
    result = subprocess.run(
        ["curl", "-sL", "--max-time", str(timeout), "-o", tmp_path, file_url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr.strip()}")
    log.info(f"Downloaded to {tmp_path}")

    with open(tmp_path, "r", encoding=cfg.get("csv_encoding", "utf-8")) as f:
        reader = csv.reader(f)
        rows = list(reader)
    log.info(f"Parsed {len(rows)} rows")

    os.remove(tmp_path)

    push_to_google_sheets(rows, cfg, log)

    return {
        "rows_pushed": len(rows),
        "filename": filename,
    }


# --- main ---

def main():
    cfg = load_config()
    try:
        run_monitor(cfg, csv_download_work)
    except KeyboardInterrupt:
        print("Interrupted")
    except Exception as e:
        logging.getLogger(__name__).exception(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
