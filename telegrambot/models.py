from django.db import models

# Create your models here.

class TelegramUser(models.Model):
	telegram_id = models.BigIntegerField()
	status = models.IntegerField(default=0)
	name = models.CharField(max_length=200,default="")

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['telegram_id'],name='telegram_id_uniq_idx'),
		]

class Movie(models.Model):
	kinopoisk_id = models.BigIntegerField()

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['kinopoisk_id'],name='kinopoisk_id_uniq_idx'),
		]

class UserMovies(models.Model):
	user = models.ForeignKey(TelegramUser,on_delete=models.DO_NOTHING)
	movie = models.ForeignKey(Movie,on_delete=models.DO_NOTHING)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['user','movie'],name='user_movie_uniq_idx'),
		]