from kinopoisk_unofficial.kinopoisk_api_client import KinopoiskApiClient
from kinopoisk_unofficial.request.films.film_request import FilmRequest
from kinopoisk_unofficial.request.films.search_by_keyword_request import SearchByKeywordRequest
from kinopoisk_unofficial.response.staff.person_response import PersonResponse
from kinopoisk_unofficial.request.staff.person_request import PersonRequest
from kinopoisk_unofficial.request.films.film_request import FilmRequest
from kinopoisk_unofficial.request.films.filters_request import FiltersRequest
from kinopoisk_unofficial.request.films.film_search_by_filters_request import FilmSearchByFiltersRequest
from kinopoisk_unofficial.response.films.film_search_by_filters_response import FilmSearchByFiltersResponse
from kinopoisk_unofficial.model.filter_genre import FilterGenre

import urllib.parse
import random
import urllib.request
import json
from django.core.exceptions import * 
import re

api_client = KinopoiskApiClient("b441a4eb-4eb2-42cd-bc88-9bd9a9502f61")

class JuliaMovie():
	def searchByName(name):
		request = SearchByKeywordRequest(name)
		movie_list = api_client.films.send_search_by_keyword_request(request)
		film = False
		
		if len(movie_list.films) >= 1:
			movie = movie_list.films[0]
			film = "{}\nОписание: {} \nГод выпуска: {} \nhttps://www.kinopoisk.ru/film/{}/".format(movie.name_ru, 
				movie.description,movie.year, movie.film_id)
		return film	

	def searchByDirector(name):

		name = urllib.parse.quote_plus(name)

		url = "https://kinopoiskapiunofficial.tech/api/v1/persons?name="+name+"&page=1"

		my_request = urllib.request.Request(url)

		my_request.add_header("X-API-KEY","b441a4eb-4eb2-42cd-bc88-9bd9a9502f61")

		films = False 

		try:
			content = urllib.request.urlopen(my_request).read()
			directors = json.loads(content)
			director_id = directors['items'][0]['kinopoiskId']

			director = PersonRequest(director_id)

			director = api_client.staff.send_person_request(director)

			director_info = "Режиссер {}\n{}\n{}".format(director.nameRu,director.posterUrl,director.webUrl)

			movies = director.films

			names = []

			for m in movies:
				if m.name_ru:
					names.append(m.name_ru)

			names = set(names)
			names_str = "" 

			for m in names:
				names_str += m + "\n"

			films = names_str + director_info

		except:
			pass		

		return films

	def getById(id):
		film = False 

		try:
			request = FilmRequest(id)
			response = api_client.films.send_film_request(request)
			movie = response.film
			film = "{}\nОписание: {} \nГод выпуска: {} \nhttps://www.kinopoisk.ru/film/{}/".format(movie.name_ru, 
				movie.description,movie.year, movie.kinopoisk_id)
		except ValidationError:
			film = "https://www.kinopoisk.ru/film/{}/".format(id)
		except:
			film = "https://www.kinopoisk.ru/film/{}/".format(id)

		return film

	def randomByGenre(genre):
		request = FiltersRequest()
		response = api_client.films.send_filters_request(request)
		gens = response.genres
		gens_box = {}
		for i in gens:
			gens_box[i.id] = i.genre
		gens_str = ""
		for i in gens:
			gens_str += i.genre + " "

		s = re.search(genre.lower(),gens_str)

		if s:
			regs = re.compile(r"(\w*{}\w*)".format(genre.lower()))
			genre = regs.findall(gens_str)[0]
			genre_id = list(gens_box.keys())[list(gens_box.values()).index(genre)]

			# все в жанре на рандомной стр
			request = FilmSearchByFiltersRequest()
			request.genre = {genre_id: genre}

			response = api_client.films.send_film_search_by_filters_request(request)

			movie = response.films[random.randint(0,len(response.films))]

			movie_str = "{}\nГод выпуска: {} \nhttps://www.kinopoisk.ru/film/{}/\n {}".format(movie.name_ru, 
				movie.year, movie.film_id, movie.poster_url_preview)

			result = {'movie':movie_str, 'genres':False}

		else:

			gens_str = ""
			for i in gens:
				gens_str += i.genre + "\n"

			result = {'movie':False, 'genres':gens_str}	

		return result	

class JuliaUser():
	def hi():
		return "Hello from User"		