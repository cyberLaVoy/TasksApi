import os
import psycopg2
import psycopg2.extras
import urllib.parse

class TODOS_DB:
    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def createTodosTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS to_dos (rowid SERIAL PRIMARY KEY, short_description VARCHAR(63), long_description VARCHAR(255), priority INTEGER, desired_completion_date DATE, due_date DATE, date_entered DATE, completion_status BOOLEAN, user_id INTEGER)")
        self.connection.commit()

    def createUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (rowid SERIAL PRIMARY KEY, email VARCHAR(255), encrypted_password VARCHAR(255), fname VARCHAR(255), lname VARCHAR(255))")
        self.connection.commit()


# TODOS operations

    def createTODO(self, short_description, long_description, priority, 
                         desired_completion_date, due_date, date_entered, completion_status, user_id):
        Query = "INSERT INTO to_dos (short_description, long_description, priority, desired_completion_date, due_date, date_entered, completion_status, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

        self.cursor.execute(Query, 
                           (short_description, long_description, priority,
                            desired_completion_date, due_date, 
                            date_entered, completion_status, user_id))
        self.connection.commit()

    def getTODOS(self, user_id):
        Query = "SELECT rowid, * FROM to_dos WHERE user_id = %s"
        self.cursor.execute(Query, (user_id,))
        rows = self.cursor.fetchall()
        return rows 

    def getTODO(self, ID):
        Query = "SELECT * FROM to_dos WHERE rowid = %s"
        self.cursor.execute(Query, (ID,))
        item = self.cursor.fetchall()
        return item

    def replaceTODO(self, short_description, long_description, 
                         desired_completion_date, due_date, 
                         completion_status, ID):
        Query = "UPDATE to_dos SET short_description = %s, long_description = %s, desired_completion_date = %s, due_date = %s, completion_status = %s WHERE rowid = %s"
        self.cursor.execute(Query,
                           (short_description, long_description,
                            desired_completion_date, due_date, 
                            completion_status, ID))
        self.connection.commit()


    def deleteTODO(self, ID):
        Query = "DELETE FROM to_dos WHERE rowid = %s"
        self.cursor.execute(Query, (ID,))
        self.connection.commit()

    def checkTODOID(self, ID, user_id):
        self.cursor.execute("SELECT rowid FROM to_dos WHERE user_id = %s", (user_id,))
        IDs = self.cursor.fetchall()

        available = False
        for i in range(len(IDs)):
            if IDs[i]["rowid"] == ID:
                available = True
                break
        return available

# USERS operations

    def createUSER(self, email, encrypted_password, fname, lname):
        Query = "INSERT INTO users (email, encrypted_password, fname, lname) VALUES (%s, %s, %s, %s)"

        self.cursor.execute(Query, (email, encrypted_password, fname, lname))
        self.connection.commit()

    def getUserAuthInfo(self, email):
        Query = "SELECT rowid, encrypted_password FROM users WHERE email = %s"
        self.cursor.execute(Query, (email,))
        user = self.cursor.fetchall()
        return user

    def getUser(self, ID):
        Query = "SELECT email, fname, lname FROM users WHERE rowid = %s"
        self.cursor.execute(Query, (ID,))
        user = self.cursor.fetchall()
        return user

    def checkUserEmail(self, email):
        self.cursor.execute("SELECT email FROM users")
        emails = self.cursor.fetchall()

        taken = False
        for i in range(len(emails)):
            if emails[i]["email"] == email:
                taken = True
                break
        return taken

