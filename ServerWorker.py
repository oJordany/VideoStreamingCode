from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket

class ServerWorker:
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'
	DESCRIBE = 'DESCRIBE'
	
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2
	
	clientInfo = {}
	
	def __init__(self, clientInfo):
		self.clientInfo = clientInfo
		
	def run(self):
		threading.Thread(target=self.recvRtspRequest).start()
	
	def recvRtspRequest(self):
		"""Receive RTSP request from the client."""
		connSocket = self.clientInfo['rtspSocket'][0]
		while True:            
			data = connSocket.recv(256)
			if data:
				print( "Data received:\n" + data)
				self.processRtspRequest(data)
	
	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		# Get the request type
		request = data.split('\n')
		line1 = request[0].split(' ')
		requestType = line1[0]
		
		# Get the media file name
		filename = line1[1]
		
		# Get the RTSP sequence number 
		seq = request[1].split(' ')
		
		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print( "processing SETUP\n")
				
				try:
					self.clientInfo['videoStream'] = VideoStream(filename)
					self.state = self.READY
				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])
				
				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)
				
				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[1])
				
				# Get the RTP/UDP port from the last line
				self.clientInfo['rtpPort'] = request[2].split(' ')[3]
		
		# Process PLAY request 		
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print( "processing PLAY\n")
				self.state = self.PLAYING
				
				# Create a new socket for RTP/UDP
				self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				
				self.replyRtsp(self.OK_200, seq[1])
				
				# Create a new thread and start sending RTP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker']= threading.Thread(target=self.sendRtp) 
				self.clientInfo['worker'].start()
		
		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print( "processing PAUSE\n")
				self.state = self.READY
				
				self.clientInfo['event'].set()
			
				self.replyRtsp(self.OK_200, seq[1])
		
		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print( "processing TEARDOWN\n")

			self.clientInfo['event'].set()
			
			self.replyRtsp(self.OK_200, seq[1])
			
			# Close the RTP socket
			self.clientInfo['rtpSocket'].close()

		# Process DESCRIBE request
		elif requestType == self.DESCRIBE:
			print("processing DESCRIBE\n")
			self.replyDescribe(self.OK_200, seq[1], filename)

	def replyDescribe(self, code, seq, filename):
		"""Send RTSP reply (DESCRIBE) with SDP to the client, using real server info."""
		if code == self.OK_200:
			# Obtém o endereço IP e a porta RTSP real do servidor/conexão
			server_ip = self.clientInfo['rtspSocket'][1][0]

			# O id de sessão (session ID) é gerado no SETUP, mas é útil ter um ID para o SDP
			session_id = randint(1000000000, 9999999999)  # ID de sessão SDP
			session_version = randint(1000000000, 9999999999)  # Versão de sessão SDP

			# Monta o corpo da mensagem SDP (Session Description Protocol)
			# Todos os valores aqui são estáticos, exceto o o=
			sdp = 'v=0\r\n'
			# o=<username> <sess-id> <sess-version> <nettype> <addrtype> <unicast-address>
			# Usamos '-' para <username>. Usamos o IP real do servidor.
			sdp += 'o=- ' + str(session_id) + ' ' + str(session_version) + ' IN IP4 ' + server_ip + '\r\n'
			sdp += 's=Video Stream: ' + filename + '\r\n'  # Inclui o nome do arquivo
			sdp += 't=0 0\r\n'
			# m=<media> <port> <proto> <fmt>
			# <media> é 'video', <port> é 0 (placeholder), <proto> é 'RTP/AVP', <fmt> é 26 (MJPEG)
			sdp += 'm=video 0 RTP/AVP 26\r\n'
			# a=control:<control-url> - O URL de controle para esta trilha (stream)
			# O URL é absoluto: rtsp://<server_ip>:<server_port>/<filename>/streamid=0
			rtsp_port = self.clientInfo['rtspSocket'][1][1]  # Obtém a porta RTSP (opcional, mas mais completo)
			sdp += 'a=control:rtsp://' + server_ip + ':' + str(rtsp_port) + '/' + filename + '/streamid=0\r\n'

			# Monta o cabeçalho de resposta RTSP
			reply = 'RTSP/1.0 200 OK\r\n'
			reply += 'CSeq: ' + seq + '\r\n'
			# O Session ID RTSP é gerado no SETUP, mas para DESCRIBE incluímos se existir
			if 'session' in self.clientInfo:
				reply += 'Session: ' + str(self.clientInfo['session']) + '\r\n'

			# Define o tipo de conteúdo e o comprimento para o corpo SDP
			reply += 'Content-Base: rtsp://' + server_ip + ':' + str(rtsp_port) + '/' + filename + '/\r\n'
			reply += 'Content-Type: application/sdp\r\n'
			reply += 'Content-Length: ' + str(len(sdp.encode('utf-8'))) + '\r\n'
			reply += '\r\n'
			reply += sdp  # Corpo SDP

			connSocket = self.clientInfo['rtspSocket'][0]
			connSocket.send(reply.encode('utf-8'))
			
	def sendRtp(self):
		"""Send RTP packets over UDP."""
		while True:
			self.clientInfo['event'].wait(0.05) 
			
			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet(): 
				break 
				
			data = self.clientInfo['videoStream'].nextFrame()
			if data: 
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:
					address = self.clientInfo['rtspSocket'][1][0]
					port = int(self.clientInfo['rtpPort'])
					self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, frameNumber),(address,port))
				except:
					print( "Connection Error")
					#print( '-'*60)
					#traceback.print(_exc(file=sys.stdout))
					#print( '-'*60)

	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0 
		
		rtpPacket = RtpPacket()
		
		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)
		
		return rtpPacket.getPacket()
		
	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		if code == self.OK_200:
			#print( "200 OK")
			reply = 'RTSP/1.0 200 OK\nCSeq: ' + seq + '\nSession: ' + str(self.clientInfo['session'])
			connSocket = self.clientInfo['rtspSocket'][0]
			connSocket.send(reply)
		
		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print( "404 NOT FOUND")
		elif code == self.CON_ERR_500:
			print( "500 CONNECTION ERROR")
