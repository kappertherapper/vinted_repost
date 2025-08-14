# Vinted Repost Script v.0.1

This script automates the process of retrieving information about listings on Vinted.

⚠️ **Note:** Using automation tools may violate Vinted's rules. Use this script at your own risk.

---

## Features

- Logs into Vinted via a browser (manual login required).  
- Navigates to your profile and finds the latest active listing.  
- Retrieves the title, price, description, details, and images of the listing.  
- Downloads images to a local `images` folder.  
- Saves listing data to a `vinted_data.json` file.  
- Can delete the latest listing (optional).  

---

## Requirements

- Python 3.10+  
- [Selenium](https://pypi.org/project/selenium/)  
- [undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/)  
- [Requests](https://pypi.org/project/requests/)  

Install the dependencies via pip:

```bash
pip install selenium undetected-chromedriver requests