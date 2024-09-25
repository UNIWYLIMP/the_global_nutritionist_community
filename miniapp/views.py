import random as ran
import random
import time

from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
import django.core.mail as mailer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.models import auth, User
from django.views.decorators.csrf import csrf_exempt
import datetime
from .models import *
from django.db.models import Q
from pathlib import Path
import os


# Create your views here.
def index(request):
    all_events = Event.objects.all()
    parse_list = []
    print(all_events)
    for event in all_events:
        start = 1
        random_id = ran.randint(start, event.images_count) - 1
        random_image = list(event.images.all())[random_id]
        meta_data = {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "event_link": event.event_link,
            "location": event.location,
            "donation_goal": event.donation_goal,
            "date": str(event.date_new.split("T")[0] + " " + event.date_new.split("T")[1]),
            "image": random_image.image.url
        }
        parse_list.append(meta_data)
        print(meta_data)
    # Parse Event To JsonObject
    parse_list = list(reversed(parse_list))
    event_list = parse_list
    print(event_list)
    print(len(event_list))
    if len(event_list)  > 5:
        event_list = parse_list[0 : 5]
        print(event_list)
    print(event_list)
    return render(request, "index.html", {"events": event_list})


def about(request):
    return render(request, "about.html")


def donate(request):
    return render(request, "donate.html")


@csrf_exempt
def sponsor_request(request):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            fullname = request.POST["fullname"]
            contact = request.POST["contact"]
            subject = request.POST["subject"]
            description = request.POST["description"]

            SponsorRequest(email=email, fullname=fullname, contact=contact, subject=subject, description=description).save()
            return JsonResponse({"message": "Sponsor Request Sent"})

        except ValueError:
            return JsonResponse({"message": "Request Failed"})

    return render(request, "sponsor.html")


@csrf_exempt
def contact_request(request):
    if request.method == "POST":
        try:
            email = request.POST["email"]
            fullname = request.POST["fullname"]
            subject = request.POST["subject"]
            description = request.POST["description"]

            ContactUs(email=email, fullname=fullname, subject=subject, description=description).save()
            return JsonResponse({"message": "Contact Request Sent"})

        except ValueError:
            return JsonResponse({"message": "Request Failed"})

    return render(request, "contact.html")


@csrf_exempt
def register(request):
    if request.method == "POST":
        fullname = request.POST['fullname']
        email = request.POST['email']
        password = request.POST['password']
        profession = request.POST['profession']
        repeat_password = request.POST['repeat_password']
        randomly = str(random.randint(3453652, 23455438))
        username = str(fullname).split(" ")[0] + randomly
        account_type = "member"

        if password == repeat_password:
            present = False
            unique_symbol = ["@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "-", "+", "=", "'"]

            for x in unique_symbol:
                if x in str(password):
                    present = True
                else:
                    pass

            if CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email Already In Use')
                return redirect("/register")

            elif CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'Username Already In Use')
                return redirect("/register")

            elif fullname == "":
                messages.info(request, 'Full name can not be empty')
                return redirect("/register")

            elif email == "":
                messages.info(request, 'Email can not be empty')
                return redirect("/register")

            elif len(password) < 8:
                messages.info(request, 'password is too short. Try again')
                return redirect("/register")

            elif not present:
                messages.info(request, 'password must contain special symbol. Try again')
                return redirect("/register")

            else:
                # create profile
                user = CustomUser.objects.create_user(username=username, email=email, password=password, codex=password,
                                                      fullname=fullname, account_type=account_type, profession=profession)
                user.save()

                auth.login(request, user)
                request.session['userId'] = email

                if request.session.get('pathRequest') == "community":
                    return redirect("/community")

                elif request.session.get('pathRequest') == "event":
                    return redirect("/event")

                elif request.session.get('pathRequest') == "resources":
                    return redirect("/resources")

                elif request.session.get('pathRequest') == "blog":
                    return redirect("/blog")

                elif request.session.get('pathRequest') == "blog":
                    return redirect("/about")

                return redirect('/')

        else:
            messages.info(request, 'passwords does not match')
            return redirect('/register')

    return render(request, "register.html")


