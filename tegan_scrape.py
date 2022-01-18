import selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import requests
import os
from PIL import Image
import io
import hashlib
# This is the path I use
#DRIVER_PATH = '/Users/anand/Desktop/chromedriver'
# Put the path for your ChromeDriver here
DRIVER_PATH = '/Users/madeleineramsey/Desktop/chromedriver'


def fetch_image_urls(query, max_links_to_fetch, wd, sleep_between_interactions):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        print(number_results)
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print(f"Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

def persist_image(folder_path,file_name,url):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        folder_path = os.path.join(folder_path,file_name)
        if os.path.exists(folder_path):
            file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        else:
            os.mkdir(folder_path)
            file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

if __name__ == '__main__':
    wd = webdriver.Chrome(executable_path=DRIVER_PATH)
    queries = ["Irish Vernacular Architecture","Slate Architecture"]  #change your set of querries here
    for query in queries:
        wd.get('https://duckduckgo.com')
        #WebDriverWait(wd, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID,"iframe[id^='sp_message_iframe']")))
        #agree = WebDriverWait(wd, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="L2AGLb"]/span/span'))) 
        #agree.click()

        #back to the main page
        #wd.switch_to_default_content()

        search_div = wd.find_elements_by_class_name('search-wrap--home')
        print(search_div)
        search_form = search_div[0].find_elements(By.ID, 'search_form_homepage')
        print(search_form)
        search_input = search_form[0].find_elements(By.ID, 'search_form_input_homepage')
        search_button = search_form[0].find_elements(By.ID, 'search_button_homepage')
        #search_box = wd.find_elements_by_class_name('js-search-input search__input--adv')
        print(search_input)
        #search_box = wd.find_element_by_css_selector('js-search-input search__input--adv')
        search_input[0].send_keys(query)
        search_button[0].click()
        links = fetch_image_urls(query,100,wd,10)
        #images_path = '/Users/anand/Desktop/contri/images'  #enter your desired image path
        images_path = '/Users/madeleineramsey/Desktop/Tegan'
        for i in links:
            persist_image(images_path,query,i)
    wd.quit()
    
