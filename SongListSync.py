import gspread
from mutagen.id3 import ID3
from mutagen.flac import FLAC
import glob
import re
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials

music_folder = r'C:\Users\Kevin\Music\Final\N'
file_formats = ('.flac','.mp3')

types = []
for type in file_formats:
	types.append(music_folder+r'\**\*'+type)

files_found = []
for files in types: 
	files_found.extend(glob.glob(files, recursive=True))
	
pprint(files_found)

tags_found = []
for path in files_found:
	if re.match('(.*)\.mp3', path):
		audio = ID3(path)
		fields = []
		if "TPE1" in audio:
			fields.append(''.join(audio["TPE1"].text))
		else:
			fields.append(' ')
		if "TALB" in audio:
			fields.append(''.join(audio["TALB"].text)) 
		else:
			fields.append(' ')
		if "TCON" in audio:	
			fields.append(''.join(audio["TCON"].text))
		else:
			fields.append(' ')
		if "TRCK" in audio:
			fields.append(''.join(audio["TRCK"].text))
		else:
			fields.append(' ')
		if "TIT2" in audio:
			fields.append(''.join(audio["TIT2"].text))
		else:
			fields.append(' ')
			
		fields.append("mp3")
		tags_found.append(fields)
	elif re.match('(.*)\.flac', path):
		audio = FLAC(path)
		tuple = (''.join(audio.tags["Artist"]), ''.join(audio.tags["Album"]), ''.join(audio.tags["Genre"]), ''.join(audio.tags["TRACKNUMBER"]), ''.join(audio.tags["Title"]), "flac")
		tags_found.append(tuple)
		
pprint(tags_found)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('SongList Python Sync-d02ec1ae7b2e.json', scope)
client = gspread.authorize(creds)  # authenticate with Google

sheet = client.open("SongList_v3").sheet1 # open sheet

row = 2
col = 1
for frame in tags_found:
	for tag in frame: 
		sheet.update_cell(row, col, tag)
		col += 1
	row += 1
	col = 1
