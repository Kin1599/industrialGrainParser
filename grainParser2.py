import requests
import fake_useragent
import time
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.distance import distance
from deep_translator import GoogleTranslator
from colorama import Fore, Back, init


init(autoreset = True)

user = fake_useragent.UserAgent().random

nom = Nominatim(user_agent = user)

header = {
    "user-agent": user
    }

#Спрашиваем пользователя откуда он и дальность закупки
fromCity = input("Откуда вы? (пример: Москва, Саратов) ")

city1 = nom.geocode(fromCity)

my_coordinates = (city1.latitude, city1.longitude)

#Спрашиваем пользователя за какой период брать объявления
try:
    period = int(input("За какой период брать объявления (в днях: например: 14) "))
    dateMax = datetime.datetime.today() - datetime.timedelta(days = period)
except ValueError:
    print(Back.RED + "[INFO]: Некорректно написаны дни, попробуйте ещё раз... ")

try:
    purchaseRange = float(input("Дальность закупки (максимальное расстояние от вашего города в км) "))
except ValueError:
    print(Back.RED + "[INFO]: Некорректно написана дальность, попробуйте ещё раз... ")
    input("Для закрытия нажмите любую кнопку... ")

#Cсылка на агро сервер поиск
productName = {
    "Сафлор": "saflor",
    "Подсолнечник": "podsolnechnik",
    "Лён": "len",
    "Горчица": "gorchitsa",
    "Кукуруза": "kukuruza",
    "Чечевица": "chechevitsa",
    "Гречка": "grechka"
} 

for key, value in productName.items():
    print("Товар {0}: {1}".format(key, value))

inputProductName = input("Введите товар на английском для парсинга сайта agroserver.ru ")

linkAgroServerSearch = f"https://agroserver.ru/{inputProductName}/"
#Cсылка на агро сервер
linkAgroServer = "https://agroserver.ru"


#Ссылка на agro russia
productID = {
    "Сафлор": "790",
    "Подсолнечник": "49",
    "Лён": "53",
    "Горчица": "54",
    "Кукуруза": "43",
    "Чечевица": "40",
    "Гречка": "36"
}

for key, value in productID.items():
    print("ID Товара {0}: {1}".format(key, value))

id_product = input("Введите id товара для парсинга сайта agro-russia.com ")
linkAgroRussiaSearch = f'https://agro-russia.com/ru/trade/?adv_search=1&r_id={id_product}&types_id=2&page='

linkAgroRussia = "https://agro-russia.com/"

name_product = input("Введите название товара на русском языке для парсинга сайта grainboard.ru ")

linkGrainBoard = "https://grainboard.ru/"
linkGrainBoardSearch = f'https://grainboard.ru/trade/search?deal=sale&search={name_product}&p='

arrName = []
arrLink = []
arrPrice = []
arrCity = []
arrDate = []
arrOrg = []

