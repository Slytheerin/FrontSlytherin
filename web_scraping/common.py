import numpy as np
from geopy.geocoders import Nominatim
import pandas as pd

# maybe create an english for certain cases
monthCorrespondances = {
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

month_digits_dictionary = {
    "Enero": "01",
    "Febrero": "02",
    "Marzo": "03",
    "Abril": "04",
    "Mayo": "05",
    "Junio": "06",
    "Julio": "07",
    "Agosto": "08",
    "Septiembre": "09",
    "Octubre": "10",
    "Noviembre": "11",
    "Diciembre": "12",
}

def addRows(names, stars, prices, grades, gps, addresses,
            start_date, end_date, links, filename, is_head,
            nb_adults, nb_children, nb_room):
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
    print("addRows")
    
    print(len(names), len(grades), len(stars), len(prices), len(addresses), len(gps), 
          len(start_date), len(end_date), len(nb_adults), len(nb_children), len(nb_room), len(links))

    df = pd.DataFrame(
        {
            "name": names,
            "grade": grades,
            "stars": stars,
            # "prices": prices,
            "address": addresses,
            "gps": gps,
            "start_date": start_date,
            "end_date": end_date,
            "nb_adulte": nb_adults,
            "nb_enfant": nb_children,
            "nb_chambre": nb_room,
            "link": links,
        }
    )

    df.to_csv(filename, index=False, mode="w" if is_head else "a", sep=";")


def getLocalisationFromAdd(add):
    """
    :param add: "address_hotel"
    :return: [latitude, longitude] else None
    """
    try:
        location = Nominatim(user_agent="main").geocode(add)
        return [location.latitude, location.longitude] if location is not None else np.nan
    except:
        return np.nan


def separateDate(date):
    """
    :param date: dd/MM/yyyy
    :return: day, month, year
    """
    return date.split("/")


def separateAmericanDate(date):
    """
    :param date: MM-dd-yyyy
    :return: day, month, year
    """
    month, day, year = date.split("-")
    return day, month, year


def date_format_us_to_website(date):
    date = list(reversed(date.split('-')))
    return date[0] + '-' + date[2] + '-' + date[1]

def date_format_MMDDYYYY_to_YYYYMMDD(date):
    date = date.split("-")
    return date[2] + '-' + date[0] + '-' + date[1]