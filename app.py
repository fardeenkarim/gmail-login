import csv
import time
import random
import sys
import threading
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
BATCH_SIZE = 10

# Thread-safe storage for drivers
drivers = []
drivers_lock = threading.Lock()

# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message, type="info"):
    timestamp = time.strftime("%H:%M:%S")
    thread_name = threading.current_thread().name
    prefix = f"[{thread_name}] " if thread_name != "MainThread" else ""
    
    if type == "info":
        print(f"{Colors.OKCYAN}[{timestamp}] {prefix}ℹ {message}{Colors.ENDC}")
    elif type == "success":
        print(f"{Colors.OKGREEN}[{timestamp}] {prefix}✔ {message}{Colors.ENDC}")
    elif type == "warning":
        print(f"{Colors.WARNING}[{timestamp}] {prefix}⚠ {message}{Colors.ENDC}")
    elif type == "error":
        print(f"{Colors.FAIL}[{timestamp}] {prefix}✖ {message}{Colors.ENDC}")
    elif type == "header":
        print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}")

def get_credentials(email_file, password_file):
    emails = []
    passwords = []
    try:
        with open(email_file, mode='r') as f:
            emails = [line.strip() for line in f if line.strip()]
        with open(password_file, mode='r') as f:
            passwords = [line.strip() for line in f if line.strip()]
        return list(zip(emails, passwords))
    except Exception as e:
        log(f"Error reading credentials: {e}", "error")
        return []

def human_typing(element, text):
    """Simulates realistic human typing with variable speed and micro-pauses."""
    for char in text:
        element.send_keys(char)
        # Base delay + random variance
        delay = random.uniform(0.05, 0.15)
        # Occasionally pause longer (simulating thinking or finding key)
        if random.random() < 0.05: 
            delay += random.uniform(0.2, 0.5)
        time.sleep(delay)

def human_mouse_move(driver, element):
    """Simulates moving the mouse to an element with a slight random offset."""
    try:
        action = ActionChains(driver)
        # Move to element with slight random offset to avoid 'perfect center' clicks
        x_offset = random.randint(1, 10)
        y_offset = random.randint(1, 10)
        action.move_to_element_with_offset(element, x_offset, y_offset).perform()
        time.sleep(random.uniform(0.3, 0.8)) # Pause after moving mouse
    except Exception:
        pass # If mouse move fails (e.g. element obscured), just ignore

def random_scroll(driver):
    """Performs a small random scroll to simulate user reading."""
    try:
        scroll_amount = random.randint(100, 300)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))
    except:
        pass

