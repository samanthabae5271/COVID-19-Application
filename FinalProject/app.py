import mysql.connector
from mysql.connector.constants import ClientFlag
import pandas as pd
import sqlite3
from helper import helper

Exit = 0
#creating separate datasets for each table
WorldData = pd.read_csv(r"WorldData.csv")
CountryLatest = pd.read_csv(r"CountryLatest.csv")
DayCountry = pd.read_csv(r"DayCountry.csv")
DayTotal = pd.read_csv(r"DayTotal.csv")
CountryCoordinates = pd.read_csv(r"CountryCoordinates.csv")

#getting rid of NAN
WorldData = WorldData.where((pd.notnull(WorldData)), None)
CountryLatest = CountryLatest.where((pd.notnull(CountryLatest)), None)
DayCountry = DayCountry.where((pd.notnull(DayCountry)), None)
DayTotal = DayTotal.where((pd.notnull(DayTotal)), None)
CountryCoordinates = CountryCoordinates.where((pd.notnull(CountryCoordinates)), None)

WD = pd.DataFrame(WorldData)
CL = pd.DataFrame(CountryLatest)
DC = pd.DataFrame(DayCountry)
DT = pd.DataFrame(DayTotal)
CC = pd.DataFrame(CountryCoordinates)

WD_list = []
CL_list = []
DC_list = []
DT_list = []
CC_list = []

WD_list = WD.to_numpy().tolist()
CL_list = CL.to_numpy().tolist()
DC_list = DC.to_numpy().tolist()
DT_list = DT.to_numpy().tolist()
CC_list = CC.to_numpy().tolist()


config = {
    'user': 'root',
    'password': 'Kstarcute527.',
    'host': '34.135.120.108',
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': r'\Users\Samantha\Downloads\server-ca.pem',
    'ssl_cert': r'\Users\Samantha\Downloads\client-cert.pem',
    'ssl_key': r'\Users\Samantha\Downloads\client-key.pem'
}

# established connection to cloud
connection = mysql.connector.connect(**config)

cursor = connection.cursor()
cursor.execute('CREATE DATABASE IF NOT EXISTS finalP') #creating new database
connection.close()

config['database'] = 'finalP'  # add new database to config dict
connection = mysql.connector.connect(**config)
cursor = connection.cursor()

cursor.execute('USE finalP')
connection.commit()

