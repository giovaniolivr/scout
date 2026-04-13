"""
Candidate insight engine — rule-based pattern detection from real activity data.

Returns two lists of Insight objects (strengths, opportunities) for display on
the candidate home page. Pure function; no DB writes; safe to call on every load.
"""

from dataclasses import dataclass
from django.db.models import Count

# ── Thresholds ────────────────────────────────────────────────────────────────
MIN_RATED_APPS_FOR_SKILL  = 1    # need this many rated apps before skill insights fire
MIN_FINAL_APPS_FOR_RATE   = 2    # need this many final-status apps for acceptance rate
ENDORSEMENT_STRENGTH      = 2    # ≥N endorsements on a skill = validated strength
MAX_UNENDORSED_SHOWN      = 2    # cap on "skill not yet validated" opportunity cards
ACCEPTANCE_STRENGTH_RATE  = 0.40 # ≥40% acceptance → strong signal
ACCEPTANCE_CONCERN_RATE   = 0.15 # ≤15% acceptance → concern signal
AVG_RATING_STRENGTH       = 4.0  # avg ≥4.0 → companies think highly of candidate


@dataclass
class Insight:
    type: str   # 'strength' | 'opportunity' | 'tip'
    title: str
    body: str
    icon: str   # Bootstrap Icon class name (bi-*)

    @property
    def css_modifier(self):
        return {
            'strength':    'insight-item--strength',
            'opportunity': 'insight-item--opportunity',
            'tip':         'insight-item--tip',
        }.get(self.type, '')


def compute_candidate_insights(profile):
    """
    Returns (strengths, opportunities) — two lists of Insight objects.

    strengths    → things the candidate is already doing well
    opportunities → things they can improve or act on (includes actionable tips)
    """
    from company.models import SkillEndorsement

    strengths     = []
    opportunities = []

    apps       = list(profile.applications.select_related('job').all())
    rated_apps = [a for a in apps if a.company_rating is not None]
    final_apps = [a for a in apps if a.status in ('accepted', 'rejected')]
    accepted   = [a for a in final_apps if a.status == 'accepted']

    # ── 1. No applications yet — prompt to start ──────────────────────────────
    if not apps:
        opportunities.append(Insight(
            type='tip',
            title='Candidate-se às primeiras vagas',
            body='Você ainda não se candidatou a nenhuma vaga. Explore as recomendações e dê o primeiro passo!',
            icon='bi-send',
        ))
        # Profile completeness is still relevant even without apps
        _add_profile_tips(profile, opportunities)
        return strengths, opportunities

    # ── 2. Skill endorsement signals ──────────────────────────────────────────
    if len(rated_apps) >= MIN_RATED_APPS_FOR_SKILL:
        endorsement_counts = dict(
            SkillEndorsement.objects
            .filter(candidate=profile)
            .values('skill_name')
            .annotate(n=Count('id'))
            .values_list('skill_name', 'n')
        )

        soft_skills = profile.get_soft_skills_list()
        unendorsed_shown = 0

        for skill in soft_skills:
            count = endorsement_counts.get(skill, 0)
            if count >= ENDORSEMENT_STRENGTH:
                strengths.append(Insight(
                    type='strength',
                    title=f'{skill} validada pelas empresas',
                    body=(
                        f'Empresas confirmaram essa habilidade em você '
                        f'{count} vez{"es" if count > 1 else ""}.'
                    ),
                    icon='bi-patch-check-fill',
                ))
            elif count == 0 and unendorsed_shown < MAX_UNENDORSED_SHOWN:
                opportunities.append(Insight(
                    type='opportunity',
                    title=f'Demonstre mais {skill}',
                    body='Você listou essa habilidade, mas ainda não recebeu validações externas por ela.',
                    icon='bi-arrow-up-circle',
                ))
                unendorsed_shown += 1

    # ── 3. Skills demanded by applied jobs but absent from profile ────────────
    if final_apps:
        all_candidate_skills = {s.lower() for s in (
            profile.get_soft_skills_list() + profile.get_hard_skills_list()
        )}
        gap_counts: dict[str, int] = {}
        for app in final_apps:
            required = (
                app.job.get_required_soft_skills_list() +
                app.job.get_required_hard_skills_list()
            )
            for skill in required:
                if skill.lower() not in all_candidate_skills:
                    gap_counts[skill] = gap_counts.get(skill, 0) + 1

        if gap_counts:
            top_gap, top_count = max(gap_counts.items(), key=lambda x: x[1])
            if top_count >= 2:
                opportunities.append(Insight(
                    type='opportunity',
                    title=f'Adicione "{top_gap}" ao seu perfil',
                    body=(
                        f'Essa habilidade aparece em {top_count} vagas às quais você '
                        f'se candidatou, mas não está no seu perfil.'
                    ),
                    icon='bi-plus-circle',
                ))

    # ── 4. Acceptance rate ────────────────────────────────────────────────────
    if len(final_apps) >= MIN_FINAL_APPS_FOR_RATE:
        rate = len(accepted) / len(final_apps)
        pct  = int(rate * 100)
        if rate >= ACCEPTANCE_STRENGTH_RATE:
            strengths.append(Insight(
                type='strength',
                title='Alta taxa de aprovação',
                body=f'Você foi aprovado em {pct}% das candidaturas concluídas — isso está acima da média.',
                icon='bi-trophy',
            ))
        elif rate <= ACCEPTANCE_CONCERN_RATE:
            opportunities.append(Insight(
                type='opportunity',
                title='Poucas aprovações',
                body='Sua taxa de aprovação está baixa. Verifique se as vagas escolhidas estão alinhadas com seu perfil e habilidades.',
                icon='bi-exclamation-circle',
            ))

    # ── 5. Average company rating ─────────────────────────────────────────────
    if len(rated_apps) >= 2:
        avg = sum(a.company_rating for a in rated_apps) / len(rated_apps)
        if avg >= AVG_RATING_STRENGTH:
            strengths.append(Insight(
                type='strength',
                title='Empresas te avaliam bem',
                body=f'Sua avaliação média é {avg:.1f}/5 com base nos feedbacks recebidos.',
                icon='bi-star-fill',
            ))

    # ── 6. Candidate rated companies — feedback participation signal ──────────
    rated_by_candidate = [a for a in apps if a.experience_rating is not None]
    if rated_by_candidate:
        count = len(rated_by_candidate)
        strengths.append(Insight(
            type='strength',
            title=f'Você avaliou {count} processo{"s" if count > 1 else ""} seletivo{"s" if count > 1 else ""}',
            body=(
                'Dar feedback às empresas contribui para a qualidade da plataforma '
                'e demonstra seu comprometimento com o ecossistema.'
            ),
            icon='bi-chat-heart',
        ))

    # ── 7. Profile completeness tips ─────────────────────────────────────────
    _add_profile_tips(profile, opportunities)

    return strengths, opportunities


def _add_profile_tips(profile, opportunities):
    """Appends a single profile-completeness tip if any important fields are missing."""
    missing = []
    if not profile.profile_cv:
        missing.append('currículo')
    if not profile.bio:
        missing.append('bio')
    if not profile.linkedin_url:
        missing.append('LinkedIn')
    if not profile.hard_skills:
        missing.append('habilidades técnicas')
    if not profile.languages:
        missing.append('idiomas')

    if missing:
        listed = ', '.join(missing[:3])
        suffix = '...' if len(missing) > 3 else '.'
        opportunities.append(Insight(
            type='tip',
            title='Complete seu perfil',
            body=f'Adicione: {listed}{suffix} Perfis completos têm mais visibilidade.',
            icon='bi-person-fill-exclamation',
        ))
