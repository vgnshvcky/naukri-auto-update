from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

EMAIL = "vigneshvcky2000@gmail.com"
PASSWORD = "Vignesh2@"
RESUME_PATH = "vignesh_resume.pdf"

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# Add a real user-agent to avoid bot detection
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
# Mask webdriver property
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

wait = WebDriverWait(driver, 40)

try:
    print("Opening Naukri login page...")
    driver.get("https://www.naukri.com/nlogin/login")

    # Wait for page to fully load
    time.sleep(5)

    print("Waiting for email input...")
    # Try multiple possible selectors
    try:
        email_box = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@placeholder='Enter Email ID / Username']")
            )
        )
    except:
        # Fallback selectors
        try:
            email_box = wait.until(
                EC.visibility_of_element_located((By.ID, "usernameField"))
            )
        except:
            email_box = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//input[@type='text' and contains(@class,'loginField')]")
                )
            )

    print("Waiting for password input...")
    try:
        password_box = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@placeholder='Enter Password']")
            )
        )
    except:
        password_box = wait.until(
            EC.visibility_of_element_located((By.ID, "passwordField"))
        )

    print("Entering credentials...")
    email_box.clear()
    email_box.send_keys(EMAIL)
    time.sleep(1)
    password_box.clear()
    password_box.send_keys(PASSWORD)
    time.sleep(1)

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Login']")
        )
    )
    login_button.click()
    print("Login submitted...")
    time.sleep(12)

    print("Opening profile page...")
    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)

    print("Waiting for resume upload field...")
    upload = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    upload.send_keys(os.path.abspath(RESUME_PATH))
    print("Resume uploaded successfully")
    time.sleep(5)

finally:
    driver.quit()
