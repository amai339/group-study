from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from room.models import Room

@login_required(login_url = '/homepage/login')
def index(request):
    return render(request, 'chat/index.html', {})

@login_required(login_url = '/homepage/login')
def room(request, room_name):
    myroom = Room.objects.get(id = room_name)
    if len(myroom.users.filter(username=request.user.username))==0:
        return redirect('/room/lobby/')
    user_name = request.user.username
    return render(request, 'chat/room.html', {
        'room_name': room_name, 'user_name': user_name})