import time
from datetime import datetime
from decimal import Decimal
import mysql.connector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re


"""
    Database table movies scheme

+-------------------+---------------+------+-----+---------+----------------+
| Field             | Type          | Null | Key | Default | Extra          |
+-------------------+---------------+------+-----+---------+----------------+
| id                | int(11)       | NO   | PRI | NULL    | auto_increment |
| title             | varchar(255)  | NO   |     | NULL    |                |
| release_date      | date          | YES  |     | NULL    |                |
| poster            | longblob      | YES  |     | NULL    |                |
| url               | varchar(2084) | NO   |     | NULL    |                |
| rating            | decimal(2,1)  | NO   |     | NULL    |                |
| number_of_ratings | int(20)       | NO   |     | NULL    |                |
| duration          | time          | NO   |     | NULL    |                |
| plot              | text          | YES  |     | NULL    |                |
| trailer_file      | varchar(50)   | YES  |     | NULL    |                |
| narration         | text          | YES  |     | NULL    |                |
+-------------------+---------------+------+-----+---------+----------------+

"""


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
        # Example
        # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

        #initialize driver
        self.chrome_options = Options()
        self.chrome_options.add_argument(f"user-agent={self.user_agent}")
        self.driver = webdriver.Chrome(options=chrome_options)

        
    def db_insert(self, table, columns, values):
        insert_query = f""" INSERT INTO {table}
                        {columns}
                        VALUES (%s, %s, %s, %s, %s);"""
        
        self.cursor.execute(insert_query, values)
        self.conn.commit()

    def db_delete(self, table, condition)
        delete_query = f"""DELETE FROM {table} WHERE {condition};"""
        self.cursor.execute(insert_query)
        self.conn.commit()


    def db_update(self, table, columns, values, condition):
        for i in range(len(columns)):
            update_query = f""" UPDATE {table}
                                SET {columns[i]} = {values[0]}
                                WHERE {condition};"""
            self.cursor.execute(insert_query)
            self.conn.commit()

    def db_rows(self, table):
        query = "SELECT * FROM movies"
        cursor.execute(query)
        return cursor.fetchall()

    def quit(self):
        self.cursor.close()
        self.conn.close()
        self.driver.quit()

    def navigate(self, url):
        self.driver.get(url)

    def find_element_by(self, method, value):
        return self.driver.find_element(By.method, value)


    #disclaimer this project and intended web scraping acts are for educational puprposes only
    #and not intended for any commercial use :)
    def populate_database_movies(self):
        """ Populate database with title, url, rating, number_of_ratings, duration, etc """

        #------------------------------------------------------------------ title, url, rating, number_of_ratings, duration ------------------------------------------------#
        self.navigate("https://www.imdb.com/search/title/?title_type=feature&user_rating=6,&num_votes=10000,")
        ul = self.find_element_by(XPATH, '//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul')
        button = self.find_element_by(XPATH, '//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/div[2]/div/span/button')

        for i in range(175):
            current_scroll_position = self.driver.execute_script("return window.scrollY;")
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll_position + 10000});")

            if i == 0:
                time.sleep(10)
            else:
                time.sleep(10)
            try:
                button.click()
            except Exception as e:
                print("Reached the end")
            time.sleep(10)


        lis = ul.find_element(By.TAG_NAME, 'li')

        time.sleep(10)
        for i in range(1, 8788):
            title_element = self.find_element_by(XPATH, f'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[{i}]/div/div/div/div[1]/div[2]/div[1]/a/h3')
            title = title_element.text
            title = title[3:]
            url_element = self.find_element_by(XPATH, f'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[{i}]/div/div/div/div[1]/div[2]/div[1]/a')
            url_text = url_element.get_attribute('href')
            url_aux = ""
            for j in url_text:
                if j == "?":
                    break
                else:
                    url_aux += j
            url = url_aux
            rating_element_xpath = f'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[{i}]/div/div/div/div[1]/div[2]/span/div/span/span[1]'
            rating_element = self.find_element_by(XPATH, rating_element_xpath)
            rating = Decimal(rating_element.text)
            number_of_ratings_element = self.find_element_by(XPATH, f'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[{i}]/div/div/div/div[1]/div[2]/span/div/span/span[2]')
            number_of_ratings = number_of_ratings_element.text
            if number_of_ratings[-2] == "K":
                number_of_ratings = int(number_of_ratings[2:-2]) * 1000
            elif number_of_ratings[-2] == "M":
                number_of_ratings = float(number_of_ratings[2:-2]) * 1000000
                number_of_ratings = int(number_of_ratings)
                
            duration_element = self.find_element_by(XPATH, f'//*[@id="__next"]/main/div[2]/div[3]/section/section/div/section/section/div[2]/div/section/div[2]/div[2]/ul/li[{i}]/div/div/div/div[1]/div[2]/div[2]/span[2]')
            duration_text = duration_element.text
            if duration_text[1] == 'h':
                if len(duration_text) == 5:
                    duration = "0" + duration_text[0] + ":" + "0" + duration_text[3] + ":00"
                else:
                    duration = "0" + duration_text[0] + ":" + duration_text[3] + duration_text[4] + ":00"
            else:
                duration = "00:" + duration_text[0:2] + ":00"

            duration = datetime.strptime(duration, "%H:%M:%S").time()
            values = (title, url, rating, number_of_ratings, duration)        
            self.db_insert( "movies", "(title, url, rating, number_of_ratings, duration)", values)
            #----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

            #-----------------------------------------------------------Adding Release_date ---------------------------------------------------------------------------------------------#

            def extract_and_convert_date(text):
                # Define a regex pattern to capture "Month Day Year" in any order
                pattern = r'(?P<month>[A-Za-z]+)?\s*(?P<day>\d{1,2})?\s*,?\s*(?P<year>\d{4})?'
                match = re.search(pattern, text)
                
                if match:
                    # Extract matched groups for month, day, and year
                    month_str = match.group('month')
                    day_str = match.group('day')
                    year_str = match.group('year')
                    
                    # If `day_str` is missing, set it to a default value
                    if not day_str:
                        day_str = '1'  # Default day
                    
                    # Check if both `month` and `year` components are available
                    if month_str and year_str:
                        # Convert month name to a month number and create a date string
                        date_str = f"{day_str} {month_str} {year_str}"
                        date_obj = datetime.strptime(date_str, "%d %B %Y")
                        # Convert to MySQL-compatible format (YYYY-MM-DD)
                        mysql_date = date_obj.strftime("%Y-%m-%d")
                        return mysql_date
                    else:
                        raise ValueError("Incomplete date information found in the input string")
                else:
                    raise ValueError("No valid date found in the input string")

            rows = self.db_rows("movies")


            for row in rows:
                driver.get(row[4] + "releaseinfo")
                wait = WebDriverWait(self.driver, 10)
                j = 1 
                sibling = 0
                try:
                    button = self.find_element_by(XPATH, '//*[@id="__next"]/main/div/section/div/section/div/div[1]/section[1]/div[2]/ul/div/span[2]/button')
                    button.click()
                except Exception as f:
                    print("no button all")

                try:
                    button = self.find_element_by(XPATH, '//*[@id="__next"]/main/div/section/div/section/div/div[1]/section[1]/div[2]/ul/div/span[1]/button')
                    button.click()
                except Exception as e:
                    print("no button 'more'")

                while sibling != -1:
                    try:
                        sibling = driver.find_element_by(XPATH, f'//*[@id="rel_{j}"]/div/ul/li/span[2]')
                        if "internet" in sibling.text.lower() or "digital" in sibling.text.lower() or "dvd" in sibling.text.lower() or "blu-ray" in sibling.text.lower() or "re-release" in sibling.text.lower() or "istanbul" in sibling.text.lower():
                            release_date_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="rel_{j}"]/div/ul/li/span[1]')))
                            try:
                                extract_and_convert_date(release_date_element.text)
                            except Exception as a:
                                j += 1
                                continue
                            break
                        try:
                            extract_and_convert_date(release_date_element.text)
                        except Exception as b:
                            j += 1
                            continue
                        print(j)
                        j += 1

                    except Exception as c:
                        release_date_element = wait.until(EC.presence_of_element_located((By.XPATH, f'//*[@id="rel_{j}"]/div/ul/li/span[1]')))
                        try:
                            extract_and_convert_date(release_date_element.text)
                        except Exception as d:
                            j += 1
                            continue
                        sibling = -1

                release_date = release_date_element.text
                print(release_date)
                release_date = extract_and_convert_date(release_date)
                self.db_update("movies", ("release_date", ), (release_date, ), f"id = {row[0]}")

            #-------------------------------------------------------------------------------------------------------------------------------------------------#
        

                


