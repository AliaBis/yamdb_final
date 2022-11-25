# import csv

# from django.core.management.base import BaseCommand
# from reviews.models import (Category, Comment, Genre, Review, Title,
#                             TitleGenreAssign, User)


# class Command(BaseCommand):
#     help = "Наполняет базу данными из csv"

#     def handle(self, *args, **options):
#         with open("./static/data/category.csv", encoding='utf-8') as c_file:
#             category_reader = csv.DictReader(c_file, delimiter=",")
#             count = 0
#             for row in category_reader:
#                 if count == 0:
#                     header = (
#                         f'Файл категорий содержит поля: {", ".join(row)}'
#                     )
#                     self.stdout.write(self.style.SUCCESS(header))
#                 if Category.objects.filter(slug=row['slug']).exists():
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (f'{row["slug"]} уже существует, пропустим')
#                         )
#                     )
#                 else:
#                     category = Category.objects.create(
#                         pk=row['id'],
#                         name=row["name"],
#                         slug=row["slug"]
#                     )
#                     self.stdout.write(
#                         self.style.SUCCESS((
#                             (f' Создана категория {row["slug"]} '
#                             f'c id = {category.pk}'))
#                         )
#                     )
#                 count += 1

#         with open("./static/data/genre.csv", encoding='utf-8') as g_file:
#             genre_reader = csv.DictReader(g_file, delimiter=",")
#             count = 0
#             for row in genre_reader:
#                 if count == 0:
#                     header = (f'Файл жанров содержит поля: {", ".join(row)}')
#                     self.stdout.write(self.style.SUCCESS(header))
#                 if Genre.objects.filter(slug=row['slug']).exists():
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (f'{row["slug"]} уже существует, пропустим')
#                         )
#                     )
#                 else:
#                     Genre.objects.create(
#                         pk=row['id'],
#                         name=row["name"],
#                         slug=row["slug"]
#                     )
#                     self.stdout.write(
#                         self.style.SUCCESS((f' Создан жанр {row["slug"]}'))
#                     )
#                 count += 1

#         with open("./static/data/titles.csv", encoding='utf-8') as t_file:
#             title_reader = csv.DictReader(t_file, delimiter=",")
#             count = 0
#             for row in title_reader:
#                 if count == 0:
#                     header = (
#           f'Файл тайтлов содержит поля: {", ".join(row)}')
#                     self.stdout.write(self.style.SUCCESS(header))
#                 if Title.objects.filter(pk=row['id']).exists():
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (f'{row["id"]} уже существует, пропустим')
#                         )
#                     )
#                 else:
#                     title_category = Category.objects.get(pk=row["category"])
#                     Title.objects.create(
#                         pk=row['id'],
#                         name=row["name"],
#                         year=row["year"],
#                         category=title_category
#                     )
#                     self.stdout.write(
#                         self.style.SUCCESS((f' Создан тайтл {row["name"]}'))
#                     )
#                 count += 1

#         with open(
#                 "./static/data/genre_title.csv", encoding='utf-8'
#         ) as gt_file:
#             gt_reader = csv.DictReader(gt_file, delimiter=",")
#             count = 0
#             for row in gt_reader:
#                 if count == 0:
#                     header = (
#                         (f'Файл связей тайтлов и жанров содержит поля: '
#                         f'{", ".join(row)}')
#                     )
#                     self.stdout.write(self.style.SUCCESS(header))
#                 if TitleGenreAssign.objects.filter(pk=row['id']).exists():
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (f'{row["id"]} уже существует, пропустим')
#                         )
#                     )
#                 else:
#                     title = Title.objects.get(pk=row["title_id"])
#                     genre = Genre.objects.get(pk=row["genre_id"])
#                     TitleGenreAssign.objects.create(
#                         pk=row['id'],
#                         title=title,
#                         genre=genre
#                     )
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (
#       f'Тайтлу {title.name} присвоен жанр {genre.name}')
#                         )
#                     )
#                 count += 1

#         with open("./static/data/users.csv", encoding='utf-8') as u_file:
#             u_reader = csv.DictReader(u_file, delimiter=",")
#             count = 0
#             for row in u_reader:
#                 if count == 0:
#                     header = (f'Файл юзеров содержит поля: {", ".join(row)}')
#                     self.stdout.write(self.style.SUCCESS(header))
#                 if User.objects.filter(pk=row['id']).exists():
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (f'{row["id"]} уже существует, пропустим')
#                         )
#                     )
#                 else:
#                     user = User.objects.create_user(
#                         pk=row['id'],
#                         username=row['username'],
#                         email=row['email'],
#                         role=row['role'],
#                         bio=row['bio'],
#                         first_name=row['first_name'],
#                         last_name=row['last_name']
#                     )
#                     self.stdout.write(
#                         self.style.SUCCESS((f'Создан юзер {user.username}'))
#                     )
#                 count += 1

#         with open("./static/data/review.csv", encoding='utf-8') as r_file:
#             r_reader = csv.DictReader(r_file, delimiter=",")
#             count = 0
#             for row in r_reader:
#                 if count == 0:
#                     header = (
#       f'Файл обзоров содержит поля: {", ".join(row)}')
#                     self.stdout.write(self.style.SUCCESS(header))
#                 if Review.objects.filter(pk=row['id']).exists():
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (f'{row["id"]} уже существует, пропустим')
#                         )
#                     )
#                 else:
#                     review_title = Title.objects.get(pk=row['title_id'])
#                     review_author = User.objects.get(pk=row['author'])
#                     review = Review.objects.create(
#                         pk=row['id'],
#                         title=review_title,
#                         text=row['text'],
#                         author=review_author,
#                         score=row['score'],
#                         pub_date=row['pub_date']
#                     )
#                     self.stdout.write(
#                         self.style.SUCCESS((f'Создан обзор {review}'))
#                     )
#                 count += 1

#         with open(
#                 "./static/data/comments.csv", encoding='utf-8'
#         ) as comment_file:
#             comment_reader = csv.DictReader(comment_file, delimiter=",")
#             count = 0
#             for row in comment_reader:
#                 if count == 0:
#                     header = (
#                         f'Файл комментов содержит поля: {", ".join(row)}'
#                     )
#                     self.stdout.write(self.style.SUCCESS(header))
#                 if Comment.objects.filter(pk=row['id']).exists():
#                     self.stdout.write(
#                         self.style.SUCCESS(
#                             (f'{row["id"]} уже существует, пропустим')
#                         )
#                     )
#                 else:
#                     comment_review = Review.objects.get(pk=row['review_id'])
#                     comment_author = User.objects.get(pk=row['author'])
#                     comment = Comment.objects.create(
#                         pk=row['id'],
#                         review=comment_review,
#                         text=row['text'],
#                         author=comment_author,
#                         pub_date=row['pub_date']
#                     )
#                     self.stdout.write(
#                         self.style.SUCCESS((f'Создан коммент {comment}'))
#                     )
#                 count += 1
