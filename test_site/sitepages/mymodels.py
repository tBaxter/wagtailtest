from __future__ import absolute_import, unicode_literals

from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock



ALIGNMENT_CHOICES = (
    ('left', 'Wrap left'), 
    ('right', 'Wrap right'), 
    ('mid', 'Mid width'), 
    ('full', 'Full width'),
)


class ImageBlock(StructBlock):
    """
    Defines an image, with caption and alignment.
    """
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment =  models.CharField(choices=ALIGNMENT_CHOICES)


class HTMLBlock(StructBlock):
    html = RawHTMLBlock()

    class Meta:
        icon = "code"


class LinkFields(models.Model):
    """
    Abstract class to define links.
    """
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


class Section(models.Model):
    """
    A section is a chunk of content on a page. 
    A page may have one or more sections.
    A section will usually -- but not always -- be made up of a group of content blocks.
    """
    title = models.CharField(blank=True, null=True, max_length=250)
    custom_id = models.CharField(
        blank=True, 
        null=True,
        max_length=50, 
        help_text=
            """
            Provides this block a custom identifier. 
            By default, a urlized version of the title will be used, if it exists.
            """
    )


class ContentBlock(StreamBlock):    
    title = CharBlock(icon="title", classname="title")
    subtitle = CharBlock(icon="title", classname="title")
    text = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    raw_html = HTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")
    custom_id = models.CharField(
        blank=True, 
        null=True, 
        max_length=50,
        help_text=
            """
            Provides this block a custom identifier. 
            By default, a urlized version of the title will be used, if it exists.
            """
    )

    # populate from... 
    # be able to create a block from already-existing longform content. 
    # Will need longform content defined. then use summary, title, etc.


class SectionBlock(models.Model):
    pass
 

class SitePage(Page):
    body = RichTextField(blank=True)

    content_panels = [
        FieldPanel('title', classname="full"),
        FieldPanel('body', classname="full")
    ]




# need through table for section/block order
# need through table for page/section order    



