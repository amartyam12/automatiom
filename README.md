# 🚀 Google Form Automation using Selenium

This project automates Google Form submission using data from a Google Sheet and uploads images automatically.

---

## 📌 Features

* Reads data from Google Sheets (CSV)
* Fills multi-page Google Forms
* Handles dropdowns dynamically
* Uploads images
* Uses Chrome profile (for login & permissions)
* Retry mechanism for stability

---

## 🧰 Requirements

### Install:

* Python 3.8+
* Google Chrome
* ChromeDriver (IMPORTANT)

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/amartyam12/automatiom.git
cd automatiom
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Linux / Mac**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

---

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🌐 Install ChromeDriver

### Step 1: Check Chrome version

Open Chrome → Settings → About

---

### Step 2: Download matching ChromeDriver

👉 https://chromedriver.chromium.org/downloads

---

### Step 3: Setup path

#### Linux:

```bash
sudo mv chromedriver /usr/local/bin/
```

#### Windows:

Place file in:

```
C:\chromedriver\chromedriver.exe
```

---

## ⚙️ Update Script Configuration

### 🔹 ChromeDriver Path

#### Linux:

```python
Service("/usr/local/bin/chromedriver")
```

#### Windows:

```python
Service("C:\\chromedriver\\chromedriver.exe")
```

---

### 🔹 Chrome Profile (IMPORTANT)

#### Linux:

```python
PROFILE_PATH = "/home/your-username/selenium-profile"
```

#### Windows:

```python
PROFILE_PATH = "C:\\Users\\YourUsername\\selenium-profile"
```

---

## 🧠 Create Chrome Profile (One-time setup)

### Linux:

```bash
google-chrome --user-data-dir=/home/your-username/selenium-profile
```

### Windows:

```bash
chrome.exe --user-data-dir="C:\\Users\\YourUsername\\selenium-profile"
```

👉 Login to your Google account once and close browser.

---

## 📂 Project Structure

```
automatiom/
│── automate_file.py
│── requirements.txt
│── README.md
│── images/
```

---

## ▶️ Run the Script

```bash
python automate_file.py
```

---

## 🖐 Manual Step

* After form is filled, manually click **Submit**
* Script waits for confirmation and continues

---

## ⚠️ Important Notes

* Chrome version must match ChromeDriver
* Internet connection required
* Google login required (handled via profile)

---

## 🛠 Troubleshooting

### ❌ Chrome not opening

✔ Check driver path

---

### ❌ Login issues

✔ Recreate Chrome profile

---

### ❌ Dropdown not selecting

✔ Ensure exact values in sheet

---

### ❌ File upload not working

✔ Ensure Google account has access

---

## 👨‍💻 Author

Amartya Mandal

---

## 🚀 Future Improvements

* Fully automated submit
* Headless execution
* Docker support
* AWS deployment (EC2 + cron)
