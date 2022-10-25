import math
import time
import numpy as np
from selenium import webdriver
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


class Booking:
    
    dbsqlite = None
    
    def __init__(self, city, filename, start_date,
                 end_date, nbr_adults=None,
                 nbr_children=None, ages_of_children=None, nbr_room=None):
        """
        :param city: string
        :param filename: string
        :param start_date: MM-dd-yyyy
        :param end_date: MM-dd-yyyy
        :param nbr_adults: int
        :param nbr_children: int
        :param ages_of_children: array with len equal to number of children
        :param nbr_room: int
        """
        self.start_date = start_date
        self.nbr_adults = nbr_adults
        self.end_date = end_date
        self.nbr_children = nbr_children
        self.ages_of_children = ages_of_children
        self.nbr_room = nbr_room
        self.city = city
        self.filename = filename

        if type(ages_of_children) is not list:
            raise "ages of children must be an array"

        if len(self.ages_of_children) != self.nbr_children:
            raise "the number of children must be equal to the length of the array of their ages"

        self.driver = webdriver.Chrome(executable_path='driver/chromedriver')
        print("[DEBUG] Current session is {}".format(self.driver.session_id))
        self.driver.delete_all_cookies()
        
        
    def getMonthCorrespondances(self):
        return {
            "01": "enero",
            "02": "febrero",
            "03": "marzo",
            "04": "abril",
            "05": "mayo",
            "06": "junio",
            "07": "julio",
            "08": "agosto",
            "09": "septiembre",
            "10": "Octubre",
            "11": "noviembre",
            "12": "diciembre",
        }
            
            
    def getLocalisationFromAdd(self, add):
        """
        :param add: "address_hotel"
        :return: [latitude, longitude] else None
        """
        try:
            location = Nominatim(user_agent="main").geocode(add)
            return [location.latitude, location.longitude] if location is not None else np.nan
        except:
            return np.nan
        

    def separateAmericanDate(self, date):
        """
        :param date: MM-dd-yyyy
        :return: day, month, year
        """
        month, day, year = date.split("-")
        return day, month, year


    def search_city(self, city):
        time.sleep(5)
        self.driver.find_element(by="id", value="ss").send_keys(city)


    def search(self):
        time.sleep(2)
        self.driver.find_element(by="class name", value="sb-searchbox__button ").click()


    def get_by_xpath(self, xpath):
        return self.driver.find_element(by="xpath", value=xpath)


    def accept_cookies(self):
        time.sleep(2)
        try:
            self.driver.find_element(by="id", value="onetrust-accept-btn-handler").click()
        except:
            ...
            

    def set_good_month_year(self, month, year):
        try:
            is_good_month_shows = False
            while not is_good_month_shows:
                time.sleep(3)
                current_date = self.get_by_xpath("//div[contains(@aria-live, 'polite')]").text
                if len(current_date) == 0:
                    current_date = self.driver.find_element(by="xpath", value="//*[contains(@class, 'bui-calendar__wrapper')]")
                    current_date = current_date.text.split(" ")[0:2]
                    current_date[1] = str(''.join(i for i in current_date[1] if i.isdigit()))
                    
                if month in current_date and year in current_date:
                    is_good_month_shows = True
                else:
                    try:
                        self.get_by_xpath("//button[contains(@class, 'c9fa5fc96d be298b15fa')]").click()
                    except:
                        self.get_by_xpath("//*[local-name()='div' and contains(@class, 'bui-calendar__control bui-calendar__control--next')]").click()
        except:
            ...


    def show_calendar(self):
        try:
            self.driver.find_element(by="xpath", value="//div[contains(@class, 'sb-date-field__display')]").click()
        except:
            self.driver.find_element(by="xpath", value="//button[contains(@data-testid, 'date-display-field-end')]").click()


    def select_day(self, day):
        # permet de scroller quand on n'a pas le bon mois affiché
        xpathDay = "//span[contains(@aria-hidden, 'true') and contains(text(), '{}')]".format(int(day))
        self.get_by_xpath(xpathDay).click()


    def set_date(self, start_date, end_date):
        """
        :param end_date: MM-dd-yyyy
        :param start_date: MM-dd-yyyy
        """
        start_day, start_month, start_year = self.separateAmericanDate(start_date)
        end_day, end_month, end_year = self.separateAmericanDate(end_date)

        monthCorrespondances = self.getMonthCorrespondances()
        start_month = monthCorrespondances[start_month]
        end_month = monthCorrespondances[end_month]
        
        time.sleep(2)
        self.set_good_month_year(start_month, start_year)
        self.select_day(start_day)
        
        self.show_calendar()
        
        time.sleep(2)
        self.set_good_month_year(end_month, end_year)
        self.select_day(end_day)


    def get_names_and_links_in_cards(self):
        return self.driver.find_elements(by="xpath", value="//a[contains(@class, 'e13098a59f')]")


    def get_names(self):
        return list(
            map(lambda hotel: hotel.text.split("\n")[0] if hotel is not None else np.nan,
                self.get_names_and_links_in_cards()))


    def get_links(self):
        return list(map(lambda hotel: hotel.get_attribute("href"), self.get_names_and_links_in_cards()))


    def get_grades(self):
        grades = []
        cards = self.get_cards()
        for card in cards:
            try:
                grade = card.find_element(by="xpath", value="./*//div[contains(@class, 'b5cd09854e d10a6220b4')]")
                grades.append(grade.text if not None else np.nan)
            except:
                grades.append(np.nan)

        return grades


    def get_prices(self):
        return list(map(lambda price: price.text if price is not None else np.nan, self.driver.find_elements(by="xpath", value="//span[contains(@class, 'fcab3ed991 bd73d13072')]")))


    def get_addresses(self):
        return list(map(lambda address: address.text if address is not None else np.nan, self.driver.find_elements(by="xpath", value="//span[contains(@data-testid, 'address')]")))


    def get_gps(self):
        return list(map(lambda address: self.getLocalisationFromAdd(address), self.get_addresses()))


    def get_cards(self):
        return self.driver.find_elements(by="xpath", value="//div[contains(@class, 'b978843432')]")


    def get_stars(self):
        stars = []
        for i in self.get_cards():
            nbr_stars = i.find_elements(by="xpath", value='./*//div[contains(@data-testid, "rating-stars")]/span')
            stars.append(len(nbr_stars) if nbr_stars else np.nan)
        return stars


    def applyFamilyAndDate(self):
        try:
            self.driver.find_element(by="xpath", value="//button[contains(@class, 'sb-searchbox__button')]").click()
        except:
            self.driver.find_element(by="xpath", value="//button[contains(@type, 'submit')]").click()


    def changePage(self):
        time.sleep(2)
        # self.driver.find_element(by="xpath", value="//button[contains(@class, 'fc63351294 f9c5690c58')]").click()
        self.driver.find_element(by="xpath", value="//button[contains(@aria-label, 'Página siguiente')]").click()


    def get_current_nbr_adults_children_rooms(self):
        return list(map(lambda nbr: int(nbr.text), self.driver.find_elements(by="xpath", value="//span[contains(@class, 'bui-stepper__display')]")))


    def get_nbr_adults(self):
        return self.get_current_nbr_adults_children_rooms()[0]


    def get_nbr_children(self):
        return self.get_current_nbr_adults_children_rooms()[1]


    def get_nbr_rooms(self):
        return self.get_current_nbr_adults_children_rooms()[2]


    def set_nbr(self, btn, current_nbr, nbr_wanted):
        """
        :param btn: the button we want to click
        :param current_nbr: fonction to get the current number
        :param nbr_wanted: the number wanted by customer
        :return: None
        """
        while current_nbr() < nbr_wanted:
            time.sleep(0.5)
            btn.click()


    def set_family_and_room(self, nbr_adults, nbr_children, nbr_room, ages_of_children):
        """
        :param nbr_adults: int
        :param nbr_children: int
        :param nbr_room: int
        :param ages_of_children: []
        :return: None
        """
        time.sleep(2)
        self.driver.find_element(by="id", value="xp__guests__toggle").click()
        
        btn_adults, btn_children, btn_room = self.driver.find_elements(by="xpath", value="//button[contains(@class, 'bui-button bui-button--secondary bui-stepper__add-button')]")
        
        self.set_nbr(btn_adults, self.get_nbr_adults, nbr_adults)
        self.set_nbr(btn_children, self.get_nbr_children, nbr_children)
        self.set_nbr(btn_room, self.get_nbr_rooms, nbr_room)

        selects = self.driver.find_elements(by="xpath", value="//select[contains(@name, 'age')]")
        for i in range(len(selects)):
            selects[i].find_element(by="xpath", value="./option[contains(@value, '{}')]".format(ages_of_children[i])).click()


    def get_current_page(self):
        try:
            return int(self.driver.find_element(by="xpath", value="//li[contains(@class, 'f32a99c8d1 ebd02eda9e')]").text)
        except Exception as err:
            ...


    def get_last_page(self):
        try:
            return int(self.driver.find_elements(by="xpath", value="//li[contains(@class, 'f32a99c8d1')]")[-1].text)
        except Exception as err:
            ...
        

    def show_calendar_init(self):
        try:
            self.driver.find_element(by="xpath", value="//div[contains(@class, 'sb-date-field__field')]").click()
        except:
            print("Error open caldenar")
    
    
    def insert_table(self, data):
        global dbsqlite
        try:
            query = "insert into lugar(nombre, latitud, longitud, fecha_inicio, fecha_fin, link, precio) values(?,?,?,?,?,?,?);"
            stmt = dbsqlite.execute(query, data)
        except SQLAlchemyError as e:
            error=str(e.__dict__['orig'])
            print(error)
        else:
            print("ID LAST RECORD ADDED: ", stmt.lastrowid)
            
            
    def clean_table(self):
        global dbsqlite
        try:
            query = "delete from lugar;"
            dbsqlite.execute(query)
        except SQLAlchemyError as e:
            error=str(e.__dict__['orig'])
            print(error)
            

    def get_item(self, x):
        if (str(x)=='nan' and type(x)!='str') or (x is None):
            return "-"
        else:
            return x
        
    def get_item_gps(self, x):
        if (str(x)=='nan' and type(x)!='str') or (x is None):
            return [0,0]
        else:
            return x

    def addRows(self, names, stars, prices, grades, gps, addresses, start_date, end_date, links, filename, is_head, nb_adults, nb_children, nb_room):
        """
            :param end_date: the date you choose for the research
            :param start_date: the date you choose for the research
            :param prices: all prices you get from the website
            :param is_head: put True if you want to erase the existing file, False to append
            :param filename: the name of the file
            :param links: all links you get from the website
            :param addresses: all addresses you get from the website
            :param gps: all gps you get from the website
            :param grades: all grades you get from the website
            :param stars: all stars you get from the website
            :param names: all names you get from the website
            :return: None
        """
        
        df = pd.DataFrame.from_dict({
            "name": names,
            "grade": grades,
            "stars": stars,
            "prices": prices,
            "address": addresses,
            "gps": gps,
            "start_date": start_date,
            "end_date": end_date,
            "nb_adulte": nb_adults,
            "nb_enfant": nb_children,
            "nb_chambre": nb_room,
            "link": links,
        }, orient='index')
        
        for (index, colname) in enumerate(df):
            row = df[colname].values
            name = self.get_item(row[0])
            price = self.get_item(row[3])
            gps = self.get_item_gps(row[5])
            start_date = self.get_item(row[6])
            end_date = self.get_item(row[7])
            link = self.get_item(row[11])

            data = (name, gps[0], gps[1], start_date, end_date, link, price)
            
            self.insert_table(data)
        
        print("[DEBUG] save csv")
        df.to_csv(filename, index=False, mode="w" if is_head else "a", sep=";")


    def process_search_results(self, path_url):
        try:
            self.driver.get(path_url)
            self.accept_cookies()

            time.sleep(5)
            print(f"[DEBUG] city: {self.city}")
            self.search_city(self.city)

            time.sleep(1)
            print("[DEBUG] show_calendar_init")
            self.show_calendar_init()
            
            print("[DEBUG] select_day")
            self.select_day(self.start_date.split("-")[1])
            self.select_day(self.end_date.split("-")[1])
            
            print("[DEBUG] set_family_and_room")
            self.set_family_and_room(self.nbr_adults, self.nbr_children, self.nbr_room, self.ages_of_children)
            self.search()
            self.set_date(self.start_date, self.end_date)
            
            self.applyFamilyAndDate()
        except Exception as err:
            print(f"[ERROR] Error process_search_results")
            

    def main(self):
        try:
            current_page = self.get_current_page()
            last_page = self.get_last_page()
            
            while current_page < last_page:
                time.sleep(3)
                print(f"[DEBUG] current_page: {current_page} - last_page: {last_page}")
                
                self.addRows(
                    names=self.get_names(),
                    stars=self.get_stars(),
                    prices=self.get_prices(),
                    gps=self.get_gps(),
                    addresses=self.get_addresses(),
                    links=self.get_links(),
                    grades=self.get_grades(),
                    filename=self.filename,
                    start_date=[self.start_date for _ in range(25)],
                    end_date=[self.end_date for _ in range(25)],
                    nb_adults=[self.nbr_adults for _ in range(25)],
                    nb_children=[self.nbr_children for _ in range(25)],
                    nb_room=[self.nbr_room for _ in range(25)],
                    is_head=current_page == 1)
                
                self.changePage()
                current_page += 1

            print("[DEBUG] Finish booking_scraping...............")
            time.sleep(2)
            self.driver.close()
            
        except Exception as err:
            print(f"[ERROR] process main....")
            self.driver.close()
            
            if not err == "All arrays must be of the same length":
                time.sleep(1)
                run()

            
