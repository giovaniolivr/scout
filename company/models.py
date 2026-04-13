from django.db import models
from django.contrib.auth.models import User
from core.roles import JOB_AREAS, SENIORITY_LEVELS, SENIORITY_ORDER, SOFT_SKILLS


class CompanyProfile(models.Model):
    SIZE_1_10 = '1_10'
    SIZE_11_50 = '11_50'
    SIZE_51_200 = '51_200'
    SIZE_201_500 = '201_500'
    SIZE_500_PLUS = '500_plus'
    SIZE_CHOICES = [
        (SIZE_1_10, '1 – 10 funcionários'),
        (SIZE_11_50, '11 – 50 funcionários'),
        (SIZE_51_200, '51 – 200 funcionários'),
        (SIZE_201_500, '201 – 500 funcionários'),
        (SIZE_500_PLUS, 'Mais de 500 funcionários'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=14, unique=True)
    responsible_name = models.CharField(max_length=200)
    cpf_responsible = models.CharField(max_length=11)
    phone = models.CharField(max_length=20)
    cep = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=200)

    # Profile fields — filled in after signup
    bio = models.CharField(max_length=300, blank=True, default='')
    description = models.TextField(blank=True, default='')
    website = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    sector = models.CharField(max_length=100, blank=True, default='')
    company_size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True, default='')

    def get_follower_count(self):
        return self.followers.count()

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"


class CompanyFollow(models.Model):
    candidate = models.ForeignKey(
        'candidates.CandidateProfile',
        on_delete=models.CASCADE,
        related_name='following',
    )
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='followers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'company')

    def __str__(self):
        return f"{self.candidate} follows {self.company}"


class SkillEndorsement(models.Model):
    """
    Records that a company observed a specific skill in a candidate during a hiring process.
    One record per skill per application — companies endorse skills they witnessed, not rate them.
    Used to build the candidate's validated skill profile over time.
    """
    candidate = models.ForeignKey(
        'candidates.CandidateProfile',
        on_delete=models.CASCADE,
        related_name='endorsements',
    )
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='given_endorsements',
    )
    job_application = models.ForeignKey(
        'candidates.JobApplication',
        on_delete=models.CASCADE,
        related_name='endorsements',
    )
    skill_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job_application', 'skill_name')

    def __str__(self):
        return f"{self.company.company_name} endorsed '{self.skill_name}' for {self.candidate}"


class CompanyQualityEndorsement(models.Model):
    """
    Records that a candidate endorsed a specific quality about a company's
    hiring process. One record per quality per application.
    Used to build the company's public reputation over time.
    """
    candidate = models.ForeignKey(
        'candidates.CandidateProfile',
        on_delete=models.CASCADE,
        related_name='company_quality_endorsements',
    )
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        related_name='quality_endorsements',
    )
    job_application = models.ForeignKey(
        'candidates.JobApplication',
        on_delete=models.CASCADE,
        related_name='company_quality_endorsements',
    )
    quality_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job_application', 'quality_name')

    def __str__(self):
        return f"{self.candidate} endorsed '{self.quality_name}' for {self.company.company_name}"


class Job(models.Model):
    STATUS_OPEN = 'open'
    STATUS_PAUSED = 'paused'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Aberta'),
        (STATUS_PAUSED, 'Pausada'),
        (STATUS_CLOSED, 'Fechada'),
    ]

    TYPE_FULL_TIME = 'full_time'
    TYPE_PART_TIME = 'part_time'
    TYPE_INTERNSHIP = 'internship'
    TYPE_CHOICES = [
        (TYPE_FULL_TIME, 'Tempo integral'),
        (TYPE_PART_TIME, 'Meio período'),
        (TYPE_INTERNSHIP, 'Estágio'),
    ]

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_FULL_TIME)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    vacancies = models.PositiveIntegerField(default=1)
    external_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Normalised matching dimensions — used by match_score(); title stays free-text for display
    job_area = models.CharField(max_length=20, choices=JOB_AREAS, blank=True, default='')
    seniority = models.CharField(max_length=20, choices=SENIORITY_LEVELS, blank=True, default='')

    # Skill requirements — comma-separated; matched against CandidateProfile skills.
    required_hard_skills = models.TextField(blank=True, default='')
    required_soft_skills = models.TextField(blank=True, default='')

    def get_required_hard_skills_list(self):
        return [s.strip() for s in self.required_hard_skills.split(',') if s.strip()]

    def get_required_soft_skills_list(self):
        return [s.strip() for s in self.required_soft_skills.split(',') if s.strip()]

    def get_approved_count(self):
        return self.applications.filter(status='accepted').count()

    def auto_close_if_full(self):
        """
        Called after a candidate is accepted. If the number of accepted
        applications reaches the vacancy target, closes the job and
        automatically rejects all remaining pending/viewed applications.
        """
        if self.status == self.STATUS_CLOSED:
            return
        if self.get_approved_count() >= self.vacancies:
            self.status = self.STATUS_CLOSED
            self.save(update_fields=['status'])
            self.applications.filter(
                status__in=['pending', 'viewed']
            ).update(status='rejected')

    def has_requirements(self):
        return bool(self.required_hard_skills.strip() or self.required_soft_skills.strip())

    def match_score(self, candidate_profile):
        """
        Returns an integer 0–100 representing how well a candidate matches
        this job, or None when no matching criteria exist on either side.

        Three weighted components (relative weights: skills 5, area 4, seniority 2):
          - Skills: overlap between required skills and candidate's skills
          - Area:   exact match between job_area and candidate.desired_area
          - Seniority: proximity between levels (25 pts deducted per step apart)

        Any component is skipped when the required data is absent on either
        side; weights are renormalised so the result stays 0–100.
        """
        required_skills = (
            self.get_required_hard_skills_list() +
            self.get_required_soft_skills_list()
        )
        has_skill_req     = bool(required_skills)
        has_area_req      = bool(self.job_area and candidate_profile.desired_area)
        has_seniority_req = bool(self.seniority and candidate_profile.desired_seniority)

        if not has_skill_req and not has_area_req and not has_seniority_req:
            return None  # Truly open — nothing to match against

        components = []  # (score, weight) tuples

        if has_skill_req:
            candidate_skills = (
                candidate_profile.get_hard_skills_list() +
                candidate_profile.get_soft_skills_list()
            )
            if candidate_skills:
                candidate_lower = {s.lower() for s in candidate_skills}
                matched = sum(1 for s in required_skills if s.lower() in candidate_lower)
                skill_score = int((matched / len(required_skills)) * 100)
            else:
                skill_score = 0
            components.append((skill_score, 5))

        if has_area_req:
            area_score = 100 if self.job_area == candidate_profile.desired_area else 0
            components.append((area_score, 4))

        if has_seniority_req:
            job_lvl  = SENIORITY_ORDER.get(self.seniority, -1)
            cand_lvl = SENIORITY_ORDER.get(candidate_profile.desired_seniority, -1)
            if job_lvl >= 0 and cand_lvl >= 0:
                seniority_score = max(0, 100 - abs(job_lvl - cand_lvl) * 25)
            else:
                seniority_score = 50  # unknown level — neutral
            components.append((seniority_score, 2))

        total_weight = sum(w for _, w in components)
        return int(sum(s * w for s, w in components) / total_weight)

    def __str__(self):
        return f"{self.title} — {self.company.company_name}"
