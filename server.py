from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from todos_db import TODOS_DB
from passlib.hash import bcrypt
from http import cookies
import json, sys, datetime

import sessionStore
gSessionStore = sessionStore.SessionStore()

class Handler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.sendCookie()
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        self.send_header("Access-Control-Allow-Credentials", "true")
        BaseHTTPRequestHandler.end_headers(self)

    def do_OPTIONS(self):
        self.loadSession()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS") 
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        return

    def do_GET(self):
        self.loadSession()
        if self.path == "/todos":
            if "userID" in self.mSession:
                self.handleTODOSList()
            else:
                self.handle401()
        elif self.path[:7] == "/todos/":
            if "userID" in self.mSession:
                available = self.checkTODOID()
                if available:
                    self.handleTODORetrieve()
                else:
                    self.handle404("member")
            else:
                self.handle401()
        else:
            self.handle404("collection")
        return

    def do_POST(self):
        self.loadSession()
        if self.path == "/todos":
            if "userID" in self.mSession:
                self.handleTODOCreate()
            else:
                self.handle401()
        elif self.path =="/users":
            self.handleUserCreate()
        elif self.path == "/sessions":
            self.handleCreateSession()
        else:
            self.handle404("collection")
        return
    
    def do_PUT(self):
        self.loadSession()
        if self.path[:7] == "/todos/":
            if "userID" in self.mSession:
                available = self.checkTODOID()
                if available:
                    self.handleTODOReplace()
                else:
                    self.handle404("member")
            else:
                self.handle401()
        else:
            self.handle404("collection")

    def do_DELETE(self):
        self.loadSession()
        if self.path[:7] == "/todos/":
            if "userID" in self.mSession:
                available = self.checkTODOID()
                if available:
                    self.handleTODODelete()
                else:
                    self.handle404("member")
            else:
                self.handle401()
        else:
            self.handle404("collection")

# TODOS methods

    def parseTODORequestBody(self, currentTodo=None):
        parsed_body = self.getParsedBody()
        todo = {"short_description":None, 
                "long_description":None,
                "priority":None,
                "desired_completion_date":None,
                "due_date":None,
                "completion_status":None}
        for key in todo:
            if parsed_body.get(key) is not None:
                todo[key] = parsed_body[key][0]
            elif currentTodo is not None:
                todo[key] = currentTodo[key]
        return todo
   
    def handleTODOReplace(self):
        db = TODOS_DB()
        ID = str(self.path[7:])
        currentTodo = db.getTODO(ID)[0]
        todo = self.parseTODORequestBody(currentTodo)
        db.replaceTODO(todo, ID)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Update successful.", "utf-8"))

    def handleTODODelete(self):
        db = TODOS_DB()
        ID = str(self.path[7:])
        db = TODOS_DB()
        db.deleteTODO(ID)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Delete successful.", "utf-8"))

    def handleTODOCreate(self):
        todo = self.parseTODORequestBody()
        todo["date_entered"] = datetime.datetime.today().strftime("%Y-%m-%d")
        db = TODOS_DB()
        db.createTODO(todo, self.mSession["userID"])
        self.send_response(201)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Post complete.", "utf-8"))

    def handleTODOSList(self):
        db = TODOS_DB()
        to_dos = db.getTODOS(self.mSession["userID"])
        self.sendJSONObject(to_dos, "tasks", 200)

    def handleTODORetrieve(self):
        ID = str(self.path[7:])
        db = TODOS_DB()
        to_do = db.getTODO(ID)
        self.sendJSONObject(to_do, "task_item", 200, True)

    def checkTODOID(self):
        ID = int(self.path[7:])
        db = TODOS_DB()
        return db.checkTODOID( ID, self.mSession["userID"] )


# USERS Methods

    def handleUserCreate(self):
        db = TODOS_DB()
        parsed_body = self.getParsedBody()

        email = parsed_body["email"][0]
        valid_email = False
        for i in range(len(email)):
            if email[i] == "@" and "." in email[i:]:
                valid_email = True

        taken = db.checkUserEmail(email)
        if taken and not valid_email:
            self.handle422()
        else:
            fname = parsed_body["fname"][0]
            lname = parsed_body["lname"][0]
            password = parsed_body["password"][0]

            encrypted_password = bcrypt.encrypt(password)
            password = ""

            db.createUSER(email, encrypted_password, fname, lname)

            self.send_response(201)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("User Created.", "utf-8"))

# SESSIONS Methods

    def handleCreateSession(self):
        db = TODOS_DB()
        parsed_body = self.getParsedBody()
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        email_exists = db.checkUserEmail(email)
        if email_exists:
            auth_info = db.getUserAuthInfo(email)
            verified = bcrypt.verify(password, auth_info[0]["encrypted_password"])
            if verified:
                self.mSession["userID"] = auth_info[0]["rowid"]
                user = db.getUser(auth_info[0]["rowid"])
                self.sendJSONObject(user, "user", 201, True)
            else:
                self.handle401()
        else:
            self.handle401()
    def loadSession(self):
        self.loadCookie()
        if "sessionID" in self.mCookie:
            sessionID = self.mCookie["sessionID"].value
            sessionData = gSessionStore.getSession(sessionID)
            if sessionData is not None:
                self.mSession = sessionData
            else:
                sessionID = gSessionStore.createSession()
                self.mCookie["sessionID"] = sessionID
                self.mSession = gSessionStore.getSession(sessionID)
        else:
            sessionID = gSessionStore.createSession()
            self.mCookie["sessionID"] = sessionID
            self.mSession = gSessionStore.getSession(sessionID)
    def sendCookie(self):
        for morsel in self.mCookie.values():
            self.send_header("Set-Cookie", morsel.OutputString()) 
    def loadCookie(self):
        print(self.headers)
        if "Cookie" in self.headers:
            self.mCookie = cookies.SimpleCookie(self.headers["Cookie"]) 
        else:
            self.mCookie = cookies.SimpleCookie()

# General Mehtods
    def checkDateFormat(self, date_string):
        try:
            datetime.datetime.strptime(date_string, '%Y-%m-%d')
        except ValueError:
            return None
        return date_string 

    def getParsedBody(self):
        length = int(self.headers["Content-length"])
        body = self.rfile.read(length).decode("utf-8")
        parsed_body = parse_qs(body)
        return parsed_body

    def sendJSONObject(self, load, label, statusCode, singleItemRequest=False):
        jsonObject = {}
        # change datatypes of values to strings
        for i in range(len(load)):
            for key in load[i]:
                load[i][key] = str(load[i][key])
        if (singleItemRequest):
            load = load[0]
        jsonObject[label] = load
        json_string = json.dumps(jsonObject)
        self.send_response(statusCode)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json_string, "utf-8"))

    def handle404(self, memberORcollection):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        if memberORcollection == "collection":
            self.wfile.write(bytes("The resource you are atempting to access was not found.", "utf-8"))
        else:
            self.wfile.write(bytes("The ID in the path provided was not found.", "utf-8"))

    def handle422(self):
        self.send_response(422)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("Invalid data entry.", "utf-8"))

    def handle401(self):
        self.send_response(401)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("This request requires user authetication.", "utf-8"))

def main():
    db = TODOS_DB()
    db.createTodosTable()
    db.createUsersTable()
    db = None

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, Handler)

    print("Listening...")
    server.serve_forever()
main()

