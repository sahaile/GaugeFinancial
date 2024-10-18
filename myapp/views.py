import os
import pandas as pd

import logging
logger = logging.getLogger(__name__)

from openai import OpenAI
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse


from .forms import SignupForm, LoginForm, UploadFileForm, EditProfileForm


from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from datetime import datetime
from django.utils import timezone

from .models import Transactions, Bankstatements, User, Chat
from django.db.models import Q, Sum, Count
from django.db.models.functions import ExtractMonth, ExtractYear

def homepage(request):
    return render(request,'myapp/index.html')
    
def register(request):
    form = SignupForm()
    if request.method == "POST":
        form=SignupForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            # Check if username is already taken
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken. Please choose a different username.')
            else:
                form.save()
                messages.success(request, 'Registration successful. You can now login.')
                return redirect("my-login")

    context = {'registerform':form}

    return render(request,'myapp/register.html',context=context)

def my_login(request):
    form = LoginForm()

    if request.method =='POST':
        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            print(5)
            if user is not None:
                login(request, user)
                return redirect("dashboard")
    
    context = {'loginform':form}
    return render(request,'myapp/my-login.html', context=context)

def user_logout(request):
    logout(request)
    return redirect('')

@login_required(login_url='my-login')
def dashboard(request):
    user = request.user
    statements = Bankstatements.objects.filter(created_by=request.user).order_by('-upload_date')[:6]
    context = {'user':user, 'statements':statements}
    return render(request, 'myapp/dashboard.html', context=context)



@login_required(login_url='my-login')
def new_bankstatement(request):
    form = UploadFileForm(initial={'user': request.user})

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES, initial={'user': request.user})
        
        if form.is_valid():
            excel_file = request.FILES["file"]
            file_extension = os.path.splitext(excel_file.name)[1].lower()

            if file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(excel_file)
            elif file_extension == '.csv':
                df = pd.read_csv(excel_file)
            else:
                # Handle unsupported file types or errors
                return render(request, "myapp/newbankstatement.html", {'uploadfileform': form})

            expected_titles = ['TransactionID', 'Date', 'Description', 'Expenses', 'Revenue']

            # Check if all expected columns are present
            if not set(expected_titles).issubset(df.columns):
                # If any expected column is missing, handle the error
                context = {'uploadfileform': form, 'error_message': 'Excel file is missing required columns.'}
                return render(request, "myapp/newbankstatement.html", context=context)
            
            if not df.empty:
                # Calculate bankstatementID
                user_bankstatement_count = Bankstatements.objects.all().count() + 1

                # Create Bankstatement object
                bankstatement = Bankstatements(
                    bankstatementID=user_bankstatement_count,
                    account=form.cleaned_data['account'],
                    start_period=pd.to_datetime(df['Date']).min().date(),
                    end_period=pd.to_datetime(df['Date']).max().date(),
                    file=excel_file,  # Store the file itself if needed
                    upload_date=timezone.now(),
                    created_by=request.user,
                    name=form.cleaned_data['title']
                )
                bankstatement.save()

                # Create Transactions from DataFrame
                for index, row in df.iterrows():
                    expenses = float(row['Expenses']) if pd.notnull(row['Expenses']) else 0.0
                    revenue = float(row['Revenue']) if pd.notnull(row['Revenue']) else 0.0
                    category="uncategorized"

                    if expenses != 0.0:
                        response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages = [
                            {"role": "system", "content": "i want you to categorize this tranasaction as Utilties, Insurance, Retail, Groceries, Investing, Entertainment, Food, Housing/Rent, or Transportation. If unsure abour the transactions category make your own or use Other. \
                            I want you only to return the category and nothing else. Anything that resemmbles a banking transfer such as 'SSV TO: 83126684982' or ends in a large number resembling a bank account number should be categorized as 'uncategorized'"},
                            {"role": "user", "content": f"Here is a list of transactions. Provide a summary or categorize them:\n\n{row['Description']}"}
                        ]
                        )
                        category=response.choices[0].message.content

                    
                    
                    transaction = Transactions(
                        transactionID=row['TransactionID'],
                        bankstatementID=bankstatement,
                        date=pd.to_datetime(row['Date']).date(),
                        description=row['Description'],
                        expenses=expenses,
                        revenue=revenue,
                        category=category.title()
                    )
                    transaction.save()

                return redirect("dashboard")

    context = {'uploadfileform': form}
    return render(request, "myapp/newbankstatement.html", context=context)



@login_required(login_url='my-login')
def bankstatements(request):
    search_query = request.GET.get('search', '')
    
    statements = Bankstatements.objects.filter(created_by=request.user)
    
    if search_query:
        statements = statements.filter( 
            Q(name__icontains=search_query) | Q(account__icontains=search_query)
        )
    
    return render(request, 'myapp/bankstatements.html', {'statements': statements})

@login_required(login_url='my-login')
def view_bankstatement(request, pk):
    bankstatement = get_object_or_404(Bankstatements, pk=pk)
    transactions = Transactions.objects.filter(bankstatementID=bankstatement.bankstatementID)

    context = {
        'bankstatement': bankstatement,  
        'transactions': transactions  
    }
    return render(request, 'myapp/viewbankstatement.html', context)



