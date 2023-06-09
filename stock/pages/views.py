from django.shortcuts import redirect, render
from .models import Login
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
import requests
import tensorflow as tf
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import seaborn as sns
import joblib
import numpy as np
import matplotlib.pyplot as plt
import plotly.io as pio
import plotly
import time
from django.http import HttpResponse
import base64
import requests
from bs4 import BeautifulSoup
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import matplotlib
import io
import urllib, base64
import streamlit as st
from PIL import Image
import io
import urllib, base64
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.io as pio
from .forms import MyForm
from . import figure, prediction
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login


load_model = tf.keras.models.load_model
yf.pdr_override()

############################################
end = datetime.now()
start = datetime(end.year - 11, end.month, end.day)

start_date = datetime.today()
next_week = []
current_date = datetime.today()

# Calculate the date of yesterday
yesterday = current_date - timedelta(days=1)

# Format the date of yesterday as a string
yesterday_str = yesterday.strftime('%Y-%m-%d')

next_week.append(yesterday.strftime('%A') + " : " + str(yesterday_str))
for day in range(6):
    current_date = start_date + timedelta(days=day)
    next_week.append(str(current_date.strftime('%A')) + " : " + str(current_date.date()))

#############################################################################
apple_df = yf.download("AAPL", start, end)

def get_dollar_data():
    result = requests.get("http://www.floatrates.com/daily/usd.json")
    dic = result.json()
    dic_df = pd.DataFrame(dic)
    dollar_df = dic_df.transpose() 
    return dollar_df

dollar_df = get_dollar_data()

def get_info(df_name):
    df = yf.download(df_name, start, end)
    last_day = df.index[-1] 
    last_value = df["Close"].iloc[-1]
    last_day_name = last_day.day_name()

    text = f"the current value of {last_day_name} : {str(last_day)[:11]} : is {last_value} $"

    return text


def Home(request):
    # This is container to show Dollar inverseRate
    alpha_html = dollar_df.to_html()
    context = {'df_html': alpha_html}
    return render(request, 'pages/Home.html', context)


#####################################company page########################3333

def company(yf_company_name, select):

    df = yf.download(yf_company_name, start, end)
    df_describe = df.describe().to_html()
    df_html = df.to_html()
    pred = prediction.predict(1, select=select)[0]

    context = {'df_html': df_html, "df_describe": df_describe, "predict_of_next_day": pred}

    return context


def Apple (request) :
    return render (request ,"pages/Apple.html", company("AAPL", "apple"))

def Google (request):
    return render (request , "pages/Google.html", company("GOOGL", "google"))

def Microsoft(request):
    return render(request, "pages/Microsoft.html", company("MSFT", "microsoft"))

def Amazon (request):
    return render (request , "pages/Amazon.html",  company("AMZN", "amazon"))

def Meta (request):
    return render (request , "pages/Meta.html", company("meta", "meta"))

def Netflix (request):
    return render (request , "pages/Netflix.html", company("NFLX", "netflix"))

def Tesla (request):
    return render (request , "pages/Tesla.html", company("TSLA", "tesla"))
    
def Intel (request):
    return render (request , "pages/Intel.html", company("INTC", "intel"))


def Nvidia (request):
    return render(request , "pages/Nvidia.html", company("NVDA", "nvidia")) 

def signup (request):

    if request.method =="POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']


        if User.objects.filter(username=username):
            messages.error(request, "username already exist! pllease try some other username")
            return redirect('signup')

        if User.objects.filter(email=email):
            messages.error(request, "email already registered!")
            return redirect('signup')

        if len(username)>15:
            messages.error(request, "username must be under 15 charaters")
            return redirect('signup')

        if pass1 != pass2:
            messages.error(request, "passwords didn't match!")
            return redirect('signup')

        if not username.isalnum():
            messages.error(request,"username must be Alpha-Numeric!")
            return redirect('signup')


        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your Account has been successfully created.")

        return redirect('signin')


    return render(request , "pages/signup.html")


def signin (request):
    if request.method =="POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username = username, password = pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "pages/Home.html", {'fname': fname})
        
        else:
            messages.error(request, "Bad Credentials!")
            return redirect('signin')

    return render(request , "pages/signin.html")


def signout (request):

    return render(request , "pages/signout.html")


def Contact (request):

    return render(request , "pages/Contact.html")

######################################## About company############################

def AboutApple(request):
    plot_model_data = figure.apple_plot_model_data

    plot_data = figure.apple_data_plot

    change_rate = figure.apple_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}
    return render(request, "pages/About_Apple.html", context)



def PredictionApple(request):

    plot_validation = figure.apple_plot_validation
    plot_prediction = figure.apple_prediction_plot

    
    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)

            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="AAPL")}
    return render(request, 'pages/Prediction_Apple.html', context)






