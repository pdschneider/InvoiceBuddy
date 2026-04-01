import requests


def download_check():
   """Checks to see number of downloads."""
   repo = "pdschneider/InvoiceBuddy"
   url = f"https://api.github.com/repos/{repo}/releases"
   headers = {"Accept": "application/vnd.github+json"}

   try:
      # Query github for the version
      response = requests.get(url, headers=headers, timeout=10)
   except Exception as e:
      print(f"{e}")

   # Gracefully exit if status code is not 200
   if response.status_code != 200:
      print(
            f"Unable to fetch latest version | Status Code: {response.status_code}")
      return

   # Parse just the version number from data
   data = response.json()

   for entry in data:
      for asset in entry["assets"]:
         print(asset["name"])
         print(asset["download_count"])

download_check()
