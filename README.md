# Simple Telegram bot for forwarding messages from Max to Telegram by using Selenium

## Required software:
- Python 3.13 and newer
- chromedriver 111.0.5563.64 and newer

## Installation

### **1. Clone repository**
```
git clone https://github.com/innocencedq/simple-max-to-telegram.git
```

***

### **2. Create a config.env file and fill it with the template**

```
STORAGE_DATA_AUTH=YOUR:__oneme_auth:FROM:LOCAL_STORAGE
STORAGE_DATA_AUTH_CALLS=YOUR:__oneme_calls_auth_token:FROM:LOCAL_STORAGE
TG_TOKEN=YOUR_TELEGRAM_TOKEN:FROM:BOTFATHER
URL=YOUR_URL_TO_DIALOG
CURRENT_DATAINDEX='1'
GROUP_CHAT_ID='YOUR_CHAT_ID_TELEGRAM' # after starting a group or dm, use /whoami and paste the value
DELAY_REQUESTING='10'
STATUS_REQUSTING='active'
```

***

### **3. Download chromedriver**

**For Windows by using python:**
```
pip install undetected-chromedriver
```
**Or from [official site](https://developer.chrome.com/docs/chromedriver/downloads)**

**For Linux:**
```
# Download the latest available Chrome for Testing binary corresponding to the Stable channel.
npx @puppeteer/browsers install chrome@stable

# Download a specific Chrome for Testing version.
npx @puppeteer/browsers install chrome@116.0.5793.0

# Download the latest available ChromeDriver version corresponding to the Canary channel.
npx @puppeteer/browsers install chromedriver@canary

# Download a specific ChromeDriver version.
npx @puppeteer/browsers install chromedriver@116.0.5793.0

```

***

**Move the chromedriver to src/app/util directory**

Linux:
```
cp chromedriver usr/home/simple-max-to-telegram/src/app/util

or

mv chromedriver usr/home/simple-max-to-telegram/src/app/util
```

***

### **4. Install requirements**

**1. Create enviroment:**
```
python -m venv .venv
```

**2. Activate enviroment:**

**For Windows:**
```
cd .venv/Scripts
activate.bat
```

**For Linux:**
```
source .venv/bin/activate
```

**3. Install packages:**
```
pip install -r requirements.txt
```

***

### **5. Run bot:**

**Local:**
```
python run.py
```

**Or by using pm2:**
```
pm2 start run.py --interpreter python3 --name "simple-max-to-telegram-bot"
```





