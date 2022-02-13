import requests
import fake_useragent
import time
import pandas as pd
from bs4 import BeautifulSoup


user = fake_useragent.UserAgent().random

header = {'user-agent': user}

#Cсылка на агро сервер поиск
# linkAgroServerSearch = 'https://agroserver.ru/len/'
linkAgroServerSearchSaflor = 'https://agroserver.ru/saflor/'
#Cсылка на агро сервер
linkAgroServer = 'https://agroserver.ru'
#Ссылка на agro russia
# linkAgroRussiaSearch = 'https://agro-russia.com/ru/trade/?adv_search=1&r_id=53&types_id=2&page='
linkAgroRussiaSearchSaflor = 'https://agro-russia.com/ru/trade/?adv_search=1&r_id=790&types_id=2&page='


arrName = []
arrLink = []
arrPrice = []
arrCity = []
arrDate = []
arrOrg = []

dictResult = {
    'Название': '',
    'Цена': '',
    'Город': '', 
    'Опубликовано': '',
    'Организация': '',
    'Ссылка': ''
}

#Функция получения кода страницы
def getSoup(link):
    response = requests.get(link, headers = header)
    soup = BeautifulSoup(response.text, 'lxml')

    return soup

#Добавление в массивы
def additionArr(name, city, price, date, org, link):
    arrName.append(name)
    arrLink.append(link)
    arrCity.append(city)
    arrPrice.append(price)
    arrDate.append(date)
    arrOrg.append(org)

#Функция записи данных в excel
def excelEntry(name, city, price, date, org, link):
        dictResult['Название'] = name
        dictResult['Город'] = city
        dictResult['Цена'] = price
        dictResult['Опубликовано'] = date
        dictResult['Организация'] = org
        dictResult['Ссылка'] = link

        dataFrame = pd.DataFrame(dictResult)
        dataFrame.to_excel("./Dad.xlsx", index=False) 

        print('Успешно перезаписан excel-файл')

#Информация с Агро Сервера
def mainAgroServer():
    indexPage = 1
    
    soupAgroServer = getSoup(linkAgroServerSearchSaflor)

    #Получение кол-ва страниц
    pages = soupAgroServer.find('ul', class_ = 'pg')

    if not pages:
        pages = ['1']
    else:
        pages = pages.find_all('li')
    
    while indexPage <= len(pages):
        # currentLink = 'https://agroserver.ru/len/Y2l0eT18cmVnaW9uPXxjb3VudHJ5PXxtZXRrYT18c29ydD0x/' + str(indexPage) + "/"
        currentLink = linkAgroServerSearchSaflor

        soupAgroServerPage = getSoup(currentLink)

        #Получение всех товаров на странице
        itemsAgroServer = soupAgroServerPage.find_all('div', class_ = 'line')

        
        for i in range(0, len(itemsAgroServer)):
            itemName = itemsAgroServer[i].find('div', class_ = 'th')
            itemLink = linkAgroServer + itemName.find('a').get('href')
            itemPrice = itemsAgroServer[i].find('div', class_ = 'price')
            itemData = itemsAgroServer[i].find('div', class_ = 'date')
            itemOrg = itemsAgroServer[i].find('a', class_ = 'personal_org_menu')
            itemGeo = itemsAgroServer[i].find('div', class_ = 'geo').text.strip()
            
            #Если геолокация начинается с г.
            if itemGeo.find('г.') == 0:
                #Записываем без г.
                newitemGeo = itemGeo[3:].strip()
            #Если геолокация начинается с доставка
            elif itemGeo.find('доставка') == 0:
                newitemGeo = itemGeo.strip()
            else:
                newitemGeo = itemGeo.strip()
            
            #Если есть цена у товара
            if itemPrice:
                print(f"{itemName.text} за {itemPrice.text} опубликован {itemData.text.strip()} у {itemOrg.text.strip()}-> {itemLink}")
                additionArr(itemName.text, newitemGeo, itemPrice.text, itemData.text.strip(), itemOrg.text.strip(), itemLink)
            else:
                print('Цена не указана')
                additionArr(itemName.text, newitemGeo, 'Цена не указана', itemData.text.strip(), itemOrg.text.strip(), itemLink)

            time.sleep(0.5)
        
        print(f'[INFO:] Обработал {indexPage}/{len(pages)}')

        indexPage += 1

def mainAgroRussia():
    indexPage = 1

    soupAgroRussia = getSoup(linkAgroRussiaSearchSaflor + str(indexPage))

    pages = soupAgroRussia.find('span', class_ = 'list')

    if not pages:
        pages = ['1']
    else:
        pages = pages.find_all('a', class_ = 'page')

    while indexPage <= len(pages) + 1:
        currentLink = linkAgroRussiaSearchSaflor + str(indexPage)

        soupAgroRussiaPage = getSoup(currentLink)

        itemsAgroRussia = soupAgroRussiaPage.find_all('div', class_ = 'i_l_i_c_mode3')

        for i in range(0, len(itemsAgroRussia)):
            itemName = itemsAgroRussia[i].find('a', class_ = 'i_title')
            if itemName:
                itemLink = itemName.get('href')
                itemPrice = itemsAgroRussia[i].find('span', class_ = 'i_price')
                if itemPrice:
                    soupAgroRussiaItem = getSoup(itemLink)
                
                    itemDate = soupAgroRussiaItem.find('time')
                    itemCity = soupAgroRussiaItem.find('span', itemprop = 'addressLocality')
                    itemOrg = soupAgroRussiaItem.find('div', class_ = 'ct_user_box_7_1')

                    if itemOrg:
                        itemOrg = itemOrg.text
                    else:
                        itemOrg = 'Не указан'
            
                    print(f'{itemName.text} за {itemPrice.text} -> {itemLink}')
                    additionArr(itemName.text, itemCity.text, itemPrice.text, itemDate.text[:10], itemOrg[:itemOrg.find('/')], itemLink)
                else:
                    soupAgroRussiaItem = getSoup(itemLink)
                
                    itemDate = soupAgroRussiaItem.find('time')
                    itemCity = soupAgroRussiaItem.find('span', itemprop = 'addressLocality')
                    itemOrg = soupAgroRussiaItem.find('div', class_ = 'ct_user_box_7_1')

                    if itemOrg:
                        itemOrg = itemOrg.text
                    else:
                        itemOrg = 'Не указан'
            
                    print(f'{itemName.text} за цена не указана -> {itemLink}')

                    additionArr(itemName.text, itemCity.text, "Цена не указана", itemDate.text[:10], itemOrg[:itemOrg.find('/')], itemLink)

            time.sleep(0.5)

        print(f'[INFO]: Обработал {indexPage}/{len(pages) + 1}')

        indexPage += 1

if __name__ == "__main__":
    start_time = time.time()
    mainAgroServer()
    time.sleep(1.5)
    mainAgroRussia()
    time.sleep(1.5)
    excelEntry(arrName, arrCity, arrPrice, arrDate, arrOrg, arrLink)
    print(time.time() - start_time)
    

