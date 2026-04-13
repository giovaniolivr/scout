from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone

from company.models import CompanyProfile, CompanyFollow, SkillEndorsement, CompanyQualityEndorsement, Job
from company.insights import compute_company_insights
from candidates.models import CandidateProfile, JobApplication
from core.skills import filter_hard_skills, filter_soft_skills, HARD_SKILLS, SOFT_SKILL_CATEGORIES
from core.roles import JOB_AREAS, SENIORITY_LEVELS, VALID_JOB_AREAS, VALID_SENIORITIES, LANGUAGES, SOFT_SKILLS, COMPANY_QUALITIES

VALID_COMPANY_SIZES = [c[0] for c in CompanyProfile.SIZE_CHOICES]


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

    strengths, opportunities = compute_company_insights(profile)

    return render(request, 'home_company.html', {
        'open_jobs_count': jobs.filter(status=Job.STATUS_OPEN).count(),
        'total_jobs_count': jobs.count(),
        'total_applications': total_applications,
        'new_applications': new_applications,
        'recent_applications': recent_applications,
        'recent_jobs': jobs[:3],
        'insight_strengths': strengths,
        'insight_opportunities': opportunities,
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

        raw_vacancies = request.POST.get('vacancies', '1').strip()
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

        vacancies = 1
        if raw_vacancies:
            if not raw_vacancies.isdigit() or int(raw_vacancies) < 1:
                errors['vacancies'] = 'Número de vagas deve ser 1 ou mais.'
            else:
                vacancies = int(raw_vacancies)

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
            vacancies=vacancies,
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
        'approved_count': job.get_approved_count(),
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
    candidate = application.candidate

    # Mark as viewed the first time the company opens the applicant page
    if application.status == JobApplication.STATUS_PENDING:
        application.status = JobApplication.STATUS_VIEWED
        application.save()

    rating_error = None

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'rate_candidate':
            # Only allowed once, and only after a final status
            final_statuses = [JobApplication.STATUS_ACCEPTED, JobApplication.STATUS_REJECTED]
            if application.company_rated_at or application.status not in final_statuses:
                messages.error(request, 'Avaliação não permitida neste momento.')
                return redirect('applicant_detail', job_id=job.id, application_id=application.id)

            raw_rating = request.POST.get('company_rating', '').strip()
            company_comment = request.POST.get('company_comment', '').strip()
            endorsed_skills = request.POST.getlist('endorsed_skills')

            # Validate rating if provided
            company_rating = None
            if raw_rating:
                if not raw_rating.isdigit() or not (1 <= int(raw_rating) <= 5):
                    rating_error = 'Selecione uma avaliação entre 1 e 5 estrelas.'
                else:
                    company_rating = int(raw_rating)

            if not rating_error:
                application.company_rating = company_rating
                application.company_comment = company_comment
                application.company_rated_at = timezone.now()
                application.save()

                # Record skill endorsements — any skill from the canonical list is valid,
                # not just what the candidate listed on their profile.
                valid_skills = set(SOFT_SKILLS)
                for skill in endorsed_skills:
                    if skill in valid_skills:
                        SkillEndorsement.objects.get_or_create(
                            candidate=candidate,
                            company=profile,
                            job_application=application,
                            skill_name=skill,
                        )

                # Recalculate Scout Score now that a new rating exists
                candidate.recalculate_scout_score()

                messages.success(request, 'Avaliação enviada com sucesso.')
                return redirect('applicant_detail', job_id=job.id, application_id=application.id)

        else:
            new_status = request.POST.get('status', '')
            allowed = [
                JobApplication.STATUS_VIEWED,
                JobApplication.STATUS_ACCEPTED,
                JobApplication.STATUS_REJECTED,
            ]
            if new_status in allowed:
                application.status = new_status
                application.save()
                if new_status == JobApplication.STATUS_ACCEPTED:
                    job.auto_close_if_full()
                messages.success(request, 'Status da candidatura atualizado.')
                return redirect('applicant_detail', job_id=job.id, application_id=application.id)
            else:
                messages.error(request, 'Status inválido.')

    # Endorsements already given on this application
    existing_endorsements = set(
        application.endorsements.values_list('skill_name', flat=True)
    ) if application.company_rated_at else set()

    return render(request, 'applicant_detail.html', {
        'job': job,
        'application': application,
        'candidate': candidate,
        'rating_error': rating_error,
        'existing_endorsements': existing_endorsements,
        'all_soft_skills': SOFT_SKILLS,
    })


# ---------------------------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------------------------

@login_required
def candidate_list(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    search    = request.GET.get('q', '').strip()
    area      = request.GET.get('area', '').strip()
    seniority = request.GET.get('seniority', '').strip()
    language  = request.GET.get('language', '').strip()
    education = request.GET.get('education', '').strip()

    candidates = (
        CandidateProfile.objects
        .filter(is_onboarded=True)
        .select_related('user')
        .order_by('user__first_name')
    )

    if search:
        candidates = (
            candidates.filter(user__first_name__icontains=search) |
            candidates.filter(user__last_name__icontains=search) |
            candidates.filter(hard_skills__icontains=search) |
            candidates.filter(soft_skills__icontains=search)
        ).filter(is_onboarded=True).select_related('user').order_by('user__first_name')

    if area and area in VALID_JOB_AREAS:
        candidates = candidates.filter(desired_area=area)

    if seniority and seniority in VALID_SENIORITIES:
        candidates = candidates.filter(desired_seniority=seniority)

    if language and language in LANGUAGES:
        candidates = candidates.filter(languages__icontains=language)

    valid_education = {c[0] for c in CandidateProfile.EDUCATION_CHOICES}
    if education and education in valid_education:
        candidates = candidates.filter(education_level=education)

    has_filters = any([search, area, seniority, language, education])

    return render(request, 'candidate_list.html', {
        'candidates': candidates,
        'search': search,
        'area': area,
        'seniority': seniority,
        'language': language,
        'education': education,
        'has_filters': has_filters,
        'job_areas': JOB_AREAS,
        'seniority_levels': SENIORITY_LEVELS,
        'languages': LANGUAGES,
        'education_choices': CandidateProfile.EDUCATION_CHOICES,
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
        .filter(is_onboarded=True)
        .exclude(id__in=already_applied_ids)
        .select_related('user')
        .annotate(application_count=Count('applications'))
        .filter(application_count__gt=0)
        .order_by('-application_count')[:20]
    )

    return render(request, 'recommendations.html', {'candidates': candidates})


# ---------------------------------------------------------------------------
# COMPANY PROFILE (own view + edit)
# ---------------------------------------------------------------------------

@login_required
def profile_company(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    jobs = profile.jobs.all().order_by('-created_at')
    total_applications = JobApplication.objects.filter(job__company=profile).count()

    return render(request, 'profile_company.html', {
        'profile': profile,
        'jobs': jobs,
        'total_applications': total_applications,
        'size_choices': CompanyProfile.SIZE_CHOICES,
    })


@login_required
def edit_profile_company(request):
    profile, redir = _require_company(request)
    if redir:
        return redir

    if request.method == 'POST':
        bio = request.POST.get('bio', '').strip()
        description = request.POST.get('description', '').strip()
        website = request.POST.get('website', '').strip()
        linkedin_url = request.POST.get('linkedin_url', '').strip()
        sector = request.POST.get('sector', '').strip()
        company_size = request.POST.get('company_size', '').strip()
        phone = request.POST.get('phone', '').strip()

        errors = {}

        if bio and len(bio) > 300:
            errors['bio'] = 'Tagline muito longa (máximo 300 caracteres).'
        if sector and len(sector) > 100:
            errors['sector'] = 'Setor muito longo (máximo 100 caracteres).'
        if company_size and company_size not in VALID_COMPANY_SIZES:
            errors['company_size'] = 'Selecione um porte válido.'
        if phone and len(phone) > 20:
            errors['phone'] = 'Telefone muito longo (máximo 20 caracteres).'

        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        if linkedin_url and not linkedin_url.startswith(('http://', 'https://')):
            linkedin_url = 'https://' + linkedin_url

        if errors:
            return render(request, 'edit_profile_company.html', {
                'profile': profile,
                'errors': errors,
                'form_data': request.POST,
                'size_choices': CompanyProfile.SIZE_CHOICES,
            })

        profile.bio = bio
        profile.description = description
        profile.website = website
        profile.linkedin_url = linkedin_url
        profile.sector = sector
        profile.company_size = company_size
        if phone:
            profile.phone = phone
        profile.save()

        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('profile_company')

    return render(request, 'edit_profile_company.html', {
        'profile': profile,
        'size_choices': CompanyProfile.SIZE_CHOICES,
    })


# ---------------------------------------------------------------------------
# PUBLIC COMPANY PROFILE (visible to candidates)
# ---------------------------------------------------------------------------

@login_required
def company_public_profile(request, company_id):
    company = get_object_or_404(CompanyProfile, id=company_id)
    jobs = company.jobs.filter(status=Job.STATUS_OPEN).order_by('-created_at')

    # Follow state — only relevant when the viewer is a candidate
    is_following = False
    viewer_is_candidate = hasattr(request.user, 'candidate_profile')
    if viewer_is_candidate:
        candidate_profile = request.user.candidate_profile
        is_following = CompanyFollow.objects.filter(
            candidate=candidate_profile, company=company
        ).exists()

    # Aggregated quality endorsements — sorted by count descending
    quality_endorsements = (
        company.quality_endorsements
        .values('quality_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return render(request, 'company_public_profile.html', {
        'company': company,
        'jobs': jobs,
        'is_following': is_following,
        'viewer_is_candidate': viewer_is_candidate,
        'follower_count': company.get_follower_count(),
        'quality_endorsements': quality_endorsements,
    })


@login_required
@require_POST
def toggle_follow_company(request, company_id):
    if not hasattr(request.user, 'candidate_profile'):
        messages.error(request, 'Apenas candidatos podem seguir empresas.')
        return redirect('company_public_profile', company_id=company_id)

    company = get_object_or_404(CompanyProfile, id=company_id)
    candidate_profile = request.user.candidate_profile

    follow, created = CompanyFollow.objects.get_or_create(
        candidate=candidate_profile, company=company
    )
    if not created:
        follow.delete()
        messages.success(request, f'Você deixou de seguir {company.company_name}.')
    else:
        messages.success(request, f'Você está seguindo {company.company_name}!')

    return redirect('company_public_profile', company_id=company_id)
