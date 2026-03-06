from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

EMAIL = "vigneshvcky2000@gmail.com"
PASSWORD = "Vignesh2@"
RESUME_PATH = "vignesh_resume.pdf"

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

wait = WebDriverWait(driver, 20)

try:
    print("Opening Naukri login page...")
    driver.get("https://www.naukri.com/nlogin/login")

    print("Waiting for login fields...")

    email_box = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email']"))
    )

    password_box = driver.find_element(By.XPATH, "//input[@type='password']")

    print("Entering credentials...")
    email_box.send_keys(EMAIL)
    password_box.send_keys(PASSWORD)

    login_button = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
    login_button.click()

    print("Login submitted...")
    time.sleep(10)

    print("Opening profile page...")
    driver.get("https://www.naukri.com/mnjuser/profile")

    print("Waiting for upload element...")
    upload = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )

    upload.send_keys(os.path.abspath(RESUME_PATH))

    print("Resume uploaded successfully")
    time.sleep(5)

finally:
    driver.quit()
