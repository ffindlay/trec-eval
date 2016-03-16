from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import HttpResponse

from trec.forms import *
from trec.models import Researcher, Task, Track
from trec.utils import run_trec_eval

def index(request):
    return render(request, 'trec/index.html')

def about(request):
    return render(request, 'trec/about.html')

def register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        researcher_form = ResearcherForm(request.POST)
        if user_form.is_valid() and researcher_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            researcher = researcher_form.save(commit=False)
            researcher.user = user
            if 'profile_pic' in request.FILES:
                researcher.profile_pic = request.FILES['profile_pic']
            researcher.save()

            user = authenticate(username=user.username,
                                password=user_form.cleaned_data['password'])
            login(request, user)
            return redirect(index)
    else:
        user_form = UserForm()
        researcher_form = ResearcherForm()
    return render(request, 'trec/register.html',
                  {'user_form': user_form, 'researcher_form': researcher_form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(index)
            else:
                return HttpResponse("Your TREC Evaluator account is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'trec/login.html', {})

def user_logout(request):
    logout(request)
    return redirect(index)

def tracks(request):
    tracks = Track.objects.all()

    for track in tracks:
        track.tasks = Task.objects.filter(track=track)

    return render(request, 'trec/tracks.html', {'tracks': tracks})

def task_results(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return redirect(index)

    runs = Run.objects.filter(task=task)

    return render(request, 'trec/view_task_runs.html',
                  {'runs': runs, 'task': task})

@login_required
def add_track(request):
    user = request.user

    if not user.is_superuser:
        return render(request, 'trec/add_track.html', {})
    else:
        if request.method == 'POST':
            track_form = TrackForm(request.POST)
            if track_form.is_valid():
                track_form.save(commit=True)
                return redirect(index)
        else:
            track_form = TrackForm(instance=user)
        return render(request, 'trec/add_track.html',
                      {'track_form': track_form})

@login_required
def profile(request):
    user = request.user
    researcher = Researcher.objects.get(user=user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        researcher_form = ResearcherForm(request.POST, instance=researcher)
        if user_form.is_valid() and researcher_form.is_valid():
            user.save()
            if 'profile_pic' in request.FILES:
                researcher.profile_pic = request.FILES['profile_pic']
            researcher.save()
            return redirect('/')
    else:
        user_form = UserUpdateForm(instance=user)
        researcher_form = ResearcherForm(instance=researcher)
    return render(request, 'trec/profile.html',
                  {'user_form': user_form, 'researcher_form': researcher_form})

@login_required
def submit_run(request, task_id):
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        return redirect(index)
    if request.method == 'POST':
        form = RunForm(request.POST, request.FILES)
        if form.is_valid():
            run = form.save(commit=False)
            run.researcher = Researcher.objects.get(user=request.user)
            run.task = task
            run.save() # needed to upload the file to its place
            run.map, run.p10, run.p20 = run_trec_eval(task.judgement_file.path,
                                                      run.results_file.path)
            if run.map is not None:
                run.save()
                return render(request, 'trec/run.html', {'run': run})
            form._errors['results_file'] = form.error_class(
                ['There was a problem evaluating your results file'])
            run.delete()
    else:
        form = RunForm()
    return render(request, 'trec/submit_run.html', {'form': form, 'task': task})
