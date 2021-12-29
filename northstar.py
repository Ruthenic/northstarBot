import requests

class northstar():
    def __init__(self, url="https://northstar.tf/client"):
        self.backendUrl = url
        self.servers    = requests.get(url + "/servers").json()

    def updateServers(self):
        self.servers = requests.get(self.backendUrl + "/servers").json()

    def getServers(self):
        return self.servers

    def searchServers(self, keyword, servers, field="name"):
        founds = []
        for server in servers:
            if keyword in server[field]:
                founds.append(server)
        return founds
