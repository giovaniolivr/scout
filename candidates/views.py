from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings

from company.models import Job, CompanyFollow, CompanyQualityEndorsement
from core.skills import filter_hard_skills, filter_soft_skills, SOFT_SKILL_CATEGORIES
from core.roles import JOB_AREAS, SENIORITY_LEVELS, VALID_JOB_AREAS, VALID_SENIORITIES, LANGUAGES, COMPANY_QUALITIES
from .models import CandidateProfile, JobApplication
from .insights import compute_candidate_insights


def _require_candidate(request):
    """
    Returns a redirect if the user is not a candidate or has not completed onboarding.
    Returns None when the request is allowed to proceed.
    """
    if not request.user.is_authenticated or not hasattr(request.user, 'candidate_profile'):
        return redirect('home')
    if not request.user.candidate_profile.is_onboarded:
        return redirect('onboarding_candidate')
    return None


def _rank_jobs_for_candidate(jobs_qs, candidate_profile):
    """
    Evaluates the queryset and attaches a `match_score` attribute to each job.
    When the candidate has skills, results are sorted by match descending.
    When no skills are set, the original ordering is preserved and match_score
    is set to None on all jobs (template handles the display).
    """
    jobs = list(jobs_qs)
    for job in jobs:
        job.match_score = job.match_score(candidate_profile)

    if candidate_profile.has_skills():
        # Jobs with no requirements (score=None) are treated as a neutral 100%
        # so they stay visible alongside strong matches.
        jobs.sort(key=lambda j: j.match_score if j.match_score is not None else 100, reverse=True)

    return jobs


# ---------------------------------------------------------------------------
# ONBOARDING — mandatory first-time profile setup after registration
# ---------------------------------------------------------------------------

EDUCATION_CHOICES = CandidateProfile.EDUCATION_CHOICES
VALID_EDUCATION_VALUES = {v for v, _ in EDUCATION_CHOICES}

_ONBOARDING_CTX = {
    'education_choices': EDUCATION_CHOICES,
    'job_areas': JOB_AREAS,
    'seniority_levels': SENIORITY_LEVELS,
    'onboarding_mode': True,
}

CV_ALLOWED_EXTENSIONS = ('.pdf', '.doc', '.docx')
CV_MAX_SIZE = 5 * 1024 * 1024  # 5 MB


def onboarding_candidate(request):
    """
    The mandatory first-time profile setup screen.
    Shown after registration, before the candidate can access any other page.
    """
    if not request.user.is_authenticated or not hasattr(request.user, 'candidate_profile'):
        return redirect('home')

    profile = request.user.candidate_profile

    if profile.is_onboarded:
        return redirect('home_candidate')

    if request.method == 'POST':
        bio = request.POST.get('bio', '').strip()
        desired_area = request.POST.get('desired_area', '').strip()
        desired_seniority = request.POST.get('desired_seniority', '').strip()
        education_level = request.POST.get('education_level', '').strip()
        soft_skills = filter_soft_skills(request.POST.get('soft_skills', ''))
        hard_skills = filter_hard_skills(request.POST.get('hard_skills', ''))
        linkedin_url = request.POST.get('linkedin_url', '').strip()
        # MOCK: CV is optional during onboarding — saved if provided, skipped if not.
        # To enforce for production: add a required check here and remove this comment.
        cv_file = request.FILES.get('profile_cv')

        errors = {}

        if not bio or len(bio) < 20:
            errors['bio'] = 'Escreva ao menos 20 caracteres sobre você.'
        if desired_area not in VALID_JOB_AREAS:
            errors['desired_area'] = 'Selecione uma área de atuação.'
        if desired_seniority not in VALID_SENIORITIES:
            errors['desired_seniority'] = 'Selecione um nível de senioridade.'
        if education_level not in VALID_EDUCATION_VALUES:
            errors['education_level'] = 'Selecione seu nível de escolaridade.'
        if not soft_skills:
            errors['soft_skills'] = 'Adicione ao menos uma habilidade comportamental.'

        if linkedin_url and not linkedin_url.startswith(('http://', 'https://')):
            linkedin_url = 'https://' + linkedin_url

        if cv_file:
            ext = f".{cv_file.name.rsplit('.', 1)[-1].lower()}"
            if ext not in CV_ALLOWED_EXTENSIONS:
                errors['profile_cv'] = 'Formato inválido. Envie um arquivo PDF, DOC ou DOCX.'
            elif cv_file.size > CV_MAX_SIZE:
                errors['profile_cv'] = 'Arquivo muito grande. O tamanho máximo é 5 MB.'

        if errors:
            return render(request, 'onboarding_candidate.html', {
                'errors': errors,
                'form_data': request.POST,
                'education_choices': EDUCATION_CHOICES,
                'job_areas': JOB_AREAS,
                'seniority_levels': SENIORITY_LEVELS,
                'onboarding_mode': True,
            })

        profile.bio = bio
        profile.desired_area = desired_area
        profile.desired_seniority = desired_seniority
        profile.education_level = education_level
        profile.soft_skills = soft_skills
        profile.hard_skills = hard_skills
        profile.linkedin_url = linkedin_url
        if cv_file:
            profile.profile_cv = cv_file
        profile.is_onboarded = True
        profile.save()

        messages.success(request, 'Perfil configurado! Bem-vindo ao Scout.')
        return redirect('home_candidate')

    return render(request, 'onboarding_candidate.html', {
        'education_choices': EDUCATION_CHOICES,
        'job_areas': JOB_AREAS,
        'seniority_levels': SENIORITY_LEVELS,
        'onboarding_mode': True,
    })


