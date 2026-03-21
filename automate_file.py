import pandas as pd
import os
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager


# ---------------- CONFIG ----------------

sheet_url = "https://docs.google.com/spreadsheets/d/1WRJF00nDqDroXi70T4PO4qqipuancUvKO2zyoVdPyhQ/export?format=csv"
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfX5zOmuBRtYlZM_FSVH2-vrTJjShX8XOIWt-cN81-P5sWDsA/viewform"

PROFILE_PATH = "/home/amartya-mandal/selenium-profile"
IMAGE_DIR = "./images"


# ---------------- LOAD DATA ----------------

print("Loading sheet...")
df = pd.read_csv(sheet_url, engine="python")

df = df.fillna("").astype(str)
for col in df.columns:
    df[col] = df[col].str.strip()

df["Date of Activity"] = pd.to_datetime(
    df["Date of Activity"], errors="coerce"
).dt.strftime("%m/%d/%Y")

print(df.head())


# ---------------- LOAD IMAGES ----------------

images = sorted(
    [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)
     if f.lower().endswith((".png", ".jpg", ".jpeg"))],
    key=os.path.getmtime
)

def get_images_for_row(i):
    idx = i * 2
    if idx + 1 < len(images):
        return images[idx], images[idx + 1]
    return None, None


# ---------------- BROWSER ----------------

options = Options()
options.add_argument("--start-maximized")
options.add_argument(f"--user-data-dir={PROFILE_PATH}")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 25)


# ---------------- HELPERS ----------------

def retry(func, attempts=3):
    for i in range(attempts):
        try:
            return func()
        except Exception as e:
            print(f"Retry {i+1} failed: {e}")
            time.sleep(2)
    raise Exception("Max retries reached")


def fill_text(label, value):
    def action():
        field = wait.until(EC.presence_of_element_located((
            By.XPATH,
            f"//div[contains(.,'{label}')]/ancestor::div[@role='listitem']//input"
        )))
        field.clear()
        field.send_keys(value)
    retry(action)


# ---------------- DROPDOWN (FINAL FIX) ----------------

def select_dropdown(label, value):
    print(f"Selecting {label}: {value}")

    actions = ActionChains(driver)

    # 1️⃣ Find the correct question block
    question = wait.until(EC.presence_of_element_located((
        By.XPATH,
        f"//div[@role='listitem'][.//text()[contains(.,'{label}')]]"
    )))

    # 2️⃣ Find dropdown INSIDE that question (🔥 FIX)
    dropdown = question.find_element(By.XPATH, ".//div[@role='listbox']")

    # 3️⃣ Click dropdown
    actions.move_to_element(dropdown).click().perform()
    time.sleep(1)

    # 4️⃣ Wait for visible options
    options = wait.until(EC.presence_of_all_elements_located((
        By.XPATH, "//div[@role='option' and not(@aria-hidden='true')]"
    )))

    print(f"Options found: {len(options)}")

    # 5️⃣ Select correct option
    for opt in options:
        data_val = opt.get_attribute("data-value")

        print("Option:", data_val)

        if data_val and data_val.strip().lower() == str(value).strip().lower():
            actions.move_to_element(opt).click().perform()
            print(f"✅ Selected: {data_val}")
            time.sleep(1)
            return

    raise Exception(f"❌ Value '{value}' not found in {label}")


# ---------------- BUTTONS ----------------

def click_next():
    btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//span[contains(text(),'Next')]"
    )))
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(2)


# ---------------- FILE UPLOAD ----------------

def upload_file(label, file_path):
    try:
        add_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            f"//div[contains(.,'{label}')]/ancestor::div[@role='listitem']//span[contains(text(),'Add file')]"
        )))
        add_btn.click()

        time.sleep(3)

        wait.until(EC.frame_to_be_available_and_switch_to_it(
            (By.XPATH, "//iframe[contains(@src,'picker')]")
        ))

        file_input = wait.until(EC.presence_of_element_located((
            By.XPATH, "//input[@type='file']"
        )))
        file_input.send_keys(os.path.abspath(file_path))

        time.sleep(10)

        driver.switch_to.default_content()
        time.sleep(3)

        print(f"Uploaded {label}")

    except Exception as e:
        print(f"Upload failed: {e}")
        driver.switch_to.default_content()


# ---------------- PAGES ----------------

def fill_page_1(row):
    fill_text("Name", row["Name"])
    fill_text("Phone Number", row["Phone Number"])

    select_dropdown("Distributor Name", row["Distributor Name"])
    time.sleep(1)

    select_dropdown("Category", row["Category"])
    time.sleep(1)

    select_dropdown("District", row["District"])

    click_next()


def fill_page_2(row, i):
    fill_text("Date of Activity", row["Date of Activity"])

    select_dropdown("Place of Activity", row["Place of Activity"])
    time.sleep(1)

    fill_text("Consumer Name", row["Consumer Name"])
    fill_text("Consumer Mobile Number", row["Consumer Mobile Number"])
    fill_text("Dealer Name", row["Dealer Name"])
    fill_text("Dealer Code", row["Dealer Code"])

    fill_text("No. of Consumers Attended", row["No. of Consumers Attended"])
    fill_text("Name of Any One Consumer", row["Name of Any One Consumer"])
    fill_text("Mobile Number of Any One Consumer", row["Mobile Number of Any One Consumer"])

    fill_text("No. of Masons Attended", row["No. of Masons Attended"])
    fill_text("No. of Engineers Attended", row["No. of Engineers Attended"])
    fill_text("No. of Dealers Attended", row["No. of Dealers Attended"])

    select_dropdown("Ring Test Conducted", row["Ring Test Conducted"])
    time.sleep(1)

    select_dropdown("Weighment Test Conducted", row["Weighment Test Conducted"])

    img1, img2 = get_images_for_row(i)

    if img1:
        upload_file("Ring Test Photo", img1)

    if img2:
        upload_file("Weighment Test Photo", img2)


# ---------------- MANUAL SUBMIT ----------------

def wait_for_manual_submit():
    input("👉 Press ENTER after clicking Submit...")

    wait.until(EC.presence_of_element_located((
        By.XPATH, "//*[contains(text(),'response has been recorded')]"
    )))

    print("✅ Submission confirmed!")
    time.sleep(2)

s


# ---------------- MAIN LOOP ----------------

for i, row in df.iterrows():

    print(f"\nProcessing row {i+1}")

    try:
        driver.get(form_url)
        time.sleep(3)

        fill_page_1(row)
        fill_page_2(row, i)

        wait_for_manual_submit()

    except Exception as e:
        print(f"Error in row {i+1}")
        traceback.print_exc()
        driver.save_screenshot(f"error_{i+1}.png")
        continue


driver.quit()
print("🎉 DONE")