@csrf_exempt
def login(request):
    if request.method == 'POST':
        identity = request.POST['email']
        password = request.POST['password']
        valid = False
        if CustomUser.objects.filter(email=identity).exists():
            if CustomUser.objects.filter(email=identity)[0].codex == password:
                valid = True
            else:
                pass

        if valid:
            user_con = CustomUser.objects.filter(email=identity)[0]
            auth.login(request, user_con)
            email_id = identity
            request.session['userId'] = email_id
            if request.session.get('pathRequest') == "community":
                return redirect("/community")

            elif request.session.get('pathRequest') == "event":
                return redirect("/event")

            elif request.session.get('pathRequest') == "resources":
                return redirect("/resources")

            elif request.session.get('pathRequest') == "blog":
                return redirect("/blog")

            elif request.session.get('pathRequest') == "blog":
                return redirect("/about")

            return redirect("/")

        else:
            messages.info(request, 'Credentials Invalid')
            return redirect("/login")
    return render(request, "login.html")


def events(request):
    if request.method == "POST":
        query = request.POST["event"]
        all_events = Event.objects.filter(name__contains=query)

        parse_list = []
        for event in all_events:
            image_list = []

            for image_item in event.images.all():
                image_list.append(str(image_item.image.url))

            start = 1
            random_id = ran.randint(start, event.images_count) - 1
            random_image = list(event.images.all())[random_id]

            upper_cut = event.date_new.split("T")[0]
            new_count_down = ""
            for x in upper_cut:
                if x == "-":
                    new_count_down += "/"
                else:
                    new_count_down += x

            meta_data = {
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "event_link": event.event_link,
                "location": event.location,
                "donation_goal": event.donation_goal,
                "date": str(event.date_new.split("T")[0] + " " + event.date_new.split("T")[1]),
                "date_one": str(event.date_new.split("T")[0]),
                "date_two": str(event.date_new.split("T")[1]),
                "new_count_down": new_count_down,
                "image": random_image.image.url,
                "all_images": image_list,
            }
            parse_list.append(meta_data)
        # Parse Event To JsonObject
        parse_list = list(reversed(parse_list))
        featured_id = "null"
        if Event.objects.filter(featured="true").exists():
            featured_id = Event.objects.filter(featured="true")[0].id
        return render(request, "events.html", {"events": parse_list, "event_count": len(all_events), "featured_id": featured_id})

    all_events = Event.objects.all()
    parse_list = []
    for event in all_events:
        image_list = []

        for image_item in event.images.all():
            image_list.append(str(image_item.image.url))

        start = 1
        random_id = ran.randint(start, event.images_count) - 1
        random_image = list(event.images.all())[random_id]

        upper_cut = event.date_new.split("T")[0]
        new_count_down = ""
        for x in upper_cut:
            if x == "-":
                new_count_down += "/"
            else:
                new_count_down += x

        meta_data = {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "event_link": event.event_link,
            "location": event.location,
            "donation_goal": event.donation_goal,
            "date": str(event.date_new.split("T")[0] + " " + event.date_new.split("T")[1]),
            "date_one": str(event.date_new.split("T")[0]),
            "date_two": str(event.date_new.split("T")[1]),
            "new_count_down": new_count_down,
            "image": random_image.image.url,
            "all_images": image_list,
        }
        parse_list.append(meta_data)
    # Parse Event To JsonObject
    parse_list = list(reversed(parse_list))
    featured_id = "null"
    if Event.objects.filter(featured="true").exists():
        featured_id = Event.objects.filter(featured="true")[0].id
    return render(request, "events.html",
                  {"events": parse_list, "event_count": len(all_events), "featured_id": featured_id})


