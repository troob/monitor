# test driver

# from selenium import webdriver # need to read html5 webpages
# from webdriver_manager.chrome import ChromeDriverManager # need to access dynamic webpages

import reader

url = 'https://google.com'
driver = reader.open_react_website(url)