# ---------------------------------------------------------------------------
# PROFILE — view and edit
# ---------------------------------------------------------------------------

@login_required
def profile_candidate(request):
    redir = _require_candidate(request)
    if redir:
        return redir
    profile = request.user.candidate_profile
    return render(request, 'profile_candidate.html', {'profile': profile})


@login_required
def edit_profile_candidate(request):
    redir = _require_candidate(request)
    if redir:
        return redir

    profile = request.user.candidate_profile

    if request.method == 'POST':
        bio = request.POST.get('bio', '').strip()
        desired_area = request.POST.get('desired_area', '').strip()
        desired_seniority = request.POST.get('desired_seniority', '').strip()
        education_level = request.POST.get('education_level', '').strip()
        soft_skills = filter_soft_skills(request.POST.get('soft_skills', ''))
        hard_skills = filter_hard_skills(request.POST.get('hard_skills', ''))
        linkedin_url = request.POST.get('linkedin_url', '').strip()
        github_url = request.POST.get('github_url', '').strip()
        portfolio_url = request.POST.get('portfolio_url', '').strip()
        selected_languages = request.POST.getlist('languages')
        cv_file = request.FILES.get('profile_cv')

        # Visibility — ensure hidden is a strict subset of the selected skills
        hidden_soft_raw = filter_soft_skills(request.POST.get('hidden_soft_skills', ''))
        hidden_hard_raw = filter_hard_skills(request.POST.get('hidden_hard_skills', ''))
        soft_set = {s.strip() for s in soft_skills.split(',') if s.strip()}
        hard_set = {s.strip() for s in hard_skills.split(',') if s.strip()}
        hidden_soft_set = {s.strip() for s in hidden_soft_raw.split(',') if s.strip()}
        hidden_hard_set = {s.strip() for s in hidden_hard_raw.split(',') if s.strip()}
        final_hidden_soft = ', '.join(sorted(hidden_soft_set & soft_set))
        final_hidden_hard = ', '.join(sorted(hidden_hard_set & hard_set))

        errors = {}

        if not bio or len(bio) < 20:
            errors['bio'] = 'Escreva ao menos 20 caracteres sobre você.'
        if desired_area not in VALID_JOB_AREAS:
            errors['desired_area'] = 'Selecione uma área de atuação.'
        if desired_seniority not in VALID_SENIORITIES:
            errors['desired_seniority'] = 'Selecione um nível de senioridade.'
        if education_level not in VALID_EDUCATION_VALUES:
            errors['education_level'] = 'Selecione seu nível de escolaridade.'
        if not soft_skills:
            errors['soft_skills'] = 'Adicione ao menos uma habilidade comportamental.'

        if linkedin_url and not linkedin_url.startswith(('http://', 'https://')):
            linkedin_url = 'https://' + linkedin_url
        if github_url and not github_url.startswith(('http://', 'https://')):
            github_url = 'https://' + github_url
        if portfolio_url and not portfolio_url.startswith(('http://', 'https://')):
            portfolio_url = 'https://' + portfolio_url

        # Only accept languages from the predefined list
        valid_language_set = set(LANGUAGES)
        languages = ', '.join(l for l in selected_languages if l in valid_language_set)

        if cv_file:
            ext = f".{cv_file.name.rsplit('.', 1)[-1].lower()}"
            if ext not in CV_ALLOWED_EXTENSIONS:
                errors['profile_cv'] = 'Formato inválido. Envie um arquivo PDF, DOC ou DOCX.'
            elif cv_file.size > CV_MAX_SIZE:
                errors['profile_cv'] = 'Arquivo muito grande. O tamanho máximo é 5 MB.'

        if errors:
            return render(request, 'edit_profile_candidate.html', {
                'profile': profile,
                'errors': errors,
                'form_data': request.POST,
                'education_choices': EDUCATION_CHOICES,
                'job_areas': JOB_AREAS,
                'seniority_levels': SENIORITY_LEVELS,
                'languages': LANGUAGES,
                'selected_languages': selected_languages,
            })

        profile.bio = bio
        profile.desired_area = desired_area
        profile.desired_seniority = desired_seniority
        profile.education_level = education_level
        profile.soft_skills = soft_skills
        profile.hard_skills = hard_skills
        profile.hidden_soft_skills = final_hidden_soft
        profile.hidden_hard_skills = final_hidden_hard
        profile.linkedin_url = linkedin_url
        profile.github_url = github_url
        profile.portfolio_url = portfolio_url
        profile.languages = languages
        if cv_file:
            profile.profile_cv = cv_file
        profile.save()

        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('profile_candidate')

    return render(request, 'edit_profile_candidate.html', {
        'profile': profile,
        'education_choices': EDUCATION_CHOICES,
        'job_areas': JOB_AREAS,
        'seniority_levels': SENIORITY_LEVELS,
        'languages': LANGUAGES,
        'selected_languages': profile.get_languages_list(),
    })


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------

