# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt
import time

# Set up Splinter
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path':ChromeDriverManager().install()}
    browser = Browser('chrome',**executable_path, headless = True) # set headless = False to watch it runs
    #time.sleep(10)
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in dictionary
    data = {
        'news_title': news_title,
        'news_paragraph': news_paragraph,
        'featured_image': featured_image(browser),
        'facts': mars_facts(),
        'last_modified':dt.datetime.now(),
        'full_image':hemisphere(browser)
    }
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):    

    # Visit the mars nasa news site
    url = 'http://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text',wait_time = 1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None


    return news_title, news_p

def featured_image(browser):
    
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    
    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html,'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img',class_ = 'fancybox-image').get('src')
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'http://spaceimages-mars.com/{img_url_rel}'

    return img_url

# Tables
def mars_facts():
    
    try:
        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    df.columns = ['description','Mars','Earth']
    df.set_index('description', inplace = True)

    return df.to_html()

# Hemisphere data
def hemisphere(browser):
    # Visit URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # Create a list to hold the images and titles
    hemisphere_image_urls = []
    # Obtain list of urls to go to each page
    html = browser.html
    news_soup = soup(html, 'html.parser')
    img_list = news_soup.find_all('div',class_="item")
    # loop through each image's page
    for i in img_list:
        # Get the page's url
        link_to_click = i.find('a',class_='itemLink')
        full_url = url+link_to_click['href']
        # Go to the page
        browser.visit(full_url)
        full_soup = soup(browser.html,'html.parser')
        img_link = full_soup.select_one("div",class_="downloads")
        full_image_link = url+img_link.find_all("li")[0].a["href"]
        title = full_soup.find("h2",class_="title").text
        # Adding image url and title to the list.
        hemisphere_image_urls.append(
            {"image_url":full_image_link,
            "title":title}
            )
    return hemisphere_image_urls

if __name__=="__main__":
    # if running as script, print scraped data
    print(scrape_all())

