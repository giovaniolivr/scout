from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def home_candidate(request):
    if not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    return render(request, 'home_candidate.html')
