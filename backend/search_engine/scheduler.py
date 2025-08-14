import sys
import platform
import subprocess
from pathlib import Path

# ===== USER CONFIGURATION =====
python_file1 = "crawler.py"
python_file2 = "indexer.py"
day_of_week = "1"  # Monday = 1, Sunday = 0 for cron; Windows uses MON, TUE, etc.
time_of_day = "09:00"  # 24-hour format HH:MM
# ==============================

python_executable = sys.executable
system_type = platform.system()

def setup_cron():
    """Setup cron job for macOS/Linux"""
    cron_command = f"{python_executable} {python_file1} && {python_executable} {python_file2}"
    cron_time = f"0 9 * * {day_of_week}"  # Runs at 09:00 on chosen day
    cron_job = f"{cron_time} {cron_command}\n"

    try:
        # Get existing crontab
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing_cron = result.stdout if result.returncode == 0 else ""

        if cron_job.strip() in existing_cron:
            print("✅ Cron job already exists.")
            return

        new_cron = existing_cron + cron_job
        proc = subprocess.run(["crontab", "-"], input=new_cron, text=True)
        if proc.returncode == 0:
            print("✅ Cron job added successfully.")
        else:
            print("❌ Failed to add cron job.")

    except Exception as e:
        print(f"Error setting up cron: {e}")

def setup_windows_task():
    """Setup Windows scheduled task"""
    days_map = {
        "0": "SUN", "1": "MON", "2": "TUE", "3": "WED", "4": "THU", "5": "FRI", "6": "SAT"
    }
    day_str = days_map.get(day_of_week, "MON")
    task_name = "WeeklyPythonScripts"

    cmd = [
        "schtasks", "/Create",
        "/SC", "WEEKLY",
        "/D", day_str,
        "/TN", task_name,
        "/TR", f'"{python_executable}" "{python_file1}" && "{python_executable}" "{python_file2}"',
        "/ST", time_of_day
    ]

    try:
        subprocess.run(cmd, check=True)
        print("✅ Windows scheduled task created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create task: {e}")

if __name__ == "__main__":
    if not Path(python_file1).exists() or not Path(python_file2).exists():
        print("❌ One or both Python file paths are invalid.")
        sys.exit(1)

    if system_type in ["Darwin", "Linux"]:
        setup_cron()
    elif system_type == "Windows":
        setup_windows_task()
    else:
        print(f"❌ Unsupported OS: {system_type}")
