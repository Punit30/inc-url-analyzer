# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# import time
# import random
# import re
#
#
# def setup_driver():
#     chrome_options = Options()
#
#     # Anti-detection settings
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_argument(
#         "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
#     chrome_options.add_argument("--lang=en-US,en;q=0.9")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--no-sandbox")
#
#     # Disable automation flags
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option('useAutomationExtension', False)
#
#     driver = webdriver.Chrome(options=chrome_options)
#
#     # Overwrite navigator properties
#     driver.execute_script(
#         "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
#     )
#
#     return driver
#
#
# def extract_metrics(driver):
#     try:
#         # Wait for main content to load
#         WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.XPATH, "//div[@role='main']"))
#         )
#
#         # Handle cookie consent
#         try:
#             cookie_btn = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label, 'cookie')]"))
#             )
#             cookie_btn.click()
#             time.sleep(1)
#         except:
#             pass
#
#         # Extract video metrics
#         metrics = {}
#
#         # Views extraction
#         try:
#             views_element = WebDriverWait(driver, 10).until(
#                 EC.visibility_of_element_located((By.XPATH,
#                                                   "//span[contains(., 'views') or contains(., 'plays')][@dir='auto']"
#                                                   ))
#             )
#             metrics['views'] = re.search(r'[\d,\.]+[KkM]?', views_element.text).group()
#         except:
#             metrics['views'] = "N/A"
#
#         # Likes extraction
#         try:
#             likes_element = WebDriverWait(driver, 10).until(
#                 EC.visibility_of_element_located((By.XPATH,
#                                                   "//span[contains(., 'likes') or contains(., 'reactions')][@dir='auto']"
#                                                   ))
#             )
#             metrics['likes'] = re.search(r'[\d,\.]+[KkM]?', likes_element.text).group()
#         except:
#             metrics['likes'] = "N/A"
#
#         # Comments extraction
#         try:
#             comments_element = WebDriverWait(driver, 10).until(
#                 EC.visibility_of_element_located((By.XPATH,
#                                                   "//span[contains(., 'comments')][@dir='auto']"
#                                                   ))
#             )
#             metrics['comments'] = re.search(r'[\d,\.]+[KkM]?', comments_element.text).group()
#         except:
#             metrics['comments'] = "N/A"
#
#         return metrics
#
#     except TimeoutException:
#         print("Timed out waiting for page elements")
#         return None
#     except Exception as e:
#         print(f"Error during scraping: {str(e)}")
#         return None
#
#
# def scrape_facebook_video(url):
#     driver = setup_driver()
#     try:
#         # Access URL with random delay
#         driver.get(url)
#         time.sleep(random.uniform(3, 6))
#
#         # Check for login redirect
#         if "login" in driver.current_url.lower():
#             print("Login required - scraping not possible")
#             return None
#
#         # Extract metrics
#         return extract_metrics(driver)
#
#     finally:
#         driver.quit()
#
#
# # Usage
# if __name__ == "__main__":
#     video_url = "https://www.facebook.com/share/v/1AVNWPWEWj/"
#     metrics = scrape_facebook_video(video_url)
#
#     if metrics:
#         print(f"Video Views: {metrics.get('views', 'N/A')}")
#         print(f"Likes: {metrics.get('likes', 'N/A')}")
#         print(f"Comments: {metrics.get('comments', 'N/A')}")
#     else:
#         print("Failed to scrape metrics")


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re


def setup_driver():
    chrome_options = Options()

    # Anti-detection settings
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    service = Service('chromedriver')  # Update with your path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Mask webdriver properties
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {},
            };
        '''
    })

    return driver


def extract_metrics(driver):
    try:
        # Wait for main content container
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='main']"))
        )

        metrics = {}

        # Extract view count - looks for number near "views" or "plays"
        try:
            views_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                                                ".//div[contains(., 'views') or contains(., 'plays')][@dir='auto']"
                                                ))
            )
            metrics['views'] = re.search(r'[\d,\.]+', views_container.text).group()
        except:
            metrics['views'] = "N/A"

        # Extract engagement metrics container
        engagement_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,
                                            "//div[contains(@aria-label, 'Reactions')]/ancestor::div[contains(@class, 'x1qjc9v5')]"
                                            ))
        )

        # Extract like count - looks for number near reaction icons
        try:
            likes_element = engagement_container.find_element(By.XPATH,
                                                              ".//span[contains(@class, 'x1e558r4') and contains(text(), ',')]"
                                                              )
            metrics['likes'] = likes_element.text
        except:
            metrics['likes'] = "N/A"

        # Extract comment count - looks for number near comment icon
        try:
            comments_element = engagement_container.find_element(By.XPATH,
                                                                 ".//span[contains(@class, 'x1e558r4') and contains(text(), ',')]/following-sibling::span"
                                                                 )
            metrics['comments'] = comments_element.text
        except:
            metrics['comments'] = "N/A"

        return metrics

    except TimeoutException:
        print("Timed out waiting for page elements")
        return None
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None


def scrape_facebook_video(url):
    driver = setup_driver()
    try:
        driver.get(url)

        # Check for age gate or login redirect
        if "login" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
            print("Login/age verification required - scraping not possible")
            return None

        # Extract metrics
        return extract_metrics(driver)

    finally:
        driver.quit()


if __name__ == "__main__":
    video_url = "https://www.facebook.com/share/v/1AVNWPWEWj/"
    metrics = scrape_facebook_video(video_url)

    if metrics:
        print(f"Video Views: {metrics.get('views', 'N/A')}")
        print(f"Likes: {metrics.get('likes', 'N/A')}")
        print(f"Comments: {metrics.get('comments', 'N/A')}")
    else:
        print("Failed to scrape metrics")