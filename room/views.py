from django.shortcuts import render,redirect
from .forms import RoomForm, EditRoom
from .models import Room, File
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.http import HttpResponse

import os
import mimetypes
from chat.models import Message
# Create your views here..


def create_room(request):
    if not request.user.is_authenticated:
        return redirect('/homepage/introduction/')
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            private = form.cleaned_data['private']
            new_room = Room(name=name, description=description, private=private)
            new_room.save()
            new_room.admin.add(request.user) #adding creator
            new_room.users.add(request.user)
            # Adding via invitation
            invitation = form.cleaned_data['invitation'].strip().split(',')
            for username in invitation:
                try:
                    user = User.objects.get(username = username)
                    new_room.invited.add(user)
                except User.DoesNotExist:
                    pass
            return redirect('/room/lobby/')
        else:
            render(request, 'room/Create_Room.html', {'user': request.user, 'form': form})
    else:
        form = RoomForm()
    return render(request, 'room/Create_Room.html', {'user':request.user,'form':form})


def decline(request,roomid):
    myroom = Room.objects.get(id=roomid)
    myroom.invited.remove(request.user)
    return redirect('/room/lobby/')

def test():
    print('test');
    return HttpResponse("test")

def lobby(request):
    if not request.user.is_authenticated:
        return redirect('/homepage/introduction/')
    # Paging for current_room
    current_room = Room.objects.filter(users = request.user)
    c_paginator = Paginator(current_room,3,allow_empty_first_page = True)
    page = request.GET.get('c_page')
    current_room = c_paginator.get_page(page)

    # Paging for public_room
    public_room = Room.objects.filter(private = False)
    public_room = public_room.exclude(users = request.user)
    p_paginator = Paginator(public_room,3,allow_empty_first_page = True)
    p_page = request.GET.get('p_page')
    public_room = p_paginator.get_page(p_page)

    # Paging for invited_room
    invited_room = Room.objects.filter(invited = request.user)
    i_paginator = Paginator(invited_room,3,allow_empty_first_page = True)
    i_page = request.GET.get('i_page')
    invited_room = i_paginator.get_page(i_page)

    # Render the room
    return render(request, 'room/Lobby.html', {'user':request.user,
                                               'current_room':current_room,
                                               'public_room':public_room    ,
                                               'invited_room':invited_room})

def leaveroom(request,roomid):
    myroom = Room.objects.get(id = roomid)
    if not request.user.is_authenticated:
        return redirect('/homepage/introduction/')
    # Paging for current_room
    d = myroom.users.exclude(username = request.user)
    myroom.users.set(d)
    current_room = Room.objects.filter(users = request.user)
    c_paginator = Paginator(current_room,3,allow_empty_first_page = True)
    page = request.GET.get('c_page')
    current_room = c_paginator.get_page(page)

    # Paging for public_room
    public_room = Room.objects.filter(private = False)
    public_room = public_room.exclude(users = request.user)
    p_paginator = Paginator(public_room,3,allow_empty_first_page = True)
    p_page = request.GET.get('p_page')
    public_room = p_paginator.get_page(p_page)

    # Paging for invited_room
    invited_room = Room.objects.filter(invited = request.user)
    i_paginator = Paginator(invited_room,3,allow_empty_first_page = True)
    i_page = request.GET.get('i_page')
    invited_room = i_paginator.get_page(i_page)

    # Render the room
    render(request, 'room/Lobby.html', {'user':request.user,
                                               'current_room':current_room,
                                               'public_room':public_room,
                                               'invited_room':invited_room})
    return redirect('/room/lobby/')

def room(request,roomid):
    class userFile():
        def __init__(self,name):
            self.name = os.path.split(name)[1]
            self.path = name
            self.MIME = mimetypes.MimeTypes().guess_type(name)[0]


    def upload_file(request,myroom):
        myfile = request.FILES['upload']
        fs = FileSystemStorage()
        filename = os.path.join(str(myroom.id),myfile.name)
        filename = fs.save(filename, myfile)
        uploaded_url = fs.url(filename)
        return userFile(uploaded_url)


    if not request.user.is_authenticated:
        return redirect('/homepage/introduction/')
    myroom = Room.objects.get(id = roomid)
    if myroom.private and len(myroom.users.filter(username = request.user.username)) == 0 and len(myroom.invited.filter(username = request.user.username)) == 0:
        # This user does not belong here
        return redirect('room/lobby/')
    # Room is entered maybe via invite, gotta check that
    myroom.invited.remove(request.user)
    # Check if this is admin
    isAdmin = len(myroom.admin.filter(username = request.user.username))!=0

    if myroom.private and len(myroom.users.filter(username = request.user.username)) == 0:
        myroom.users.add(request.user)

    # Else, render this room for the user
    user_list = myroom.users.all()
    myroom.users.add(request.user)
    # handle file upload request
    if request.method == 'POST' and request.FILES.get('upload',False):
        file = upload_file(request,myroom)
        record_of_file = File(name= file.name,file=file.path,room=myroom)
        record_of_file.save()
        print(file)
        return render(request, 'room/Room.html', {'room': myroom, 'user_list': user_list,'file':file,
                                                  'file_set':myroom.file_set.all(),
                                                  'isAdmin':isAdmin})
    if request.method == 'POST':
        file_to_open = request.POST.get('open_file',False)
        if file_to_open:
            file = userFile(file_to_open)
            return render(request, 'room/Room.html', {'room': myroom, 'user_list': user_list, 'file': file,
                                                      'file_set': myroom.file_set.all(),
                                                      'isAdmin':isAdmin})
    return render(request, 'room/Room.html', {'room':myroom,'user_list':user_list,
                                              'file_set':myroom.file_set.all(),
                                              'isAdmin':isAdmin})


def edit(request,roomid):
    myroom = Room.objects.get(id = roomid)
    x = []
    if not request.user.is_authenticated:
        return redirect('/homepage/introduction/')
    if len(myroom.admin.filter(username=request.user.username))==0:
        return redirect('/room/'+str(roomid)+'/')
    if request.method == "POST":
        form = EditRoom(request.POST)
        if 'delete' in request.POST:
            myroom.delete()
            Message.objects.filter(roomname = roomid).delete()
            return redirect('/room/lobby')
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            private = form.cleaned_data['private']
            myroom.name = name
            myroom.description = description
            myroom.private = private
            myroom.users.clear()
            myroom.users.add(request.user)
            myroom.save()
            invitation = form.cleaned_data['invitation'].strip().split(',')
            for username in invitation:
                try:
                    user = User.objects.get(username=username)
                    myroom.invited.add(user)
                except User.DoesNotExist:
                    pass
            manage = form.cleaned_data['manage'].strip().split(',')
            for username in manage:
                try:
                    user = User.objects.get(username=username)
                    myroom.users.add(user)
                except User.DoesNotExist:
                    pass
            return redirect('/room/'+str(roomid))
        else:
            render(request, '/room/edit_room.html', {'user': request.user, 'form': form})
    else:
        form = EditRoom()
        form.fields["name"].initial = myroom.name
        form.fields["description"].initial = myroom.description
        for users in myroom.users.all():
            if (users != request.user):
                x.append(users)
        form.fields["manage"].initial = ','.join(map(str,x))
        form.fields["private"].initial = myroom.private
    return render(request, 'room/edit_room.html', {'user': request.user, 'form': form})

