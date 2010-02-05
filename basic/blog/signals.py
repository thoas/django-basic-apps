from django.core.cache import cache
from basic.blog.models import Settings
from sugar.cache.utils import create_cache_key
import twitter
import urllib2
from django_bitly.models import Bittle
from django.core.urlresolvers import reverse
from django_twitter.models import TwitterAccount
from django.contrib.sites.models import Site

def invalidate_settings_cache(sender=None, instance=None, isnew=False, **kwargs):

    if isnew:
        return

    site_id = instance.site.id
    key = create_cache_key(Settings, field='site__id', field_value=site_id)
    #invalidate cache, set to None for 5 seconds to safegaurd
    #against race condition; concept borrowed from mmalone's django-caching
    cache.set(key, None, 5)


    import twitter
    import urllib2
    from django_bitly.models import Bittle
    from django.core.urlresolvers import reverse
    from django_twitter.models import TwitterAccount
    

def post_to_twitter(sender, instance, **kwargs):
    """ 
    Post new saved, "published" Tweet objects to Twitter.
    """

    #confirm the post is a Public status, according to basic.blog
    status = getattr(instance, "status", 1)
    if status == 1:
        return False

    #if the instance already existed
    if instance.pk:
        #grab the previous instance of the object
        try:
            prior_instance = instance._default_manager.get(pk=instance.pk)
            prior_status = getattr(prior_instance, "status", 1)
            #if this post was published
            if prior_status == 2:
                return False
        except:
            #todo: better logging/handling
            return False
        
    accounts = TwitterAccount.objects.all()
    for account in accounts:

        url = ''
        try:
            bittle = Bittle.objects.bitlify(instance.get_absolute_url())
            url = bittle.shortUrl
        except (AttributeError, Bittle.DoesNotExist):
            pass

        prefix_message = account.default_message
        if prefix_message is None:
            prefix_message = "New Blog Post"

        if url == '':
            current_domain = Site.objects.get_current().domain
            url = "http://%s%s" % (current_domain, instance.get_absolute_url())

        mesg = "%s: %s" % (prefix_message, url)
        username = account.username
        password = account.get_password()
        try:
           twitter_api = twitter.Api(username, password)
           twitter_api.PostUpdate(mesg)
        except urllib2.HttpError, ex:
           return False