@login_required(login_url='my-login')
def delete_bankstatement(request,pk):
    bankstatement = get_object_or_404(Bankstatements, pk=pk)
    if request.method == 'POST':
        # If the user confirms deletion (after showing the confirmation page)
        bankstatement.delete()
        return redirect('dashboard')  # Redirect to dashboard or any other page after deletion
    
    # Render a confirmation page with the option to confirm or cancel deletion
    return render(request, 'myapp/delete-bankstatement.html', {'bankstatement': bankstatement})

@login_required(login_url='my-login')
def analyze_bankstatement(request, pk):
    statement = get_object_or_404(Bankstatements, pk=pk)
    all_transactions = Transactions.objects.filter(bankstatementID=statement.bankstatementID)
    all_transactions = all_transactions.order_by('bankstatementID')

    monthly_data = all_transactions.annotate(
        month=ExtractMonth('date'),
        year=ExtractYear('date')
    ).values('month', 'year').annotate(
        total_revenue=Sum('revenue'),
        total_expenses=Sum('expenses')
    ).order_by('year', 'month')

    monthly_summary_revenue = [
        {'x': str(data['month']) + '-' + str(data['year']), 'y': float(data['total_revenue'])}
        for data in monthly_data
    ]

    monthly_summary_expenses = [
        {'x': str(data['month']) + '-' + str(data['year']), 'y': float(data['total_expenses'])}
        for data in monthly_data
    ]

    yearly_data = all_transactions.annotate(
        year=ExtractYear('date')
    ).values('year').annotate(
        total_revenue=Sum('revenue'),
        total_expenses=Sum('expenses')
    ).order_by('year')

    yearly_summary_revenue = [
        {'x': data['year'], 'y': float(data['total_revenue'])}
        for data in yearly_data
    ]
    yearly_summary_expenses = [
        {'x': data['year'], 'y': float(data['total_expenses'])}
        for data in yearly_data
    ]

    categorical_data = all_transactions.values('category'
    ).annotate(
        total_expenses=Sum('expenses'),
        total_transactions = Count('bankstatementID_id')
    ).order_by('category')

    categorical_summary=[
        {
            'category': data['category'],
            'total_expenses' : float(data['total_expenses']),
            'total_transactions' : data['total_transactions']
        }
            for data in categorical_data
            if data['category'].lower() != 'uncategorized'
        ]
    
    transaction_details = all_transactions.values('category', 'expenses', 'revenue', 'description').order_by('category')

    # Include all transaction details and summaries in the context
    data = {
        'all_transactions': transaction_details,
        'monthly_summary_revenue': monthly_summary_revenue,
        'yearly_summary_revenue': yearly_summary_revenue,
        'monthly_summary_expenses': monthly_summary_expenses,
        'yearly_summary_expenses': yearly_summary_expenses,
        'categorical_summary': categorical_summary
    }    
    chats = Chat.objects.filter(user=request.user).order_by('created_at')
    chat_history = [{'role': 'user', 'content': chat.message} for chat in chats] + [{'role': 'assistant', 'content': chat.response} for chat in chats]

    if request.method == 'POST':
        message = request.POST.get('message')
        
        # Append the latest user message to chat history
        chat_history.append({'role': 'user', 'content': message})

        # Get the response from the AI model with chat history context
        response = ask_openai(message, chat_history, data)
        
        # Save the new chat
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()

        # Append the assistant's response to chat history
        chat_history.append({'role': 'assistant', 'content': response})
        
        return JsonResponse({'message': message, 'response': response})

    return render(request, 'myapp/analyze-bankstatement.html', {
        'statement': statement,
        'monthly_summary_revenue': monthly_summary_revenue,
        'yearly_summary_revenue': yearly_summary_revenue,
        'monthly_summary_expenses': monthly_summary_expenses,
        'yearly_summary_expenses': yearly_summary_expenses,
        'categorical_summary':categorical_summary,
        'chats': chats,
    })

def truncate_chat_history(chat_history, max_tokens=3000):
    """
    Truncate the chat history to ensure it stays within a token limit.
    """
    current_tokens = sum(len(msg['content'].split()) for msg in chat_history)
    
    while current_tokens > max_tokens and chat_history:
        chat_history.pop(0)  # Remove oldest message
        current_tokens = sum(len(msg['content'].split()) for msg in chat_history)
    
    return chat_history

def ask_openai(message, chat_history, data):
    chat_history = truncate_chat_history(chat_history, max_tokens=3000)
    
    messages = [
        {"role": "system", "content": f"You are a financial assistant that uses bank statement information to aid the user's question. Here is the data: {data}"},
    ] + chat_history + [{"role": "user", "content": message}]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    
    answer = response.choices[0].message.content
    return answer

@login_required(login_url='my-login')
def profile(request):
    user = request.user
    return render(request, 'myapp/profile.html', {'user':user} )

@login_required(login_url='my-login')
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = EditProfileForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'myapp/edit-profile.html', context)

@login_required(login_url='my-login')
def edit_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        return redirect('/')
    context = {'editform': form}
    return render(request, 'myapp/edit-password.html', context=context)


@login_required(login_url='my-login')
def delete_profile(request):
    user = request.user
    if request.method == "POST":
        user.delete()
        return render(request,'myapp/index.html')
    return render(request, 'myapp/delete-profile.html', {'user':user} )

