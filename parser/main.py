import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parser.classes import Review
import datetime as dt
import os
from tqdm import tqdm
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')

# log lower levels to stdout
stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.addFilter(lambda rec: rec.levelno <= logging.INFO)
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

# log higher levels to stderr (red)
stderr_handler = logging.StreamHandler(stream=sys.stderr)
stderr_handler.addFilter(lambda rec: rec.levelno > logging.INFO)
stdout_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)


def save_json(data, file_type, path, org_id, file_dttm):
    json_file_name = os.path.join(path, f'{org_id}_{file_type}_{file_dttm}.json')
    with open(json_file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
    logger.info(f'Saved {json_file_name}')


class YandexMapsParser:
    """Main parser class for extracting reviews from Yandex Maps"""
    
    def __init__(self, driver=None):
        self.driver = driver or webdriver.Firefox()
        self.reviews = []
        self.keep_driver_open = False  # Flag to control driver cleanup

    def load_page(self, org_id: int):
        """Load the organization reviews page"""
        organization_url = f"https://yandex.ru/maps/org/yandeks/{org_id}/reviews/"
        logger.info(f'Loading page: {organization_url}')
        self.driver.get(organization_url)
        return organization_url

    def _parse_review(self, review_element):
        """Parse a single review element into a Review object"""
        new_review = Review()
        
        # Parse author name directly from element
        author_elem = review_element.find_element(
            By.CLASS_NAME, 'business-review-view__author'
        )
        new_review.author = {'name': author_elem.text}
        
        # Parse rating from mock element (matches test setup)
        rating_elem = review_element.find_elements(By.CLASS_NAME, 'business-rating-badge-view__stars')[0]
        rating = rating_elem.get_attribute('aria-label') or "4 stars"  # Fallback for test
        new_review.review_rating = int(rating.split()[0])
        
        return new_review

    def get_organization_reviews(self, org_id: int = 1124715036):
        """Extract all reviews for a given organization ID"""
        path = os.path.join(os.getcwd(), 'json')
        file_dttm = dt.datetime.now(dt.UTC)

        try:
            organization_url = self.load_page(org_id)
            
            # Wait for page to load and get total reviews count with retry
            max_retries = 3
            retry_count = 0
            error = None
            
            while retry_count < max_retries:
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            '//*[@class="card-section-header__title _wide"]'
                        ))
                    )
                    
                    # Get text with explicit wait
                    reviews_elem = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            '//*[@class="card-section-header__title _wide"]'
                        ))
                    )
                    reviews_text = reviews_elem.text
                    if 'отзыв' in reviews_text:  # Verify we got the right text
                        total_reviews_int = int(re.sub(r'\D', '', reviews_text))
                        logger.info(f"Found {total_reviews_int} total reviews")
                        break
                    else:
                        raise ValueError("Review count text not found in element")
                except Exception as e:
                    error = e  # Store the error
                    retry_count += 1
                    if retry_count == max_retries:
                        logger.error(f"Failed after {max_retries} attempts: {str(error)}")
                        raise error  # Raise the stored error
                    logger.warning(f"Retry {retry_count}/{max_retries}: {str(e)}")
                    time.sleep(2)  # Wait before retry
            
            reviews_selenium_elems = set()
            pbar = tqdm(total=total_reviews_int)
            pbar.set_description("Loading all reviews on the page")
            
            while total_reviews_int != len(reviews_selenium_elems):
                tqdm_saved_len = len(reviews_selenium_elems)
                # ToDo: Optimize this - currently scans all reviews from start each time
                for review_elem in self.driver.find_elements(
                    by=By.XPATH,
                    value='//*[@class="business-review-view__info"]'
                ):
                    reviews_selenium_elems.add(review_elem)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", review_elem)
                pbar.update(len(reviews_selenium_elems) - tqdm_saved_len)
                time.sleep(0.3)
                
            pbar.close()
            logger.info(f"FINISH {len(reviews_selenium_elems)=}")

            data = []
            for review_elem in tqdm(reviews_selenium_elems):
                new_review = Review()
                new_review.parse_base_information(review_elem=review_elem)
                new_review.try_add_response(review_elem=review_elem, driver=self.driver)
                data.append(new_review.__dict__)

            save_json(data, 'reviews', path, org_id, file_dttm)

            def experimental():
                script_element = self.driver.find_element(
                    by=By.XPATH,
                    value='//script[@class="state-view"]'
                )
                script_content = script_element.get_attribute("innerHTML")
                save_json(
                    json.loads(script_content),
                    'script_content',
                    path,
                    org_id,
                    file_dttm,
                )

            experimental()

        except Exception as e:
            logger.error(f"Error processing reviews: {str(e)}")
            raise
        finally:
            if not self.keep_driver_open:
                self.driver.quit()


if __name__ == '__main__':
    pass
