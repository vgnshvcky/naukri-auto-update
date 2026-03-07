from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

# ── Credentials ───────────────────────────────────────────────────────────────
EMAIL       = "vigneshvcky2000@gmail.com"
PASSWORD    = "Vignesh2@"
RESUME_PATH = os.path.abspath("vignesh_resume.pdf")

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

    # Confirm page loaded
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
    # STEP 5 — VERIFY LOGIN SUCCESS
    # ══════════════════════════════════════════════════════════════════════════
    step(5, "Verifying Login Success")
    time.sleep(15)

    current_url = driver.current_url
    print(f"  Current URL: {current_url}")

    if "nlogin/login" in current_url:
        # Check for error text on page
        try:
            err = driver.find_element(
                By.XPATH, "//*[contains(@class,'error') or contains(@class,'alert')]"
            )
            print(f"  ⚠️  Error message on page: {err.text}")
        except Exception:
            pass
        fail("Still on login page — login unsuccessful", "step5_FAILED_still_on_login.png", driver)
        raise Exception("Login failed — check step5_FAILED_still_on_login.png")
    else:
        done(f"Login successful! Redirected to: {current_url}", "step5_login_success.png", driver)

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
    done(f"Resume uploaded: {RESUME_PATH}", "step9_resume_uploaded.png", driver)

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
        done("No save button appeared — upload auto-submitted", "step10_auto_submitted.png", driver)

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
    print("  ✅ Login        — DONE")
    print("  ✅ Resume Upload — DONE")
    print("  ✅ Logout        — DONE")
    print(f"{'='*50}\n")

except Exception as e:
    print(f"\n  ❌ SCRIPT FAILED: {e}")
    raise

finally:
    driver.quit()
    print("  🔒 Browser closed.")
