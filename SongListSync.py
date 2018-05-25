import gspread
from mutagen.id3 import ID3, TRCK
from mutagen.flac import FLAC
import glob
import re
import operator
from pprint import pprint
from oauth2client.service_account import ServiceAccountCredentials

music_folder = r'C:\Users\Kevin\Music\Final'
file_formats = ('.flac','.mp3','.m4a')

def main():
	types = []
	for type in file_formats:
		types.append(music_folder+r'\**\*'+type)
	
	files_found = []
	for files in types: 
		files_found.extend(glob.glob(files, recursive=True))
		
	#this is the raw paths in the system structure
	pprint(files_found)
	
	verify_database(files_found)
	

def verify_database(files_found):
	tags_found = []
	for path in files_found:
		if re.match('(.*)\.mp3', path):
			audio = ID3(path)
			fields = []
			if "TPE2" in audio:
				fields.append(''.join(audio["TPE2"].text))
			else:
				fields.append(' ')
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
				t = ''.join(audio["TRCK"].text)
				if re.match(r'(?<!\S)\d(?!\S)',t):
					fields.append('0'+t)
					audio.add(TRCK(encoding=3, text='0'+t))
					audio.save()
				else:
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
			fields = []
			if "ALBUMARTIST" in audio:
				fields.append(''.join(audio.tags["ALBUMARTIST"]))
			if "ARTIST" in audio:
				fields.append(''.join(audio.tags["Artist"]))
			else:
				fields.append(' ')
			if "ALBUM" in audio:
				fields.append(''.join(audio.tags["Album"]))
			else:
				fields.append(' ')
			if "GENRE" in audio:
				fields.append(''.join(audio.tags["Genre"]))
			else:
				fields.append(' ')
			if "TRACKNUMBER" in audio:
				t = ''.join(audio.tags["TRACKNUMBER"])
				if re.match(r'(?<!\S)\d(?!\S)',t):
					fields.append('0'+t)
					audio.tags["TRACKNUMBER"] = '0'+t
					audio.save()
				else:
					fields.append(t)
			else:
				fields.append(' ')
			if "TITLE" in audio:
				fields.append(''.join(audio.tags["Title"]))
			else:
				fields.append(' ')
	
			fields.append("flac")
			tags_found.append(fields)
			
	#tags_found is a list of all the tags 
	#tags are of the form ['albumartist', 'artist', 'album', 'genre', 'tracknumber', 'title', 'extension']
	tags_found = sorted(tags_found, key=operator.itemgetter(0,2,4))
	pprint(tags_found)
	
	row = 2
	col = 2
	# use creds to create a client to interact with the Google Drive API
	scope = ['https://spreadsheets.google.com/feeds']
	creds = ServiceAccountCredentials.from_json_keyfile_name('SongList Python Sync-d02ec1ae7b2e.json', scope)
	client = gspread.authorize(creds)  # authenticate with Google
	
	sheet = client.open("SongList_v3").sheet1 # open sheet
	
	
	for attributes in tags_found:
		current_row = sheet.row_values(row)
		if current_row[1] == attributes[0] and current_row[2] == attributes[1] and current_row[3] == attributes[2] and current_row[4] == attributes[3] and current_row[6] == attributes[5] and current_row[7] == attributes[6]:
			row += 1
			print("Verified entry:", attributes)
		else:	
			if current_row[1] != '' and current_row[2] != '':
				sheet.insert_row('',row)
				print("Inserted New Row")
			for tag in attributes: 
				sheet.update_cell(row, col, tag)
				col += 1
			row += 1
			col = 2
			print("Added entry:", attributes)
	

if __name__ == "__main__":
	main()