def admin_events(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if CustomUser.objects.get(email=user_email).account_type != "staff":
        return redirect('/events')

    if request.method == "POST":
        query = request.POST["event"]
        all_events = Event.objects.filter(name__contains=query)

        parse_list = []
        for event in all_events:
            start = 1
            random_id = ran.randint(start, event.images_count) - 1
            random_image = list(event.images.all())[random_id]
            meta_data = {
                "id": event.id,
                "name": event.name,
                "description": event.description,
                "event_link": event.event_link,
                "location": event.location,
                "donation_goal": event.donation_goal,
                "date": str(event.date_new.split("T")[0] + " " + event.date_new.split("T")[1]),
                "image": random_image.image.url
            }
            parse_list.append(meta_data)
        # Parse Event To JsonObject
        parse_list = list(reversed(parse_list))
        featured_id = "null"
        if Event.objects.filter(featured="true").exists():
            featured_id = Event.objects.filter(featured="true")[0].id
        return render(request, "admin-event.html", {"events": parse_list, "event_count": len(all_events), "featured_id": featured_id})

    all_events = Event.objects.all()
    parse_list = []
    for event in all_events:
        start = 1
        random_id = ran.randint(start, event.images_count) - 1
        random_image = list(event.images.all())[random_id]
        meta_data = {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "event_link": event.event_link,
            "location": event.location,
            "donation_goal": event.donation_goal,
            "date": str(event.date_new.split("T")[0] + " " + event.date_new.split("T")[1]),
            "image": random_image.image.url
        }
        parse_list.append(meta_data)
    # Parse Event To JsonObject
    parse_list = list(reversed(parse_list))
    featured_id = "null"
    if Event.objects.filter(featured="true").exists():
        featured_id = Event.objects.filter(featured="true")[0].id
    return render(request, "admin-event.html", {"events": parse_list, "event_count": len(all_events), "featured_id": featured_id})


def delete_event(request, pk):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if CustomUser.objects.get(email=user_email).account_type != "staff":
        auth.logout(request)
        return redirect('/login')

    if request.method != "POST":
        event_id = pk
        if not Event.objects.filter(id=event_id).exists():
            return redirect("/admin_events")
        event = Event.objects.get(id=event_id)
        event.delete()
        return redirect("/admin_events")


def featured_event(request, pk):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if CustomUser.objects.get(email=user_email).account_type != "staff":
        auth.logout(request)
        return redirect('/login')

    if request.method != "POST":
        event_id = pk
        if not Event.objects.filter(id=event_id).exists():
            return redirect("/admin_events")
        event = Event.objects.get(id=event_id)
        all_event = Event.objects.all()

        for mini_event in all_event:
            mini_event.featured = "null"
            mini_event.save()

        event.featured = "true"
        event.save()

        return redirect("/admin_events")


@csrf_exempt
def create_event(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if CustomUser.objects.get(email=user_email).account_type != "staff":
        auth.logout(request)
        return redirect('/login')

    print("\n\n\n\n\n\n Point Reached INITIAL \n\n\n\n\n\n")

    if request.method == "POST":
        print("\n\n\n\n\n\n Point Reached POST\n\n\n\n\n\n")
        name = request.POST["event-name"]
        description = request.POST["event-description"]
        donationGoal = request.POST["event-donation-goal"]
        event_link = request.POST["event-link"]
        location = request.POST["event-location"]
        dateEvent = request.POST["event-date"]
        images_0 = request.FILES.getlist("event-images")
        count_of_images = len(list(images_0))

        if location == "":
            location = "Virtual-Event(Online)"

        if event_link == "":
            event_link = "#null"

        new_event = Event(name=name, event_link=event_link, location=location, images_count=count_of_images, description=description, donation_goal=donationGoal, date_new=dateEvent)
        new_event.save()
        for image in images_0:
            event_image = ImageDump(image=image)
            event_image.save()
            new_event.images.add(event_image)
        new_event.save()
        return redirect("/admin_events")
    else:
        return render(request, "create_event.html")


@csrf_exempt
def admin_get_event(request):
    if request.method != "POST":
        return JsonResponse({"message": "Invalid Request Type"})

    event_id = request.POST["event_id"]
    if not Event.objects.filter(id=event_id).exists():
        return JsonResponse({"message": "Invalid Event Id"})

    event = Event.objects.get(id=event_id)
    image_list = []

    for image_item in event.images.all():
        image_list.append(str(image_item.image.url))
    event_replies = event.eventreply_set.all()
    eventReplies = []
    for reply in list(event_replies):
        metadata = {
            "comment": reply.comment,
            "username": reply.poster.username,
            "fullname": reply.poster.fullname,
        }
        eventReplies.append(metadata)

    event_attendance = event.eventattendance_set.all()
    eventAttendance = []
    for event_attendant in list(event_attendance):
        metadata = {
            "username": event_attendant.attendant.username,
            "fullname": event_attendant.attendant.fullname,
        }
        eventAttendance.append(metadata)

    data = {
        "eventID": event.id,
        "eventName": event.name,
        "eventDescription": event.description,
        "eventDonation": event.donation_goal,
        "eventDate": convert_to_date(event.date),
        "eventImages": image_list,
        "eventReplies": eventReplies,
        "eventAttendance": eventAttendance,
    }

    return JsonResponse({"message": "success", "event": data})


def get_event(request, pk):
    if not Event.objects.filter(id=pk).exists():
        return redirect("/events")

    event = Event.objects.get(id=pk)
    image_list = []

    for image_item in event.images.all():
        image_list.append(str(image_item.image.url))
    event_replies = event.eventreply_set.all()
    eventReplies = []
    for reply in list(event_replies):
        metadata = {
            "comment": reply.comment,
            "username": reply.poster.username,
            "fullname": reply.poster.fullname,
        }
        eventReplies.append(metadata)

    event_attendance = event.eventattendance_set.all()
    eventAttendance = []
    for event_attendant in list(event_attendance):
        metadata = {
            "username": event_attendant.attendant.username,
            "fullname": event_attendant.attendant.fullname,
        }
        eventAttendance.append(metadata)

    start = 1
    random_id = ran.randint(start, event.images_count) - 1
    random_image = list(event.images.all())[random_id]

    upper_cut = event.date_new.split("T")[0]
    new_count_down = ""
    for x in upper_cut:
        if x == "-":
            new_count_down += "/"
        else:
            new_count_down += x

    meta_data = {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "event_link": event.event_link,
        "location": event.location,
        "donation_goal": event.donation_goal,
        "date": str(event.date_new.split("T")[0] + " " + event.date_new.split("T")[1]),
        "new_count_down": new_count_down,
        "image": random_image.image.url,
        "all_images": image_list,
    }

    return render(request, "single_event.html", {"event": meta_data})


def comment_on_event(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if request.method == "POST":
        user = CustomUser.objects.get(email=user_email)
        comment = request.POST["comment"]
        event_id = request.POST["event_id"]

        if not Event.objects.filter(id=event_id).exists():
            return redirect("/events")

        event = Event.objects.get(id=event_id)
        new_comment = EventReply(poster=user, comment=comment, event=event)
        new_comment.save()

        return JsonResponse({"message": "success"})
    return JsonResponse({"message": "Invalid Request"})


def attend_an_event(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if request.method == "POST":
        user = CustomUser.objects.get(email=user_email)
        event_id = request.POST["event_id"]

        event = Event.objects.get(id=event_id)
        new_attendance = EventAttendance(attendant=user, event=event)
        new_attendance.save()

        return JsonResponse({"message": "success"})
    return JsonResponse({"message": "Invalid Request"})


def community_offline(request):
    all_topic = list(CommunityTopic.objects.all())
    for topic in all_topic:
        topic.insight = topic.insight + 1
        topic.save()

    all_topics = list(CommunityTopic.objects.all())
    parsed_data = []

    for topic in all_topics:
        is_voted = "no"
        metadata = {
            "posterName": topic.poster.fullname,
            "posterUsername": topic.poster.username,
            "posterProfession": topic.poster.profession,
            "id": topic.id,
            "topic": topic.topic,
            "date": topic.date,
            "votes": topic.votes,
            "insight": topic.insight,
            "is_voted": is_voted,
            "replies": len(list(topic.communitytopicreply_set.all())),
            "profile_color": ran.choice(["red", "blue", "green", "tomato", "yellow", "black"]),
        }
        parsed_data.append(metadata)
    parsed_data = list(reversed(parsed_data))
    return render(request, "community-offline.html", {"topics": parsed_data})


def community(request):
    if not request.user.is_authenticated:
        return redirect("/community_offline")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/community_offline')

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)

    user = {
        "userName": user_con.username,
        "name": user_con.fullname,
        "email": user_con.email,
        "is_authenticated": True,
    }

    all_topic = list(CommunityTopic.objects.all())
    for topic in all_topic:
        topic.insight = topic.insight + 1
        topic.save()

    all_topics = list(CommunityTopic.objects.all())
    parsed_data = []

    for topic in all_topics:
        is_voted = "no"
        if topic.voted_users.filter(email=user_con.email).exists():
            is_voted = "yes"
        metadata = {
           "posterName": topic.poster.fullname,
           "posterUsername": topic.poster.username,
           "posterProfession": topic.poster.profession,
           "id": topic.id,
           "topic": topic.topic,
           "date": topic.date,
           "votes": topic.votes,
           "insight": topic.insight,
           "is_voted": is_voted,
           "replies": len(list(topic.communitytopicreply_set.all())),
           "profile_color": ran.choice(["red", "blue", "green", "tomato", "yellow", "black"]),
        }
        parsed_data.append(metadata)
    parsed_data = list(reversed(parsed_data))
    return render(request, "community.html", {"topics": parsed_data, "user": user})


def member_directory(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')
    
    if request.method == "POST":
        query = request.POST["username"]
        all_user = CustomUser.objects.filter(fullname__contains=query)
        all_users = []
        for user in all_user:
            meta_data = {
                "fullname": user.fullname,
                "email": user.email,
                "username": user.username,
                "profession": user.profession,
                "account_type": user.account_type,
                "profile_color": ran.choice(["red", "blue", "green", "tomato", "yellow", "black"]),
            }
            all_users.append(meta_data)
        all_users = reversed(all_users)

        return render(request, "member-directory.html", {"all_users": all_users, "members_count": len(all_user)})

    all_user = CustomUser.objects.all()
    all_users = []
    for user in all_user:
        meta_data = {
            "fullname": user.fullname,
            "email": user.email,
            "username": user.username,
            "profession": user.profession,
            "account_type": user.account_type,
            "profile_color": ran.choice(["red", "blue", "green", "tomato", "yellow", "black"]),
        }
        all_users.append(meta_data)
    all_users = reversed(all_users)
    return render(request, "member-directory.html", {"all_users": all_users, "members_count": len(all_user)})


@csrf_exempt
def create_topic(request):
    if not request.user.is_authenticated:
        return redirect('/login')

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    if request.method != "POST":
        return render(request, "create_topic.html")

    topic = request.POST['topic']
    if topic == "":
        return redirect('/community')

    if len(topic) == 0:
        return redirect('/community')

    new_topic = CommunityTopic(poster=user_con, topic=topic, votes=0)
    new_topic.save()
    return redirect('/community')


def delete_topic(request, pk):
    if not request.user.is_authenticated:
        return redirect("/login")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect("/login")

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    topic_id = pk

    if not CommunityTopic.objects.filter(id=topic_id).exists():
        return HttpResponse("invalid Id")

    topic = CommunityTopic.objects.get(id=topic_id)
    if topic.poster.id != user_con.id:
        return HttpResponse("insufficient Permission")

    topic.delete()
    return redirect("/community")


def delete_reply(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "invalid"})

    if not request.session.get('userId', None):
        auth.logout(request)
        return JsonResponse({"message": "invalid"})

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    if request.method != "POST":
        return JsonResponse({"message": "invalid"})

    reply_id = request.POST['reply_id']

    if not CommunityTopicReply.objects.filter(id=reply_id).exists():
        return JsonResponse({"message": "invalid"})

    reply = CommunityTopicReply.objects.get(id=reply_id)
    if reply.user.id != user_con.id:
        return JsonResponse({"message": "insufficient Permission"})

    reply.delete()
    return JsonResponse({"message": "success"})


def like_topic(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "invalid"})

    if not request.session.get('userId', None):
        auth.logout(request)
        return JsonResponse({"message": "invalid"})

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    if request.method != "POST":
        return JsonResponse({"message": "invalid"})

    topic_id = request.POST['topic_id']

    if not CommunityTopic.objects.filter(id=topic_id).exists():
        return JsonResponse({"message": "invalid id"})

    topic = CommunityTopic.objects.get(id=topic_id)
    if topic.voted_users.filter(email=user_con.email).exists():
        topic.votes = topic.votes - 1
        topic.voted_users.remove(user_con)
        topic.save()
        return JsonResponse({"message": "success", "type": "dislike"})
    else:
        topic.votes = topic.votes + 1
        topic.voted_users.add(user_con)
        topic.save()
        return JsonResponse({"message": "success", "type": "like"})


def like_reply(request):
    if not request.user.is_authenticated:
        return JsonResponse({"message": "invalid"})

    if not request.session.get('userId', None):
        auth.logout(request)
        return JsonResponse({"message": "invalid"})

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    if request.method != "POST":
        return JsonResponse({"message": "invalid"})

    reply_id = request.POST['reply_id']

    if not CommunityTopicReply.objects.filter(id=reply_id).exists():
        return JsonResponse({"message": "invalid id"})

    reply = CommunityTopicReply.objects.get(id=reply_id)
    if reply.voted_users.filter(email=user_con.email).exists():
        reply.votes = reply.votes - 1
        reply.voted_users.remove(user_con)
        reply.save()
        return JsonResponse({"message": "success", "type": "dislike"})
    else:
        reply.votes = reply.votes + 1
        reply.voted_users.add(user_con)
        reply.save()
        return JsonResponse({"message": "success", "type": "like"})


def single_topic(request, pk):
    if not request.user.is_authenticated:
        return redirect("/community_offline")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/community_offline')

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    user = {
        "userName": user_con.username,
        "name": user_con.fullname,
        "email": user_con.email,
    }

    if not CommunityTopic.objects.filter(id=pk).exists():
        return redirect("/community")

    active_topic = CommunityTopic.objects.get(id=pk)
    all_topics = active_topic.communitytopicreply_set.all()
    parsed_data = []
    for topic in all_topics:
        is_voted = "no"
        if topic.voted_users.filter(email=user_con.email).exists():
            is_voted = "yes"
        metadata = {
            "replierName": topic.user.fullname,
            "replierUsername": topic.user.username,
            "reply": topic.comment,
            "date": topic.date,
            "votes": topic.votes,
            "is_voted": is_voted,
        }
        parsed_data.append(metadata)

    topic = CommunityTopic.objects.get(id=pk)
    is_voted = "no"
    if topic.voted_users.filter(email=user_con.email).exists():
        is_voted = "yes"
    topic_data = {
        "posterName": topic.poster.fullname,
        "posterUsername": topic.poster.username,
        "topic": topic.topic,
        "date": topic.date,
        "votes": topic.votes,
        "is_voted": is_voted,
        "replies": len(list(topic.communitytopicreply_set.all())),
    }

    return render(request, "single-topic.html", {"user": user, "topic": topic_data, "replies": parsed_data})


def reply_topic(request):
    if not request.user.is_authenticated:
        return redirect("/community_offline")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/community_offline')

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    if request.method != "POST":
        return JsonResponse({"message": "invalid"})

    topic_id = request.POST['topic_id']
    topic_reply = request.POST['topic_reply']

    if not CommunityTopic.objects.filter(id=topic_id).exists():
        return redirect("/community")

    topic = CommunityTopic.objects.get(id=topic_id)
    reply = CommunityTopicReply(user=user_con, comment=topic_reply, topic=topic, votes=0)
    reply.save()

    return JsonResponse({"message": "success"})


def resources(request):
    all_resources = Resource.objects.all()
    resources_counts = len(list(all_resources))
    if request.method == "POST":
        query = request.POST['resource']
        all_resources = Resource.objects.filter(name__contains=query)
        resources_counts = len(list(all_resources))
    parse_list = []
    for resource in all_resources:
        start = 1
        random_id = ran.randint(start, len(list(resource.images.all()))) - 1
        random_image = list(resource.images.all())[random_id]
        meta_data = {
            "id": resource.id,
            "name": resource.name,
            "description": resource.description,
            "date": resource.date,
            "downloads": resource.downloads,
            "image": random_image.image.url
        }
        parse_list.append(meta_data)
    return render(request, "resources.html", {"resources": parse_list, "resources_counts": resources_counts})


def admin_resources(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if CustomUser.objects.get(email=user_email).account_type != "staff":
        return redirect('/resources')

    all_resources = Resource.objects.all()
    resources_counts = len(list(all_resources))
    if request.method == "POST":
        query = request.POST['resource']
        all_resources = Resource.objects.filter(name__contains=query)
        resources_counts = len(list(all_resources))
    parse_list = []
    for resource in all_resources:
        start = 1
        random_id = ran.randint(start, len(list(resource.images.all()))) - 1
        random_image = list(resource.images.all())[random_id]
        meta_data = {
            "id": resource.id,
            "name": resource.name,
            "description": resource.description,
            "date": resource.date,
            "downloads": resource.downloads,
            "image": random_image.image.url
        }
        parse_list.append(meta_data)
    return render(request, "admin-resources.html", {"resources": parse_list, "resources_counts": resources_counts})


def get_resources(request):
    all_resources = Resource.objects.all()
    return render(request, "library.html", {"resources": all_resources})


def single_resource(request, pk):
    if not request.user.is_authenticated:
        return redirect("/login")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)
    user = {
        "userName": user_con.username,
        "name": user_con.fullname,
        "email": user_con.email,
    }

    if not Resource.objects.filter(id=pk).exists():
        return redirect("/single_resource")

    resource = Resource.objects.get(id=pk)

    files_url = []
    images_url = []

    for image in resource.images.all():
        images_url.append(image.image.url)

    for file in resource.media.all():
        files_url.append({"name": str(str(file.file.url).split("/")[-1]), "url": file.file.url})

    start = 1
    random_id = ran.randint(start, len(list(resource.images.all()))) - 1
    random_image = list(resource.images.all())[random_id]

    parsed_data = {
        "id": resource.id,
        "name": resource.name,
        "description": resource.description,
        "downloads": resource.downloads,
        "date": resource.date,
        "images": images_url,
        "files": files_url,
        "image_cover": random_image.image.url,
    }
    return render(request, "single-resource.html", {"resource": parsed_data})


def upload_resource(request):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect('/login')

    user_email = request.session.get("userId")
    if CustomUser.objects.get(email=user_email).account_type != "staff":
        auth.logout(request)
        return redirect('/login')

    if request.method == "POST":
        name = request.POST["resource-name"]
        description = request.POST["resource-description"]
        images_0 = request.FILES.getlist("resource-images")
        media_0 = request.FILES.getlist("resource-media")

        new_resource = Resource(name=name, description=description)
        new_resource.save()

        for image in images_0:
            resource_image = ImageDump(image=image)
            resource_image.save()
            new_resource.images.add(resource_image)
        new_resource.save()

        for media in media_0:
            resource_media = FileDump(file=media)
            resource_media.save()
            new_resource.media.add(resource_media)
        new_resource.save()
        return redirect("/admin-resources")
    else:
        return render(request, "create_resource.html")


def delete_resource(request, pk):
    if not request.user.is_authenticated:
        return redirect("/")

    if not request.session.get('userId', None):
        auth.logout(request)
        return redirect("/")

    user_email = request.session.get("userId")
    user_con = CustomUser.objects.get(email=user_email)

    if user_con.account_type != "staff":
        auth.logout(request)
        return redirect("/")

    user = {
        "userName": user_con.username,
        "name": user_con.fullname,
        "email": user_con.email,
    }

    if request.method != "POST":
        resource_id = pk

        if not Resource.objects.filter(id=resource_id).exists():
            return redirect("/admin-resources")
        Resource.objects.get(id=resource_id).delete()
        return redirect("/admin-resources")

    return redirect("/admin-resources")


@csrf_exempt
def resources_download(request):
    if request.method == "POST":
        resource_id = request.POST["material_id"]
        if not Resource.objects.filter(id=resource_id).exists():
            return JsonResponse({"message": "invalid"})
        resource = Resource.objects.get(id=resource_id)
        resource.downloads = resource.downloads + 1
        resource.save()

        return JsonResponse({"message": "success", "resources_downloads": resource.downloads})


def get_blog(request):
    blog = Blog.objects.all()
    return render(request, "blog.html", {"blog": blog})


def convert_to_int(year, month, day, hour, minute, second=0):
    dt = datetime.datetime(year, month, day, hour, minute, second)
    timestamp = int(time.mktime(dt.timetuple()))
    return timestamp


def convert_to_date(int_date):
    return 0


def logout(request):
    auth.logout(request)
    return redirect('/')
