import requests
from bs4 import BeautifulSoup
import smtplib
import time
import soupsieve
from products import PRODUCTS
from settings import SETTINGS

HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
}

def read_price(URL, soup):
  if('flipkart' in URL):
    price_string = soup.select("#container > div > div._2c7YLP.UtUXW0._6t1WkM._3HqJxg > div._1YokD2._2GoDe3 > div._1YokD2._3Mn1Gg.col-8-12 > div:nth-child(2) > div > div.dyC4hf > div.CEmiEU > div > div")[0].get_text()
    return int(price_string[1:].replace(',', ''))
  elif('amazon'  in URL):
    return int(float(soup.find(id='priceblock_ourprice').get_text()[1:].replace(',', '').strip()))
  else:
    print('URL not of flipkart or amazon')
    return

def check_price():
  for product in PRODUCTS:
    try:
      page = requests.get(product['URL'], headers=HEADERS)
      soup = BeautifulSoup(page.content, 'html.parser')

      title = soup.title.text
      priceInt = read_price(product['URL'], soup)

      print(f'Current price: {priceInt} | Target price: {product["TARGET_PRICE"]} | {title}')
      if(priceInt <= product['TARGET_PRICE']):
        print(f'Price below {product["TARGET_PRICE"]}')
        send_email(title=title, currentPrice=priceInt, product=product)
    except Exception as e:
      print(e)

def send_email(title, currentPrice, product):
  print('sending email')
  try:
    server = smtplib.SMTP(SETTINGS['SMTP_SERVER'], SETTINGS['PORT'])
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(SETTINGS['EMAIL'], SETTINGS['PASSWORD'])

    subject = f'Price Rs. {currentPrice} | {title}'
    msg = f"""Subject: {subject}

    {title}
    Price dropped below Rs. {product['TARGET_PRICE']}
    {product['URL']}
    """
    server.sendmail(SETTINGS['EMAIL'], SETTINGS['EMAIL'], msg)
    print('email has been sent')
    server.quit()
  except Exception as e:
    print(e)

while(True):
  check_price()
  time.sleep(60*60) # Check every 1 hour = 60*60 seconds