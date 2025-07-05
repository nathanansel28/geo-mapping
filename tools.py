import subprocess
import os
import sys

def open_html_in_chrome(html_path, chrome_path=None, user_data_dir=None):
    """
    Open an HTML file in Google Chrome using your own user profile.

    Args:
        html_path (str): Path to the HTML file.
        chrome_path (str): Full path to Chrome executable.
        user_data_dir (str): Path to Chrome's user profile directory.

    Raises:
        FileNotFoundError: If the HTML file or Chrome executable is not found.
    """
    if not os.path.isfile(html_path):
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    # Guess Chrome path if not provided
    if chrome_path is None:
        if sys.platform == "win32":
            chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        elif sys.platform == "darwin":
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        else:  # Linux
            chrome_path = "/usr/bin/google-chrome"

    if not os.path.isfile(chrome_path):
        raise FileNotFoundError(f"Chrome executable not found at: {chrome_path}")

    # Default to your main Chrome profile if not provided
    if user_data_dir is None:
        if sys.platform == "win32":
            user_data_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
        elif sys.platform == "darwin":
            user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        else:  # Linux
            user_data_dir = os.path.expanduser("~/.config/google-chrome")

    command = [
        chrome_path,
        f"--user-data-dir={user_data_dir}",
        os.path.abspath(html_path)
    ]

    subprocess.Popen(command)
