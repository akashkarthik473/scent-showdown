import sqlite3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By  # For element location
from selenium.webdriver.support.ui import WebDriverWait  # For waiting until elements load
from selenium.webdriver.support import expected_conditions as EC  # For specifying the condition
from bs4 import BeautifulSoup
import time
import re



# Read the HTML content from the file
with open("./fragrances2.html", "r", encoding="utf-8") as file:
    html_content = file.read()
    print("Success")

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all anchor tags with class 'link-span'
anchors = soup.find_all('a')

# Initialize a list to store URLs
anchor_urls = []

# Process and store the href of anchors
for anchor in anchors:
    href = anchor.get('href')  # Get the href attribute
    if href and href[-5:] == ".html" and "perfume" in href:  # Ensure it's not None
        integers = re.findall(r'\d+', href)
        integers = [int(num) for num in integers]  # Convert to integers
        if len(integers) == 2:
            anchor_urls.append(integers[1])
        else:
            anchor_urls.append(integers[0])


connection = sqlite3.connect('database.db')  # Creates a database file if it doesn't exist
cursor = connection.cursor()

for numbers in anchor_urls[150:]:
    print(numbers)
    cursor.execute('INSERT OR IGNORE INTO fragrances (image_id) VALUES (?)', (numbers,))
    connection.commit()
    print(f"ID {numbers} processed (inserted if unique).")

connection.close()
