import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager


# -------- CONFIG --------

sheet_url = "https://docs.google.com/spreadsheets/d/1BiOnjOKH8wBLYQkvg6yq6BaJVW_4KAaDE5rIxZ2oZX4/export?format=csv"
form_url = "https://docs.google.com/forms/d/e/1FAIpQLScYx9xIdKuV0VSin3tLX53rMtYxCStq53jjJcJ1GffSZuywRw/viewform"


# -------- LOAD DATA --------

df = pd.read_csv(sheet_url)

# Clean data
df["Name"] = df["Name"].astype(str).str.strip()
df["Image1"] = df["Image1"].astype(str).str.strip()
df["Image2"] = df["Image2"].astype(str).str.strip()

print(df[["Name", "Image1", "Image2"]].head())


# -------- BROWSER --------

options = Options()
options.add_argument("--start-maximized")

# 🔥 IMPORTANT: Keeps you logged into Google
options.add_argument("--user-data-dir=/home/amartya-mandal/.config/google-chrome")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 30)


# -------- FUNCTIONS --------

def fill_name(name):
    field = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//div[contains(.,'Name')]/ancestor::div[@role='listitem']//input"
    )))
    field.send_keys(name)


def click_next():
    next_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//span[contains(text(),'Next')]"
    )))
    next_btn.click()
    time.sleep(2)


# -------- FILE UPLOAD FUNCTION --------

def upload_file_by_index(index, file_path):
    print(f"Uploading file {index}: {file_path}")

    # Wait for file inputs
    file_inputs = wait.until(EC.presence_of_all_elements_located((
        By.XPATH, "//input[@type='file']"
    )))

    if index >= len(file_inputs):
        raise Exception(f"❌ File input index {index} not found")

    file_input = file_inputs[index]

    # 🔥 Upload file directly
    file_input.send_keys(file_path)

    print(f"✅ Uploaded: {file_path}")

    # Wait for upload to finish (important for Google Forms)
    time.sleep(5)


# -------- WAIT FOR MANUAL SUBMIT --------

def wait_for_manual_submit():
    print("🖐 Waiting for you to click Submit...")

    wait.until(EC.presence_of_element_located((
        By.XPATH, "//*[contains(text(),'Your response has been recorded')]"
    )))

    print("✅ Submission detected. Moving to next row...")
    time.sleep(2)


# -------- MAIN LOOP --------

for i, row in df.iterrows():
    print(f"\n🚀 Processing row {i+1}")

    driver.get(form_url)
    time.sleep(3)

    # 🔥 If login required → do it once manually
    if "accounts.google.com" in driver.current_url:
        print("🔐 Please login to Google manually...")
        input("Press ENTER after login...")

    # -------- Page 1 --------
    fill_name(row["Name"])
    click_next()

    # -------- Page 2 (Upload Images) --------
    upload_file_by_index(0, row["Image1"])  # First upload
    upload_file_by_index(1, row["Image2"])  # Second upload

    # -------- Submit manually --------
    wait_for_manual_submit()


driver.quit()
print("✅ Done")