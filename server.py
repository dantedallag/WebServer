import socket
import threading
import datetime

# class that overrides Thread. Used to fetch a requested file.
class myClientThread(threading.Thread):

	def __init__(self, conn, addr):
		threading.Thread.__init__(self)
		self.conn = conn
		self.addr = addr

	# helper function to return content type
	# can handle all file types listed explicitly and will handle every other one as raw binary
	def __content_type_picker(self, filename):
		filetype = filename.split(".")

		# no file extension
		if len(filetype) == 1:
			return "application/octet-stream"

		filetype = filetype[1]
		if filetype == "html":
			return "text/html"
		elif filetype == "css":
			return "text/css"
		elif filetype == "txt":
			return "text/plain"
		elif filetype == "jpg" or filetype == "jpeg":
			return "image/jpeg"
		elif filetype == "gif":
			return "image/gif"
		elif filetype == "png":
			return "image/png"
		elif filetype == "js" or filetype == "mjs":
			return "text/javascript"
		else:
			return "application/octet-stream"


	# helper function to return an error response
	def __get_error_response(self, errno):
		if errno == 400:
			return "HTTP/1.1 400 Not Found\r\n\r\n".encode("UTF-8")
		elif errno == 403:
			return "HTTP/1.1 403 Not Found\r\n\r\n".encode("UTF-8")
		elif errno == 404:
			return "HTTP/1.1 404 Not Found\r\n\r\n".encode("UTF-8")


	# overrriden run method will fetch and send file
	def run(self):
		print('Connected to: ', self.addr)

		# read in request
		message = ""
		while True:
			data = self.conn.recv(1024)
			dataString = data.decode("UTF-8")
			message += dataString
			if not data or dataString.find("\r\n\r\n") != -1:
				break

		# Split up request for processing
		messageFields = message.split("\r\n");

		# Verify correct format and extract wanted filename
		request = messageFields[0].split(" ")
		if request[0] != "GET" or request[2] != "HTTP/1.1":
			print("Cannot Understand Request")
			response = self.__get_error_response(400)
			self.conn.sendall(response)
			self.conn.close()
		filename = request[1][1:]
		if filename == "":
			filename = "index.html"
		print("filename requested: " + filename)

		# open file and begin sending
		try:
			contentType = self.__content_type_picker(filename)
			file = open(FILEPATH + filename, "rb")
			fileContent = file.read()
			file.close()
			response = ("HTTP/1.1 200 OK\r\nDate: " + str(datetime.datetime.now()) + "\r\nContent-Type: "+ contentType + "\r\nContent-Length: " + str(len(fileContent)) + "\r\n\r\n").encode("UTF-8")
			response += fileContent
			print(str(response))
			self.conn.sendall(response)
			self.conn.close()
		except FileNotFoundError:
			print("Cannot Find Requested File: " + filename)
			response = self.__get_error_response(404)
			self.conn.sendall(response)
			self.conn.close()
		except PermissionError:
			print("Cannot Access Requested File: " + filename)
			response = self.__get_error_response(403)
			self.conn.sendall(response)
			self.conn.close()


# server class that handles socket and creating threads to fetch files
class myServer(object):

	def __init__(self, host, port, filepath):
		self.HOST = host
		self.PORT = port
		self.FILEPATH = filepath
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.bind((self.HOST, self.PORT))

	# server listens for requests and creates a thread to handle each one
	def run_server(self):
		self.s.listen()
		while True:
			conn, addr = self.s.accept()
			myClientThread(conn, addr).start()


# main function
if __name__ == "__main__":
	HOST = "127.0.0.1"
	PORT = 8765
	FILEPATH = "/Users/dantedg/Documents/ClassWork/DistributedSystems/"
	server = myServer(HOST, PORT, FILEPATH).run_server()