def run():
    global dbsqlite
    dbsqlite = create_engine("sqlite:///bd/booking.db")
    
    book = Booking(city="Asuncion",
                start_date="10-20-2022",
                end_date="10-30-2022",
                nbr_adults=2,
                nbr_children=2, 
                nbr_room=2,
                ages_of_children=[5, 9],
                filename="booking.csv")
    
    # en caso que sea necesario, limpiar la tabla y volver a poblar. Si no corresponde comentar este linea: book.clean_table()
    book.clean_table()
    
    # path url que sera utilizando para procesar el web scraping de la pagina de booking
    path_url = "https://www.booking.com/index.es.html?aid=376374;label=esrow-OtlvhU2CXhSVxek50Z_17wS410489931081:pl:ta:p1:p22.563.000:ac:ap:neg:fi:tikwd-65526620:lp9069967:li:dec:dm:ppccp=UmFuZG9tSVYkc2RlIyh9YcUSe6BbHz0Ad_yDShFFSHQ;ws=&gclid=EAIaIQobChMIteebzOf2-gIVDTORCh1o_gCvEAAYASAAEgIfVvD_BwE"
    
    # inicia proceso 
    book.process_search_results(path_url)
    
    # encargado de leer los datos y poblar la base de datos
    book.main()


if __name__ == '__main__':
    run()
