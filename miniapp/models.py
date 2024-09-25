from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Primary Models Initialization.


# User Profiles
class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(_('User Name'), unique=True, max_length=250)
    fullname = models.CharField(_('Full Name'), default="", max_length=250)
    unique_code = models.CharField(_('Unique Code'), default="", max_length=250)
    profession = models.CharField(_('Profession'), default="", max_length=250)
    account_type = models.CharField(_('Account Type'), default="member", max_length=250)
    profile_pic = models.ImageField(_('Profile Picture'), upload_to='profile_pic/', null=True, blank=True)
    address = models.CharField(_('User Address'), max_length=250, default="")
    mobile = models.CharField(_('User Mobile'), max_length=50, default="")
    codex = models.CharField(_('Codex'), default="", max_length=250)

    class Meta:
        db_table = 'Profiles'


class Event(models.Model):
    name = models.CharField(_('Event Name'), default="", max_length=250)
    description = models.TextField(_('Event Description'), default="",)
    event_link = models.URLField(_("Event Link"),default="")
    location = models.TextField(_("Event Location"), default="")
    donation_goal = models.PositiveIntegerField(_('Donation Goal'), default=1)
    date_new = models.TextField(_('Event Date'), default=0)
    images_count = models.PositiveIntegerField(_("Images Count"), default=0)
    images = models.ManyToManyField("ImageDump", _("Event_Images"), default=1)
    featured = models.CharField(_("Featured Event"), default="null", max_length=300)

    class Meta:
        db_table = 'Events'


class EventReply(models.Model):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    comment = models.TextField(_('Event Comment'), default="")
    poster = models.ForeignKey("CustomUser", on_delete=models.CASCADE)

    class Meta:
        db_table = 'Event Replies'


class EventAttendance(models.Model):
    event = models.ForeignKey("Event",  on_delete=models.CASCADE, default=1)
    attendant = models.ForeignKey("CustomUser", on_delete=models.CASCADE)

    class Meta:
        db_table = 'Event Attendance'


class CommunityTopic(models.Model):
    poster = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="poster")
    topic = models.TextField(_("Topic"), default="")
    insight = models.PositiveIntegerField(_("Insight"), default=0)
    votes = models.PositiveIntegerField(_("Votes"), default=0)
    date = models.DateTimeField(auto_now_add=True)
    voted_users = models.ManyToManyField("CustomUser", related_name="community_voted_users")

    class Meta:
        db_table = 'Community Topic'


class CommunityTopicReply(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    comment = models.TextField(_("Topic"), default="")
    votes = models.PositiveIntegerField(_("Votes"), default=0)
    date = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey("CommunityTopic", on_delete=models.CASCADE)
    insight = models.PositiveIntegerField(_("Insight"), default=0)
    voted_users = models.ManyToManyField("CustomUser", related_name="community_reply_voted_users")

    class Meta:
        db_table = 'Community Topic Replies'


class Blog(models.Model):
    name = models.CharField(_("Blog Name"), default="", max_length=250)
    description = models.TextField(_('Blog Description'))
    date = models.DateTimeField(auto_now_add=True)
    images = models.ManyToManyField("ImageDump", default=1)
    reads = models.PositiveIntegerField(_("Reads"), default=0)
    votes = models.PositiveIntegerField(_("Votes"), default=0)
    voted_users = models.ManyToManyField("CustomUser", related_name="voted_users_blog")

    class Meta:
        db_table = 'Blogs'


class BlogReply(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    comment = models.TextField(_("Comment"), default="")
    date = models.DateTimeField(auto_now_add=True)
    blog = models.ForeignKey("Blog", default=1, on_delete=models.CASCADE)
    votes = models.PositiveIntegerField(_("Votes"), default=0)
    voted_users = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="voted_users")

    class Meta:
        db_table = 'Blog Replies'


class Resource(models.Model):
    name = models.CharField(_("Resource Name"), default="", max_length=250)
    description = models.TextField(_('Resource Description'))
    downloads = models.PositiveIntegerField(_("Downloads"), default=0)
    date = models.DateTimeField(auto_now_add=True)
    images = models.ManyToManyField("ImageDump", default=1)
    media = models.ManyToManyField("FileDump", default=1)

    class Meta:
        db_table = 'Resources'


class FileDump(models.Model):
    file = models.FileField(_('File'), upload_to='fileDumps/', null=True, blank=True)

    class Meta:
        db_table = 'File Dumps'


class ImageDump(models.Model):
    image = models.ImageField(_('Image'), upload_to='dumps/', null=True, blank=True)

    class Meta:
        db_table = 'Image Dumps'


class ContactUs(models.Model):
    email = models.EmailField(_("Email"), default="", max_length=250)
    fullname = models.CharField(_("Fullname"), default="", max_length=250)
    subject = models.CharField(_("Subject"), default="", max_length=250)
    description = models.TextField(_("Description"), default="", max_length=2500)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Contact Us"


class SponsorRequest(models.Model):
    email = models.EmailField(_("Email"), default="", max_length=250)
    fullname = models.CharField(_("Fullname"), default="", max_length=250)
    contact = models.CharField(_("Contact"), default="", max_length=250)
    subject = models.CharField(_("Subject"), default="", max_length=250)
    description = models.TextField(_("Description"), default="", max_length=2500)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Sponsor Request"
