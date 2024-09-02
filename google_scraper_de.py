# Set up virtual environment 
# python -m venv venv
# venv\Scripts\activate

# Install required libraries
# pip install selenium pandas dataclasses

# Ensure the Chromedriver path is correct

# Insert list of URLS in the script

# Run using 'python google_scraper_de.py'

import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from dataclasses import dataclass, asdict, field
import pandas as pd
import os
from seleniumbase import Driver

# Data class to store review information
@dataclass
class ReviewInformation:
    appName: str = None
    fullName: str = None
    stars: int = None
    date: str = None
    platform: str = None
    reviewDescription: str = None
    helpful: int = None

# Data class to handle the list of reviews and saving to file
@dataclass
class ReviewInformationList:
    reviewInfoList: list[ReviewInformation] = field(default_factory=list)
    save_at: str = 'output'

    def dataframe(self):
        """Transform reviewInfoList to pandas dataframe."""
        return pd.DataFrame([asdict(review) for review in self.reviewInfoList])

    def save_to_excel(self, filename):
        """Save pandas dataframe to an Excel (xlsx) file."""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_excel(f"{self.save_at}/{filename}.xlsx", index=False)

    def save_to_csv(self, filename):
        """Save pandas dataframe to a CSV file."""
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)

# Selenium driver initialization
driver = Driver(
    browser="chrome",
    wire=True,
    uc=True,
    headless2=True,
    incognito=False,
    agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    do_not_track=True,
    undetectable=True,
    extension_dir=None,
    locale_code="de"
)

# List of URLs to scrape
urls = [
    "https://play.google.com/store/apps/details?id=com.pix4d.capturepro&hl=de_DE",
    "https://play.google.com/store/apps/details?id=tiar.ua.slf&hl=de_DE",
    "https://play.google.com/store/apps/details?id=com.flir.tools&hl=de_DE"
]

# Base XPaths
app_name_xpath_base = "//h1[@itemprop='name']"
platform_xpath_base = "(//i[@class='google-material-icons Ka7T4c'])[last()]"
full_name_xpath_base = "(//div[@class='X5PpBb'])[{}]"
review_date_xpath_base = "(//span[@class='bp9Aid'])[{}]"
stars_xpath_base = "(//div[@class='iXRFPc' and contains(@aria-label, 'Mit')])[{}]"
review_description_xpath_base = "(//div[@class='h3YV2d'])[{}]"
helpful_xpath_base = "(//div[@class='AJTPZc'])[{}]"

# Start extracting data from index 4
start_index = 4
total_reviews_count = 0

def scroll_through_reviews(driver):
    global total_reviews_count
    step_size = 20  # Start by scrolling 20 elements at a time
    current_index = step_size
    max_index = current_index
    keep_scrolling = True

    while keep_scrolling:
        try:
            # Locate the nth element by its index
            review_element_xpath = f"//div[@class='RHo1pe'][{current_index}]"
            review_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, review_element_xpath))
            )

            # Scroll to the nth element
            ActionChains(driver).scroll_to_element(review_element).perform()
            print(f"Scrolled to review number {current_index}")
            time.sleep(2)  # Add a slight delay to ensure the page has time to load new content

            # Increase the index by step_size for the next iteration
            current_index += step_size
            max_index = current_index

        except Exception as e:
            print(f"Cannot scroll to review number {current_index}: {e}")
            print("Decreasing step size...")
            step_size -= 1  # Decrease the step size if we can't find the element

            if step_size == 0:  # Stop when step size becomes 0
                keep_scrolling = False

            # Try to scroll to the maximum index reached, to ensure all reviews are loaded
            current_index = max_index - step_size
            
            total_reviews_count = current_index - step_size

    print("Finished scrolling through all reviews.")

def main():
    try:
        for url in urls:
            driver.get(url)
            driver.maximize_window()

            # Create a new ReviewInformationList for each URL
            review_list = ReviewInformationList()

            try:
                # Wait until the 'See All Reviews' button is present in the DOM
                print("Waiting for 'See All Reviews' button to be present...")
                see_all_reviews = driver.find_elements(By.CLASS_NAME, "LQeN7.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.aLey0c.ksBjEc.lKxP2d")
                print("'See All Reviews' button found.")

                # Find the correct 'See All Reviews' button
                for button in see_all_reviews:
                    if "Alle Rezensionen ansehen" in button.text:
                        see_all_reviews_button = button
                        break
                else:
                    raise Exception("'See All Reviews' button not found.")

                # Scroll to the 'See All Reviews' button to make it visible
                ActionChains(driver).scroll_to_element(see_all_reviews_button).perform()
                time.sleep(2)  # Give some time for the scroll action
                print("Scrolled to 'See All Reviews' button.")

                # Wait until the 'See All Reviews' button is visible and clickable
                see_all_reviews_button = WebDriverWait(driver, 20).until(
                    EC.visibility_of(see_all_reviews_button)
                )
                print("'See All Reviews' button is visible.")

                # Now wait until the element is clickable
                see_all_reviews_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable(see_all_reviews_button)
                )
                print("'See All Reviews' button is clickable.")

                see_all_reviews_button.click()
                print("Clicked the 'See All Reviews' button.")

                scroll_through_reviews(driver)

            except Exception as e:
                print(f"Error occurred: {e}")
                print(f"Exception type: {type(e).__name__}")

            time.sleep(5)

            # Now extract reviews
            for i in range(start_index, total_reviews_count):
                try:
                    # Extract app name
                    appName = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, app_name_xpath_base))
                    ).text

                    # Extract platform
                    platform = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, platform_xpath_base))
                    ).text

                    # Extract full name
                    full_name_xpath = full_name_xpath_base.format(i)
                    full_name = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, full_name_xpath))
                    ).text

                    # Extract review date
                    review_date_xpath = review_date_xpath_base.format(i)
                    review_date = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, review_date_xpath))
                    ).text

                    # Extract stars
                    stars_xpath = stars_xpath_base.format(i)
                    stars_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, stars_xpath))
                    )
                    stars_text = stars_element.get_attribute("aria-label")
                    stars_count = re.search(r'\d+', stars_text).group()

                    # Extract review description
                    review_description_xpath = review_description_xpath_base.format(i)
                    review_description = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, review_description_xpath))
                    ).text

                    # Extract helpful count
                    helpful_xpath = helpful_xpath_base.format(i)
                    helpful_text = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, helpful_xpath))
                    ).text
                    helpful_count = re.search(r'\d+', helpful_text).group()

                    # Add the extracted data to the list
                    review = ReviewInformation(
                        appName=appName,
                        fullName=full_name,
                        stars=int(stars_count),
                        date=review_date,
                        platform=platform,
                        reviewDescription=review_description,
                        helpful=int(helpful_count)
                    )
                    review_list.reviewInfoList.append(review)

                    print(f"Review {i-3}:")
                    print(f"Full Name: {full_name}")
                    print(f"Review Date: {review_date}")
                    print(f"Platform: {platform}")
                    print(f"Stars: {stars_count}")
                    print(f"Review Description: {review_description}")
                    print(f"Helpful: {helpful_count}")
                    print("----------")

                except Exception as e:
                    print(f"Error occurred for review {i-3}: {e}")
                    print(f"Exception type: {type(e).__name__}")

                
                            # Save to CSV
            review_list.save_to_csv(f"reviews_{url.split('id=')[1]}")
            print(f"Saved reviews to CSV for {url}")


    except Exception as e:
        print(f"An error occurred during the scraping process: {e}")
        print(f"Exception type: {type(e).__name__}")
    finally:
        driver.quit()
        print("Driver closed.")

if __name__ == "__main__":
    main()