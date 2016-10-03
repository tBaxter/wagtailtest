from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailsnippets.models import register_snippet


@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class CallToAction(models.Model):
    title = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    url = models.URLField(
    	"Link URL", 
    	null=True, 
    	blank=True, 
    	help_text="""
    		Use local links for pages on the site, without the root domain. Example: "/shop/". 
    		Use the full URL for pages on subdomains. Example: "https://memberhub.virginmobileusa.com".
    		"""
    	)
    link_text = models.CharField(max_length=255, null=True, blank=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('text'),
        FieldPanel('url'),
        FieldPanel('link_text'),
    ]

    def __str__(self):
        return self.text