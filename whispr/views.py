from django.shortcuts import render, redirect, get_object_or_404
from .models import ChatRoom, ChatMessage
from django.utils.text import slugify

def index(request):
    chatrooms = ChatRoom.objects.all()
    return render(request, 'whispr/index.html', {'chatrooms': chatrooms})

def chatroom(request, slug):
    chatroom = get_object_or_404(ChatRoom, slug=slug)
    messages = ChatMessage.objects.filter(room=chatroom).order_by('date')[:50]
    return render(request, 'whispr/room.html', {
        'chatroom': chatroom,
        'messages': messages
    })

def create_room(request):
    if request.method == "POST":
        name = request.POST.get("room_name")
        if name:
            slug = slugify(name)
            room, created = ChatRoom.objects.get_or_create(name=name, slug=slug)
            return redirect("chatroom", slug=room.slug)
    return redirect("index")
