from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Credentials (for now directly here)
EMAIL = "vigneshvcky2000@gmail.com"
PASSWORD = "Vignesh2@"

# Resume file
RESUME_PATH = "vignesh_resume.pdf"

# Chrome options for GitHub server (headless mode)
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Start browser
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

try:
    print("Opening Naukri login page...")
    driver.get("https://www.naukri.com/nlogin/login")

    time.sleep(5)

    print("Entering login credentials...")
    driver.find_element(By.ID, "usernameField").send_keys(EMAIL)
    driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)

    driver.find_element(By.XPATH, "//button[text()='Login']").click()

    time.sleep(10)

    print("Navigating to profile page...")
    driver.get("https://www.naukri.com/mnjuser/profile")

    time.sleep(10)

    print("Uploading resume...")
    upload = driver.find_element(By.XPATH, "//input[@type='file']")
    upload.send_keys(os.path.abspath(RESUME_PATH))

    time.sleep(5)

    print("Resume uploaded successfully")

finally:
    driver.quit()