while Exit == 0:
    #main program
    print("""
    1) Print Record(s)
    2) Search for Attribute
    3) Add Record(s)
    4) Update Record(s)
    5) Delete Record(s)
    6) Information of attributes
    7) Input another dataset
    8) Export table to csv
    9) Rollback
    10) Commit
    11) Exit
    """)

    userInput = input("Enter your option: ")
    userInput = int(userInput)

    if userInput == 1: #Printing records
        helper.print_records(cursor)
    elif userInput == 2: #Searching attributes
        helper.search_attributes(cursor)
    elif userInput == 3: #Add records
        helper.add_records(cursor)
    elif userInput == 4: #Update records
        helper.update_record(cursor)
    elif userInput == 5: #Delete records
        helper.delete_record(cursor)
    elif userInput == 6: #Get attribute info
        print("""
        Choose what type of data:
        1) World total cases per country
        2) Latest cases per country
        3) Cases per day per country
        4) Total cases per day
        5) Country coordinates
        """)
        userInput = input("Enter your option: ")
        userInput = int(userInput)
        if(userInput == 1):
            print("""
            Which attribute would you like info on?:
            1) CID
            2) Country
            3) Continent
            4) Population
            5) TotalCases
            6) TotalDeaths
            7) TotalRecovered
            8) TotalActive
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1):
                print("CID represents the primary key of the table and the ID of each record")
            elif(userInput == 2):
                print("Country represents which country the cases are from")
            elif(userInput == 3):
                print("Continent represents which continent the cases are from")
            elif(userInput == 4):
                print("Population represents the population number of the country")
            elif(userInput == 5):
                print("TotalCases represent the total number of cases in the country")
            elif(userInput == 6):
                print("TotalDeaths represent the total number of deaths in the country")
            elif(userInput == 7):
                print("TotalRecovered represents the total number of recovered cases in the country")
            elif(userInput == 8):
                print("TotalActive represents the total number of active cases in the country")
        elif(userInput == 2):
            print("""
            Which attribute would you like info on?:
            1) CID
            2) Country
            3) Confirmed
            4) Deaths
            5) Recovered
            6) Active
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1):
                print("CID represents the primary key of the table and the ID of each record")
            elif(userInput == 2):
                print("Country represents the country the cases are from")
            elif(userInput == 3):
                print("Confirmed represents the number of confirmed cases")
            elif(userInput == 4):
                print("Deaths represents the number of death cases")
            elif(userInput == 5):
                print("Recovered represents the number of recovered cases")
            elif(userInput == 6):
                print("Active represents the number of active cases")
        elif(userInput == 3):
            print("""
            Which attribute would you like info on?:
            1) ID
            2) Date
            3) Country
            4) Confirmed
            5) Deaths
            6) Recovered
            7) Active
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1):
                print("ID represents the primary key of the table and the ID of each record")
            elif(userInput == 2):
                print("Date represents the date of the record from Jan 21, 2020 to July 26,2020")
            elif(userInput == 3):
                print("Country represents the country the cases are from")
            elif(userInput == 4):
                print("Confirmed represents the number of confirmed cases")
            elif(userInput == 5):
                print("Deaths represents the number of death cases")
            elif(userInput == 6):
                print("Recovered represents the number of recovered cases")
            elif(userInput == 7):
                print("Active represents the number of active cases")
        elif(userInput == 4):
            print("""
            Which attribute would you like info on?:
            1) Date
            2) Country
            3) Confirmed
            4) Deaths
            5) Recovered
            6) Active
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1):
                print("Date represents the date of the record from Jan 21, 2020 to July 26,2020")
            elif(userInput == 2):
                print("Country represents the country the cases are from")
            elif(userInput == 3):
                print("Confirmed represents the number of confirmed cases")
            elif(userInput == 4):
                print("Deaths represents the number of death cases")
            elif(userInput == 5):
                print("Recovered represents the number of recovered cases")
            elif(userInput == 6):
                print("Active represents the number of active cases")
        elif(userInput == 5):
            print("""
            Which attribute would you like info on?:
            1) CID
            2) Province
            3) Country
            4) Latitude
            5) Longitude
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1):
                print("CID represents the primary key of the table and the CID of each record")
            elif(userInput == 2):
                print("Province represents the province the cases are from")
            elif(userInput == 3):
                print("Country represents the country the cases are from")
            elif(userInput == 4):
                print("Latitude represents the latitude number of the province/country")
            elif(userInput == 5):
                print("Longitude represents the longitude number of the province/country")
    elif userInput == 7: #Input another dataset
        #loading dataset to list
        dataset = input("input name of dataset: ")
        newdata = pd.read_csv(dataset)
        newdata = newdata.where((pd.notnull(newdata)), None)
        nD = pd.DataFrame(newdata)

        nD_list = []
        nD_list = nD.to_numpy().tolist()

        #creating table for list
        query = input("Please enter create table query: ")
        cursor.execute(query)

        #inserting data
        query = input("Please enter insert query with %s: ")
        cursor.executemany(query, nD_list)
    elif userInput == 8: #Export files to csv
        print("""
        Choose what type of data:
        1) World total cases per country
        2) Latest cases per country
        3) Cases per day per country
        4) Total cases per day
        5) Country coordinates
        """)
        userInput = input("Enter number: ")
        userInput = int(userInput)
        name = input("What do you want to name the file? (End with .csv): ")
        if(userInput == 1): #WorldData
            query = ('''
            SELECT*
            FROM WorldData
            ''')
            results = pd.read_sql_query(query, connection)
            results.to_csv(name, index = False)
        elif(userInput == 2): #countryLatest
            query = ('''
            SELECT*
            FROM WorldData
            ''')
            results = pd.read_sql_query(query, connection)
            results.to_csv(name, index = False)
        elif(userInput == 3): #DayCountry
            query = ('''
            SELECT*
            FROM WorldData
            ''')
            results = pd.read_sql_query(query, connection)
            results.to_csv(name, index = False)
        elif(userInput == 4): #DayTotal
            query = ('''
            SELECT*
            FROM WorldData
            ''')
            results = pd.read_sql_query(query, connection)
            results.to_csv(name, index = False)
        elif(userInput == 5): #CountryCoordinates
            query = ('''
            SELECT*
            FROM WorldData
            ''')
            results = pd.read_sql_query(query, connection)
            results.to_csv(name, index = False)
    elif userInput == 9: #Rollback
        connection.rollback()
    elif userInput == 10: #Commit
        connection.commit()
    elif userInput == 11: #Exit
        Exit = 1


connection.close()
