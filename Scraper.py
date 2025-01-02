import time
from datetime import datetime
from decimal import Decimal
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class Scraper:
    def __init__(self, host, user, password, database, user_agent):
        # Replace these credentials with yours of local sql database
        # our database is kinda large so we didn't manage to host it on a server

        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = mysql.connector.connect(host = self.host,
                               user = self.user,
                               password = self.password,
                               database = self.database)

        self.cursor = conn.cursor()
        self.user_agent = user_agent
        # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        
        
    def db_insert(self)
