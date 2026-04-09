from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count

from company.models import CompanyProfile, Job
from candidates.models import CandidateProfile, JobApplication
from core.skills import filter_hard_skills, filter_soft_skills, HARD_SKILLS, SOFT_SKILL_CATEGORIES
from core.roles import JOB_AREAS, SENIORITY_LEVELS, VALID_JOB_AREAS, VALID_SENIORITIES


def _require_company(request):
    """Returns (company_profile, None) or (None, redirect_response)."""
    if not hasattr(request.user, 'company_profile'):
        return None, redirect('home')
    return request.user.company_profile, None


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------

@login_required
def home_company(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    jobs = profile.jobs.all().order_by('-created_at')
    recent_applications = (
        JobApplication.objects
        .filter(job__company=profile)
        .select_related('candidate__user', 'job')
        .order_by('-applied_at')[:5]
    )
    total_applications = JobApplication.objects.filter(job__company=profile).count()
    new_applications = JobApplication.objects.filter(
        job__company=profile, status=JobApplication.STATUS_PENDING
    ).count()

    return render(request, 'home_company.html', {
        'open_jobs_count': jobs.filter(status=Job.STATUS_OPEN).count(),
        'total_jobs_count': jobs.count(),
        'total_applications': total_applications,
        'new_applications': new_applications,
        'recent_applications': recent_applications,
        'recent_jobs': jobs[:3],
    })


# ---------------------------------------------------------------------------
# JOB MANAGEMENT
# ---------------------------------------------------------------------------

@login_required
def job_list(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    jobs = (
        profile.jobs
        .annotate(application_count=Count('applications'))
        .order_by('-created_at')
    )
    return render(request, 'job_list.html', {'jobs': jobs})


@login_required
def job_create(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        location = request.POST.get('location', '').strip()
        job_type = request.POST.get('job_type', '')
        job_area = request.POST.get('job_area', '')
        seniority = request.POST.get('seniority', '')
        external_url = request.POST.get('external_url', '').strip()
        required_hard_skills = filter_hard_skills(request.POST.get('required_hard_skills', ''))
        required_soft_skills = filter_soft_skills(request.POST.get('required_soft_skills', ''))

        errors = {}

        if not title:
            errors['title'] = 'Título é obrigatório.'
        elif len(title) > 200:
            errors['title'] = 'Título muito longo (máximo 200 caracteres).'
        if not description:
            errors['description'] = 'Descrição é obrigatória.'
        if not location:
            errors['location'] = 'Localização é obrigatória.'
        elif len(location) > 100:
            errors['location'] = 'Localização muito longa (máximo 100 caracteres).'
        if job_type not in [Job.TYPE_FULL_TIME, Job.TYPE_PART_TIME, Job.TYPE_INTERNSHIP]:
            errors['job_type'] = 'Selecione um tipo de vaga válido.'
        if job_area not in VALID_JOB_AREAS:
            errors['job_area'] = 'Selecione uma área válida.'
        if seniority not in VALID_SENIORITIES:
            errors['seniority'] = 'Selecione um nível válido.'

        if errors:
            return render(request, 'job_create.html', {
                'errors': errors,
                'form_data': request.POST,
                'type_choices': Job.TYPE_CHOICES,
                'job_areas': JOB_AREAS,
                'seniority_levels': SENIORITY_LEVELS,
                'soft_skill_categories': SOFT_SKILL_CATEGORIES,
            })

        Job.objects.create(
            company=profile,
            title=title,
            description=description,
            location=location,
            job_type=job_type,
            job_area=job_area,
            seniority=seniority,
            external_url=external_url,
            required_hard_skills=required_hard_skills,
            required_soft_skills=required_soft_skills,
            status=Job.STATUS_OPEN,
        )

        messages.success(request, 'Vaga publicada com sucesso!')
        return redirect('job_list_company')

    return render(request, 'job_create.html', {
        'type_choices': Job.TYPE_CHOICES,
        'job_areas': JOB_AREAS,
        'seniority_levels': SENIORITY_LEVELS,
        'soft_skill_categories': SOFT_SKILL_CATEGORIES,
    })


@login_required
def job_detail_company(request, job_id):
    profile, redir = _require_company(request)
    if redir:
        return redir

    job = get_object_or_404(Job, id=job_id, company=profile)
    applications = (
        job.applications
        .select_related('candidate__user')
        .order_by('-applied_at')
    )

    return render(request, 'job_detail_company.html', {
        'job': job,
        'applications': applications,
        'status_choices': Job.STATUS_CHOICES,
    })


@login_required
@require_POST
def job_update_status(request, job_id):
    profile, redir = _require_company(request)
    if redir:
        return redir

    job = get_object_or_404(Job, id=job_id, company=profile)
    new_status = request.POST.get('status', '')
    valid_statuses = [s[0] for s in Job.STATUS_CHOICES]

    if new_status in valid_statuses:
        job.status = new_status
        job.save()
        messages.success(request, f'Status da vaga atualizado para "{job.get_status_display()}".')
    else:
        messages.error(request, 'Status inválido.')

    return redirect('job_detail_company', job_id=job.id)


@login_required
@require_POST
def job_delete(request, job_id):
    profile, redir = _require_company(request)
    if redir:
        return redir

    job = get_object_or_404(Job, id=job_id, company=profile)
    job.delete()
    messages.success(request, f'A vaga "{job.title}" foi removida.')
    return redirect('job_list_company')


# ---------------------------------------------------------------------------
# APPLICANT DETAIL
# ---------------------------------------------------------------------------

@login_required
def applicant_detail(request, job_id, application_id):
    profile, redir = _require_company(request)
    if redir:
        return redir

    job = get_object_or_404(Job, id=job_id, company=profile)
    application = get_object_or_404(JobApplication, id=application_id, job=job)

    # Mark as viewed the first time the company opens the applicant page
    if application.status == JobApplication.STATUS_PENDING:
        application.status = JobApplication.STATUS_VIEWED
        application.save()

    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        allowed = [
            JobApplication.STATUS_VIEWED,
            JobApplication.STATUS_ACCEPTED,
            JobApplication.STATUS_REJECTED,
        ]
        if new_status in allowed:
            application.status = new_status
            application.save()
            messages.success(request, 'Status da candidatura atualizado.')
            return redirect('applicant_detail', job_id=job.id, application_id=application.id)
        else:
            messages.error(request, 'Status inválido.')

    return render(request, 'applicant_detail.html', {
        'job': job,
        'application': application,
        'candidate': application.candidate,
    })


# ---------------------------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------------------------

@login_required
def candidate_list(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    search = request.GET.get('q', '').strip()

    candidates = CandidateProfile.objects.select_related('user').order_by('user__first_name')

    if search:
        candidates = candidates.filter(
            user__first_name__icontains=search
        ) | candidates.filter(
            user__last_name__icontains=search
        ) | candidates.filter(
            hard_skills__icontains=search
        ) | candidates.filter(
            soft_skills__icontains=search
        )
        candidates = candidates.select_related('user').order_by('user__first_name')

    return render(request, 'candidate_list.html', {
        'candidates': candidates,
        'search': search,
    })


@login_required
def recommendations(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    # IDs of candidates who already applied to this company's jobs
    already_applied_ids = (
        JobApplication.objects
        .filter(job__company=profile)
        .values_list('candidate_id', flat=True)
    )

    # RECOMMENDATION HOOK — replace this queryset with the Scout Score ranking
    # algorithm when it's ready. For now: show active candidates (at least 1
    # application on the platform) who haven't yet applied to this company,
    # ordered by total application count as a proxy for engagement/experience.
    candidates = (
        CandidateProfile.objects
        .exclude(id__in=already_applied_ids)
        .select_related('user')
        .annotate(application_count=Count('applications'))
        .filter(application_count__gt=0)
        .order_by('-application_count')[:20]
    )

    return render(request, 'recommendations.html', {'candidates': candidates})