@login_required
def home_candidate(request):
    redir = _require_candidate(request)
    if redir:
        return redir

    profile = request.user.candidate_profile

    applied_job_ids = set(
        JobApplication.objects.filter(candidate=profile).values_list('job_id', flat=True)
    )

    recent_applications = (
        JobApplication.objects
        .filter(candidate=profile, is_archived=False)
        .select_related('job', 'job__company')
        .order_by('-applied_at')[:3]
    )
    total_applications = JobApplication.objects.filter(candidate=profile, is_archived=False).count()

    open_jobs = (
        Job.objects
        .filter(status=Job.STATUS_OPEN)
        .exclude(id__in=applied_job_ids)
        .select_related('company')
        .order_by('-created_at')
    )

    recommended_jobs = _rank_jobs_for_candidate(open_jobs, profile)[:3]

    strengths, opportunities = compute_candidate_insights(profile)

    return render(request, 'home_candidate.html', {
        'profile': profile,
        'recent_applications': recent_applications,
        'total_applications': total_applications,
        'recommended_jobs': recommended_jobs,
        'insight_strengths': strengths,
        'insight_opportunities': opportunities,
    })


@login_required
def all_applications(request):
    redir = _require_candidate(request)
    if redir:
        return redir

    profile = request.user.candidate_profile
    applications = (
        JobApplication.objects
        .filter(candidate=profile, is_archived=False)
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
    area = request.GET.get('area', '').strip()

    jobs = Job.objects.filter(status=Job.STATUS_OPEN).select_related('company').order_by('-created_at')

    if query:
        jobs = jobs.filter(title__icontains=query)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if area and area in VALID_JOB_AREAS:
        jobs = jobs.filter(job_area=area)

    profile = request.user.candidate_profile
    applied_ids = set(
        JobApplication.objects.filter(candidate=profile).values_list('job_id', flat=True)
    )
    jobs = jobs.exclude(id__in=applied_ids)

    jobs = _rank_jobs_for_candidate(jobs, profile)

    return render(request, 'search_jobs.html', {
        'jobs': jobs,
        'query': query,
        'location': location,
        'job_type': job_type,
        'area': area,
        'type_choices': Job.TYPE_CHOICES,
        'job_areas': JOB_AREAS,
        'candidate_has_skills': profile.has_skills(),
    })


@login_required
def job_detail(request, job_id):
    redir = _require_candidate(request)
    if redir:
        return redir

    job = get_object_or_404(Job, pk=job_id)
    profile = request.user.candidate_profile
    application = JobApplication.objects.filter(candidate=profile, job=job).first()
    match = job.match_score(profile)

    return render(request, 'job_detail.html', {
        'job': job,
        'application': application,
        'match_score': match,
        'candidate_has_skills': profile.has_skills(),
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
        cv_file = request.FILES.get('cv')

        cv_error = None
        if not cv_file:
            cv_error = 'O envio do currículo é obrigatório.'
        else:
            allowed_extensions = ('.pdf', '.doc', '.docx')
            ext = cv_file.name.rsplit('.', 1)[-1].lower()
            if f'.{ext}' not in allowed_extensions:
                cv_error = 'Formato inválido. Envie um arquivo PDF, DOC ou DOCX.'
            elif cv_file.size > 5 * 1024 * 1024:
                cv_error = 'O arquivo é muito grande. O tamanho máximo é 5 MB.'

        if cv_error:
            return render(request, 'apply_job.html', {'job': job, 'cv_error': cv_error, 'message': message_text})

        JobApplication.objects.create(
            candidate=profile,
            job=job,
            message=message_text,
            cv=cv_file,
        )

        profile.recalculate_internal_score()
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
    application = get_object_or_404(JobApplication, pk=application_id, candidate=profile, is_archived=False)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'hide':
            application.is_archived = True
            application.save()
            return redirect('home_candidate')

        final_statuses = [JobApplication.STATUS_ACCEPTED, JobApplication.STATUS_REJECTED]
        if action == 'rate' and application.status in final_statuses and application.experience_rating is None:
            rating = request.POST.get('rating', '')
            comment = request.POST.get('comment', '').strip()
            endorsed_qualities = request.POST.getlist('endorsed_qualities')

            if rating and (not rating.isdigit() or not (1 <= int(rating) <= 5)):
                return render(request, 'application_detail.html', {
                    'application': application,
                    'rating_error': 'Selecione uma avaliação de 1 a 5.',
                    'can_rate': True,
                    'show_dev_tools': settings.DEBUG,
                    'company_qualities': COMPANY_QUALITIES,
                })

            application.experience_rating = int(rating) if rating else None
            application.experience_comment = comment
            application.is_archived = True
            application.save()

            # Record company quality endorsements
            valid_qualities = set(COMPANY_QUALITIES)
            company = application.job.company
            for quality in endorsed_qualities:
                if quality in valid_qualities:
                    CompanyQualityEndorsement.objects.get_or_create(
                        candidate=profile,
                        company=company,
                        job_application=application,
                        quality_name=quality,
                    )

            messages.success(request, 'Avaliação enviada. Obrigado pelo feedback!')
            return redirect('home_candidate')

    final_statuses = [JobApplication.STATUS_ACCEPTED, JobApplication.STATUS_REJECTED]

    # Qualities already endorsed (if candidate already rated — shouldn't normally reach here)
    existing_quality_endorsements = set(
        application.company_quality_endorsements.values_list('quality_name', flat=True)
    )

    return render(request, 'application_detail.html', {
        'application': application,
        'rating_error': '',
        'can_rate': application.status in final_statuses and application.experience_rating is None,
        'show_dev_tools': settings.DEBUG,
        'company_qualities': COMPANY_QUALITIES,
        'existing_quality_endorsements': existing_quality_endorsements,
    })

# ---------------------------------------------------------------------------
# PUBLIC CANDIDATE PROFILE (visible to companies and other logged-in users)
# ---------------------------------------------------------------------------

@login_required
def candidate_public_profile(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id, is_onboarded=True)
    return render(request, 'candidate_public_profile.html', {'candidate': candidate})


# ---------------------------------------------------------------------------
# DEV ONLY — simulate company response on a candidate's application
# Remove this view and its URL before production deployment.
# ---------------------------------------------------------------------------

@login_required
@require_POST
def dev_simulate_response(request, application_id):
    if not settings.DEBUG:
        return redirect('home')
    redir = _require_candidate(request)
    if redir:
        return redir
    profile = request.user.candidate_profile
    application = get_object_or_404(JobApplication, pk=application_id, candidate=profile)
    new_status = request.POST.get('status', '')
    if new_status in [JobApplication.STATUS_ACCEPTED, JobApplication.STATUS_REJECTED]:
        application.status = new_status
        application.save()
    return redirect('application_detail', application_id=application_id)
