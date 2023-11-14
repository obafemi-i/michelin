from playwright.sync_api import sync_playwright, Playwright
from bs4 import BeautifulSoup
import requests
import time
import os
import pandas as pd


path = os.getcwd()

shop_domain_file = 'michelin_my_maps_Manipulated_output.csv'
scraped_urls_file = 'new_scraped.txt'

domains = []

# 6992
# get individual domain URLs from csv file
df = pd.read_csv(shop_domain_file)
new_head = df.head(6992)
for index, row in new_head.iterrows():
    restaurant = row['Title'] + ' ' + row['Address']
    domains.append(restaurant)
    # domains.append(row['Michelin Url'])


# Load previously scraped URLs from the file
try:
    with open(scraped_urls_file, 'r') as file:
        scraped_urls = set(file.read().splitlines())
except FileNotFoundError:
    scraped_urls = set()


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    page = context.new_page()
    for domain in domains:
        # Check if the URL has already been scraped, if it has been scraped it will be skipped
        if domain in scraped_urls:
            print(f"Skipping {domain} as it has already been scraped.")
            continue

        # 'https://guide.michelin.com/en/restaurants?q='
        page.goto(f'https://guide.michelin.com/en/restaurants?q={domain}')
        page.click('div.flex-fill')

        time.sleep(5)
    

        trial = page.inner_html('body')
        soup = BeautifulSoup(trial, 'lxml')


        images = soup.find_all('img')

        for img in images:
            linksss = img.get('src')
            # print(linksss)
        # try:
            if 'cloudimg' in linksss:
                # print('cloudy',linksss.split('?')[0])
                actual = linksss.split('?')[0]
                break
        # except TypeError:
        #     pass


        # image name
        length = len(scraped_urls)
        imageName = f'{length+1}.jpg'
        
        with open(os.path.join(path, imageName), "wb") as f:
            image = requests.get(actual)
            f.write(image.content)


        # Add the scraped URL to the set of scraped URLs
        scraped_urls.add(domain)

        # Save the scraped URLs to the file
        with open(scraped_urls_file, 'a') as file:
            file.write(domain + '\n')

        print(f'{domain} succesfully scraped, moving on...')
        time.sleep(4)


    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

