from basic.blog.models import Settings, Post
from basic.blog.signals import invalidate_settings_cache, post_to_twitter
from django.db.models import signals

signals.post_save.connect(invalidate_settings_cache, Settings, True)
signals.pre_save.connect(post_to_twitter, Post)
