from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os
import base64
import urllib
import json
from dotenv import load_dotenv
import requests



load_dotenv()

FILMAPI = os.getenv('FILMAPI')

hostName = "localhost"
serverPort = 8082

USERNAME = "user"
PASSWORD = "password"

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        auth_header = self.headers.get('Authorization')

        if auth_header is None or not self.authenticate(auth_header):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Authentication required"')
            self.end_headers()
            self.wfile.write(b'Unauthorized')
        else:
            try:
                if self.path == '/':
                    file_path = os.path.join(os.path.dirname(__file__), 'index.html')
                    with open(file_path, 'rb') as file:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(file.read())

                elif self.path == '/form':
                    file_path = os.path.join(os.path.dirname(__file__), 'form.html')
                    with open(file_path, 'rb') as file:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(file.read())

                elif self.path == '/analytics':
                    file_path = os.path.join(os.path.dirname(__file__), 'analytics.html')
                    with open(file_path, 'rb') as file:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(file.read())
                elif self.path == '/input':
                    with open('profile.json', 'rb') as proFile:
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(proFile.read())
                
                else:
                    self.send_error(404, 'Not Found: {}'.format(self.path))
            except Exception as e:
                self.send_error(500, 'Internal Server Error: {}'.format(e))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = urllib.parse.parse_qs(post_data)

        name = parsed_data.get('name', [''])[0]

        year = parsed_data.get('birthyear', [''])[0]

        filedata = requests.get('https://www.omdbapi.com/?y=' + year + '&apikey=' + FILMAPI + '&t=' + name[0]).json()


        animalChoice = parsed_data.get('pets[]', [''])[0]

        profileData = {}

        if animalChoice == 'cat':
            #do cat api call
            catImage = requests.get("https://api.thecatapi.com/v1/images/search").json()["url"]
            profileData.update({"animal" : catImage})
        elif animalChoice == 'dog':   
            dogImage = requests.get("https://dog.ceo/api/breeds/image/random").json()["message"]
            profileData.update({"animal" : dogImage})

        elif animalChoice == 'duck':
            duckImage = requests.get("https://random-d.uk/api/v2/random").json()["url"]
            profileData.update({"animal" : duckImage})

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(f'Successfully received and written data', 'utf-8'))
        profileData.update(parsed_data)

        profileData.update(filedata)

        with open('final.json', 'w') as file:
            file.write(json.dumps(profileData))


        
    def authenticate(self, auth_header):
        credentials = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
        username, password = credentials.split(':', 1)

        return username == USERNAME and password == PASSWORD
if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")