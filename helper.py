# module contains miscellaneous functions
import mysql.connector
from mysql.connector.constants import ClientFlag
import pandas as pd
import sqlite3

class helper():

    @staticmethod
    def upload_create_tables():
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

        #creating tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS WorldData(
        CID INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
        Country VARCHAR(50),
        Continent VARCHAR(50),
        Population INTEGER NOT NULL,
        TotalCases INTEGER NOT NULL,
        TotalDeaths INTEGER NOT NULL,
        TotalRecovered INTEGER NOT NULL,
        TotalActive INTEGER NOT NULL)
        '''
        )
        connection.commit() #WorldData cannot make a foreign key with countryLatest with country or CID since there are different number of countries/regions

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CountryLatest(
        CID INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
        Country VARCHAR(50),
        Confirmed INTEGER NOT NULL,
        Deaths INTEGER NOT NULL,
        Recovered INTEGER NOT NULL,
        Active INTEGER NOT NULL)
        '''
        )
        connection.commit()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS DayTotal(
        Date DATE NOT NULL PRIMARY KEY,
        Country VARCHAR(50),
        Confirmed INTEGER NOT NULL,
        Deaths INTEGER NOT NULL,
        Recovered INTEGER NOT NULL,
        Active INTEGER NOT NULL)
        '''
        )
        connection.commit()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS DayCountry(
        ID INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
        Date DATE,
        Country VARCHAR(50),
        Confirmed INTEGER NOT NULL,
        Deaths INTEGER NOT NULL,
        Recovered INTEGER NOT NULL,
        Active INTEGER NOT NULL)
        '''
        )
        connection.commit()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CountryCoordinates(
        CID INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
        Province VARCHAR(50),
        Country VARCHAR(50),
        Latitude INTEGER NOT NULL,
        Longitude INTEGER NOT NULL)
        '''
        )
        connection.commit()



        #inserting data into tables
        query = ('''
        INSERT INTO WorldData(Country, Continent, Population, TotalCases, TotalDeaths, TotalRecovered, TotalActive)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
        '''
        )
        cursor.executemany(query, WD_list)
        connection.commit()

        query = ('''
        INSERT INTO CountryLatest(Country, Confirmed, Deaths, Recovered, Active)
        VALUES(%s, %s, %s, %s, %s)
        '''
        )
        cursor.executemany(query, CL_list)
        connection.commit()

        query = ('''
        INSERT INTO DayCountry(Date, Country, Confirmed, Deaths, Recovered, Active)
        VALUES(%s, %s, %s, %s, %s, %s)
        '''
        )
        cursor.executemany(query, DC_list)
        connection.commit()

        query = ('''
        INSERT INTO DayTotal(Date, Confirmed, Deaths, Recovered, Active)
        VALUES(%s, %s, %s, %s, %s)
        '''
        )
        cursor.executemany(query, DT_list)
        connection.commit()

        query = ('''
        INSERT INTO CountryCoordinates(Province, Country, Latitude, Longitude)
        VALUES(%s, %s, %s, %s)
        '''
        )
        cursor.executemany(query, CC_list)
        connection.commit() #initial upload of tables
        connection.close()

    @staticmethod
    def create_views(cursor):
        query = ('''
        CREATE VIEW tritable AS
        SELECT WorldData.CID, WorldData.Country, Population, TotalCases, TotalDeaths, TotalActive, TotalRecovered, Co.Confirmed, Co.Deaths, Co.Active, Co.Recovered, CC.Province, CC.Latitude, CC.Longitude
        FROM WorldData
        INNER JOIN CountryLatest as Co
        ON WorldData.CID = Co.CID
        INNER JOIN CountryCoordinates CC
        ON WorldData.CID = CC.CID
        ''')
        cursor.execute(query) #creating used views

    @staticmethod
    def print_records(cursor):
        print("""
        Choose what type of data:
        1) World total cases per country
        2) Latest cases per country
        3) Cases per day per country
        4) Total cases per day
        5) Country coordinates
        6) Tables 1, 2, 5 together: World data, latest cases, and coordinates per country
        7) Tables 3, 4 together: Cases per country, day, total cases perday
        """)
        userInput = input("Enter your option: ")
        userInput = int(userInput)
        if(userInput == 1): #Printing records for WorldData
            print("""
            How would you like to search?:
            1) CID
            2) Country
            3) Continent
            4) Print all records
            5) Get top # of records
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1): #Searching through CID
                userInput = input("Enter CID: ")
                userInput = int(userInput)
                query = ('''
                SELECT*
                FROM WorldData
                WHERE CID = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 2): #Searching through Country
                userInput = input("Enter Country Name: ")
                query = ('''
                SELECT*
                FROM WorldData
                WHERE Country = %s
                ''')
                tuple = userInput
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 3): #Searching through Continent
                userInput = input("Enter Continent: ")
                query = ('''
                SELECT*
                FROM WorldData
                WHERE Continent = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 4): #Printing all records
                query = ('''
                SELECT*
                FROM WorldData
                ''')
                cursor.execute(query)
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 5): #Getting top # of records
                num = input("What number of records do you want?: ")
                num = int(num)
                query = ('''
                SELECT*
                FROM WorldData
                LIMIT %s
                ''')
                tuple = (num)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
        elif(userInput == 2): #Printing records for CountryLatest
            print("""
            How would you like to search?:
            1) CID
            2) Country
            3) Print all records
            4) Print top # of records
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1): #Searching through CID
                userInput = input("Enter CID: ")
                userInput = int(userInput)
                query = ('''
                SELECT*
                FROM CountryLatest
                WHERE CID = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 2): #Searching through Country
                userInput = input("Enter Country Name: ")
                query = ('''
                SELECT*
                FROM CountryLatest
                WHERE Country = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 3): #Printing all records
                query = ('''
                SELECT*
                FROM CountryLatest
                ''')
                cursor.execute(query)
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 4): #Getting top # of records
                num = input("What number of records do you want?: ")
                num = int(num)
                query = ('''
                SELECT*
                FROM CountryLatest
                LIMIT %s
                ''')
                tuple = (num)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
        elif(userInput == 3): #Printing records for DayCountry
            print("""
            How would you like to search?:
            1) ID
            2) Date
            3) Country
            4) Print all records
            5) Print top # of records
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1): #Searching through ID
                userInput = input("Enter ID: ")
                userInput = int(userInput)
                query = ('''
                SELECT*
                FROM DayCountry
                WHERE ID = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 2): #Searching through Date
                userInput = input("Enter Date in YYYY-MM-DD format: ")
                query = ('''
                SELECT*
                FROM DayCountry
                WHERE Date = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 3): #Searching through Country
                userInput = input("Enter Country: ")
                query = ('''
                SELECT*
                FROM DayCountry
                WHERE Country = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 4): #Printing all records
                query = ('''
                SELECT*
                FROM DayCountry
                ''')
                cursor.execute(query)
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 5): #Getting top # of records
                num = input("What number of records do you want?: ")
                num = int(num)
                query = ('''
                SELECT*
                FROM DayCountry
                LIMIT %s
                ''')
                tuple = (num)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
        elif(userInput == 4): #Printing records for DayTotal
            print("""
            How would you like to search?:
            1) Date
            2) Country
            3) Print all records
            4) Print top # of records
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1): #Searching through Date
                userInput = input("Enter Date in YYYY-MM-DD format: ")
                query = ('''
                SELECT*
                FROM DayTotal
                WHERE Date = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 2): #Searching through Country
                userInput = input("Enter Country: ")
                query = ('''
                SELECT*
                FROM DayTotal
                WHERE Country = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 3): #Printing all records
                query = ('''
                SELECT*
                FROM DayTotal
                ''')
                cursor.execute(query)
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 4): #Getting top # of records
                num = input("What number of records do you want?: ")
                num = int(num)
                query = ('''
                SELECT*
                FROM DayTotal
                LIMIT %s
                ''')
                tuple = (num)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
        elif(userInput == 5): #Printing records for CountryCoordinates
            print("""
            How would you like to search?:
            1) CID
            2) Province
            3) Country
            4) Print all records
            5) Print top # of records
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1): #Searching through CID
                userInput = input("Enter CID: ")
                userInput = int(userInput)
                query = ('''
                SELECT*
                FROM CountryCoordinates
                WHERE CID = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 2): #Searching through Province
                userInput = input("Enter Province: ")
                query = ('''
                SELECT*
                FROM CountryCoordinates
                WHERE Province = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 3): #Searching through Country
                userInput = input("Enter Country: ")
                query = ('''
                SELECT*
                FROM CountryCoordinates
                WHERE Country = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 4): #Printing all records
                query = ('''
                SELECT*
                FROM CountryCoordinates
                ''')
                cursor.execute(query)
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 5): #Getting top # of records
                num = input("What number of records do you want?: ")
                num = int(num)
                query = ('''
                SELECT*
                FROM CountryCoordinates
                LIMIT %s
                ''')
                tuple = (num)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
        elif(userInput == 6): #Printing records for tables 1, 2, 5 joined (Joining queries)
            print("""
            How would you like to search?:
            1) CID
            2) Country
            3) Continent
            4) Print all records
            5) Print top # of records
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1): #Searching through CID
                userInput = input("Enter CID: ")
                userInput = int(userInput)
                query = ("""
                SELECT*
                FROM tritable
                WHERE CID = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 2): #Searching through Country
                userInput = input("Enter Country Name: ")
                query = ('''
                SELECT *
                FROM WorldData
                INNER JOIN CountryLatest
                ON WorldData.CID = CountryLatest.CID
                INNER JOIN CountryCoordinates
                ON WorldData.CID = CountryCoordinates.CID
                WHERE WorldData.Country = %s
                ''')
                tuple = userInput
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 3): #Searching through Continent
                userInput = input("Enter Continent: ")
                query = ('''
                SELECT *
                FROM WorldData
                INNER JOIN CountryLatest
                ON WorldData.CID = CountryLatest.CID
                INNER JOIN CountryCoordinates
                ON WorldData.CID = CountryCoordinates.CID
                WHERE Continent = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 4): #Printing all records
                query = ("""
                SELECT *
                FROM WorldData
                INNER JOIN CountryLatest
                ON WorldData.CID = CountryLatest.CID
                INNER JOIN CountryCoordinates
                ON WorldData.CID = CountryCoordinates.CID
                """)
                cursor.execute(query)
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 5): #Getting top # of records
                num = input("What number of records do you want?: ")
                num = int(num)
                query = ('''
                SELECT *
                FROM WorldData
                INNER JOIN CountryLatest
                ON WorldData.CID = CountryLatest.CID
                INNER JOIN CountryCoordinates
                ON WorldData.CID = CountryCoordinates.CID
                LIMIT %s
                ''')
                tuple = (num)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
        elif(userInput == 7): #Printing records for tables 3, 4 joined (Joining queries)
            print("""
            How would you like to search?:
            1) ID
            2) Date
            3) Country
            4) Print all records
            5) Print top # of records
            """)
            userInput = input("Enter your option: ")
            userInput = int(userInput)
            if(userInput == 1): #Searching through ID
                userInput = input("Enter ID: ")
                userInput = int(userInput)
                query = ('''
                SELECT*
                FROM DayCountry
                INNER JOIN DayTotal
                ON DayCountry.Date = DayTotal.Date
                WHERE ID = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 2): #Searching through Date
                userInput = input("Enter Date in YYYY-MM-DD format: ")
                query = ('''
                SELECT*
                FROM DayCountry
                INNER JOIN DayTotal
                ON DayCountry.Date = DayTotal.Date
                WHERE DayCountry.Date = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 3): #Searching through Country
                userInput = input("Enter Country: ")
                query = ('''
                SELECT*
                FROM DayCountry
                INNER JOIN DayTotal
                ON DayCountry.Date = DayTotal.Date
                WHERE DayCountry.Country = %s
                ''')
                tuple = (userInput)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 4): #Printing all records
                query = ('''
                SELECT*
                FROM DayCountry
                INNER JOIN DayTotal
                ON DayCountry.Date = DayTotal.Date
                ''')
                cursor.execute(query)
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x)
            elif(userInput == 5): #Getting top # of records
                num = input("What number of records do you want?: ")
                num = int(num)
                query = ('''
                SELECT*
                FROM DayCountry
                INNER JOIN DayTotal
                ON DayCountry.Date = DayTotal.Date
                LIMIT %s
                ''')
                tuple = (num)
                cursor.execute(query, (tuple,))
                results = cursor.fetchall()
                num_fields = len(cursor.description)
                field_names = [i[0] for i in cursor.description]
                print(field_names)
                for x in results:
                    print(x) #printing records

    @staticmethod
    def search_attributes(cursor):
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
        #choose which attribute you want
        if(userInput == 1): #From WorldData table
            userInput = input("1)Non-Numerical or 2)Numerical attribute?")
            userInput = int(userInput)
            if(userInput == 1): #non-numerical attributes
                print("""
                Choose which attribute:
                1)CID
                2)Country
                3)Continent
                """)
                var = input("Enter number: ")
                var = int(var)
                if(var == 1): #CID attribute
                    query = ('''
                    SELECT CID
                    FROM WorldData
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 2): #Country attribute
                    query = ('''
                    SELECT Country
                    FROM WorldData
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 3): #Continent attribute
                    query = ('''
                    SELECT Continent
                    FROM WorldData
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
            elif(userInput == 2): #numerical attributes
                print("Would you like to use grouping? Yes or No: ")
                group = input()
                group = str(group)
                print("""
                Choose which attribute:
                1)Population
                2)TotalCases
                3)TotalActive
                4)TotalDeaths
                5)TotalRecovered
                """)
                var = input("Enter number: ")
                var = int(var)
                if(group == "No"):
                    print("""
                    Choose your aggregate:
                    1) Max
                    2) Min
                    3) Sum
                    4) Average
                    5) Count
                    6) Count records that have more than # of the attribute
                    7) No filter
                    """)
                    userInput = input("Enter number: ")
                    userInput = int(userInput)
                    if(userInput == 1): #getting max for numerical attribute
                        if(var == 1): #population
                            query = ('''
                            SELECT MAX(Population)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #TotalCases
                            query = ('''
                            SELECT MAX(TotalCases)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #TotalActive
                            query = ('''
                            SELECT MAX(TotalActive)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #TotalDeaths
                            query = ('''
                            SELECT MAX(TotalDeaths)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 5): #TotalRecovered
                            query = ('''
                            SELECT MAX(TotalRecovered)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 2): #getting min for numerical attribute
                        if(var == 1): #population
                            query = ('''
                            SELECT MIN(Population)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #TotalCases
                            query = ('''
                            SELECT MIN(TotalCases)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #TotalActive
                            query = ('''
                            SELECT MIN(TotalActive)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #TotalDeaths
                            query = ('''
                            SELECT MIN(TotalDeaths)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 5): #TotalRecovered
                            query = ('''
                            SELECT MIN(TotalRecovered)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 3): #getting sum for numerical attribute
                        if(var == 1): #population
                            query = ('''
                            SELECT SUM(Population)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #TotalCases
                            query = ('''
                            SELECT SUM(TotalCases)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #TotalActive
                            query = ('''
                            SELECT SUM(TotalActive)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #TotalDeaths
                            query = ('''
                            SELECT SUM(TotalDeaths)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 5): #TotalRecovered
                            query = ('''
                            SELECT SUM(TotalRecovered)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 4): #getting average for numerical attribute
                        if(var == 1): #population
                            query = ('''
                            SELECT AVG(Population)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #TotalCases
                            query = ('''
                            SELECT AVG(TotalCases)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #TotalActive
                            query = ('''
                            SELECT AVG(TotalActive)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #TotalDeaths
                            query = ('''
                            SELECT AVG(TotalDeaths)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 5): #TotalRecovered
                            query = ('''
                            SELECT AVG(TotalRecovered)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 5): #getting Count for numerical attribute/records
                        if(var == 1): #population
                            query = ('''
                            SELECT COUNT(Population)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #TotalCases
                            query = ('''
                            SELECT COUNT(TotalCases)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #TotalActive
                            query = ('''
                            SELECT COUNT(TotalActive)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #TotalDeaths
                            query = ('''
                            SELECT COUNT(TotalDeaths)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 5): #TotalRecovered
                            query = ('''
                            SELECT COUNT(TotalRecovered)
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 6): #getting count for records that have more than # of attribute (subqueries)
                        if(var == 1): #population
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE Population > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE Population < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 2): #TotalCases
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalCases > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalCases < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 3): #TotalActive
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalActive > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalActive < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 4): #TotalDeaths
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalDeaths > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalDeaths < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 5): #TotalRecovered
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalRecovered > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM WorldData
                                WHERE TotalRecovered < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                    elif(userInput == 7): #getting all attributes
                        if(var == 1): #population
                            query = ('''
                            SELECT Population
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #TotalCases
                            query = ('''
                            SELECT TotalCases
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #TotalActive
                            query = ('''
                            SELECT TotalActive
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #TotalDeaths
                            query = ('''
                            SELECT TotalDeaths
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 5): #TotalRecovered
                            query = ('''
                            SELECT TotalRecovered
                            FROM WorldData
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                elif(group == "Yes"):
                    print("""
                    Group by what?:
                    1)CID
                    2)Country
                    3)Continent
                    """)
                    group = int(input())
                    if(var == 1): #population
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, Population
                            FROM WorldData
                            GROUP BY CID, Population
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Population
                            FROM WorldData
                            GROUP BY Country, Population
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #continent
                            query = ("""
                            SELECT Continent, Population
                            FROM WorldData
                            GROUP BY Continent, Population
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 2): #TotalCases
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, TotalCases
                            FROM WorldData
                            GROUP BY CID, TotalCases
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, TotalCases
                            FROM WorldData
                            GROUP BY Country, TotalCases
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #continent
                            query = ("""
                            SELECT Continent, TotalCases
                            FROM WorldData
                            GROUP BY Continent, TotalCases
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 3): #TotalActive
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, TotalActive
                            FROM WorldData
                            GROUP BY CID, TotalActive
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, TotalActive
                            FROM WorldData
                            GROUP BY Country, TotalActive
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #continent
                            query = ("""
                            SELECT Continent, TotalActive
                            FROM WorldData
                            GROUP BY Continent, TotalActive
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 4): #TotalDeaths
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, TotalDeaths
                            FROM WorldData
                            GROUP BY CID, TotalDeaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, TotalDeaths
                            FROM WorldData
                            GROUP BY Country, TotalDeaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #continent
                            query = ("""
                            SELECT Continent, TotalDeaths
                            FROM WorldData
                            GROUP BY Continent, TotalDeaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 5): #TotalRecovered
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, TotalRecovered
                            FROM WorldData
                            GROUP BY CID, TotalRecovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, TotalRecovered
                            FROM WorldData
                            GROUP BY Country, TotalRecovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #continent
                            query = ("""
                            SELECT Continent, TotalRecovered
                            FROM WorldData
                            GROUP BY Continent, TotalRecovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)

        elif(userInput == 2): #From CountryLatest
            userInput = input("1)Non-Numerical or 2)Numerical attribute?")
            userInput = int(userInput)
            if(userInput == 1): #non-numerical attributes
                print("""
                Choose which attribute:
                1)CID
                2)Country
                """)
                var = input("Enter number: ")
                var = int(var)
                if(var == 1): #CID attribute
                    query = ('''
                    SELECT CID
                    FROM WorldData
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 2): #Country attribute
                    query = ('''
                    SELECT Country
                    FROM WorldData
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
            elif(userInput == 2): #numerical attributes
                print("Would you like to use grouping? Yes or No: ")
                group = input()
                group = str(group)
                print("""
                Choose which attribute:
                1)Confirmed
                2)Deaths
                3)Active
                4)Recovered
                """)
                var = input("Enter number: ")
                var = int(var)
                if(group == "No"):
                    print("""
                    Choose your aggregate:
                    1) Max
                    2) Min
                    3) Sum
                    4) Average
                    5) Count
                    6) Count records that greater or less than # of attributes
                    7) No filter
                    """)
                    userInput = input("Enter number: ")
                    userInput = int(userInput)
                    if(userInput == 1): #getting max for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT MAX(Confirmed)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT MAX(Deaths)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT MAX(Active)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT MAX(Recovered)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 2): #getting min for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT MIN(Confirmed)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT MIN(Deaths)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT MIN(Active)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT MIN(Recovered)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 3): #getting sum for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT SUM(Confirmed)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT SUM(Deaths)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT SUM(Active)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT SUM(Recovered)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 4): #getting average for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT AVG(Confirmed)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT AVG(Deaths)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT AVG(Active)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT AVG(Recovered)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 5): #getting Count for numerical attribute/records
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT COUNT(Confirmed)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT COUNT(Deaths)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT COUNT(Active)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT COUNT(Recovered)
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 6): #getting count for records that have more than # of attribute
                        if(var == 1): #Confirmed
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Confirmed > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Confirmed < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 2): #deaths
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Deaths > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Deaths < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 3): #Active
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Active > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Active < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 4): #Recovered
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Recovered > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Recovered < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                    elif(userInput == 7): #getting all attributes
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT Confirmed
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT Deaths
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT Active
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT Recovered
                            FROM CountryLatest
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                elif(group == "Yes"):
                    print("""
                    Group by what?:
                    1)CID
                    2)Country
                    """)
                    group = int(input())
                    if(var == 1): #Confirmed
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, Confirmed
                            FROM CountryLatest
                            GROUP BY CID, Confirmed
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Confirmed
                            FROM CountryLatest
                            GROUP BY Country, Confirmed
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 2): #Deaths
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, Deaths
                            FROM CountryLatest
                            GROUP BY CID, Deaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Deaths
                            FROM CountryLatest
                            GROUP BY Country, Deaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 3): #Active
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, Active
                            FROM CountryLatest
                            GROUP BY CID, Active
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Active
                            FROM CountryLatest
                            GROUP BY Country, Active
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 4): #Recovered
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, Recovered
                            FROM CountryLatest
                            GROUP BY CID, Recovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Recovered
                            FROM CountryLatest
                            GROUP BY Country, Recovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
        elif(userInput == 3): #From DayCountry
            userInput = input("1)Non-Numerical or 2)Numerical attribute?")
            userInput = int(userInput)
            if(userInput == 1): #non-numerical attributes
                print("""
                Choose which attribute:
                1)ID
                2)Date
                3)Country
                """)
                var = input("Enter number: ")
                var = int(var)
                if(var == 1): #ID attribute
                    query = ('''
                    SELECT ID
                    FROM DayCountry
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 2): #Date attribute
                    query = ('''
                    SELECT Date
                    FROM DayCountry
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 3): #Country attribute
                    query = ('''
                    SELECT Country
                    FROM DayCountry
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
            elif(userInput == 2): #numerical attributes
                print("Would you like to use grouping? Yes or No: ")
                group = input()
                group = str(group)
                print("""
                Choose which attribute:
                1)Confirmed
                2)Deaths
                3)Active
                4)Recovered
                """)
                var = input("Enter number: ")
                var = int(var)
                if(group == "No"):
                    print("""
                    Choose your aggregate:
                    1) Max
                    2) Min
                    3) Sum
                    4) Average
                    5) Count
                    6) Count records with greater or less # of attribute
                    7) No filter
                    """)
                    userInput = input("Enter number: ")
                    userInput = int(userInput)
                    if(userInput == 1): #getting max for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT MAX(Confirmed)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT MAX(Deaths)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT MAX(Active)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT MAX(Recovered)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 2): #getting min for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT MIN(Confirmed)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT MIN(Deaths)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT MIN(Active)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT MIN(Recovered)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 3): #getting sum for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT SUM(Confirmed)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT SUM(Deaths)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT SUM(Active)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT SUM(Recovered)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 4): #getting average for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT AVG(Confirmed)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT AVG(Deaths)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT AVG(Active)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT AVG(Recovered)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 5): #getting Count for numerical attribute/records
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT COUNT(Confirmed)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT COUNT(Deaths)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT COUNT(Active)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT COUNT(Recovered)
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 6): #getting Count of records with more or less than # of attribute
                        if(var == 1): #Confirmed
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayCountry
                                WHERE Confirmed > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayCountry
                                WHERE Confirmed < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 2): #deaths
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayCountry
                                WHERE Deaths > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayCountry
                                WHERE Deaths < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 3): #Active
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Active > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Active < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 4): #Recovered
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Recovered > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Recovered < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                    elif(userInput == 7): #getting all attributes
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT Confirmed
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT Deaths
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT Active
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT Recovered
                            FROM DayCountry
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                elif(group == "Yes"):
                    print("""
                    Group by what?:
                    1)CID
                    2)Date
                    3)Country
                    """)
                    group = int(input())
                    if(var == 1): #Confirmed
                        if(group == 1): #ID grouping
                            query = ("""
                            SELECT ID, Confirmed
                            FROM DayCountry
                            GROUP BY ID, Confirmed
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Date
                            query = ("""
                            SELECT Date, Confirmed
                            FROM DayCountry
                            GROUP BY Date, Confirmed
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #Country
                            query = ("""
                            SELECT Country, Confirmed
                            FROM DayCountry
                            GROUP BY Country, Confirmed
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 2): #Deaths
                        if(group == 1): #ID grouping
                            query = ("""
                            SELECT ID, Deaths
                            FROM DayCountry
                            GROUP BY ID, Deaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Date
                            query = ("""
                            SELECT Date, Deaths
                            FROM DayCountry
                            GROUP BY Date, Deaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #Country
                            query = ("""
                            SELECT Country, Deaths
                            FROM DayCountry
                            GROUP BY Country, Deaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 3): #Active
                        if(group == 1): #ID grouping
                            query = ("""
                            SELECT ID, Active
                            FROM DayCountry
                            GROUP BY ID, Active
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Date
                            query = ("""
                            SELECT Date, Active
                            FROM DayCountry
                            GROUP BY Date, Active
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #Country
                            query = ("""
                            SELECT Country, Active
                            FROM DayCountry
                            GROUP BY Country, Active
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 4): #Recovered
                        if(group == 1): #ID grouping
                            query = ("""
                            SELECT ID, Recovered
                            FROM DayCountry
                            GROUP BY ID, Recovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Date
                            query = ("""
                            SELECT Date, Recovered
                            FROM DayCountry
                            GROUP BY Date, Recovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #Country
                            query = ("""
                            SELECT Country, Recovered
                            FROM DayCountry
                            GROUP BY Country, Recovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
        elif(userInput == 4): #From DayTotal
            userInput = input("1)Non-Numerical or 2)Numerical attribute?")
            userInput = int(userInput)
            if(userInput == 1): #non-numerical attributes
                print("""
                Choose which attribute:
                1)Date
                2)Country
                """)
                var = input("Enter number: ")
                var = int(var)
                if(var == 1): #Date attribute
                    query = ('''
                    SELECT Date
                    FROM DayTotal
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 2): #Country attribute
                    query = ('''
                    SELECT Country
                    FROM DayTotal
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
            elif(userInput == 2): #numerical attributes
                print("Would you like to use grouping? Yes or No: ")
                group = input()
                group = str(group)
                print("""
                Choose which attribute:
                1)Confirmed
                2)Deaths
                3)Active
                4)Recovered
                """)
                var = input("Enter number: ")
                var = int(var)
                if(group == "No"):
                    print("""
                    Choose your aggregate:
                    1) Max
                    2) Min
                    3) Sum
                    4) Average
                    5) Count
                    6) Count records with greater or less # of attribute
                    7) No filter
                    """)
                    userInput = input("Enter number: ")
                    userInput = int(userInput)
                    if(userInput == 1): #getting max for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT MAX(Confirmed)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT MAX(Deaths)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT MAX(Active)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT MAX(Recovered)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 2): #getting min for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT MIN(Confirmed)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT MIN(Deaths)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT MIN(Active)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT MIN(Recovered)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 3): #getting sum for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT SUM(Confirmed)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT SUM(Deaths)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT SUM(Active)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT SUM(Recovered)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 4): #getting average for numerical attribute
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT AVG(Confirmed)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT AVG(Deaths)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT AVG(Active)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT AVG(Recovered)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 5): #getting Count for numerical attribute/records
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT COUNT(Confirmed)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT COUNT(Deaths)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT COUNT(Active)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT COUNT(Recovered)
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 6): #getting count for records with greater or less than # of attribute
                        if(var == 1): #Confirmed
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayTotal
                                WHERE Confirmed > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayTotal
                                WHERE Confirmed < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 2): #deaths
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayTotal
                                WHERE Deaths > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM DayTotal
                                WHERE Deaths < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 3): #Active
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Active > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Active < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 4): #Recovered
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Recovered > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryLatest
                                WHERE Recovered < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                    elif(userInput == 7): #getting all attributes
                        if(var == 1): #Confirmed
                            query = ('''
                            SELECT Confirmed
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Deaths
                            query = ('''
                            SELECT Deaths
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 3): #Active
                            query = ('''
                            SELECT Active
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 4): #Recovered
                            query = ('''
                            SELECT Recovered
                            FROM DayTotal
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                elif(group == "Yes"):
                    print("""
                    Group by what?:
                    1)Date
                    2)Country
                    """)
                    group = int(input())
                    if(var == 1): #Confirmed
                        if(group == 1): #Date
                            query = ("""
                            SELECT Date, Confirmed
                            FROM DayTotal
                            GROUP BY Date, Confirmed
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Confirmed
                            FROM DayTotal
                            GROUP BY Country, Confirmed
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 2): #Deaths
                        if(group == 1): #Date
                            query = ("""
                            SELECT Date, Deaths
                            FROM DayTotal
                            GROUP BY Date, Deaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Deaths
                            FROM DayTotal
                            GROUP BY Country, Deaths
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 3): #Active
                        if(group == 1): #Date
                            query = ("""
                            SELECT Date, Active
                            FROM DayTotal
                            GROUP BY Date, Active
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Active
                            FROM DayTotal
                            GROUP BY Country, Active
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 4): #Recovered
                        if(group == 1): #Date
                            query = ("""
                            SELECT Date, Recovered
                            FROM DayTotal
                            GROUP BY Date, Recovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Country
                            query = ("""
                            SELECT Country, Recovered
                            FROM DayTotal
                            GROUP BY Country, Recovered
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
        elif(userInput == 5): #From CountryCoordinates
            userInput = input("1)Non-Numerical or 2)Numerical attribute?")
            userInput = int(userInput)
            if(userInput == 1): #non-numerical attributes
                print("""
                Choose which attribute:
                1)CID
                2)Province
                3)Country
                """)
                var = input("Enter number: ")
                var = int(var)
                if(var == 1): #CID attribute
                    query = ('''
                    SELECT CID
                    FROM CountryCoordinates
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 2): #Province attribute
                    query = ('''
                    SELECT Province
                    FROM CountryCoordinates
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
                elif(var == 3): #Country attribute
                    query = ('''
                    SELECT Country
                    FROM CountryCoordinates
                    ''')
                    cursor.execute(query)
                    results = cursor.fetchall()
                    for x in results:
                        print(x)
            elif(userInput == 2): #numerical attributes
                print("Would you like to use grouping? Yes or No: ")
                group = input()
                group = str(group)
                print("""
                Choose which attribute:
                1)Latitude
                2)Longitude
                """)
                var = input("Enter number: ")
                var = int(var)
                if(group == "No"):
                    print("""
                    Choose your aggregate:
                    1) Max
                    2) Min
                    3) Sum
                    4) Average
                    5) Count
                    6) Count records with greater or less than # of attribute
                    7) No filter
                    """)
                    userInput = input("Enter number: ")
                    userInput = int(userInput)
                    if(userInput == 1): #getting max for numerical attribute
                        if(var == 1): #Latitude
                            query = ('''
                            SELECT MAX(Latitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Longitude
                            query = ('''
                            SELECT MAX(Longitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 2): #getting min for numerical attribute
                        if(var == 1): #Latitude
                            query = ('''
                            SELECT MIN(Latitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Longitude
                            query = ('''
                            SELECT MIN(Longitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 3): #getting sum for numerical attribute
                        if(var == 1): #Latitude
                            query = ('''
                            SELECT MIN(Latitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Longitude
                            query = ('''
                            SELECT MIN(Longitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 4): #getting average for numerical attribute
                        if(var == 1): #Latitude
                            query = ('''
                            SELECT AVG(Latitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Longitude
                            query = ('''
                            SELECT AVG(Longitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 5): #getting Count for numerical attribute/records
                        if(var == 1): #Latitude
                            query = ('''
                            SELECT COUNT(Latitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Longitude
                            query = ('''
                            SELECT COUNT(Longitude)
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(userInput == 6): #getting count for records with greater or less than # of attribute
                        if(var == 1): #Longitude
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryCoordinates
                                WHERE Latitude > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Latitude
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryCoordinates
                                WHERE Latitude < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                        elif(var == 2): #deaths
                            userInput = input("1)Greater or 2)Less?")
                            userInput = int(userInput)
                            if(userInput == 1): #Greater
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryCoordinates
                                WHERE Longitude > %s
                                ) as ct
                                ''')
                                tuple = (userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                            elif(userInput == 2): #Less
                                userInput = input("What number?: ")
                                userInput = int(userInput)
                                query = ('''
                                SELECT COUNT(*)
                                FROM (
                                SELECT *
                                FROM CountryCoordinates
                                WHERE Longitude < %s
                                ) as ct
                                ''')
                                tuple(userInput)
                                cursor.execute(query, (tuple,))
                                results = cursor.fetchall()
                                for x in results:
                                    print(x)
                    elif(userInput == 7): #getting all attributes
                        if(var == 1): #Latitude
                            query = ('''
                            SELECT Latitude
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(var == 2): #Longitude
                            query = ('''
                            SELECT Longitude
                            FROM CountryCoordinates
                            ''')
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                elif(group == "Yes"):
                    print("""
                    Group by what?:
                    1)CID
                    2)Province
                    3)Country
                    """)
                    group = int(input())
                    if(var == 1): #Latitude
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, Latitude
                            FROM CountryCoordinates
                            GROUP BY CID, Latitude
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Province
                            query = ("""
                            SELECT Province, Latitude
                            FROM CountryCoordinates
                            GROUP BY Province, Latitude
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #Country
                            query = ("""
                            SELECT Country, Latitude
                            FROM CountryCoordinates
                            GROUP BY Country, Latitude
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                    elif(var == 2): #Longitude
                        if(group == 1): #CID grouping
                            query = ("""
                            SELECT CID, Longitude
                            FROM CountryCoordinates
                            GROUP BY CID, Longitude
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 2): #Province
                            query = ("""
                            SELECT Province, Longitude
                            FROM CountryCoordinates
                            GROUP BY Province, Longitude
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x)
                        elif(group == 3): #Country
                            query = ("""
                            SELECT Country, Longitude
                            FROM CountryCoordinates
                            GROUP BY Country, Longitude
                            """)
                            cursor.execute(query)
                            results = cursor.fetchall()
                            for x in results:
                                print(x) #print attributes based on search

    @staticmethod
    def add_records(cursor):
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
            var1 = input("Enter Country: ")
            var2 = input("Enter Continent: ")
            var3 = input("Enter Population: ")
            var3 = int(var3)
            var4 = input("Enter Total Cases: ")
            var4 = int(var4)
            var5 = input("Enter Total Deaths: ")
            var5 = int(var5)
            var6 = input("Enter Total Recovered: ")
            var6 = int(var6)
            var7 = input("Enter Total Active: ")
            var7 = int(var7)
            query = ('''
                INSERT INTO WorldData(Country, Continent, Population, TotalCases, TotalDeaths, TotalRecovered, TotalActive)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''')
            tuple = (var1, var2, var3, var4, var5, var6, var7)
            cursor.execute(query, tuple)
        elif(userInput == 2):
            var1 = input("Enter Country: ")
            var2 = input("Enter Confirmed Case Number: ")
            var2 = int(var2)
            var3 = input("Enter Death Case Number: ")
            var3 = int(var3)
            var4 = input("Enter Recovered Case Number: ")
            var4 = int(var4)
            var5 = input("Enter Active Case: ")
            var5 = int(var5)
            query = ('''
                INSERT INTO CountryLatest(Country, Confirmed, Deaths, Recovered, Active)
                VALUES (%s, %s, %s, %s, %s)
                ''')
            tuple = (var1, var2, var3, var4, var5)
            cursor.execute(query, tuple)
        elif(userInput == 3):
            var1 = input("Enter Date: ")
            var2 = input("Enter Country: ")
            var3 = input("Enter Confirmed Case Number: ")
            var3 = int(var3)
            var4 = input("Enter Deaths Case Number: ")
            var4 = int(var4)
            var5 = input("Enter Recovered Case Number: ")
            var5 = int(var5)
            var6 = input("Enter Active Case Number: ")
            var6 = int(var6)
            query = ('''
                INSERT INTO DayCountry(Date, Country, Confirmed, Deaths, Recovered, Active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''')
            tuple = (var1, var2, var3, var4, var5, var6)
            cursor.execute(query, tuple)
        elif(userInput == 4):
            var1 = input("Enter Date: ")
            var2 = input("Enter Country: ")
            var3 = input("Enter Confirmed Case Number: ")
            var3 = int(var3)
            var4 = input("Enter Deaths Case Number: ")
            var4 = int(var4)
            var5 = input("Enter Recovered Case Number: ")
            var5 = int(var5)
            var6 = input("Enter Active Case Number: ")
            var6 = int(var6)
            query = ('''
                INSERT INTO DayTotal(Date, Country, Confirmed, Deaths, Recovered, Active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ''')
            tuple = (var1, var2, var3, var4, var5, var6)
            cursor.execute(query, tuple)
        elif(userInput == 5):
            var1 = input("Enter Province: ")
            var2 = input("Enter Country: ")
            var3 = input("Enter Latitude: ")
            var3 = int(var3)
            var4 = input("Enter Longitude: ")
            var4 = int(var4)
            query = ('''
                INSERT INTO CountryCoordinates(Province, Country, Latitude, Longitude)
                VALUES (%s, %s, %s, %s)
                ''')
            tuple = (var1, var2, var3, var4)
            cursor.execute(query, tuple) #insert new records

    @staticmethod
    def update_record(cursor):
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
        if(userInput == 1): #updating world data
            var = input('''
            Which attribute would you like to update?:
            1) Country
            2) Continent
            3) Population
            4) TotalCases
            5) TotalDeaths
            6) TotalRecovered
            7) TotalActive
            ''')
            var = int(var)
            userInput = input('''
            How would you like to search/filter?:
            1) CID
            2) Country
            3) Continent
            4) Nothing
            ''')
            userInput = int(userInput)
            if(userInput == 1): #filtering with CID
                if(var == 1): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE WorldData
                    SET Country = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating continent
                    var = input("What would you like to update the continent to: ")
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE WorldData
                    SET Continent = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating population
                    var = input("What would you like to update the population number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE WorldData
                    SET Population = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating total case number
                    var = input("What would you like to update the total case number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE WorldData
                    SET TotalCases = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating total deaths number
                    var = input("What would you like to update the total death number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE WorldData
                    SET TotalDeaths = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating total case number
                    var = input("What would you like to update the total recovered number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE WorldData
                    SET TotalRecovered = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 7): #updating total case number
                    var = input("What would you like to update the total active number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE WorldData
                    SET TotalActive = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 2): #filtering with Country
                if(var == 1): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE WorldData
                    SET Country = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating continent
                    var = input("What would you like to update the continent to: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE WorldData
                    SET Continent = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating population
                    var = input("What would you like to update the population number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE WorldData
                    SET Population = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating total case number
                    var = input("What would you like to update the total case number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalCases = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating total deaths number
                    var = input("What would you like to update the total death number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalDeaths = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating total case number
                    var = input("What would you like to update the total recovered number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalRecovered = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 7): #updating total case number
                    var = input("What would you like to update the total active number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalActive = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 3): #filtering with Continent
                if(var == 1): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = input("Whats the Continent?: ")
                    query = ('''
                    UPDATE WorldData
                    SET Country = %s
                    WHERE Continent = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating continent
                    var = input("What would you like to update the continent to: ")
                    userInput = input("Whats the Continent?: ")
                    query = ('''
                    UPDATE WorldData
                    SET Continent = %s
                    WHERE Continent = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating population
                    var = input("What would you like to update the population number to: ")
                    var = int(var)
                    userInput = input("Whats the Continent?: ")
                    query = ('''
                    UPDATE WorldData
                    SET Population = %s
                    WHERE Continent = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating total case number
                    var = input("What would you like to update the total case number to: ")
                    var = int(var)
                    userInput = input("Whats the Continent?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalCases = %s
                    WHERE Continent = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating total deaths number
                    var = input("What would you like to update the total death number to: ")
                    var = int(var)
                    userInput = input("Whats the Continent?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalDeaths = %s
                    WHERE Continent = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating total case number
                    var = input("What would you like to update the total recovered number to: ")
                    var = int(var)
                    userInput = input("Whats the Continent?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalRecovered = %s
                    WHERE Continent = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 7): #updating total case number
                    var = input("What would you like to update the total active number to: ")
                    var = int(var)
                    userInput = input("Whats the Continent?: ")
                    query = ('''
                    UPDATE WorldData
                    SET TotalActive = %s
                    WHERE Continent = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 4): #filtering with nothing
                if(var == 1): #updating country
                    var = input("What would you like to update the country to: ")
                    query = ('''
                    UPDATE WorldData
                    SET Country = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating continent
                    var = input("What would you like to update the continent to: ")
                    query = ('''
                    UPDATE WorldData
                    SET Continent = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating population
                    var = input("What would you like to update the population number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE WorldData
                    SET Population = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating total case number
                    var = input("What would you like to update the total case number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE WorldData
                    SET TotalCases = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating total deaths number
                    var = input("What would you like to update the total death number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE WorldData
                    SET TotalDeaths = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating total case number
                    var = input("What would you like to update the total recovered number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE WorldData
                    SET TotalRecovered = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 7): #updating total case number
                    var = input("What would you like to update the total active number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE WorldData
                    SET TotalActive = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
        elif(userInput == 2): #updating country latest data
            var = input('''
            Which attribute would you like to update?:
            1) Country
            2) Confirmed cases
            3) Death cases
            4) Recovered cases
            5) Active cases
            ''')
            var = int(var)
            userInput = input('''
            How would you like to filter?:
            1) CID
            2) Country
            3) Nothing
            ''')
            userInput = int(userInput)
            if(userInput == 1): #filtering with CID
                if(var == 1): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryLatest
                    SET Country = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating confirmed case number
                    var = input("What would you like to update the confirmed case number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryLatest
                    SET Confirmed = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating death case number
                    var = input("What would you like to update the death case number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryLatest
                    SET Deaths = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating recovered case number
                    var = input("What would you like to update the recovered case number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryLatest
                    SET Recovered = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating active case number
                    var = input("What would you like to update the active case number to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryLatest
                    SET Active = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 2): #filtering with Country
                if(var == 1): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryLatest
                    SET Country = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating confirmed case number
                    var = input("What would you like to update the confirmed case number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryLatest
                    SET Confirmed = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating death case number
                    var = input("What would you like to update the death case number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryLatest
                    SET Deaths = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating recovered case number
                    var = input("What would you like to update the recovered case number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryLatest
                    SET Recovered = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating active case number
                    var = input("What would you like to update the active case number to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryLatest
                    SET Active = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 3): #filtering with nothing
                if(var == 1): #updating country
                    var = input("What would you like to update the country to: ")
                    query = ('''
                    UPDATE CountryLatest
                    SET Country = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating confirmed case number
                    var = input("What would you like to update the confirmed case number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE CountryLatest
                    SET Confirmed = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating death case number
                    var = input("What would you like to update the death case number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE CountryLatest
                    SET Deaths = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating recovered case number
                    var = input("What would you like to update the recovered case number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE CountryLatest
                    SET Recovered = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating active case number
                    var = input("What would you like to update the active case number to: ")
                    var = int(var)
                    query = ('''
                    UPDATE CountryLatest
                    SET Active = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
        elif(userInput == 3): #updating day country data
            var = input('''
            Which attribute would you like to update?:
            1) Date
            2) Country
            3) Confirmed cases
            4) Death cases
            5) Recovered cases
            6) Active cases
            ''')
            var = int(var)
            userInput = input('''
            How would you like to filter?:
            1) ID
            2) Date
            3) Country
            4) nothing
            ''')
            userInput = int(userInput)
            if(userInput == 1): #filtering with ID
                if(var == 1): #updating date
                    var = input("What would you like to update the date to in YYYY-MM-DD: ")
                    userInput = int(input("Whats the ID?: "))
                    query = ('''
                    UPDATE DayCountry
                    SET Date = %s
                    WHERE ID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating Country
                    var = input("What would you like to update the Country: ")
                    userInput = int(input("Whats the ID?: "))
                    query = ('''
                    UPDATE DayCountry
                    SET Country = %s
                    WHERE ID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating Confirmed cases
                    var = input("What would you like to update the confirmed case to: ")
                    var = int(var)
                    userInput = int(input("Whats the ID?: "))
                    query = ('''
                    UPDATE DayCountry
                    SET Confirmed = %s
                    WHERE ID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating death cases
                    var = input("What would you like to update the death case to: ")
                    var = int(var)
                    userInput = int(input("Whats the ID?: "))
                    query = ('''
                    UPDATE DayCountry
                    SET Deaths = %s
                    WHERE ID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating Recovered cases
                    var = input("What would you like to update the recovered case to: ")
                    var = int(var)
                    userInput = int(input("Whats the ID?: "))
                    query = ('''
                    UPDATE DayCountry
                    SET Recovered = %s
                    WHERE ID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating Active cases
                    var = input("What would you like to update the active case to: ")
                    var = int(var)
                    userInput = int(input("Whats the ID?: "))
                    query = ('''
                    UPDATE DayCountry
                    SET Active = %s
                    WHERE ID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 2): #filtering with Date
                if(var == 1): #updating date
                    var = input("What would you like to update the date to in YYYY-MM-DD: ")
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Date = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating Country
                    var = input("What would you like to update the Country: ")
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Country = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating Confirmed cases
                    var = input("What would you like to update the confirmed case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Confirmed = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating death cases
                    var = input("What would you like to update the death case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Deaths = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating Recovered cases
                    var = input("What would you like to update the recovered case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Recovered = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating Active cases
                    var = input("What would you like to update the active case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Active = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 3): #filtering with Country
                if(var == 1): #updating date
                    var = input("What would you like to update the date to in YYYY-MM-DD: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Date = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating Country
                    var = input("What would you like to update the Country: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Country = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating Confirmed cases
                    var = input("What would you like to update the confirmed case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Confirmed = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating death cases
                    var = input("What would you like to update the death case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Deaths = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating Recovered cases
                    var = input("What would you like to update the recovered case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Recovered = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating Active cases
                    var = input("What would you like to update the active case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Active = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 4): #filtering with nothing
                if(var == 1): #updating date
                    var = input("What would you like to update the date to in YYYY-MM-DD: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Date = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating Country
                    var = input("What would you like to update the Country: ")
                    query = ('''
                    UPDATE DayCountry
                    SET Country = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating Confirmed cases
                    var = input("What would you like to update the confirmed case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayCountry
                    SET Confirmed = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating death cases
                    var = input("What would you like to update the death case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayCountry
                    SET Deaths = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating Recovered cases
                    var = input("What would you like to update the recovered case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayCountry
                    SET Recovered = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating Active cases
                    var = input("What would you like to update the active case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayCountry
                    SET Active = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
        elif(userInput == 4): #updating day total data
            var = input('''
            Which attribute would you like to update?:
            1) Date
            2) Country
            3) Confirmed cases
            4) Death cases
            5) Recovered cases
            6) Active cases
            ''')
            var = int(var)
            userInput = input('''
            How would you like to filter?:
            1) Date
            2) Country
            3) nothing
            ''')
            userInput = int(userInput)
            if(userInput == 1): #filtering with Date
                if(var == 1): #updating date
                    var = input("What would you like to update the date to in YYYY-MM-DD: ")
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Date = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating Country
                    var = input("What would you like to update the Country: ")
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Country = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating Confirmed cases
                    var = input("What would you like to update the confirmed case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Confirmed = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating death cases
                    var = input("What would you like to update the death case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Deaths = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating Recovered cases
                    var = input("What would you like to update the recovered case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Recovered = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating Active cases
                    var = input("What would you like to update the active case to: ")
                    var = int(var)
                    userInput = input("Whats the Date?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Active = %s
                    WHERE Date = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 2): #filtering with Country
                if(var == 1): #updating date
                    var = input("What would you like to update the date to in YYYY-MM-DD: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Date = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating Country
                    var = input("What would you like to update the Country: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Country = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating Confirmed cases
                    var = input("What would you like to update the confirmed case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Confirmed = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating death cases
                    var = input("What would you like to update the death case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Deaths = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating Recovered cases
                    var = input("What would you like to update the recovered case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Recovered = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating Active cases
                    var = input("What would you like to update the active case to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Active = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 3): #filtering with nothing
                if(var == 1): #updating date
                    var = input("What would you like to update the date to in YYYY-MM-DD: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Date = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating Country
                    var = input("What would you like to update the Country: ")
                    query = ('''
                    UPDATE DayTotal
                    SET Country = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating Confirmed cases
                    var = input("What would you like to update the confirmed case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayTotal
                    SET Confirmed = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating death cases
                    var = input("What would you like to update the death case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayTotal
                    SET Deaths = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 5): #updating Recovered cases
                    var = input("What would you like to update the recovered case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayTotal
                    SET Recovered = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 6): #updating Active cases
                    var = input("What would you like to update the active case to: ")
                    var = int(var)
                    query = ('''
                    UPDATE DayTotal
                    SET Active = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
        elif(userInput == 5): #updating country coordinates data
            var = input('''
            Which attribute would you like to update?:
            1) Province
            2) Country
            3) Latitude
            4) Longitude
            ''')
            var = int(var)
            userInput = input('''
            How would you like to filter?:
            1) CID
            2) Province
            3) Country
            4) Nothing
            ''')
            userInput = int(userInput)
            if(userInput == 1): #filtering with CID
                if(var == 1): #updating Province
                    var = input("What would you like to update the Province to: ")
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Province = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Country = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating latitude
                    var = input("What would you like to update the Latitude to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Latitude = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating Longitude number
                    var = input("What would you like to update the Longitude to: ")
                    var = int(var)
                    userInput = int(input("Whats the CID?: "))
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Longitude = %s
                    WHERE CID = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 2): #filtering with Province
                if(var == 1): #updating Province
                    var = input("What would you like to update the Province to: ")
                    userInput = input("Whats the Province?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Province = %s
                    WHERE Province = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = input("Whats the Province?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Country = %s
                    WHERE Province = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating latitude
                    var = input("What would you like to update the Latitude to: ")
                    var = int(var)
                    userInput = input("Whats the Province?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Latitude = %s
                    WHERE Province = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating Longitude number
                    var = input("What would you like to update the Longitude to: ")
                    var = int(var)
                    userInput = input("Whats the Province?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Longitude = %s
                    WHERE Province = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 3): #filtering with Country
                if(var == 1): #updating Province
                    var = input("What would you like to update the Province to: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Province = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating country
                    var = input("What would you like to update the country to: ")
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Country = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating latitude
                    var = input("What would you like to update the Latitude to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Latitude = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating Longitude number
                    var = input("What would you like to update the Longitude to: ")
                    var = int(var)
                    userInput = input("Whats the Country?: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Longitude = %s
                    WHERE Country = %s
                    ''')
                    tuple = (var, userInput)
                    cursor.execute(query, tuple)
            elif(userInput == 4): #filtering with Nothing
                if(var == 1): #updating Province
                    var = input("What would you like to update the Province to: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Province = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 2): #updating country
                    var = input("What would you like to update the country to: ")
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Country = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 3): #updating latitude
                    var = input("What would you like to update the Latitude to: ")
                    var = int(var)
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Latitude = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple)
                elif(var == 4): #updating Longitude number
                    var = input("What would you like to update the Longitude to: ")
                    var = int(var)
                    query = ('''
                    UPDATE CountryCoordinates
                    SET Longitude = %s
                    ''')
                    tuple = (var)
                    cursor.execute(query, tuple) #update records

    @staticmethod
    def delete_record(cursor):
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
        if(userInput == 1): #delete from WorldData
            var = input('''
            How would you like to filter the delete?:
            1) Country
            2) Continent
            3) Population
            4) TotalCases
            5) TotalDeaths
            6) TotalRecovered
            7) TotalActive
            8) Null attribute
            ''')
            var = int(var)
            if(var == 1): #delete filtering with country
                userInput = input("Enter country name: ")
                query = ("""
                DELETE FROM WorldData
                WHERE Country = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 2): #delete filtering with continent
                userInput = input("Enter continent name: ")
                query = ("""
                DELETE FROM WorldData
                WHERE Continent = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 3): #delete filtering with population
                userInput = input("Enter population number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM WorldData
                WHERE Population = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 4): #delete filtering with total cases number
                userInput = input("Enter total cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM WorldData
                WHERE TotalCases = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 5): #delete filtering with total deaths number
                userInput = input("Enter total deaths number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM WorldData
                WHERE TotalDeaths = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 6): #delete filtering with total recovered number
                userInput = input("Enter total recovered cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM WorldData
                WHERE TotalCases = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 7): #delete filtering with total active number
                userInput = input("Enter total active cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM WorldData
                WHERE TotalActive = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 8): #delete filtering by attribute seeing if there are any nulls
                print("""
                Type which attribute you want to check and delete if null:
                Country, Continent, TotalCases, TotalDeaths, TotalRecovered, TotalActive
                """)
                userInput = input()
                query = ("""
                DELETE FROM WorldData
                WHERE %s IS NULL
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
        elif(userInput == 2): #deleting from countryLatest
            var = input('''
            How would you like to filter the delete?:
            1) Country
            2) Confirmed
            3) Deaths
            4) Recovered
            5) Active
            6) Null attribute
            ''')
            var = int(var)
            if(var == 1): #delete filtering by country
                userInput = input("Enter country name: ")
                query = ("""
                DELETE FROM CountryLatest
                WHERE Country = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 2): #delete filtering by confirmed cases number
                userInput = input("Enter confirmed cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM CountryLatest
                WHERE Confirmed = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 3): #delete filtering by death cases number
                userInput = input("Enter death cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM CountryLatest
                WHERE Deaths = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 4): #delete filtering by recovered cases number
                userInput = input("Enter recovered cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM CountryLatest
                WHERE Recovered = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 5): #delete filtering by active cases number
                userInput = input("Enter active cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM CountryLatest
                WHERE Active = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 6): #delete filering by attribute null
                print('''
                Type which attribute you want to check and delete if null:
                Country, Confirmed, Deaths, Recovered, Active
                ''')
                userInput = input()
                query = ("""
                DELETE FROM CountryLatest
                WHERE %s IS NULL
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
        elif(userInput == 3): #delete from DayCountry
            var = input('''
            How would you like to filter the delete?:
            1) Date
            2) Country
            3) Confirmed
            4) Deaths
            5) Recovered
            6) Active
            7) Null attribute
            ''')
            var = int(var)
            if(var == 1): #delete filtering with date
                userInput = input("Enter date in YYYY-MM-DD: ")
                query = ("""
                DELETE FROM DayCountry
                WHERE Date = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 2): #delete filtering with country
                userInput = input("Enter country name: ")
                query = ("""
                DELETE FROM DayCountry
                WHERE Country = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 3): #delete filtering with confirmed case number
                userInput = input("Enter confirmed cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayCountry
                WHERE Confirmed = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 4): #delete filtering with death case number
                userInput = input("Enter death cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayCountry
                WHERE Deaths = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 5): #delete filtering with recovered cases number
                userInput = input("Enter recovered cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayCountry
                WHERE Recovered = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 6): #delete filtering with active cases number
                userInput = input("Enter active cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayCountry
                WHERE Active = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 7): #delete filtering with null attribute
                print('''
                Type which attribute you want to check and delete if null:
                Date, Country, Confirmed, Deaths, Recovered, Active
                ''')
                userInput = input()
                query = ("""
                DELETE FROM DayCountry
                WHERE %s IS NULL
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
        elif(userInput == 4): #deleting from DayTotal
            var = input('''
            How would you like to filter the delete?:
            1) Date
            2) Country
            3) Confirmed
            4) Deaths
            5) Recovered
            6) Active
            7) Null attribute
            ''')
            var = int(var)
            if(var == 1): #delete filtering with date
                userInput = input("Enter date in YYYY-MM-DD: ")
                query = ("""
                DELETE FROM DayTotal
                WHERE Date = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 2): #delete filtering with country
                userInput = input("Enter country name: ")
                query = ("""
                DELETE FROM DayTotal
                WHERE Country = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 3): #delete filtering with confirmed case number
                userInput = input("Enter confirmed cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayTotal
                WHERE Confirmed = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 4): #delete filtering with death case number
                userInput = input("Enter death cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayTotal
                WHERE Deaths = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 5): #delete filtering with recovered cases number
                userInput = input("Enter recovered cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayTotal
                WHERE Recovered = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 6): #delete filtering with active cases number
                userInput = input("Enter active cases number: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM DayTotal
                WHERE Active = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 7): #delete filtering with null attribute
                print('''
                Type which attribute you want to check and delete if null:
                Date, Country, Confirmed, Deaths, Recovered, Active
                ''')
                userInput = input()
                query = ("""
                DELETE FROM DayTotal
                WHERE %s IS NULL
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
        elif(userInput == 5): #deleting from CountryCoordinates
            var = input('''
            How would you like to filter the delete?:
            1) Province
            2) Country
            3) Latitude
            4) Longitude
            5) Null attribute
            ''')
            var = int(var)
            if(var == 1): #delete filtering with province
                userInput = input("Enter Province: ")
                query = ("""
                DELETE FROM CountryCoordinates
                WHERE Province = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 2): #delete filtering with country
                userInput = input("Enter Country: ")
                query = ("""
                DELETE FROM CountryCoordinates
                WHERE Country = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 3): #delete filtering with Latitude
                userInput = input("Enter Latitude: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM CountryCoordinates
                WHERE Latitude = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 4): #delete filtering with longitude
                userInput = input("Enter Longitude: ")
                userInput = int(userInput)
                query = ("""
                DELETE FROM CountryCoordinates
                WHERE Longitude = %s
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,))
            elif(var == 5): #delete filtering with attribute is null
                print('''
                Type attribute to check and delete if null:
                Province, Country, Latitude, Longitude
                ''')
                userInput = input()
                query = ("""
                DELETE FROM CountryCoordinates
                WHERE %s IS NULL
                """)
                tuple = (userInput)
                cursor.execute(query, (tuple,)) #delete records

    @staticmethod
    def create_index(cursor): #index of primary keys
        query = ("""
        CREATE INDEX WorldDataID
        ON WorldData (CID)
        """)
        cursor.execute(query)
        query = ("""
        CREATE INDEX CountryLatestID
        ON CountryLatest (CID)
        """)
        cursor.execute(query)
        query = ("""
        CREATE INDEX DayCountryID
        ON DayCountry(ID)
        """)
        cursor.execute(query)
        query = ("""
        CREATE INDEX DayTotalDate
        ON DayTotal(Date)
        """)
        cursor.execute(query)
        query = ("""
        CREATE INDEX CountryCoordinatesID
        ON CountryCoordinates (CID)
        """)
        cursor.execute(query)
