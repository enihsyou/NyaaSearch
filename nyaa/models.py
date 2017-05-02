from django.db import models


class SubCategories(models.Model):
    sub_category_id = models.IntegerField(primary_key=True)
    sub_category_name = models.TextField(unique=True)

    def __str__(self):
        return self.sub_category_name

    class Meta:
        db_table = 'sub_categories'


class Categories(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.TextField(unique=True)

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'categories'


class Status(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_name = models.TextField(unique=True)

    def __str__(self):
        return self.status_name

    class Meta:
        db_table = 'status'


class Torrents(models.Model):
    torrent_id = models.IntegerField(verbose_name='ID', primary_key=True)
    torrent_name = models.TextField(verbose_name='名字', )
    torrent_hash = models.TextField(verbose_name='哈希', )

    category = models.ForeignKey('Categories')
    sub_category = models.ForeignKey('SubCategories')
    status = models.ForeignKey('Status')

    def __str__(self):
        return self.torrent_name

    class Meta:
        db_table = 'torrents'
        verbose_name = "种子"
        verbose_name_plural = "种子"
