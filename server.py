# HTTP Server Shell
# Author: Barak Gonen
# Purpose: Provide a basis for Ex. 4.4
# Note: The code is written in a simple way, without classes, log files or other utilities, for educational purpose
# Usage: Fill the missing functions and constants

import os
import socket

# constants
IP = '0.0.0.0'
PORT = 8080
DEFAULT_URL = 'webroot\\index.html'
REDIRECTION_DICTIONARY = {'/js/box1.js':'/js/box.js'}
SOCKET_TIMEOUT = 10

def get_file_data(filename):
    " Gets the file data. "
    if not os.path.isfile(filename):
        return None
    with open(filename, 'rb') as file:
        return file.read()

def get_http_header(status_code, content_type=None, content_length=None, location=None):
    """ Generate the http header based on the status code and additional params. """
    header = f"HTTP/1.0 {status_code} \r\n"
    if content_type:
        header += f"Content-Type: {content_type}\r\n"
    if content_length:
        header += f"Content-Length: {content_length}\r\n"
    if location:
        header += f"Location: {location}\r\n"
    header += "\r\n"
    return header

def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    if resource == '/':
        url = DEFAULT_URL
    else:
        url = resource

    if url in REDIRECTION_DICTIONARY:
        new_location = REDIRECTION_DICTIONARY[url]
        client_socket.send(get_http_header("302 Found", location=new_location).encode('utf-8'))
        return

    filename = resource.lstrip('/')
    filetype = filename.split('.')[-1]

    if filetype == 'html':
        content_type = 'text/html; charset=utf-8'
    elif filetype == 'jpg':
        content_type = 'image/jpeg'
    elif filetype == 'txt':
        content_type = 'text/html; charset=utf-8'
    elif filetype == 'js':
        content_type = 'text/javascript; charset=UTF-8'
    elif filetype == 'css':
        content_type = 'text/css'

    data = get_file_data(filename)
    if not data:
        client_socket.send(get_http_header(status_code='404 Not Found').encode('utf-8'))
        return

    content_length = len(data)
    http_response = get_http_header('200 OK', content_type=content_type, content_length=content_length) + data
    client_socket.send(http_response)

def validate_http_request(request):
        """ Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL """
        try:
            lines = request.split('\r\n')
            request_line = lines[0]
            method, url, version = request_line.split(' ')
            if method == 'GET' and version.startswith('HTTP/'):
                return True, url
        except Exception:
            pass
        return False, None

def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    try:
        client_request = client_socket.recv(1024).decode()
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print(f'Got a valid HTTP request, {resource}')
            handle_client_request(resource, client_socket)
        else:
            print(f'Error: Not a valid HTTP request, {resource}')
            http_header = get_http_header('500 Internal Server Error')
            client_socket.send(http_header.encode())
    except Exception as e:
        print(f'Error handling client: {e}')
    finally:
        client_socket.close()

def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(10)
    print ("Listening for connections on port %d" % PORT)

    while True:
        client_socket, client_address = server_socket.accept()
        print ('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)

if __name__ == "__main__":
    # Call the main handler function
    main()