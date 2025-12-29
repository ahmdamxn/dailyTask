from __future__ import annotations
import os
import yaml
from flask import Flask, render_template

from tools.git_tools import get_recent_commits, get_changed_files_since, get_diff_text_since
from tools.alarm_tools import compile_patterns, extract_alarm_hits
from tools.planner import plan_tests

APP = Flask(__name__)

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

@APP.route("/")
def index():
    config = load_yaml("config.yaml")
    repo_path = config.get("repo_path", ".")
    max_commits = int(config.get("max_commits", 30))

    # Simple rev range (last N commits). You can change this logic later to "since yesterday", tag, etc.
    rev_range = f"HEAD~{min(10, max_commits)}..HEAD"

    tasks = load_yaml(os.path.join("data", "tasks.yaml")) or []
    commits = get_recent_commits(repo_path, max_commits=max_commits)
    files = get_changed_files_since(repo_path, rev_range=rev_range)

    diff_text = get_diff_text_since(repo_path, rev_range=rev_range)
    patterns = compile_patterns(config.get("alarm_patterns", []))
    alarm_hits = extract_alarm_hits(diff_text, patterns)

    planned = plan_tests(tasks, files)[:15]  # top 15

    return render_template(
        "index.html",
        repo_path=os.path.abspath(repo_path),
        rev_range=rev_range,
        commits=commits,
        files=files,
        alarm_hits=alarm_hits,
        planned=planned,
    )

if __name__ == "__main__":
    APP.run(host="127.0.0.1", port=5000, debug=True)
