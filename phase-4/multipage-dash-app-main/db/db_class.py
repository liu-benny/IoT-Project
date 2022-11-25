import mysql.connector

class DbConnector:
    def __init__(self, default_admin_card):
        self.mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="root"
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
UserID VARCHAR(255), 
Name VARCHAR(255),
TempThreshold INT,
HumidityThreshold INT,
LightThreshold INT)''')
            self.insertUser(default_admin_card, "admin", 22, 80, 500)
        
        self.mycursor.execute("USE smarthome_db")
        self.changeUser(default_admin_card)
        
        self.readAll()
        
        
        
        
    def fetch_table_data(self, table_name):
    # The connect() constructor creates a connection to the MySQL server and returns a MySQLConnection object.
        cnx = mysql.connector.connect(
            host='localhost',
            database='smarthome_db',
            user='root',
            password='root'
        )

        cursor = cnx.cursor()
        cursor.execute('select * from ' + table_name)

        header = [row[0] for row in cursor.description]

        rows = cursor.fetchall()

        # Closing connection
        cnx.close()

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
        
    def insertUser(self, user_id, name, temp_threshold, humidity_threshold, light_threshold):
        sql = "INSERT INTO users (UserID, Name, TempThreshold, HumidityThreshold, LightThreshold) VALUES (%s, %s, %s, %s, %s)"
        values = (user_id, name, temp_threshold, humidity_threshold, light_threshold)
        self.mycursor.execute(sql, values)

        ids = self.getAllIds()
        print(ids)
        
        for id in ids:
            if user_id in id:
                return False
                
        self.mydb.commit()
        self.export('users')
        return True
    
    def updateTempThreshold(self, temp_threshold):
        sql = "UPDATE users SET TempThreshold = %d WHERE UserId = %s"
        values = (temp_threshold, user_id)
        self.mycursor.execute(sql, values)
        
        self.mydb.commit()
        export('users')
    
    def updateHumidityThreshold(self, humidity_threshold):
        sql = "UPDATE users SET HumidityThreshold = %d WHERE UserId = %s"
        values = (humidity_threshold, user_id)
        self.mycursor.execute(sql, values)
        
        self.mydb.commit()
        self.export('users')
    
    def updateLightThreshold(self, light_threshold):
        sql = "UPDATE users SET LightThreshold = %d WHERE UserId = %s"
        values = (light_threshold, user_id)
        self.mycursor.execute(sql, values)
        
        self.mydb.commit()
        self.export('users')
    
    def changeUser(self, user_id):
        sql = "SELECT * FROM users WHERE UserId='" + user_id + "'"

        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()

        for row in myresult:
            self.current_user_id = row[0]
            self.current_name = row[1]
            self.current_temp_threshold = row[2]
            self.current_humidity_threshold = row[3]
            self.current_light_threshold = row[4]
    
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
            
    def getAllIds(self):
        sql = "SELECT * FROM users"

        self.mycursor.execute(sql)
        myresult = self.mycursor.fetchall()

        ids = []

        for row in myresult:
            ids.append(row[0])
        
        return ids
