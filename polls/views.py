from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import RegisterUserForm

from .models import Choice, Question, Member, MemberVote

@login_required
def home(request):
	return render(request, 
		'index.html', {
		})


def login_user(request):
    if request.method == "POST":
        lower_username = request.POST['username'].lower()
        password = request.POST['password']
        user = authenticate(request, username=lower_username, password=password)
        if user is not None:
            login(request, user)
            return redirect('polls:index')
        else:
            messages.error(request, "There was an error logging in. Please try again.")
            return redirect('polls:login_user')  # Update this line
    else:
        return render(request, 'polls/login.html', {})

def logout_user(request):
	logout(request)
	messages.success(request, ("You Were Logged Out!"))
	return redirect('polls:index')

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            new_username = form.cleaned_data['username'].lower()  # Convert to lowercase
            password = form.cleaned_data['password1']

            User = get_user_model()  # Get the custom user model
            
            # Create a new user instance and set is_active to False
            User.objects.create_user(username=new_username, password=password)

            messages.success(request, "Registration Successful!")
            return redirect('polls:index')
    else:
        form = RegisterUserForm()

    return render(request, 'polls/register_user.html', {
        'form': form,
    })


def member_vote_detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    member = request.user

    # Retrieve the MemberVote for the member and the question
    try:
        member_vote = MemberVote.objects.get(member=member, question=question)
    except MemberVote.DoesNotExist:
        # Handle the case where the member hasn't voted for this question
        messages.error(request, "You haven't voted for this question.")
        return redirect('polls:index')

    return render(request, 'polls/member_vote_detail.html', {
        'question': question,
        'member_vote': member_vote,
    })


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'question_lists'
    
    
    def get_queryset(self):
        now = timezone.now()
        user = self.request.user

        # Get the member if the user is authenticated, or None if not
        member = None
        if user.is_authenticated:
            try:
                member = get_user_model().objects.get(username=user)
            except get_user_model().DoesNotExist:
                # Handle the case where the member does not exist
                member = None

        open_questions = Question.objects.filter(
            is_published=True,
            closing_date_time__gt=now,
            pub_date__lt=now
        ).order_by('-pub_date')  # Currently open and published questions

        upcoming_questions = Question.objects.filter(
            is_published=True,
            pub_date__gt=now
        ).order_by('pub_date')  # Questions that will open soon

        closed_questions = Question.objects.filter(
            is_published=True,
            closing_date_time__lt=now
        ).order_by('-pub_date')  # Questions that have been published but are closed

        # Questions where the member has already voted but the poll is still open
        voted_questions = Question.objects.filter(
            is_published=True,
            pub_date__lt=now,
            membervote__member=member
        ).exclude(pub_date__gt=now)


        return {
            'open_questions': open_questions,
            'upcoming_questions': upcoming_questions,
            'closed_questions': closed_questions,
            'voted_questions': voted_questions,
        }

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'polls/password_reset.html'
    email_template_name = 'polls/password_reset_email.html'
    subject_template_name = 'polls/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('polls:index')



class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    member = request.user  # Assuming you're using authentication

     # Check if the question is published
    if not question.is_published:
        messages.error(request, "This question is not currently published.")
        return redirect('polls:index')

    # Check if the voting period for the question is still open
    if not question.is_open():
        messages.error(request, "Voting for this question is closed.")
        return redirect('polls:index')

    # Check if the member has already voted for this question
    if MemberVote.objects.filter(member=member, question=question).exists():
        messages.error(request, "You have already voted for this question.")
        return redirect('polls:index')

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()

        # Create a MemberVote record to track the member's vote
        MemberVote.objects.create(member=member, question=question, choice=selected_choice)

        return redirect('polls:results', pk=question.id)
    


