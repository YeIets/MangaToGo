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

##########################################################################

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

def get_chapters_with_offset(mangaid, limit=20, offset=0):
    languages = ["en"]

    # Define the request parameters
    params = {
        "translatedLanguage[]": languages,  # Language filter
        "order[volume]": "asc",             # Sorting by volume ascending
        "order[chapter]": "asc",            # Sorting by chapter ascending
        "limit": limit,                     # Number of items per page
        "offset": offset                    # Skip previous items
    }

    # Make the API request
    url = f"{BASE_URL}/manga/{mangaid}/feed"
    response = requests.get(url, params=params)

    if response.status_code == 200:
        jsonResponse = response.json()

        # Check if the response contains data
        if not jsonResponse["data"]:
            return None  # No more chapters to fetch
        
        # Extract the relevant chapter information
        chapters = [(

        	chapter["id"],  #0
        	chapter["attributes"]["volume"], #1
            chapter["attributes"]["chapter"], #2
            chapter["attributes"]["title"], #3
            chapter["attributes"]["externalUrl"], #4
            )

            for chapter in jsonResponse["data"]
        ]
        return chapters
    else:
        print(f"Error: {response.status_code}")
        return None

def fetch_all_chapters(mangaid, limit=20):
    offset = 0
    all_chapters = []

    while True:
        chapters = get_chapters_with_offset(mangaid, limit, offset)
        
        if not chapters:
            break  # No more chapters to fetch
        
        all_chapters.extend(chapters)
        offset += limit  # Move to the next page

    return all_chapters
	

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


def images_to_PDF(NumberImages, mangaTitle, chapterTitle, pdfNum):
    
    target_size = (1080, 1696)

    images = [
        Image.open(f"{get_local_folder()}/Img{x}.jpg").resize(target_size)
        for x in range(NumberImages)
    ]

    pdf_path = f"{get_local_folder()}/{mangaTitle}-{chapterTitle}-{pdfNum}.pdf"
    
    # Save the first image and append the rest as a PDF
    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:], dpi=(100, 100)
    )

    print("DONE")



#######################################################################################################


def main():

	if os.path.exists(LOCAL_PATH):
		pass
	else:
		os.makedirs(LOCAL_PATH)
		userFile = open(LOCAL_FILE, "w")
		userFile.write(LOCAL_PATH)
		userFile.close()


	#Ask for the namne of the manga and looks for all the matches
	nameSearch = input("Search for a manga: ")
	manga = get_manga_id(nameSearch)

	print(manga[0][1]['en'])

	#Iterates over the manga list ands prints out the NAMES of the manga
	for x in range(len(manga)):
		element = manga.pop(0)
		manga.append(element)
		print(f"{x+1} - {element[1]}")

	#Asks for the desired manga option and stores its ID and TITLE
	desiredManga = int(input("Which manga do you want?"))
	mangaID = manga[desiredManga-1][0]
	mangaTitle = manga[desiredManga-1][1]

	ids = fetch_all_chapters(mangaID)

	#Filters the fetched chapter by "externalUrl", all mangas that have a chapter within another website wont be showed
	#This can be changed in the get_chapters_with_offset params fields

	filtered_data = [item for item in ids if item[4] == None]

	#Prints all the manga's chapters (filtered_data elements) 
	for x in range(len(filtered_data)):
		element = filtered_data.pop(0)
		filtered_data.append(element)

		print(f"{x+1} - Vol = {element[1]}  -  Chapter={element[2]}     -  Title = {element[3]}")

	#Asks for the manga chapter and stores its ID and TITLE
	desiredChapter = int(input("Which chapter do you want?"))
	chapterID = filtered_data[desiredChapter-1][0]
	chapterTitle = filtered_data[desiredChapter-1][3]

	#Fetches bot the HASH and the URL completions for each chapter img
	imgs = get_chapter_imgs(chapterID)

	#Pop the data and store it
	url_hash = imgs.pop(0)
	url_completions = imgs.pop(0)

	NumberImages = len(url_completions)

	download_image(url_completions,url_hash)

	images_to_PDF(NumberImages, mangaTitle, chapterTitle, desiredChapter)

	for x in range(NumberImages):
		os.remove(f"{get_local_folder()}/Img{x}.jpg")





if __name__ == '__main__':
	main()
