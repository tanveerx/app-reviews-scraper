# Set up virtual environment 
# python -m venv venv
# venv\Scripts\activate

# Install required libraries
# pip install selenium pandas dataclasses

# Ensure the Chromedriver path is correct

# Insert list of URLS in the script

# Run using 'python apple_scraper_de.py'

import re, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass, asdict, field
import pandas as pd
import os


#cookies accept

@dataclass
class ReviewInformation:
    appName: str = None
    fullName: str = None
    stars: int = None
    date: str = None
    reviewTitle: str = None
    reviewDescription: str = None

@dataclass
class ReviewInformationList:
    reviewInfoList : list[ReviewInformation] = field(default_factory=list)
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


from seleniumbase import Driver

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


# List of URLs to scrape reviews from
urls = [
    "https://apps.apple.com/de/app/funimate-videobearbeitung-app/id844570015?see-all=reviews",
    "https://apps.apple.com/de/app/snapchat-chatte-mit-freunden/id447188370?see-all=reviews"# Add more URLs as needed
]

#Base XPaths
app_name_xpath_base = "//a[@class='see-all-header__link link']"
review_title_xpath_base = "(//h3[@class='we-truncate we-truncate--single-line  we-customer-review__title'])[{}]"
full_name_xpath_base = "(//span[@class='we-truncate we-truncate--single-line  we-customer-review__user'])[{}]"
review_date_xpath_base = "(//time[@class='we-customer-review__date'])[{}]"
stars_xpath_base = "(//figure[@class='we-star-rating we-customer-review__rating we-star-rating--large' and contains(@aria-label, 'von 5')])[{}]" 
review_description_xpath_base = "(//div[@class='we-clamp'])[{}]"

review_list = ReviewInformationList()

def main():

# Loop over each URL and scrape the reviews
    for url in urls:
        driver.get(url)
        driver.maximize_window()

        # Create a new ReviewInformationList for each URL
        review_list = ReviewInformationList()

        # Extract reviews
        for i in range(1, 11):  # Adjust range according to the number of reviews
            try:
                # Extract app name
                appName = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, app_name_xpath_base))
                ).text

                # Extract review title
                review_title_xpath = review_title_xpath_base.format(i)
                reviewTitle = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, review_title_xpath))
                ).text

                # Extract full name
                full_name_xpath = full_name_xpath_base.format(i)
                full_name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, full_name_xpath))
                ).text

                # Extract review date
                review_date_xpath = review_date_xpath_base.format(i)
                review_date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, review_date_xpath))
                )
                review_date = review_date_element.get_attribute("aria-label")

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

                # Add the extracted data to the list
                review = ReviewInformation(
                    appName=appName, 
                    fullName=full_name, 
                    stars=int(stars_count), 
                    date=review_date, 
                    reviewTitle=reviewTitle, 
                    reviewDescription=review_description
                )
                review_list.reviewInfoList.append(review)

                print(f"Review {i}:")
                print(f"App Name: {appName}")
                print(f"Full Name: {full_name}")
                print(f"Review Date: {review_date}")
                print(f"Review Title: {reviewTitle}")
                print(f"Stars: {stars_count}")
                print(f"Review Description: {review_description}")
                print("----------")

            except Exception as e:
                print(f"Error occurred for review {i}: {e}")
                print(f"Exception type: {type(e).__name__}")

        # Save to CSV after extracting all reviews from the current URL
        review_list.save_to_csv(f"app_store_reviews_{url.split('/')[-2]}")

        # Pause before the next request
        time.sleep(5)


main()  

time.sleep(5)
driver.quit()
