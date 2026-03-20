import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


# -------- CONFIG --------

sheet_url = "https://docs.google.com/spreadsheets/d/1lOtw0uB8HQ-ItYbyvA-U_d59heb1FGDUp4TY6rmQNzY/export?format=csv"
form_url = "https://docs.google.com/forms/d/e/1FAIpQLSeKILHgJaj9ZDUCj5OCywjDUHBmi7Af85gVyUbV6-Sj8oZpQQ/viewform"


# -------- LOAD DATA --------

df = pd.read_csv(sheet_url)

# Clean data
df["Name"] = df["Name"].astype(str).str.strip()
df["Location"] = df["Location"].astype(str).str.strip()
df["Agree"] = df["Agree"].astype(str).str.strip()

print(df[["Name", "Location", "Agree"]].head())


# -------- BROWSER --------

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 20)


# -------- FUNCTIONS --------

def fill_name(name):
    field = wait.until(EC.presence_of_element_located((
        By.XPATH,
        "//div[contains(.,'Name')]/ancestor::div[@role='listitem']//input"
    )))
    field.send_keys(name)


def select_location(location):
    print(f"Selecting Location: {location}")

    # 1️⃣ Open dropdown
    dropdown = wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[@role='listbox']"
    )))
    dropdown.click()

    # 2️⃣ Wait for visible options (IMPORTANT)
    options = wait.until(EC.visibility_of_all_elements_located((
        By.XPATH, "//div[@role='option']"
    )))

    print(f"Found {len(options)} options")

    # 3️⃣ Loop and match
    for opt in options:
        text = opt.text.strip()
        print("Option:", text)

        if text.lower() == location.lower():
            # 🔥 FORCE CLICK (most important fix)
            driver.execute_script("arguments[0].click();", opt)
            print(f"✅ Selected: {text}")
            return

    raise Exception(f"❌ Location '{location}' not found")

def click_next():
    next_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//span[contains(text(),'Next')]"
    )))
    next_btn.click()
    time.sleep(2)

# ------------------------------------------------------------------------------------------
# def submit_form():
#     print("Submitting form...")

#     # 1️⃣ Wait until overlay disappears (VERY IMPORTANT)
#     wait.until(EC.invisibility_of_element_located((
#         By.XPATH, "//div[contains(@class,'ThHDze')]"
#     )))

#     # 2️⃣ Wait for submit button
#     submit = wait.until(EC.element_to_be_clickable((
#         By.XPATH, "//span[text()='Submit']"
#     )))

#     # 3️⃣ Scroll into view (important)
#     driver.execute_script("arguments[0].scrollIntoView(true);", submit)
#     time.sleep(1)

#     # 4️⃣ Force click (bypass interception)
#     driver.execute_script("arguments[0].click();", submit)

#     print("✅ Form submitted")

# ----------------------------------------------------------------------------------------------

# Multiple Dropdown-----------------------------------------------------------------------------

def select_dropdown_by_index(index, value):
    print(f"Selecting dropdown {index}: {value}")

    actions = ActionChains(driver)

    # 🔁 ALWAYS re-fetch dropdowns (VERY IMPORTANT)
    dropdowns = wait.until(EC.presence_of_all_elements_located((
        By.XPATH, "//div[@role='listbox']"
    )))

    dropdown = dropdowns[index]

    # Click dropdown
    actions.move_to_element(dropdown).click().perform()
    time.sleep(1)

    # Get visible options
    options = wait.until(EC.presence_of_all_elements_located((
        By.XPATH, "//div[@role='option' and not(@aria-hidden='true')]"
    )))

    print(f"Visible options found: {len(options)}")

    for opt in options:
        data_val = opt.get_attribute("data-value")

        print("Option:", data_val)

        if data_val and data_val.strip().lower() == value.strip().lower():
            actions.move_to_element(opt).click().perform()
            print(f"✅ Selected: {data_val}")
            time.sleep(1)  # 🔥 allow DOM to settle
            return

    raise Exception(f"❌ '{value}' not found in dropdown {index}")

# ----------------------------------------------------------------------------------------------





# manual submit then continue to next row
def wait_for_manual_submit():
    print("🖐 Waiting for you to click Submit...")

    # Wait until confirmation page appears
    wait.until(EC.presence_of_element_located((
        By.XPATH, "//*[contains(text(),'Your response has been recorded')]"
    )))

    print("✅ Submission detected. Moving to next row...")
    time.sleep(2)


# -------- MAIN LOOP --------

for i, row in df.iterrows():
    print(f"Processing row {i+1}")

    driver.get(form_url)
    time.sleep(2)

    # Page 1
    fill_name(row["Name"])
    click_next()

    # Page 2
    # select_location(row["Location"])
    # Page 2
    select_dropdown_by_index(0, row["Location"])   # First dropdown
    select_dropdown_by_index(1, row["Agree"])      # Second dropdown

    # submit
    wait_for_manual_submit()
    


driver.quit()
print("Done ✅")