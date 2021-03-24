from pprint import pprint

from requests import get, post, delete

# pprint(get('http://localhost:8080/api/news').json())
#
# pprint(get('http://localhost:8080/api/news/1').json())

# pprint(get('http://localhost:8080/api/news/999').json())


# Добавление новой новости с помощью POST-запроса.

# пустой запрос
# pprint(post('http://localhost:8080/api/news').json())

# только заголовка новости
# pprint(post('http://localhost:8080/api/news',
#            json={'title': 'Заголовок'}).json())

# корректный запрос
# pprint(post('http://localhost:8080/api/news',
#            json={'title': 'Заголовок',
#                  'content': 'Текст новости',
#                  'user_id': 1,
#                  'is_private': False}).json())


# Удаления новости:

# print(delete('http://localhost:8080/api/news/999').json())
# # новости с id = 999 нет в базе
#
# print(delete('http://localhost:8080/api/news/8').json())


# pprint(get('http://localhost:8080/api/v2/news').json())

# pprint(get('http://localhost:8080/api/v2/news/1').json())

pprint(get('http://localhost:8080/api/v2/news/99').json())