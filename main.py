import random
import time
import csv
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager


class Constants:
    SCROLL_DELAY = random.uniform(2, 5)
    BUTTON_CLICK_DELAY = random.randint(5, 10)
    CHROME_PROFILE_PATH = "C:\\Users\\Brackets\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 8"
    LOGIN_URL = "https://www.crunchbase.com/login"
    HOMEPAGE_URL = "https://www.crunchbase.com"
    ORGANIZATION_CSV = "organizations.csv"  # CSV file containing organization URLs
    PROGRESS_FILE = "progress.txt"  # File to keep track of progress


def initialize_driver():
    options = Options()
    options.add_argument(f"user-data-dir={Constants.CHROME_PROFILE_PATH}")
    options.add_argument("profile-directory=Default")
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver
def login_to_crunchbase(driver, email, password):
    driver.get(Constants.HOMEPAGE_URL)
    wait = WebDriverWait(driver, 20)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/discover')]")))
        print("Already logged in to Crunch base")
        return

    except TimeoutException:
        print("Not logged in, attempting to log in...")

    try:
        driver.get(Constants.LOGIN_URL)
        email_field = wait.until(EC.presence_of_element_located((By.ID, "mat-input-0")))
        email_field.send_keys(email)
        time.sleep(Constants.BUTTON_CLICK_DELAY)

        password_field = wait.until(EC.presence_of_element_located((By.ID, "mat-input-1")))
        password_field.send_keys(password)

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_button.click()

        wait.until(EC.url_contains("discover"))
        print("Successfully logged in to Crunch base")

    except TimeoutException:
        print("Login process timed out.")
    except NoSuchElementException as e:
        print(f"Element not found during login: {e}")
    except Exception as e:
        print(f"Unexpected error during login: {e}")

def extract_org_name_from_url(url):
    # Extract the organization name from the URL
    return url.split("/")[-1]

def go_to_people(driver, org_url):
    driver.get(org_url)
    time.sleep(Constants.BUTTON_CLICK_DELAY)
    wait = WebDriverWait(driver, 30)

    try:
        people_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-tab-link-3"]/span[2]/span/span')))
        driver.execute_script("arguments[0].scrollIntoView(true);", people_button)
        time.sleep(5)
        people_button.click()
        print(f"Successfully clicked on the People button for {org_url}")

    except ElementClickInterceptedException:
        print("Element click intercepted, retrying...")
        driver.execute_script("arguments[0].scrollIntoView(true);", people_button)
        time.sleep(5)
        people_button.click()

    except TimeoutException:
        print("Failed to click on the People button. Timeout occurred.")
    except NoSuchElementException as e:
        print(f"People button not found: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def save_to_csv(contacts_data, filename="crunchbase_contacts.csv"):
    try:
        file_exists = os.path.isfile(filename)
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Organization", "Name", "LinkedIn", "Designation", "Tags", "Location", "Twitter", "Class"])
            if not file_exists:
                writer.writeheader()  # Write header only once at the start
            writer.writerows(contacts_data)
        print(f"Contacts and Employees Profiles details saved to {filename}")
    except Exception as e:
        print(f"Failed to save contact details to CSV: {e}")

def scroll_to_load_contacts(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_pause_time = random.uniform(5, 10)

    while True:
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(scroll_pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Break the loop if no new content is loaded

        last_height = new_height

    print("Finished scrolling to load contacts.")

def random_scroll(driver):
    scroll_pause_time = random.uniform(5, 10)
    for i in range(random.randint(5, 10)):
        driver.execute_script(f"window.scrollTo(0, {random.randint(200, 1000)});")
        time.sleep(scroll_pause_time)

def extract_A_details(driver, org_name):
    wait = WebDriverWait(driver, 30)

    try:
        contact_section = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                     '//*[@id="mat-tab-nav-panel-0"]/div/full-profile/page-centered-layout[2]/div/div/div[1]/row-card[1]/profile-section/section-card/mat-card/div[2]')))

        contact_cards = contact_section.find_elements(By.XPATH, './/contacts-card')

        contacts_data = []

        for card in contact_cards:
            try:
                card_rows = card.find_elements(By.XPATH, './/contacts-card-row')

                for row in card_rows:
                    contact_info = {}

                    try:
                        name_element = row.find_element(By.XPATH,
                                                        './/contact-details/div[1]/field-formatter/blob-formatter/span')
                        contact_info['Name'] = name_element.text
                    except NoSuchElementException:
                        contact_info['Name'] = ''

                    try:
                        linkedin_link_element = row.find_element(By.XPATH,
                                                                 './/contact-details/div[1]/linkedin-link/a')
                        contact_info['LinkedIn'] = linkedin_link_element.get_attribute('href')
                    except NoSuchElementException:
                        contact_info['LinkedIn'] = ''

                    try:
                        designation_element = row.find_element(By.XPATH, './/contact-details/div[2]/div[1]')
                        contact_info['Designation'] = designation_element.text
                    except NoSuchElementException:
                        contact_info['Designation'] = ''

                    try:
                        tags_element = row.find_element(By.XPATH, './/contact-details/div[2]/div[2]')
                        contact_info['Tags'] = tags_element.text
                    except NoSuchElementException:
                        contact_info['Tags'] = ''
                    contact_info['Class'] = 'A'
                    contact_info['Organization'] = org_name

                    contacts_data.append(contact_info)

            except Exception as e:
                print(f"Unexpected error while extracting contact details: {e}")

        return contacts_data

    except TimeoutException:
        print("Failed to load the contact section. Timeout occurred.")
    except Exception as e:
        print(f"Unexpected error while accessing the contact section: {e}")
        return None

