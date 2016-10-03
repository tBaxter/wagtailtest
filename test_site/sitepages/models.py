from datetime import date

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, FieldRowPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, \
    RichTextBlock, RawHTMLBlock, URLBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsnippets.blocks import SnippetChooserBlock

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from snippets.models import CallToAction


EVENT_AUDIENCE_CHOICES = (
    ('public', "Public"),
    ('private', "Private"),
)

# Global Streamfield definition


class PullQuoteBlock(StructBlock):
    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()


class AlignedImageBlock(ImageBlock):
    alignment = models.CharField(
        choices=(
            ('left', 'Wrap left'), 
            ('right', 'Wrap right'), 
            ('mid', 'Mid width'), 
            ('full', 'Full width'),
        )
    )

class AlignedHTMLBlock(StructBlock):
    html = RawHTMLBlock()
    alignment = models.CharField(
        choices=(('normal', 'Normal'), ('full', 'Full width'),)
    )

    class Meta:
        icon = "code"


# A couple of abstract classes that contain commonly used fields

class LinkFields(models.Model):
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



class LinkBlock(StructBlock):
    link_text = models.CharField(max_length=255, help_text="Link text")




# Stream block types
class DemoStreamBlock(StreamBlock):
    title = CharBlock(icon="title", classname="title")
    subtitle = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    raw_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    link = URLBlock()
    call_to_action = SnippetChooserBlock(CallToAction)


class HeroStreamBlock(StreamBlock):
    """
    Defines hero blocks at top of page.
    """
    image = ImageBlock(icon="image")
    title = CharBlock(icon="title", classname="title", blank=True, null=True)
    subtitle = CharBlock(icon="title", classname="title", blank=True, null=True)


class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True



class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True



class PageSection(models.Model):
    columns = models.IntegerField(
        default=1, 
        help_text="On a full-size display, how many columns would you like?"
    )
    section_title = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Allows you to created a headline above your blocks of content (optional)."
    )
    override_id = models.CharField(
        'Override ID', 
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="Create a custom ID as needed for React, etc.")

    blocks = StreamField(
        DemoStreamBlock(), 
    #    #HeroStreamBlock(),
    )

    panels = [
        FieldPanel('columns'),
        FieldPanel('section_title'),
        FieldPanel('override_id'),
        FieldPanel('blocks'),
    ]

    class Meta:
        abstract = True





class SitePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('SitePage', related_name='carousel_items')


class SitePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('SitePage', related_name='related_links')


class SitePageSection(Orderable, PageSection):
    page = ParentalKey('SitePage', related_name='sections')



class SitePage(Page):
    hero = StreamField(
        HeroStreamBlock(), 
        blank=True,
        null=True,
        help_text="Optional. Defines hero image at top of page."
    )
    intro = RichTextField(blank=True)

    body = StreamField(DemoStreamBlock(), help_text="Use for long-form text")
    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    class Meta:
        verbose_name = "page"

SitePage.content_panels = [
    StreamFieldPanel('hero'),
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="intro"),
    StreamFieldPanel('body'),
    #FieldPanel('section_one', classname="section"),
    InlinePanel('sections', label="Sections"),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
]

SitePage.promote_panels = Page.promote_panels



class StandardIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('StandardIndexPage', related_name='related_links')


class StandardIndexPage(Page):
    intro = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

StandardIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

StandardIndexPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]


# Standard page

class StandardPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('StandardPage', related_name='carousel_items')


class StandardPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('StandardPage', related_name='related_links')


class StandardPage(Page):
    intro = RichTextField(blank=True)
    body = RichTextField(blank=True)
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

StandardPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('carousel_items', label="Carousel items"),
    FieldPanel('body', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

StandardPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]


# Text index page

class TextIndexPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('TextIndexPage', related_name='related_links')


class TextIndexPage(Page):
    intro = RichTextField(blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    @property
    def child_pages(self):
        # Get list of live blog pages that are descendants of this page
        child_pages = TextPage.objects.live().descendant_of(self)

        # Order by most recent date first
        child_pages = child_pages.order_by('-date')

        return child_pages

    def get_context(self, request):
        child_pages = self.child_pages

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(child_pages, 10)  # Show 10 blogs per page
        try:
            child_pages = paginator.page(page)
        except PageNotAnInteger:
            child_pages = paginator.page(1)
        except EmptyPage:
            child_pages = paginator.page(paginator.num_pages)

        # Update template context
        context = super(TextIndexPage, self).get_context(request)
        context['child_pages'] = blogs
        return context

TextIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

TextIndexPage.promote_panels = Page.promote_panels


# Text pages

class TextPageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('TextPage', related_name='carousel_items')


class TextPageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('TextPage', related_name='related_links')


class TextPage(Page):
    """
    For content-heavy pages with one main body section.
    """
    body = StreamField(DemoStreamBlock())
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    @property
    def child_index(self):
        # Find closest ancestor which is a text index
        return self.get_ancestors().type(TextIndexPage).last()

TextPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    StreamFieldPanel('body'),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
]

TextPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
]
