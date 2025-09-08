#!/usr/bin/env python3
import sys, json, time, os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Input JSON passed as single argv
input_json = json.loads(sys.argv[1])
prompt = input_json.get("prompt")
image_url = input_json.get("image_url")

if not prompt or not image_url:
    print(json.dumps({"error":"missing prompt or image_url"}))
    sys.exit(1)

TMP_IMAGE = "/tmp/image.jpg"

# Download image (must be a direct image URL)
resp = requests.get(image_url, timeout=30)
resp.raise_for_status()
with open(TMP_IMAGE, "wb") as f:
    f.write(resp.content)

# Selenium + Chrome options
chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
chromedriver_bin = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

options = Options()
options.add_argument("--headless=new")  # new headless if Chrome supports it, fallback to --headless if needed
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,720")
options.binary_location = chrome_bin

service = Service(executable_path=chromedriver_bin)
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.set_page_load_timeout(90)
    driver.get("https://vheer.com/ai-image-to-video")

    # Wait for file input, accept cookie UI changes if needed
    wait = WebDriverWait(driver, 30)
    file_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
    # Upload file
    file_input.send_keys(TMP_IMAGE)

    # Type prompt into first textarea (adjust selector if site changed)
    textarea = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea")))
    textarea.clear()
    textarea.send_keys(prompt)

    # Click generate button (adjust selector if site changed)
    generate_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.generate-button")))
    generate_btn.click()

    # Wait for the generated video element (increase timeout if slow)
    video_wait = WebDriverWait(driver, 300)  # up to 5 minutes
    video_el = video_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "video.generated-video-element")))
    video_url = video_el.get_attribute("src")
    if not video_url:
        raise Exception("video element present but no src found")

    print(json.dumps({"video_url": video_url}))
    sys.exit(0)

except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
finally:
    try:
        driver.quit()
    except:
        pass