import sys
import socket
import http.client

# Funtions
def parse_url(url):
    scheme_end = url.find("://")
    scheme = url[:scheme_end]
    domain_start = scheme_end + 3
    path_start = url.find("/", domain_start)
    if path_start == -1:
        domain = url[domain_start:]
        path = ''
    else:
        domain = url[domain_start:path_start]
        path = url[path_start:]
    return scheme, domain, path

def use_response(response, host):
	# Separate headers and body
	header_end = response.find(b'\r\n\r\n')
	headers = response[:header_end].decode('utf-8').split('\r\n')
	# Status check
	status= ' '.join(headers[0].split(' ')[1:])
	print("Status: " + status)
	type = ' '.join(headers[-1].split(' ')[1:])
	if(type[:5] != 'image'):
		response_txt = response[header_end + 4:].decode('utf-8')

		if status[0] == "3":
			# create var for unbound
			new_url = None

			for header in headers:
				if header.lower().startswith('location:'):
					# Extract the new URL
					new_url = header.split(' ', 1)[1].strip()
					print(f"Redirected URL: {new_url}")
					break
			url_type(new_url)

		elif status[0] == "2":
			html_txt = response_txt.split('\n')
			for html_line in html_txt:
				if html_line.lower().startswith('<img'):
					img_link = ' '.join(html_line.split('"')[1:2])
					if img_link[:4] != "http":
						img_url = "http://" + host + img_link
						print("Referenced URL: " + img_url)
						url_type(img_url)
					else:
						print("Referenced URL: " + img_link)
						url_type(img_link)

def url_type(url):
	scheme, host, path = parse_url(url)

	if scheme == 'https':
		https_request(host, path)
	elif scheme == 'http':
		http_request(host, path)
	else:
		print("error!")

def http_request(host, path):
	port = 80

	sock = None
	# create client socket, connect to server
	try:
		sock = socket.create_connection((host, port), timeout=5)
	except Exception:
		print('Status: Network Error')

	if sock:
		# send http request
		request = f'GET {path} HTTP/1.0\r\n'
		request += f'Host: {host}\r\n'
		request += '\r\n'
		sock.send(bytes(request, 'utf-8'))

		# receive http response
		response = b''
		while True:
			data = sock.recv(4096)
			if not data:
				break
			response += data

		use_response(response,host)

		# Close socket
		sock.close()

def https_request(host, path):
	port = 443
	sock = None

	conn = http.client.HTTPSConnection(host, port)
	conn.putrequest('GET', '/')
	conn.endheaders()
	r = conn.getresponse()
	if r.status == 200:
		print("Status: 200 OK")
	elif r.status == 404:
		print("Status: 404 Not Found")
	else:
		print("Status: " + str(r.status))


## MAIN

# get urls_file name from command line
if len(sys.argv) != 2:
    print('Usage: monitor urls_file')
    sys.exit()

# text file to get list of urls
urls_file = sys.argv[1]

# URL array
url_array = []
# Open the text file in read mode
with open(urls_file, 'r') as file:
    # Loop through each line in the file
    for line in file:
        # Append the line to the list
        url_array.append(line.strip())


for url in url_array:
	print("URL: " + url)
	url_type(url)

	# Space between
	print()
