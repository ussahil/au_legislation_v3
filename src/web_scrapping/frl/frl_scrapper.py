
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from time import sleep
import os, re, time, random

url = "https://www.legislation.gov.au/search/collection(Act)/status(InForce)/type(Principal)"

# --- Chrome setup ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Download folder: project directory / epubs
download_dir = os.path.join(os.getcwd(), "epubs")
os.makedirs(download_dir, exist_ok=True)
prefs = {"download.default_directory": download_dir,
         "download.prompt_for_download": False,
         "download.directory_upgrade": True,
         "safebrowsing.enabled": True}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=options)

# OPTIONAL (recommended): allow programmatic downloads via DevTools
try:
    driver.execute_cdp_cmd("Page.setDownloadBehavior",
                           {"behavior": "allow", "downloadPath": download_dir})
except Exception:
    pass

driver.get(url)
sleep(4)  # initial settle

TOTAL_ROWS_PER_PAGE = 100
ROW_HEIGHT = 70
wait = WebDriverWait(driver, 15)
page_number = 1

def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()

# --- polite delay to comply with robots.txt crawl-delay = 10 ---
CRAWL_DELAY_SECONDS = 10
DELAY_JITTER_RANGE = (0.6, 1.8)  # small randomness to avoid a fixed pattern
def polite_sleep(base=CRAWL_DELAY_SECONDS):
    time.sleep(base + random.uniform(*DELAY_JITTER_RANGE))

while True:
    print(f"\n--- Page {page_number} ---")

    for i in range(1, TOTAL_ROWS_PER_PAGE + 1):
        try:
            # Scroll to row (UI settle, not the crawl-delay)
            scroll = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="maincontent"]/frl-search-results/frl-template-one-col/div[2]/div/frl-zone/frl-data-grid/ngx-datatable/div/datatable-body/datatable-selection/datatable-scroller')
            ))
            driver.execute_script("arguments[0].scrollTop = arguments[1];", scroll, i * ROW_HEIGHT)
            sleep(0.3)

            xpath = f'//*[@id="maincontent"]/frl-search-results/frl-template-one-col/div[2]/div/frl-zone/frl-data-grid/ngx-datatable/div/datatable-body/datatable-selection/datatable-scroller/datatable-row-wrapper[{i}]/datatable-body-row/div[2]/datatable-body-cell[1]/div/frl-grid-cell-title-name-in-force/div/div[3]/div[1]/a'

            link = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            act_name = sanitize(link.text)
            act_url = link.get_attribute("href")
            print(f"Row {i}: {act_name} -> {act_url}")

            # --- Respect crawl-delay before opening Act page ---
            polite_sleep()

            # --- Open Act in new tab ---
            driver.execute_script("window.open(arguments[0]);", act_url)
            driver.switch_to.window(driver.window_handles[1])
            sleep(2)  # UI settle

            # --- Click EPUB dynamically ---
            try:
                # Respect crawl-delay before triggering a potentially heavy download
                polite_sleep()

                # find all possible EPUB buttons on page (viewer toolbar fallback)
                epub_buttons = driver.find_elements(By.XPATH, "//frl-epub-viewer//frl-epub-toolbar/button[1]")
                if epub_buttons:
                    epub_btn = epub_buttons[0]
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", epub_btn)
                    driver.execute_script("arguments[0].click();", epub_btn)
                    print(f"  [INFO] EPUB download triggered for '{act_name}'. Check epubs/ folder.")
                    # wait briefly for the download to start (not a crawl-delay)
                    sleep(2)
                else:
                    print(f"  [INFO] No EPUB button for '{act_name}', skipping.")
            except Exception as e:
                print(f"  [ERROR EPUB] for '{act_name}': {e}")

            # --- Close tab and return to main page ---
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            sleep(2)

        except TimeoutException:
            continue

    # --- Next page ---
    try:
        next_button = driver.find_element(
            By.XPATH,
            '//*[@id="maincontent"]/frl-search-results/frl-template-one-col/div[2]/div/frl-zone/frl-data-grid/ngx-datatable/div/datatable-footer/div/frl-datagrid-pager/nav/ul/li[8]/a'
        )
        parent_li = next_button.find_element(By.XPATH, "..")
        if "disabled" in parent_li.get_attribute("class"):
            print("Reached last page.")
            break

        first_row_before = driver.find_element(
            By.XPATH,
            '//datatable-row-wrapper[1]//frl-grid-cell-title-name-in-force//a'
        ).text

        # Respect crawl-delay before paginating
        polite_sleep()

        next_button.click()
        sleep(1)

        wait.until(lambda d: d.find_element(
            By.XPATH, '//datatable-row-wrapper[1]//frl-grid-cell-title-name-in-force//a'
        ).text != first_row_before)

        page_number += 1
        sleep(1)

    except Exception:
        print("Next button not found. Finished scraping.")
        break

driver.quit()