def AboutAmazon (request):
    
    plot_model_data = figure.amazon_plot_model_data

    plot_data = figure.amazon_data_plot

    change_rate = figure.amazon_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}
    return render(request, "pages/About_Amazon.html", context)



def PredictionAmazon (request):

    plot_validation = figure.amazon_plot_validation
    plot_prediction = figure.amazon_prediction_plot
    
    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="AMZN")}
    
    
    return render(request, "pages/Prediction_Amazon.html", context)


def AboutIntel (request):
    
    plot_model_data = figure.intel_plot_model_data

    plot_data = figure.intel_data_plot

    change_rate = figure.intel_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}
    
    return render(request, "pages/About_Intel.html", context)



def PredictionIntel (request):

    plot_validation = figure.intel_plot_validation
    plot_prediction = figure.intel_prediction_plot

    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="INTC")}    
    
    return render(request, "pages/Prediction_Intel.html", context)



def AboutGoogle(request):
    plot_model_data = figure.google_plot_model_data

    plot_data = figure.google_data_plot

    change_rate = figure.google_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}

    return render(request, "pages/About_Google.html", context)




def PredictionGoogle(request):

    plot_validation = figure.google_plot_validation
    plot_prediction = figure.google_prediction_plot

    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="GOOGL")}
    return render(request, "pages/Prediction_Google.html", context)




def AboutNvidia (request):
    
    plot_model_data = figure.nvidia_plot_model_data

    plot_data = figure.nvidia_data_plot

    change_rate = figure.nvidia_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}
    
    return render(request, "pages/About_Nvidia.html", context)



def PredictionNvidia (request):

    
    plot_validation = figure.nvidia_plot_validation
    plot_prediction = figure.nvidia_prediction_plot
    
    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="NVDA")}    
    
    
    return render(request, "pages/Prediction_Nvidia.html", context)





def AboutMeta (request):

    plot_model_data = figure.meta_plot_model_data

    plot_data = figure.meta_data_plot

    change_rate = figure.meta_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}
    return render(request, "pages/About_Meta.html", context)



def PredictionMeta (request):

    plot_validation = figure.meta_plot_validation
    plot_prediction = figure.meta_prediction_plot

    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="meta")}
    
    return render(request, "pages/Prediction_Meta.html", context)





def AboutMicrosoft (request):
    plot_model_data = figure.microsoft_plot_model_data

    plot_data = figure.microsoft_data_plot

    change_rate = figure.microsoft_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}

    return render(request, "pages/About_Microsoft.html", context)



def PredictionMicrosoft (request):

    plot_validation = figure.microsoft_plot_validation
    plot_prediction = figure.microsoft_prediction_plot

    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="MSFT")}

    return render(request, "pages/Prediction_Microsoft.html", context)




def AboutNetflix (request):

    plot_model_data = figure.netflix_plot_model_data

    plot_data = figure.netflix_data_plot

    change_rate = figure.netflix_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}
    
    return render(request, "pages/About_Netflix.html", context)



def PredictionNetflix (request):

    plot_validation = figure.netflix_plot_validation
    plot_prediction = figure.netflix_prediction_plot

    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="NFLX")}
    
    
    return render(request, "pages/Prediction_Netflix.html", context)




def AboutTesla (request):
    
    plot_model_data = figure.tesla_plot_model_data

    plot_data = figure.tesla_data_plot

    change_rate = figure.tesla_change_rate
    # Render the template with the image and line chart
    context = {"plot_data": plot_data, "plot_model_data": plot_model_data, "change_rate": change_rate}
    
    return render(request, "pages/About_Tesla.html", context)



def PredictionTesla (request):

    plot_validation = figure.tesla_plot_validation
    plot_prediction = figure.tesla_prediction_plot
    
    messages = []
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            # Get the user's choices
            currency_name = form.cleaned_data['my_list_field']
            num_days = form.cleaned_data['number_field']     

            try:
                for num, i in enumerate(prediction.predict(int(num_days), select="apple"), start=0):
                    if currency_name == "Dollar":
                        message = f"The prediction of day {next_week[num]} is : '{i}' $"
                    else:
                        n = float(dollar_df["rate"][dollar_df["name"] == currency_name])
                        message = f"The prediction of day {next_week[num]} is : '{i*n}' in : {currency_name} "

                    messages.append(message)
            except:    
                message = "Sorry Error in Model procse !"
                messages.append(message)
                print("Sorry Error in Model procse !")
    else:
        form = MyForm()
        
    context = {'form': form, 'messages': messages, "plot_validation": plot_validation, "plot_prediction": plot_prediction, "text": get_info(df_name="TSLA")}    
    
    return render(request, "pages/Prediction_Tesla.html", context)