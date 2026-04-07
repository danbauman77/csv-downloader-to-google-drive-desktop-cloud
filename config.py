# Config / Algebra

DEFAULTS = {
    # --- Identity ---
    "monitor_name": "",

    # --- Paths ---
    "data_directory": "data",
    "state_file": "state.json",
    "config_file": "config.json",
    "log_file": "",
    # "baseline_file": "",

    # --- File Cleanup ---
    "keep_files": 2,
    "cleanup_patterns": [],

    # --- HTTP ---
    "user_agent": "Monitor/1.0",
    "request_timeout": 30,
    "request_delay": 1.0,

    # --- Email / SMTP ---
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "",
    "sender_password": "",
    "recipient_emails": [],
    "email_subject_prefix": "",

    # --- unused other parameters ---
    # "tophat_base_url": "https://www.askebsa.dol.gov/tophatplansearch/Home/Search",
    # "tophat_records_per_page": 100,
    # "tophat_propublica_delay": 0.5,
    # "tophat_reference_file": "",
    # "reginfo_rins": [],
    # "reginfo_agenda_url": "https://www.reginfo.gov/public/do/eAgendaXmlReport",
    # "trademark_api_key": "",
    # "trademark_batch_size": 20,
    # "trademark_max_empty_batches": 3,
    # "trademark_max_results_per_email": 100,
    # "trademark_rate_limit_delay": None,
    # "trademark_filters": {},
    # "scheduler_enabled": False,
    # "scheduler_run_times": [],
    # "scheduler_run_on_start": False,

    # --- CSV Downloader ---
    "csv_file_url": "",
    "csv_filename": "",
    "csv_credentials_file": "credentials.json",
    "csv_spreadsheet_id": "",
    "csv_sheet_name": "importXML",
    "csv_encoding": "utf-8",
}


def load_config(config_file="config.json"):
    import json, os, re
    cfg = dict(DEFAULTS)
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            raw = f.read()
        stripped = re.sub(r'^\s*//.*$', '', raw, flags=re.MULTILINE)
        user = json.loads(stripped)
        for k, v in user.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k] = {**cfg[k], **v}
            else:
                cfg[k] = v
    return cfg
