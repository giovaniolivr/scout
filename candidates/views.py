from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from company.models import Job
from .models import JobApplication


def _require_candidate(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    return None


@login_required
def home_candidate(request):
    redir = _require_candidate(request)
    if redir:
        return redir

    profile = request.user.candidate_profile

    applied_job_ids = set(
        JobApplication.objects.filter(candidate=profile).values_list('job_id', flat=True)
    )

    # ----------------------------------------------------------------
    # ALGORITHM HOOK — replace this queryset with the ranking algorithm
    # when it's ready. The home page always renders the first 3 results.
    # ----------------------------------------------------------------
    recent_applications = (
        JobApplication.objects
        .filter(candidate=profile)
        .select_related('job', 'job__company')
        .order_by('-applied_at')[:3]
    )
    total_applications = JobApplication.objects.filter(candidate=profile).count()

    # ----------------------------------------------------------------
    # RECOMMENDATION HOOK — replace with soft-skill / preference
    # matching algorithm when profile data is available.
    # ----------------------------------------------------------------
    recommended_jobs = (
        Job.objects
        .filter(status=Job.STATUS_OPEN)
        .exclude(id__in=applied_job_ids)
        .select_related('company')
        .order_by('-created_at')[:3]
    )

    return render(request, 'home_candidate.html', {
        'recent_applications': recent_applications,
        'total_applications': total_applications,
        'recommended_jobs': recommended_jobs,
    })


@login_required
def all_applications(request):
    redir = _require_candidate(request)
    if redir:
        return redir

    profile = request.user.candidate_profile
    applications = (
        JobApplication.objects
        .filter(candidate=profile)
        .select_related('job', 'job__company')
        .order_by('-applied_at')
    )

    return render(request, 'all_applications.html', {'applications': applications})


@login_required
def search_jobs(request):
    redir = _require_candidate(request)
    if redir:
        return redir

    query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    job_type = request.GET.get('type', '').strip()

    jobs = Job.objects.filter(status=Job.STATUS_OPEN).select_related('company').order_by('-created_at')

    if query:
        jobs = jobs.filter(title__icontains=query)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    profile = request.user.candidate_profile
    applied_ids = set(
        JobApplication.objects.filter(candidate=profile).values_list('job_id', flat=True)
    )

    # Exclude already-applied jobs from results
    jobs = jobs.exclude(id__in=applied_ids)

    return render(request, 'search_jobs.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'job_type': job_type,
        'type_choices': Job.TYPE_CHOICES,
    })


@login_required
def job_detail(request, job_id):
    redir = _require_candidate(request)
    if redir:
        return redir

    job = get_object_or_404(Job, pk=job_id)
    profile = request.user.candidate_profile
    application = JobApplication.objects.filter(candidate=profile, job=job).first()

    return render(request, 'job_detail.html', {
        'job': job,
        'application': application,
    })


@login_required
def apply_job(request, job_id):
    redir = _require_candidate(request)
    if redir:
        return redir

    job = get_object_or_404(Job, pk=job_id, status=Job.STATUS_OPEN)
    profile = request.user.candidate_profile

    if JobApplication.objects.filter(candidate=profile, job=job).exists():
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()

        JobApplication.objects.create(
            candidate=profile,
            job=job,
            message=message_text,
        )

        messages.success(request, f'Candidatura enviada para "{job.title}"!')
        return redirect('search_jobs')

    return render(request, 'apply_job.html', {'job': job})


@login_required
@require_POST
def apply_external(request, job_id):
    """One-click apply for external jobs. No form needed."""
    redir = _require_candidate(request)
    if redir:
        return redir

    job = get_object_or_404(Job, pk=job_id, status=Job.STATUS_OPEN)
    profile = request.user.candidate_profile

    JobApplication.objects.get_or_create(candidate=profile, job=job)

    messages.success(request, f'Candidatura enviada para "{job.title}"!')
    return redirect('search_jobs')


@login_required
def application_detail(request, application_id):
    redir = _require_candidate(request)
    if redir:
        return redir

    profile = request.user.candidate_profile
    application = get_object_or_404(JobApplication, pk=application_id, candidate=profile)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'hide':
            application.delete()
            return redirect('home_candidate')

        if action == 'rate' and application.job.status != Job.STATUS_OPEN and application.experience_rating is None:
            rating = request.POST.get('rating', '')
            comment = request.POST.get('comment', '').strip()

            if not rating.isdigit() or not (1 <= int(rating) <= 5):
                return render(request, 'application_detail.html', {
                    'application': application,
                    'rating_error': 'Selecione uma avaliação de 1 a 5.',
                })

            application.experience_rating = int(rating)
            application.experience_comment = comment
            application.save()

            # Cycle complete — remove from home
            application.delete()
            messages.success(request, 'Avaliação enviada. Obrigado pelo feedback!')
            return redirect('home_candidate')

    return render(request, 'application_detail.html', {
        'application': application,
        'rating_error': '',
    })
