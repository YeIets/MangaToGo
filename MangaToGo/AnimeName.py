from PIL import Image 
import requests
import json
import os


base_url = 'https://api.mangadex.org/'
base_url_download = 'https://uploads.mangadex.org/data-saver/'
local_folder= '/home/omar/HOME/MangaToGo/'


#Fetches the manga by title and returns the json response

def get_manga_id(title):
	url = f"{base_url}/manga"
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
	url = f"{base_url}/manga/{mangaid}/feed"
	response = requests.get(url)

	jsonResponse = response.json()

	ids = [( chapters["id"], 
		chapters["attributes"]["volume"], 
		chapters["attributes"]["chapter"],
		chapters["attributes"]["translatedLanguage"]) for chapters in jsonResponse["data"]]	

	return ids

#Fetches the manga chapter "images" and the HASH to complete the URL 

def get_chapter_imgs(chapterid):

	url = f"{base_url}/at-home/server/{chapterid}"
	response = requests.get(url)

	jsonResponse = response.json()
	#print(json.dumps(jsonResponse,indent=2))

	imgs = [jsonResponse["chapter"]["hash"] ,jsonResponse["chapter"]["dataSaver"]]

	return imgs


#Downloads all images 

def download_image(completions, hash):

    for x in range(len(completions)):

        image_url = f'{base_url_download}/{hash}/{completions[x]}'
        save_as = f"Img{x}.jpg"

        # This line should be at the same level as the above ones
        response = requests.get(image_url)

        # This block should be inside the for loop
        with open(save_as, 'wb') as file:
            file.write(response.content)


#Puts all the images into a PDF


def images_to_PDF(completions, pdfNum):
    
    target_size = (1080, 1696)

    images = [
        Image.open(f"{local_folder}/Img{x}.jpg").resize(target_size)
        for x in range(len(completions))
    ]

    pdf_path = f"{local_folder}/Chapter{pdfNum}.pdf"
    
    # Save the first image and append the rest as a PDF
    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:], dpi=(100, 100)
    )






def main():

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

	#print(json.dumps(ids,indent=2))


	filtered_data = [item for item in ids if item[3] == "en"]
	sorted_data = sorted(filtered_data, key=lambda x: (
		int(x[1]) if x[1] is not None else 0,
		str(x[2]),
		x[3] if x[3] is not None else '',
	))


	#print(json.dumps(sorted_data,indent=2))


	for x in range(len(sorted_data)):
		element = sorted_data.pop(0)
		sorted_data.append(element)

		print(f"{x+1} - Vol = {element[1]} - Chapter = {element[2]} - Language = {element[3]}")

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
		os.remove(f"{local_folder}/Img{x}.jpg")





if __name__ == '__main__':
	main()
