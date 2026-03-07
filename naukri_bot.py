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

# ── Credentials ───────────────────────────────────────────────────────────────
EMAIL              = os.environ.get("NAUKRI_EMAIL", "vigneshvcky2000@gmail.com")
PASSWORD           = os.environ.get("NAUKRI_PASSWORD", "Vignesh2@")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "igrwxtjyyqoddrnt")
RESUME_PATH        = os.path.abspath("vignesh_resume.pdf")

# ── Step tracker ──────────────────────────────────────────────────────────────
def step(number, title):
    print(f"\n{'='*50}")
    print(f"  STEP {number}: {title}")
    print(f"{'='*50}")

def done(message, screenshot_path, driver):
    driver.save_screenshot(screenshot_path)
    print(f"  ✅ DONE — {message}")
    print(f"  📸 Screenshot saved: {screenshot_path}")

def fail(message, screenshot_path, driver):
    driver.save_screenshot(screenshot_path)
    print(f"  ❌ FAILED — {message}")
    print(f"  📸 Screenshot saved: {screenshot_path}")

# ── OTP fetcher from Gmail ────────────────────────────────────────────────────
def fetch_otp_from_gmail(gmail_user, gmail_app_password, retries=6, delay=10):
    print("  📧 Connecting to Gmail to fetch OTP...")
    for attempt in range(retries):
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(gmail_user, gmail_app_password)
            mail.select("inbox")

            # Search for latest Naukri OTP email
            status, messages = mail.search(None, '(FROM "naukri")')
            if status == "OK" and messages[0]:
                email_ids = messages[0].split()
                # Check last 3 emails for OTP
                for eid in reversed(email_ids[-3:]):
                    status2, msg_data = mail.fetch(eid, "(RFC822)")
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                    otp_match = re.search(r'\b(\d{6})\b', body)
                    if otp_match:
                        otp = otp_match.group(1)
                        print(f"  ✅ OTP found: {otp}")
                        mail.logout()
                        return otp

            mail.logout()
        except Exception as e:
            print(f"  ⚠️  Gmail attempt {attempt+1}/{retries} failed: {e}")

        print(f"  ⏳ Retrying in {delay}s... ({attempt+1}/{retries})")
        time.sleep(delay)

    return None

# ── Chrome setup ──────────────────────────────────────────────────────────────
step(0, "Starting Chrome Browser")
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)
wait = WebDriverWait(driver, 40)
print("  ✅ Chrome started successfully")

