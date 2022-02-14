import requests
import fake_useragent
import time
import pandas as pd
from bs4 import BeautifulSoup

user = fake_useragent.UserAgent().random

header = {
    'user-agent': user
    }

#Cсылка на агро сервер поиск
productName = {
    "Сафлор": "saflor",
    "Подсолнечник": "podsolnechnik",
    "Лён": "len",
    "Горчица": "gorchitsa"
} 

for key, value in productName.items():
    print("Товар {0}: {1}".format(key, value))

inputProductName = input("Введите товар на английском для парсинга сайта agroserver.ru ")

linkAgroServerSearchSaflor = f'https://agroserver.ru/{inputProductName}/'
#Cсылка на агро сервер
linkAgroServer = 'https://agroserver.ru'


#Ссылка на agro russia
productID = {
    "Сафлор": "790",
    "Подсолнечник": "49",
    "Лён": "53",
    "Горчица": "54"
}

for key, value in productID.items():
    print("ID Товара {0}: {1}".format(key, value))

id_product = input("Введите id товара для парсинга сайта agro-russia.com ")
linkAgroRussiaSearchSaflor = f'https://agro-russia.com/ru/trade/?adv_search=1&r_id={id_product}&types_id=2&page='

linkAgroRussia = 'https://agro-russia.com/'

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
    print(f'[INFO]: Началась обработка с сайта {linkAgroServer}')

    indexPage = 1
    
    soupAgroServer = getSoup(linkAgroServerSearchSaflor)

    #Получение кол-ва страниц
    try:
        pages = soupAgroServer.find('ul', class_ = 'pg').find_all('li')
    except:
        pages = ['1']
    
    while indexPage <= len(pages):
        # currentLink = 'https://agroserver.ru/len/Y2l0eT18cmVnaW9uPXxjb3VudHJ5PXxtZXRrYT18c29ydD0x/' + str(indexPage) + "/"
        currentLink = linkAgroServerSearchSaflor

        soupAgroServerPage = getSoup(currentLink)

        #Получение всех товаров на странице
        itemsAgroServer = soupAgroServerPage.find_all('div', class_ = 'line')
        
        for i in range(0, len(itemsAgroServer)):
            
            #Берём имя товара и ссылку на товар
            try:
                itemName = itemsAgroServer[i].find('div', class_ = 'th')
                itemLink = linkAgroServer + itemName.find('a').get('href')
                itemName = itemName.text
            except:
                itemName = "Без имени"    

            #Берём цену товара
            try:
                itemPrice = itemsAgroServer[i].find('div', class_ = 'price').text
            except:
                itemPrice = 'цена не указана'
            
            #Когда опубликовали товар
            try:
                itemData = itemsAgroServer[i].find('div', class_ = 'date').text.strip()
            except:
                itemData = 'не указано, когда опубликовано'

            #Организация, продающая товар
            try:
                itemOrg = itemsAgroServer[i].find('a', class_ = 'personal_org_menu').text.strip()
            except:
                itemOrg = 'компания не указана'

            #Город товара
            try:
                itemGeo = itemsAgroServer[i].find('div', class_ = 'geo').text.strip()
                #Если город начинается с г.
                if itemGeo.find('г.') == 0:
                    #Записываем без г.
                    itemGeo = itemGeo[3:].strip()
                #Если город начинается с доставка
                elif itemGeo.find('доставка') == 0:
                    itemGeo = itemGeo.strip()
                else:
                    itemGeo = itemGeo.strip()
            except:
                itemGeo = 'город не указан'
            
            print(f"{itemName} за {itemPrice} опубликован {itemData} у {itemOrg}-> {itemLink}")
            additionArr(itemName, itemGeo, itemPrice, itemData, itemOrg, itemLink)

        time.sleep(1)
        print(f'[INFO]: Обработал {indexPage}/{len(pages)}')

        indexPage += 1

def mainAgroRussia():
    print(f'[INFO]: Началась обработка с сайта {linkAgroRussia}')

    indexPage = 1

    soupAgroRussia = getSoup(linkAgroRussiaSearchSaflor + str(indexPage))

    #Получение кол-ва страниц
    try:
        pages = soupAgroRussia.find('span', class_ = 'list').find_all('a', class_ = 'page')
    except:
        pages = []

    while indexPage <= len(pages) + 1:
        currentLink = linkAgroRussiaSearchSaflor + str(indexPage)

        soupAgroRussiaPage = getSoup(currentLink)

        #Получение всех товаров на странице
        itemsAgroRussia = soupAgroRussiaPage.find_all('div', class_ = 'i_l_i_c_mode3')

        for i in range(0, len(itemsAgroRussia)):
            
            #Берём имя товара
            itemName = itemsAgroRussia[i].find('a', class_ = 'i_title')
            
            if itemName:
                #Ссылка товара
                itemLink = itemName.get('href')

                #Берём цену на товар
                try:
                    itemPrice = itemsAgroRussia[i].find('span', class_ = 'i_price').text
                except:
                    itemPrice = 'цена не указана'

                soupAgroRussiaItem = getSoup(itemLink)
                
                #Когда опубликовали товар
                try:
                    itemDate = soupAgroRussiaItem.find('time').text[:10]
                except:
                    itemDate = 'не указано, когда опубликовано'

                #Город товара
                try: 
                    itemCity = soupAgroRussiaItem.find('span', itemprop = 'addressLocality').text
                except:
                    itemCity = 'город не указан'
                
                #Организация, продающая товар
                try:
                    itemOrg = soupAgroRussiaItem.find('div', class_ = 'ct_user_box_7_1').text[:itemOrg.find('/')]                 
                except:
                    itemOrg = 'компания не указана'

                print(f'{itemName.text} за {itemPrice} -> {itemLink}')
                additionArr(itemName.text, itemCity, itemPrice, itemDate, itemOrg, itemLink)

        time.sleep(2)
        print(f'[INFO]: Обработал {indexPage}/{len(pages) + 1}')
        indexPage += 1


def main():
    start_time = time.time()
    mainAgroServer()
    time.sleep(1.5)
    mainAgroRussia()
    time.sleep(1.5)
    excelEntry(arrName, arrCity, arrPrice, arrDate, arrOrg, arrLink)
    print(time.time() - start_time)
    print(input("[INFO]: Программа успешно завершена -> для выхода нажмите любую кнопку... "))

if __name__ == "__main__":
    main()

