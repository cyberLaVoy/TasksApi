import base64, os

class SessionStore:

    def __init__(self):
        self.mSessionStore = {}

    def generateSessionID(self):
        random_number = os.urandom(32)
        random_string = base64.b64encode(random_number).decode("utf-8")
        return random_string

    def createSession(self):
        sessionID = self.generateSessionID()
        self.mSessionStore[sessionID] = {}
        return sessionID
    
    def getSession(self, sessionID):
        if sessionID in self.mSessionStore:
            return self.mSessionStore[sessionID]
        else:
            return None
