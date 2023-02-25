from settings import ChromeSettings
# from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
import time
import os

from selenium import webdriver
from dotenv import load_dotenv

host = load_dotenv(".env")
host = os.environ.get("HOST_URL")

class LaunchSpider:
    def __init__(self) -> None:
        self.chromedriver = ChromeSettings(set_chrome_options= False)
        self.driver = self.chromedriver.chef(host+"auth")
        self.waiting_condition = WebDriverWait(self.driver, 20)

    def login(self,phone,password):
        """Login to App"""

        phone_number_field = self.driver.find_element(By.XPATH,value= '//*[@id="root"]/div/div/div[2]/div/form/div[2]/div/div/input')
        phone_number_field.click()
        phone_number_field.send_keys(phone)

        login_button = self.driver.find_element(By.XPATH,value = '//*[@id = "root"]/div/div/div[2]/div/form/div[3]/div/button')
        login_button.click()

        password_field = self.waiting_condition.until(EC.presence_of_element_located((By.XPATH, '//*[@id="password"]')))
        password_field.find_element(by = By.XPATH,value = '//*[@id="password"]')
        password_field.click()
        password_field.send_keys(password)

        login_button = self.driver.find_element(by= By.XPATH,value= '//*[@id="root"]/div/div/div[2]/div/form/div[4]/div/button' )
        login_button.click()
        return True
    
    def load_data(self):
        """Load all data"""
        time.sleep(5)    
        product_links = set() #stores product links
        href = host+"categories" 
        for i in range(2,53):
        #for href in links:

            self.driver.get(f"{href}/{i}")
            #wait explicitly for grid to show

            #find the number of cards available
            try:
                grid = self.waiting_condition.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'grid')]"))) 
                product_cards = self.driver.find_elements(by = By.XPATH,value = "//a[contains(@class,'flex flex-col')]")
                #get product links
                for card in product_cards:
                    product_links.add(card.get_property('href'))

            except exceptions.NoSuchElementException:
                continue
            except exceptions.TimeoutException as timeout:
                print(f'{href}/{i} generated a timeout exception')
                continue

            else:
                if len(product_cards)>=19:
                    self.scroll_page(clickable_xpath = "//a[contains(@class,'flex flex-col')][1]",
                                    items_xpath="//a[contains(@class,'flex flex-col')]")


        #get data from product links
        database = {}
        for link in product_links:
            database.update(self.get_products(link))
            print(database)
        return database

    def get_products(self,link):
        
        data = {}
        self.driver.get(link)
        description = self.waiting_condition.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[3]/div/p')))
        #description  = self.driver.find_element(by = By.XPATH,value = '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[3]/div/p')
        description = description.text
        data.update({"description":description})

        price = self.driver.find_element(by = By.XPATH,value = '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[3]')
        price = price.text
        data.update({"price":price})
        
        name =  self.driver.find_element(by = By.XPATH,value = '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[1]')
        name = name.text
        data.update({"product_name":name})

        product_code = self.driver.find_element(by = By.XPATH,value = '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/div[1]/span[2]')
        rating = self.driver.find_element(by = By.XPATH,value = '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/div[3]/div[1]/span')
        rating = rating.text
        data.update({"rating":rating})

        delivery = self.driver.find_element(by = By.XPATH,value = '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/div[3]/div[2]/span')
        delivery = delivery.text
        data.update({"delivery":delivery})
        
        similar_products = self.driver.find_elements(by = By.XPATH,value = '//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/div[2]/div//img')
        #similar_products = self.driver.find_element(by = By.CLASS_NAME,value = "keen-slider")
        #for tag in similar_products
        return data


    def scroll_page(self,clickable_xpath:str,items_xpath:str):
        retry = 5
        current_size_of_items = 0
        retry = 0
        clickable = self.driver.find_element(by = By.XPATH,value= clickable_xpath)

        clickable = self.waiting_condition.until(EC.element_to_be_clickable((By.XPATH, clickable_xpath)))

        while True:
            clickable.send_keys(Keys.END)
            items = self.driver.find_elements(by = By.XPATH,value = items_xpath)
            if len(items) == current_size_of_items:
                retry += 1
            else:
                retry = 0
                current_size_of_items = len(items)
            if retry == 5:
                break
            print({"current size of items":current_size_of_items,"retry":retry})
            time.sleep(5)

            #----- temporal script for testing ------
            if current_size_of_items > 30:
                break
            #--------------------

        return items

        
    def __call__(self):
        
        try:
            response = self.login(phone = 551409594,password = "M1I1K1E1y!")
            assert response is True
        except AssertionError as ass_error:
            raise (ass_error,"Login Failed")
        
        items = self.load_data()
        print(items)





if __name__ == "__main__":
    spider = LaunchSpider()
    spider()









