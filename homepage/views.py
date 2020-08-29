from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from .forms import UserForm,CreateUser
from django.contrib.auth.models import User
import string
from django.contrib.auth.password_validation import *

# Create your views here.

def introduction(request):
    return render(request, 'homepage/introduction.html', {})



def homepage(request):
    if not request.user.is_authenticated:
        return redirect('/homepage/introduction/')
    return redirect('/room/lobby/')




def log_out(request):
    logout(request)
    return redirect('/homepage/')


def log_in(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            username = form.cleaned_data['username']
            if (string.whitespace+string.punctuation) in username:
                return render(request, 'homepage/login.html', {'error_message': "username cannot contain special characters",
                                                        'form': zip(form.fields, form)})
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('/homepage/')
            else:
                error_message = "Wrong username or password!"
                return render(request,'homepage/login.html',{'error_message' : error_message,
                                                             'form' : zip(form.fields,form)})
        else:
            # Error in putting in field
            return render(request,'homepage/login.html',{'form':zip(form.fields,form)})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserForm()
    return render(request, 'homepage/login.html', {'error_message': "",
                                                   'form': zip(form.fields,form)})



def register(request):
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            password_2 = form.cleaned_data['confirm_password']
            email = form.cleaned_data['email']
            user = User.objects.filter(username = username).all()
            e = User.objects.filter(email = email).all()
            if len(user):
                error_message = "User already exists"
                return render(request, 'homepage/register.html',
                              {'error_message': error_message, 'form': zip(form.fields,form)})
            elif len(e):
                error_message = "Email already used"
                return render(request, 'homepage/register.html',
                              {'error_message': error_message, 'form': zip(form.fields, form)})
            else:
                if (password != password_2):
                    error_message = "Passwords are not the same"
                    return render(request, 'homepage/register.html',
                                  {'error_message': error_message, 'form': zip(form.fields,form)})
                try:
                    validate_password(password)
                except ValidationError as err_msg:
                    error_message = err_msg
                    return render(request, 'homepage/register.html',
                                  {'error_message': error_message, 'form': zip(form.fields, form)})
                else:
                    user = User.objects.create_user(username=username,
                                                    email=email,
                                                    password=password)
                    user.save()
                    error_message = "User Created"
                    return render(request, 'homepage/register.html',
                                  {'error_message': error_message, 'form': zip(form.fields, form)})

        else:
            # Error in putting in field
            error_message = "User was not created, please enter a different email/username"
            return render(request,'homepage/register.html',{'error_message':error_message,
                                                            'form':zip(form.fields,form)})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreateUser()
    return render(request, 'homepage/register.html',
                  {'error_message': "", 'form': zip(form.fields,form)})
