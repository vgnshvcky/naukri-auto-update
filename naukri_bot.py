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

print(f"Using email: {EMAIL}")

# ── Chrome setup ──────────────────────────────────────────────────────────────
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

try:
    # ── STEP 1: LOGIN ─────────────────────────────────────────────────────────
    print("Opening Naukri login page...")
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(5)
    driver.save_screenshot("01_login_page.png")

    print("Entering email...")
    email_box = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Enter Email ID / Username']")
        )
    )
    email_box.click()
    email_box.clear()
    email_box.send_keys(EMAIL)
    time.sleep(1)

    print("Entering password...")
    password_box = wait.until(
        EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Enter Password']")
        )
    )
    password_box.click()
    password_box.clear()
    password_box.send_keys(PASSWORD)
    time.sleep(1)

    driver.save_screenshot("01b_credentials_entered.png")

    print("Clicking Login...")
    login_btn = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Login']"))
    )
    login_btn.click()
    print("Login submitted, waiting...")
    time.sleep(15)
    driver.save_screenshot("02_after_login.png")

    # ── STEP 2: VERIFY LOGIN SUCCESS ──────────────────────────────────────────
    current_url = driver.current_url
    print(f"URL after login: {current_url}")

    if "nlogin/login" in current_url:
        try:
            err = driver.find_element(By.XPATH, "//*[contains(@class,'error') or contains(@class,'alert')]")
            print(f"Login error on page: {err.text}")
        except Exception:
            pass
        driver.save_screenshot("02_login_failed.png")
        raise Exception(
            "❌ Login failed — still on login page after 15s.\n"
            "Check screenshot 02_login_failed.png\n"
            "Possible causes: wrong credentials, CAPTCHA, or account locked."
        )

    print(f"✅ Login successful! URL: {current_url}")

    # ── STEP 3: GO TO PROFILE PAGE ────────────────────────────────────────────
    print("Navigating to profile page...")
    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(8)
    driver.save_screenshot("03_profile_page.png")

    # ── STEP 4: DISMISS ANY POPUP ─────────────────────────────────────────────
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
        print("Dismissed popup")
        time.sleep(2)
    except Exception:
        print("No popup to dismiss")

    # ── STEP 5: UPLOAD RESUME ─────────────────────────────────────────────────
    print("Looking for file input on profile page...")
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)

    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    print(f"Found {len(file_inputs)} file input(s)")

    if not file_inputs:
        driver.save_screenshot("03_no_file_input.png")
        raise Exception(
            "❌ No file input found on profile page.\n"
            "Check screenshot 03_no_file_input.png"
        )

    upload = file_inputs[0]
    driver.execute_script("arguments[0].style.display    = 'block';",   upload)
    driver.execute_script("arguments[0].style.visibility = 'visible';", upload)
    driver.execute_script("arguments[0].style.opacity    = '1';",       upload)
    driver.execute_script("arguments[0].removeAttribute('class');",     upload)

    upload.send_keys(RESUME_PATH)
    print(f"✅ Resume sent: {RESUME_PATH}")
    time.sleep(6)
    driver.save_screenshot("04_after_upload.png")

    # ── STEP 6: CLICK SAVE/CONFIRM IF PRESENT ────────────────────────────────
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
        print("Clicked save/confirm button")
        time.sleep(5)
        driver.save_screenshot("05_after_save.png")
    except Exception:
        print("No save/confirm button — upload likely auto-submitted")

    print("✅ Resume updated successfully!")

    # ── STEP 7: LOGOUT ────────────────────────────────────────────────────────
    print("Logging out...")
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
        driver.save_screenshot("06_menu_open.png")

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
        driver.save_screenshot("07_logged_out.png")
        print("✅ Logged out via menu!")

    except Exception as e:
        print(f"Menu logout failed ({e}), using direct URL...")
        driver.get("https://www.naukri.com/nlogin/logout")
        time.sleep(3)
        driver.save_screenshot("07_logged_out.png")
        print("✅ Logged out via URL!")

except Exception as e:
    driver.save_screenshot("error.png")
    print(f"❌ Script failed: {e}")
    raise

finally:
    driver.quit()
    print("Browser closed.")