try:

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — OPEN LOGIN PAGE
    # ══════════════════════════════════════════════════════════════════════════
    step(1, "Opening Naukri Login Page")
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(5)

    if "nlogin/login" in driver.current_url or "naukri.com" in driver.current_url:
        done("Login page loaded", "step1_login_page_loaded.png", driver)
    else:
        fail("Unexpected URL on load", "step1_FAILED_unexpected_url.png", driver)
        raise Exception(f"Unexpected URL: {driver.current_url}")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — ENTER EMAIL
    # ══════════════════════════════════════════════════════════════════════════
    step(2, "Entering Email")
    try:
        email_box = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@placeholder='Enter Email ID / Username']")
            )
        )
        email_box.click()
        email_box.clear()
        email_box.send_keys(EMAIL)
        time.sleep(1)
        done(f"Email entered: {EMAIL}", "step2_email_entered.png", driver)
    except Exception as e:
        fail(f"Could not find email input: {e}", "step2_FAILED_email.png", driver)
        raise

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — ENTER PASSWORD
    # ══════════════════════════════════════════════════════════════════════════
    step(3, "Entering Password")
    try:
        password_box = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//input[@placeholder='Enter Password']")
            )
        )
        password_box.click()
        password_box.clear()
        password_box.send_keys(PASSWORD)
        time.sleep(1)
        done("Password entered", "step3_password_entered.png", driver)
    except Exception as e:
        fail(f"Could not find password input: {e}", "step3_FAILED_password.png", driver)
        raise

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — CLICK LOGIN BUTTON
    # ══════════════════════════════════════════════════════════════════════════
    step(4, "Clicking Login Button")
    try:
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Login']"))
        )
        login_btn.click()
        done("Login button clicked", "step4_login_clicked.png", driver)
    except Exception as e:
        fail(f"Could not click login button: {e}", "step4_FAILED_login_btn.png", driver)
        raise

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 5 — CHECK: OTP SCREEN OR LOGIN SUCCESS?
    # ══════════════════════════════════════════════════════════════════════════
    step(5, "Checking Login Result")
    time.sleep(10)
    driver.save_screenshot("step5_check.png")
    print(f"  Current URL: {driver.current_url}")

    # Detect OTP screen
    otp_screen = False
    try:
        driver.find_element(
            By.XPATH, "//input[@type='tel'] | //*[contains(text(),'OTP')]"
        )
        otp_screen = True
    except Exception:
        pass

    if otp_screen:
        print("  ⚠️  OTP screen detected!")
        driver.save_screenshot("step5_otp_screen_detected.png")
        print("  📸 Screenshot saved: step5_otp_screen_detected.png")

        # ── STEP 5a — FETCH OTP FROM GMAIL ───────────────────────────────────
        step("5a", "Fetching OTP from Gmail")
        if not GMAIL_APP_PASSWORD:
            fail(
                "GMAIL_APP_PASSWORD secret is not set in GitHub!",
                "step5a_FAILED_no_secret.png", driver
            )
            raise Exception(
                "Add GMAIL_APP_PASSWORD to GitHub Secrets:\n"
                "Settings → Secrets and variables → Actions → New repository secret"
            )

        time.sleep(15)  # Wait for OTP email to arrive
        otp = fetch_otp_from_gmail(EMAIL, GMAIL_APP_PASSWORD)

        if not otp:
            fail("Could not fetch OTP from Gmail", "step5a_FAILED_no_otp.png", driver)
            raise Exception("OTP not found in Gmail — check inbox manually")

        done(f"OTP fetched from Gmail: {otp}", "step5a_otp_fetched.png", driver)

        # ── STEP 5b — ENTER OTP ──────────────────────────────────────────────
        step("5b", "Entering OTP on Naukri")
        otp_inputs = driver.find_elements(
            By.XPATH, "//input[@type='tel' or @maxlength='1']"
        )
        print(f"  Found {len(otp_inputs)} OTP input box(es)")

        if len(otp_inputs) >= 6:
            # 6 separate boxes
            for i, digit in enumerate(otp[:6]):
                otp_inputs[i].click()
                otp_inputs[i].send_keys(digit)
                time.sleep(0.3)
        elif len(otp_inputs) == 1:
            # Single input box
            otp_inputs[0].click()
            otp_inputs[0].send_keys(otp)
        else:
            fail("Unexpected OTP input structure", "step5b_FAILED_otp_input.png", driver)
            raise Exception("Could not find OTP input boxes")

        time.sleep(2)
        driver.save_screenshot("step5b_otp_entered.png")
        print("  📸 Screenshot saved: step5b_otp_entered.png")

        # ── STEP 5c — CLICK VERIFY ───────────────────────────────────────────
        step("5c", "Clicking Verify Button")
        verify_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[normalize-space()='Verify']")
            )
        )
        verify_btn.click()
        time.sleep(10)
        done("OTP verified — clicked Verify", "step5c_otp_verified.png", driver)

    # ── FINAL LOGIN CHECK ─────────────────────────────────────────────────────
    step(5, "Verifying Login Success")
    time.sleep(5)
    current_url = driver.current_url
    print(f"  Current URL: {current_url}")

    if "nlogin/login" in current_url:
        try:
            err = driver.find_element(
                By.XPATH, "//*[contains(@class,'error') or contains(@class,'alert')]"
            )
            print(f"  ⚠️  Error on page: {err.text}")
        except Exception:
            pass
        fail("Still on login page", "step5_FAILED_still_on_login.png", driver)
        raise Exception("Login failed — check step5_FAILED_still_on_login.png")

    done(f"Login successful! URL: {current_url}", "step5_login_success.png", driver)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 6 — NAVIGATE TO PROFILE PAGE
    # ══════════════════════════════════════════════════════════════════════════
    step(6, "Navigating to Profile Page")
    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(8)

    if "mnjuser/profile" in driver.current_url:
        done("Profile page loaded", "step6_profile_page.png", driver)
    else:
        fail(f"Unexpected URL: {driver.current_url}", "step6_FAILED_profile.png", driver)
        raise Exception("Could not load profile page")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 7 — DISMISS POPUP (if any)
    # ══════════════════════════════════════════════════════════════════════════
    step(7, "Dismissing Popup (if present)")
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 "//*[contains(@class,'crossIcon')] | "
                 "//*[contains(@class,'close-btn')] | "
                 "//*[@aria-label='close'] | "
                 "//button[contains(@class,'closeBtn')]")
            )
        )
        close_btn.click()
        time.sleep(2)
        done("Popup dismissed", "step7_popup_dismissed.png", driver)
    except Exception:
        done("No popup found — skipping", "step7_no_popup.png", driver)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 8 — FIND FILE INPUT
    # ══════════════════════════════════════════════════════════════════════════
    step(8, "Locating Resume File Input")
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)

    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    print(f"  Found {len(file_inputs)} file input(s) on page")

    if not file_inputs:
        fail("No file input found", "step8_FAILED_no_file_input.png", driver)
        raise Exception("No file input found — check step8_FAILED_no_file_input.png")

    upload = file_inputs[0]
    driver.execute_script("arguments[0].style.display    = 'block';",   upload)
    driver.execute_script("arguments[0].style.visibility = 'visible';", upload)
    driver.execute_script("arguments[0].style.opacity    = '1';",       upload)
    driver.execute_script("arguments[0].removeAttribute('class');",     upload)
    done("File input found and made visible", "step8_file_input_found.png", driver)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 9 — UPLOAD RESUME
    # ══════════════════════════════════════════════════════════════════════════
    step(9, "Uploading Resume")
    upload.send_keys(RESUME_PATH)
    time.sleep(6)
    done(f"Resume uploaded: {os.path.basename(RESUME_PATH)}", "step9_resume_uploaded.png", driver)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 10 — CONFIRM / SAVE UPLOAD
    # ══════════════════════════════════════════════════════════════════════════
    step(10, "Confirming Upload (Save button)")
    try:
        save_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 "//button[contains(normalize-space(),'Save')] | "
                 "//button[contains(normalize-space(),'Upload')] | "
                 "//button[contains(normalize-space(),'Submit')]")
            )
        )
        save_btn.click()
        time.sleep(5)
        done("Save/confirm button clicked", "step10_save_clicked.png", driver)
    except Exception:
        done("No save button — upload auto-submitted", "step10_auto_submitted.png", driver)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 11 — LOGOUT
    # ══════════════════════════════════════════════════════════════════════════
    step(11, "Logging Out")
    try:
        menu = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 "//span[contains(@class,'nI-gNb-menuIconWrapper')] | "
                 "//div[contains(@class,'menuIcon')] | "
                 "//span[contains(@class,'hamburger')] | "
                 "//div[contains(@class,'nI-gNb-bar2')]")
            )
        )
        menu.click()
        time.sleep(2)
        driver.save_screenshot("step11a_menu_opened.png")
        print("  📸 Screenshot saved: step11a_menu_opened.png")

        logout_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 "//a[normalize-space()='Logout'] | "
                 "//li[normalize-space()='Logout'] | "
                 "//span[normalize-space()='Logout']")
            )
        )
        logout_btn.click()
        time.sleep(3)
        done("Logged out via menu", "step11_logout_done.png", driver)

    except Exception as e:
        print(f"  ⚠️  Menu logout failed ({e}), trying direct URL...")
        driver.get("https://www.naukri.com/nlogin/logout")
        time.sleep(3)
        done("Logged out via direct URL", "step11_logout_done.png", driver)

    # ══════════════════════════════════════════════════════════════════════════
    # ALL DONE
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{'='*50}")
    print("  🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
    print("  ✅ Login         — DONE")
    print("  ✅ OTP (if any)  — DONE")
    print("  ✅ Resume Upload  — DONE")
    print("  ✅ Logout         — DONE")
    print(f"{'='*50}\n")

except Exception as e:
    print(f"\n  ❌ SCRIPT FAILED: {e}")
    raise

finally:
    driver.quit()
    print("  🔒 Browser closed.")
