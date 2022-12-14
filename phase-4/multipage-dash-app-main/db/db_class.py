import mysql.connector

class DbConnector:
    def __init__(self, default_admin_card):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
#             password=""
        )

        self.mycursor = self.mydb.cursor()

        self.mycursor.execute("SHOW DATABASES")

        db_exists = False
        for x in self.mycursor:
            if "smarthome_db" in x:
                db_exists = True

        if (not db_exists):
            
            self.mycursor.execute("CREATE DATABASE smarthome_db")
            self.mycursor.execute("USE smarthome_db")
            self.mycursor.execute('''CREATE TABLE users (
UserID VARCHAR(255) PRIMARY KEY, 
Name VARCHAR(255),
TempThreshold INT,
HumidityThreshold INT,
LightThreshold INT,
Avatar VARCHAR(255))''')
            self.insertUser(default_admin_card, "admin", 22, 80, 500, "https://cdn.theatlantic.com/media/mt/science/cat_caviar.jpg")
            self.addDefaultUsers()
        
        self.mycursor.execute("USE smarthome_db")
        self.updateCurrentUser(default_admin_card)
        
        # self.readAll()
        
    def fetch_table_data(self, table_name):
    # The connect() constructor creates a connection to the MySQL server and returns a MySQLConnection object.
        self.mycursor.execute('select * from ' + table_name)

        header = [row[0] for row in self.mycursor.description]

        rows = self.mycursor.fetchall()
        return header, rows


    def export(self, table_name):
        header, rows = self.fetch_table_data(table_name)

        # Create csv file
        f = open(table_name + '.csv', 'w')

        # Write header
        f.write(','.join(header) + '\n')

        for row in rows:
            f.write(','.join(str(r) for r in row) + '\n')

        f.close()
        print(str(len(rows)) + ' rows written successfully to ' + f.name)
        
    def insertUser(self, user_id, name, temp_threshold, humidity_threshold, light_threshold, avatar):
        sql = "INSERT INTO users (UserID, Name, TempThreshold, HumidityThreshold, LightThreshold, Avatar) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (user_id, name, temp_threshold, humidity_threshold, light_threshold, avatar)
        
        ids = self.getAllIds()
        
        for id in ids:
            if str(user_id) == str(id):
                return False
                PRIMARY
        self.mycursor.execute(sql, values)
        self.mydb.commit()
        self.export('users')
        return True
    
    def updateThresholds(self, user_id, name, temp_threshold, humidity_threshold, light_threshold):
        sql = "UPDATE users SET Name = %s, TempThreshold = %s, HumidityThreshold = %s, LightThreshold = %s WHERE UserID = %s"
        values = (name, temp_threshold, humidity_threshold, light_threshold, user_id)
        self.mycursor.execute(sql, values)
        
        self.mydb.commit()
        self.export('users')

        return True
    
    def updateCurrentUser(self, user_id):
        sql = "SELECT * FROM users"

        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()
        print(myresult)
        for row in myresult:
            # print(str(row[0]) + " " + str(user_id))
            if (str(row[0]) == str(user_id)):
                self.current_user_id = row[0]
                self.current_name = row[1]
                self.current_temp_threshold = row[2]
                self.current_humidity_threshold = row[3]
                self.current_light_threshold = row[4]
                self.avatar = row[5]
                return True
        
        return False
    
    def readAll(self):
        sql = "SELECT * FROM users"

        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()

        for row in myresult:
            print(row[0])
            print(row[1])
            print(row[2])
            print(row[3])
            print(row[4])
            print(row[5])
            
    def getAllIds(self):
        sql = "SELECT * FROM users"

        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()

        ids = []

        for row in myresult:
            ids.append(row[0])
        
        return ids
    
    def addDefaultUsers(self):
        self.insertUser(18813910010, "John Denver", 20, 85, 300, "https://sob-prd-cdn-products.azureedge.net/media/image/product/en/large/0002446306309.jpg")
        self.insertUser(1951804919, "George Foreman", 25, 70, 500, "https://api.time.com/wp-content/uploads/2019/08/tired-spongebob-meme.png")
        self.insertUser(11515410413, "Angus Macgyver", 23, 60, 450, "https://pyxis.nymag.com/v1/imgs/0f9/f96/029acbf4c6d8c67e138e1eb06a277204bf-05-patrick.rsquare.w700.jpg")
