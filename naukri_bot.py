from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

EMAIL = "vigneshvcky2000@gmail.com"
PASSWORD = "Vignesh2@"
RESUME_PATH = "vignesh_resume.pdf"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    driver.get("https://www.naukri.com/nlogin/login")

    time.sleep(5)

    driver.find_element(By.ID,"usernameField").send_keys(EMAIL)
    driver.find_element(By.ID,"passwordField").send_keys(PASSWORD)

    driver.find_element(By.XPATH,"//button[text()='Login']").click()

    time.sleep(10)

    driver.get("https://www.naukri.com/mnjuser/profile")

    time.sleep(10)

    upload = driver.find_element(By.XPATH,"//input[@type='file']")
    upload.send_keys(os.path.abspath(RESUME_PATH))

    time.sleep(5)

    print("Resume uploaded successfully")

finally:
    driver.quit()