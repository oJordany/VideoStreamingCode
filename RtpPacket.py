import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())
		header = bytearray(HEADER_SIZE)
		#--------------
		# TO COMPLETE
		#--------------
		# Fill the header bytearray with RTP header fields
		# RTP tem cabeçalho com HEADER_SIZE = 12

		# Byte 0: V(2 bits) | P(1 bit) | X(1 bit) | CC (4 bits)
		# V=2, P=0, X=0, CC=0 (conforme as instruções)
		# O campo versão (V) deve ser 2, ocupando os 2 bits mais significativos.
		header[0] = (version << 6) | (padding << 5) | (extension << 4) | cc
		# Byte 1: Marker (1 bit) | PT (7 bits)
		# Marker=0, PT=26 (MJPEG)
		# O campo marker é o bit mais significativo (bit 8).
		header[1] = (marker << 7) | pt
		# Bytes 2 e 3: Sequence Number (16 bits)
		# Sequência de pacotes (número do quadro)
		header[2] = seqnum >> 8  # 8 bits mais significativos
		header[3] = seqnum & 0xFF  # 8 bits menos significativos
		# Bytes 4 a 7: Timestamp (32 bits)
		# Marca de tempo para o quadro de vídeo
		header[4] = (timestamp >> 24) & 0xFF
		header[5] = (timestamp >> 16) & 0xFF
		header[6] = (timestamp >> 8) & 0xFF
		header[7] = timestamp & 0xFF
		# Bytes 8 a 11: SSRC (32 bits)
		# Identificador da fonte de sincronização (o servidor neste caso)
		header[8] = (ssrc >> 24) & 0xFF
		header[9] = (ssrc >> 16) & 0xFF
		header[10] = (ssrc >> 8) & 0xFF
		header[11] = ssrc & 0xFF

		self.header = header
		self.payload = payload
		
	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def seqNum(self):
		"""Return sequence (frame) number."""
		seqNum = self.header[2] << 8 | self.header[3]
		return int(seqNum)
	
	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[4] << 24 | self.header[5] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		"""Return RTP packet."""
		return self.header + self.payload