def login_procedure(driver, email, password, is_first_account):
    try:
        log(f"Processing Account: {email}", "info")
        
        if is_first_account:
            driver.get("https://accounts.google.com/signin/v2/identifier?service=mail&flowName=GlifWebSignIn&flowEntry=ServiceLogin")
        else:
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get("https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=AddSession")

        # Initial random behavior
        if random.random() < 0.3:
            random_scroll(driver)

        # Wait for email fields
        wait = WebDriverWait(driver, 20)
        time.sleep(random.uniform(2, 4)) 
        
        email_field = wait.until(EC.presence_of_element_located((By.ID, "identifierId")))
        
        log(f"Entering email...", "info")
        human_mouse_move(driver, email_field)
        email_field.click() # Explicit click before typing
        email_field.clear()
        human_typing(email_field, email)
        
        time.sleep(random.uniform(0.5, 1.2))
        email_field.send_keys(Keys.RETURN)

        # Wait for password field
        log("Waiting for password field...", "info")
        time.sleep(random.uniform(3, 6)) # Longer wait for page load
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
        
        log("Entering password...", "info")
        human_mouse_move(driver, password_field)
        password_field.click()
        password_field.clear()
        human_typing(password_field, password)
        
        time.sleep(random.uniform(0.5, 1.2))
        password_field.send_keys(Keys.RETURN)

        # Handle Policy / "Not Now" / Bengali screens
        log("Checking for post-login screens (Policy / Not Now / Bengali)...", "info")
        time.sleep(random.uniform(5, 8)) 
        
        # Helper to click button
        def click_button_by_text(texts):
            start_time = time.time()
            max_try_time = 12
            while time.time() - start_time < max_try_time: 
                # ID Check
                try:
                    confirm_btn = driver.find_element(By.ID, "confirm")
                    if confirm_btn.is_displayed():
                        log(f"Found button with id='confirm'...", "success")
                        human_mouse_move(driver, confirm_btn)
                        confirm_btn.click()
                        time.sleep(random.uniform(2, 4))
                        return True
                except:
                    pass

                # Name Check
                try:
                    confirm_btn = driver.find_element(By.NAME, "confirm")
                    if confirm_btn.is_displayed():
                        log(f"Found button with name='confirm'...", "success")
                        human_mouse_move(driver, confirm_btn)
                        confirm_btn.click()
                        time.sleep(random.uniform(2, 4))
                        return True
                except:
                    pass

                # Text/Value Check
                for text in texts:
                    try:
                        xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}') or contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                        elements = driver.find_elements(By.XPATH, xpath)
                        
                        for element in elements:
                            if element.is_displayed():
                                log(f"Found '{text}' element...", "success")
                                human_mouse_move(driver, element)
                                try:
                                    element.click()
                                except:
                                    driver.execute_script("arguments[0].click();", element)
                                time.sleep(random.uniform(2, 4))
                                return True
                    except:
                        continue
                time.sleep(1)
            return False

        # Common texts
        clicked = click_button_by_text(["Not now", "I agree", "Accept", "Confirm", "আমি বুঝেছি", "I understand"])
        
        if clicked:
            log("Post-login action handled successfully.", "success")
        
        time.sleep(random.uniform(1.5, 3))
        click_button_by_text(["Not now", "I agree", "Accept", "Confirm", "আমি বুঝেছি", "I understand"])

        log(f"Login flow complete for {email}.", "success")

    except Exception as e:
        log(f"An error occurred for {email}: {e}", "error")

def process_batch(batch, batch_index):
    """Function to be run in a separate thread for each batch."""
    thread_name = f"Batch-{batch_index + 1}"
    threading.current_thread().name = thread_name
    
    log(f"Starting Batch {batch_index + 1} ({len(batch)} accounts)", "header")
    
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--guest")
    
    try:
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        # Randomize window size slightly for extra 'human-ness'
        try:
             width = random.randint(1200, 1400)
             height = random.randint(800, 1000)
             driver.set_window_size(width, height)
        except:
             pass

        with drivers_lock:
            drivers.append(driver)

        for index, (email, password) in enumerate(batch):
            is_first = (index == 0)
            login_procedure(driver, email, password, is_first)
            # Longer pause between accounts to look natural
            time.sleep(random.uniform(5, 10)) 

        log(f"Batch {batch_index + 1} completed.", "success")
    
    except Exception as e:
        log(f"Critical error in batch {batch_index + 1}: {e}", "error")

def main():
    log("Gmail Login Automation Started (Advanced Human-Like Mode)", "header")
    credentials = get_credentials('email.csv', 'password.csv')
    if not credentials:
        log("Could not retrieve credentials from email.csv and password.csv", "error")
        return

    # Chunk credentials into batches
    total_accounts = len(credentials)
    batches = [credentials[i:i + BATCH_SIZE] for i in range(0, total_accounts, BATCH_SIZE)]
    
    log(f"Loaded {total_accounts} accounts. Launching {len(batches)} parallel browser batches.", "info")

    threads = []
    for i, batch in enumerate(batches):
        t = threading.Thread(target=process_batch, args=(batch, i))
        threads.append(t)
        t.start()
        # Stagger start times significantly to look less like a botfarm
        time.sleep(random.uniform(3, 6)) 

    for t in threads:
        t.join()

    log("All batches finished processing.", "header")
    log("Browsers are left open. Press Enter to close all browsers and exit script.", "warning")
    input()
    
    log("Closing browsers...", "info")
    for driver in drivers:
        try:
            driver.quit()
        except:
            pass
    log("Done.", "success")

if __name__ == "__main__":
    main()