dictResult = {
    "Название": "",
    "Цена": "",
    "Город": "", 
    "Опубликовано": "",
    "Организация": "",
    "Ссылка": ""
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

        print("Успешно перезаписан excel-файл")

#Функция подсчёта расстояния между городами
def distancebetweencities(myCity, alienCity):
    city1 = nom.geocode(myCity)
    city2 = nom.geocode(alienCity)

    my_coordinates = (city1.latitude, city1.longitude)
    alien_coordinates = (city2.latitude, city2.longitude)

    distanceCities = round(distance(my_coordinates, alien_coordinates).km, 2)
    return distanceCities

#Информация с Агро Сервера
def mainAgroServer():
    print(Back.GREEN + Fore.WHITE + f'[INFO]: Началась обработка с сайта {linkAgroServer}')

    indexPage = 1
    
    soupAgroServer = getSoup(linkAgroServerSearch)

    #Получение кол-ва страниц
    try:
        pages = soupAgroServer.find('ul', class_ = 'pg').find_all('li')
    except:
        pages = ["1"]
    
    while indexPage <= len(pages):
        currentLink = f'{linkAgroServerSearch}Y2l0eT18cmVnaW9uPXxjb3VudHJ5PXxtZXRrYT18c29ydD0x/{indexPage}/'
        # currentLink = linkAgroServerSearch

        soupAgroServerPage = getSoup(currentLink)

        #Получение всех товаров на странице
        itemsAgroServer = soupAgroServerPage.find_all('div', class_ = 'line')
        
        for i in range(0, len(itemsAgroServer)):
            #Когда опубликовали товар
            try:
                itemDate = itemsAgroServer[i].find('div', class_ = 'date').text.strip()
                if itemDate.find("сегодня") == -1 or itemDate.find("вчера") == -1:
                    date = GoogleTranslator(source= "auto", target= "en").translate(text = itemDate)
                    date = datetime.datetime.strptime(date, '%d %B %Y')
                    if dateMax > date:
                        print("Устаревшее объявление")
                        continue
            except:
                itemDate = "не указано, когда опубликовано"

            #Город товара
            try:
                itemGeo = itemsAgroServer[i].find('div', class_ = 'geo').text.strip()
                #Если город начинается с г.
                if itemGeo.find('г.') == 0:
                    #Записываем без г.
                    itemGeo = itemGeo[3:].strip()
                    beetween = float(distancebetweencities(fromCity, itemGeo))
                    #Если расстояние между городами больше максимальной дальности закупки, то просто продолжаем
                    if beetween > purchaseRange:
                        print("Город не подходит")
                        continue
                #Если город начинается с доставка
                elif itemGeo.find("доставка") == 0:
                    itemGeo = itemGeo.strip()
                else:
                    itemGeo = itemGeo.strip()
            except:
                itemGeo = "город не указан"

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
                itemPrice = "цена не указана"

            #Организация, продающая товар
            try:
                itemOrg = itemsAgroServer[i].find('a', class_ = 'personal_org_menu').text.strip()
            except:
                itemOrg = "компания не указана"
            
            print(f'{itemName} за {itemPrice} опубликован {itemDate} у {itemOrg}-> {itemLink}')
            additionArr(itemName, itemGeo, itemPrice, itemDate, itemOrg, itemLink)

        time.sleep(1)
        print(Back.GREEN + Fore.WHITE + f'[INFO]: Обработал {indexPage}/{len(pages)}')

        indexPage += 1

def mainAgroRussia():
    print(Back.GREEN + Fore.WHITE + f'[INFO]: Началась обработка с сайта {linkAgroRussia}')

    indexPage = 1

    soupAgroRussia = getSoup(linkAgroRussiaSearch + str(indexPage))

    #Получение кол-ва страниц
    try:
        pages = soupAgroRussia.find('span', class_ = 'list').find_all('a', class_ = 'page')
    except:
        pages = []

    while indexPage <= len(pages) + 1:
        currentLink = linkAgroRussiaSearch + str(indexPage)

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
                    itemPrice = "цена не указана"

                soupAgroRussiaItem = getSoup(itemLink)

                #Когда опубликовали товар
                try:
                    itemDate = soupAgroRussiaItem.find('time').text[:10]
                    if itemDate.find("Сегодня") == -1 or itemDate.find("Вчера") == -1:
                        date = datetime.datetime.strptime(itemDate, '%d-%m-%Y')
                        if dateMax > date:
                            print("Устаревшее объявление")
                            continue
                except:
                    itemDate = "не указано, когда опубликовано"

                #Город товара
                try: 
                    itemCity = soupAgroRussiaItem.find('span', itemprop = 'addressLocality').text

                    beetween = float(distancebetweencities(fromCity, itemCity))
                    #Если расстояние между городами больше максимальной дальности закупки, то просто продолжаем
                    if beetween > purchaseRange:
                        print("Город не подходит")
                        continue
                except:
                    itemCity = "город не указан"
                
                #Организация, продающая товар
                try:
                    itemOrg = soupAgroRussiaItem.find('div', class_ = 'ct_user_box_7_1').text[:itemOrg.find('/')]                 
                except:
                    itemOrg = "компания не указана"

                print(f'{itemName.text} за {itemPrice} -> {itemLink}')
                additionArr(itemName.text, itemCity, itemPrice, itemDate, itemOrg, itemLink)

        time.sleep(1)
        print(Back.GREEN + Fore.WHITE + f'[INFO]: Обработал {indexPage}/{len(pages) + 1}')

        indexPage += 1

def mainGrainBoard(link):
    print(Back.GREEN + Fore.WHITE + f'[INFO]: Началась обработка с сайта {linkGrainBoard}')

    indexPage = 1

    soupGrainBoard = getSoup(link + str(indexPage))

    #Получение кол-ва страниц
    try:
        if soupGrainBoard.find('a', attrs={'title': 'Последняя страница'}):
            pages = soupGrainBoard.find('div', class_='pagerBox').find('a', attrs={'title':'Последняя страница'}).text
            if int(pages) > 9:
                link = soupGrainBoard.find('div', class_='pagerBox').find('a', attrs={'title':'Последняя страница'}).get('href')[:-2]
            else:
                link = soupGrainBoard.find('div', class_='pagerBox').find('a', attrs={'title':'Последняя страница'}).get('href')[:-1]
        else:
            pages = len(soupGrainBoard.find('p', class_='pages').find_all('a'))
    except:
        pages = 1

    while indexPage <= int(pages):
        currentLink = link + str(indexPage)

        print(currentLink)
        soupGrainBoardPage = getSoup(currentLink)

        #Получение всех товаров на странице
        itemsGrainBoard = soupGrainBoardPage.find_all('tr', class_='offer-row')

        for i in range(0, len(itemsGrainBoard)):
            #Когда опубликовали товар
            try:
                itemDate = itemsGrainBoard[i].find('td', class_='td-date').find('span').get('title').strip()
                date_new = itemDate[:itemDate.find('г')]
                date = GoogleTranslator(source= "auto", target= "en").translate(text = date_new)
                date = datetime.datetime.strptime(date, '%B %d, %Y')
                if dateMax > date:
                    print("Устаревшее объявление")
                    continue
            except:
                itemDate = "не указано, когда опубликовано"

            #Город товара
            try:
                itemCity = itemsGrainBoard[i].find('div', class_='p-city').text.strip()
                beetween = float(distancebetweencities(fromCity, itemCity))
                #Если расстояние между городами больше максимальной дальности закупки, то просто продолжаем
                if beetween > purchaseRange:
                    print("Город не подходит")
                    continue
            except:
                itemCity = "город не указан"

            #Берём имя товара
            try:
                itemName = itemsGrainBoard[i].find('div', class_='row').text.strip()
            except:
                itemName = "без названия"
            
            #Ссылка товара
            try:
                itemLink = "https:" + itemsGrainBoard[i].find('div', class_='row').find('a').get('href')
            except:
                itemLink = "ссылка не найдена"

            #Берём цену на товар
            try:
                itemPrice = itemsGrainBoard[i].find('td', class_='td-name').find('span', class_='price').text.strip()
            except:
                itemPrice = "цена не указана"

            #Организация, продающая товар
            try:
                itemOrg = itemsGrainBoard[i].find('div', class_='media-body').find('a').text.strip()
            except:
                itemOrg = "компания не указана"
            
            print(f'{itemName} за {itemPrice} -> {itemLink}')
            additionArr(itemName, itemCity, itemPrice, itemDate, itemOrg, itemLink)

        time.sleep(1.5)
        print(Back.GREEN + Fore.WHITE + f'[INFO]: Обработал {indexPage}/{pages}')

        indexPage += 1


def main():
    start_time = time.time()
    # mainAgroServer()
    # time.sleep(1.5)
    # mainAgroRussia()
    # time.sleep(1.5)
    mainGrainBoard(linkGrainBoardSearch)
    time.sleep(1.5)
    excelEntry(arrName, arrCity, arrPrice, arrDate, arrOrg, arrLink)
    print(time.time() - start_time)
    print(Back.GREEN + Fore.WHITE + input("[INFO]: Программа успешно завершена -> для выхода нажмите любую кнопку... "))

if __name__ == "__main__":
    main()

