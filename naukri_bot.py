from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import imaplib
import email
import re
import os
import time

# ── Environment Variables (from GitHub Secrets) ───────────────────────────────
EMAIL = os.environ["NAUKRI_EMAIL"]
PASSWORD = os.environ["NAUKRI_PASSWORD"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

RESUME_PATH = os.path.abspath("vignesh_resume.pdf")

# ── STEP PRINT HELPER ─────────────────────────────────────────────────────────
def step(n, msg):
    print("\n" + "="*50)
    print(f"STEP {n}: {msg}")
    print("="*50)

# ── OTP FETCHER ───────────────────────────────────────────────────────────────
def fetch_otp():

    for i in range(6):

        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(EMAIL, GMAIL_APP_PASSWORD)
            mail.select("inbox")

            status, messages = mail.search(None, '(FROM "naukri")')

            if status == "OK":

                email_ids = messages[0].split()

                for eid in reversed(email_ids[-3:]):

                    status2, msg_data = mail.fetch(eid, "(RFC822)")
                    raw_email = msg_data[0][1]

                    msg = email.message_from_bytes(raw_email)

                    body = ""

                    if msg.is_multipart():

                        for part in msg.walk():

                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:

                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    otp = re.search(r"\b(\d{6})\b", body)

                    if otp:
                        print("OTP FOUND:", otp.group(1))
                        mail.logout()
                        return otp.group(1)

            mail.logout()

        except Exception as e:
            print("GMAIL ERROR:", e)

        time.sleep(10)

    return None


# ── CHROME SETUP ──────────────────────────────────────────────────────────────
step(0, "Starting Browser")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, 40)

try:

    # ── STEP 1 LOGIN PAGE ─────────────────────────────────────────────
    step(1, "Open Login Page")

    driver.get("https://www.naukri.com/nlogin/login")

    email_box = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Enter Email ID / Username']")
        )
    )

    email_box.send_keys(EMAIL)

    password_box = driver.find_element(
        By.XPATH, "//input[@placeholder='Enter Password']"
    )

    password_box.send_keys(PASSWORD)

    driver.find_element(By.XPATH, "//button[text()='Login']").click()

    time.sleep(10)

    # ── STEP 2 OTP CHECK ──────────────────────────────────────────────
    step(2, "Checking OTP")

    otp_inputs = driver.find_elements(By.XPATH, "//input[@type='tel']")

    if otp_inputs:

        print("OTP detected")

        time.sleep(15)

        otp = fetch_otp()

        if not otp:
            raise Exception("OTP not received")

        otp_inputs = driver.find_elements(By.XPATH, "//input[@type='tel']")

        if len(otp_inputs) >= 6:

            for i, digit in enumerate(otp[:6]):
                otp_inputs[i].send_keys(digit)

        else:
            otp_inputs[0].send_keys(otp)

        verify = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Verify']"))
        )

        verify.click()

        time.sleep(8)

    # ── STEP 3 PROFILE PAGE ───────────────────────────────────────────
    step(3, "Open Profile")

    driver.get("https://www.naukri.com/mnjuser/profile")

    time.sleep(8)

    # ── STEP 4 CLOSE POPUP ────────────────────────────────────────────
    try:

        close = driver.find_element(
            By.XPATH,
            "//*[contains(@class,'crossIcon') or contains(@class,'close')]"
        )

        close.click()

        time.sleep(2)

    except:
        pass

    # ── STEP 5 FIND FILE INPUT ────────────────────────────────────────
    step(4, "Uploading Resume")

    driver.execute_script("window.scrollTo(0,600);")

    file_input = driver.find_element(By.XPATH, "//input[@type='file']")

    driver.execute_script(
        "arguments[0].style.display='block'; arguments[0].style.visibility='visible';",
        file_input
    )

    file_input.send_keys(RESUME_PATH)

    time.sleep(6)

    print("Resume uploaded")

    # ── STEP 6 LOGOUT ─────────────────────────────────────────────────
    step(5, "Logout")

    driver.get("https://www.naukri.com/nlogin/logout")

    time.sleep(3)

    print("Logout success")

    print("\nAUTOMATION COMPLETE")

finally:

    driver.quit()
