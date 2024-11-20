from PIL import Image 
import requests
import json
import os, os.path
from pathlib import Path

home = os.path.expanduser('~')
nested = 'MangaToGO/Chapters'

BASE_URL = 'https://api.mangadex.org/'
BASE_URL_DOWNLOAD = 'https://uploads.mangadex.org/data-saver/'
LOCAL_PATH = home + '/MangaToGO/Chapters'
LOCAL_FILE = home + '/MangaToGO/userPath.txt'

def get_local_folder():
	f = open(LOCAL_FILE, "r")
	return f.read()



#Fetches the manga by title and returns the json response

def get_manga_id(title):
	url = f"{BASE_URL}/manga"
	response = requests.get(
		url,
		params={"title":title}
	)
	jsonResponse = response.json()

	#If you want to print the jsonResponse prettyfied
	#print(json.dumps(jsonResponse,indent=2))

	ids = [( mangas["id"], mangas["attributes"]["title"]) for mangas in jsonResponse["data"]]

	return ids
 

#Fetches the manga chapter given the manga ID and returns the json response

def get_chapter_id(mangaid):
	url = f"{BASE_URL}/manga/{mangaid}/feed"
	response = requests.get(url)

	jsonResponse = response.json()

	ids = [( chapters["id"], 
		chapters["attributes"]["volume"], 
		chapters["attributes"]["chapter"],
		chapters["attributes"]["translatedLanguage"]) for chapters in jsonResponse["data"]]	

	return ids

#Fetches the manga chapters "URL" for each image and the HASH to complete the urls  

def get_chapter_imgs(chapterid):

	url = f"{BASE_URL}/at-home/server/{chapterid}"
	response = requests.get(url)

	jsonResponse = response.json()
	#print(json.dumps(jsonResponse,indent=2))

	imgs = [jsonResponse["chapter"]["hash"] ,jsonResponse["chapter"]["dataSaver"]]

	return imgs


#Downloads all images to the specified path 


def download_image(completions, hash):

    for x in range(len(completions)):

        image_url = f'{BASE_URL_DOWNLOAD}/{hash}/{completions[x]}'
        save_as = f"{get_local_folder()}/Img{x}.jpg"

        response = requests.get(image_url)

        with open(save_as, 'wb') as file:
            file.write(response.content)


#Puts all the images into a PDF
#The pdf is saved to the same path where the images where downloaded


def images_to_PDF(completions, pdfNum):
    
    target_size = (1080, 1696)

    images = [
        Image.open(f"{get_local_folder()}/Img{x}.jpg").resize(target_size)
        for x in range(len(completions))
    ]

    pdf_path = f"{get_local_folder()}/Chapter{pdfNum}.pdf"
    
    # Save the first image and append the rest as a PDF
    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:], dpi=(100, 100)
    )

    print("DONE")






def main():

	if os.path.exists(LOCAL_PATH):
		pass
	else:
		os.makedirs(LOCAL_PATH)
		userFile = open(LOCAL_FILE, "w")
		userFile.write(LOCAL_PATH)
		userFile.close()


	#manga is a "list" and manga's elements are "tuples" containing strings

	nameSearch = input("Search for a manga: ")
	manga = get_manga_id(nameSearch)

	#Iterates over the manga list ands prints out the NAMES of the manga
	for x in range(len(manga)):
		element = manga.pop(0)
		manga.append(element)
		print(f"{x+1} - {element[1]}")

	#Asks for the manga and stores it
	desiredManga = int(input("Which manga do you want?"))
	
	mangaID = manga[desiredManga-1][0]
	#print(mangaID)

	ids = get_chapter_id(mangaID)


	filtered_data = [item for item in ids if item[3] == "en"]
	sorted_data = sorted(filtered_data, key=lambda x: (
		int(x[1]) if x[1] is not None else 0,
		str(x[2]),
		x[3] if x[3] is not None else '',
	))

	for x in range(len(sorted_data)):
		element = ids.pop(0)
		sorted_data.append(element)

		print(f"{x+1} Chapter = {element[2]} - ID = {element[x][0]}")
		#print(f"{x+1} - Vol = {element[1]} - Chapter = {element[2]} - Language = {element[3]}")

	#Asks for the manga chapter and stores it	
	desiredChapter = int(input("Which chapter do you want?"))

	chapterID = sorted_data[desiredChapter-1][0]
	#print(chapterID)


	imgs = get_chapter_imgs(chapterID)

	url_hash = imgs.pop(0)
	url_completions = imgs.pop(0)

	download_image(url_completions,url_hash)

	images_to_PDF(url_completions, desiredChapter)

	for x in range(len(url_completions)):
		os.remove(f"{get_local_folder()}/Img{x}.jpg")





if __name__ == '__main__':
	main()