def extract_B_details(driver, org_name):
    wait = WebDriverWait(driver, 30)
    employees_data = []

    try:
        print("Successfully clicked on the Employee Profiles Card")

        time.sleep(5)

        employee_list = driver.find_elements(By.XPATH,
                                             '//*[@id="mat-tab-nav-panel-0"]/div/full-profile/page-centered-layout[2]/div/div/div[1]/row-card[2]/profile-section/section-card/mat-card/div[2]/image-list-card/ul/li')

        for i, employee in enumerate(employee_list, start=1):
            try:
                name_element = employee.find_element(By.XPATH, './/div/a')
                name = name_element.text
                profile_url = name_element.get_attribute('href')
                title = employee.find_element(By.XPATH, './/div/field-formatter/span').text

                main_window = driver.current_window_handle

                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[-1])

                driver.get(profile_url)
                time.sleep(5)

                location = safe_find_element(driver, By.XPATH,
                                             '//*[@id="mat-tab-nav-panel-0"]/div/full-profile/page-centered-layout/div/div/div[1]/row-card[1]/profile-section/section-card/mat-card/div[2]/fields-card[2]/ul/li[1]/field-formatter/identifier-multi-formatter/span')
                linkedin = safe_find_element(driver, By.XPATH,
                                             '//*[@id="mat-tab-nav-panel-0"]/div/full-profile/page-centered-layout/div/div/div[1]/row-card[1]/profile-section/section-card/mat-card/div[2]/fields-card[3]/ul/li[1]/field-formatter/link-formatter/a',
                                             'href')
                twitter = safe_find_element(driver, By.XPATH, '//a[contains(@href, "twitter.com")]',
                                            'href')
                classs = "B"
                employee_data = {
                    'Name': name,
                    'Designation': title,
                    'Location': location,
                    'LinkedIn': linkedin,
                    'Twitter': twitter,
                    'Class': classs,
                    'Organization': org_name
                }
                employees_data.append(employee_data)
                print(f"Extracted data for {name}")

                driver.close()
                driver.switch_to.window(main_window)

            except NoSuchElementException:
                print(f"Could not find all elements for employee {i}")
            except Exception as e:
                print(f"Error processing employee {i}: {str(e)}")

    except TimeoutException:
        print("Failed to load employee profiles. Timeout occurred.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return employees_data

def safe_find_element(driver, by, value, attribute=None):
    try:
        element = driver.find_element(by, value)
        return element.get_attribute(attribute) if attribute else element.text
    except NoSuchElementException:
        return None

def read_organization_urls(filename, progress_file):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        org_urls = [row['Organization_URL'] for row in csv.DictReader(csvfile)]

    start_index = 0
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as file:
            start_index = int(file.read().strip())

    return org_urls, start_index

def update_progress(progress_file, index):
    with open(progress_file, 'w') as file:
        file.write(str(index))

if __name__ == "__main__":

    email = "bdm@bracketsltd.com"
    password = "@Brackets23"

    with open('progress.txt','r') as file:
        no_of_org = file.read()
    print("Total organizations fetched : ", no_of_org)

    limit = int(input("Enter limit of organization to be fetched by bot : "))
    driver = initialize_driver()

    login_to_crunchbase(driver, email, password)
    random_scroll(driver)

    organization_urls, start_index = read_organization_urls(Constants.ORGANIZATION_CSV, Constants.PROGRESS_FILE)
   # User can specify this

    end_index = min(start_index + limit, len(organization_urls))

    for i in range(start_index, end_index):
        org_url = organization_urls[i]
        org_name = extract_org_name_from_url(org_url)  # Extract organization name from URL
        go_to_people(driver, org_url)
        scroll_to_load_contacts(driver)

        contacts = extract_A_details(driver, org_name)
        if contacts:
            save_to_csv(contacts)

        employees = extract_B_details(driver, org_name)
        if employees:
            save_to_csv(employees)

        update_progress(Constants.PROGRESS_FILE, i + 1)

    print("Finished processing the ",limit," organizations.")
    input("Press Enter to close the browser...")
    driver.quit()

