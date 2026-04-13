"""
Company insight engine — rule-based pattern detection from real activity data.

Returns two lists of Insight objects (strengths, opportunities) for display on
the company home page. Pure function; no DB writes; safe to call on every load.
"""

from dataclasses import dataclass
from django.db.models import Avg, Count

# ── Thresholds ────────────────────────────────────────────────────────────────
MIN_QUALITY_ENDORSEMENTS  = 1    # ≥N endorsements on a quality = validated strength
MIN_APPS_FOR_PENDING_WARN = 3    # need at least this many apps before pending-rate fires
PENDING_CONCERN_RATE      = 0.30 # >30% of total apps still pending → concern
MIN_RATINGS_FOR_EXP       = 2    # need at least this many candidate ratings for avg
EXP_RATING_STRENGTH       = 4.0  # avg candidate experience ≥4.0 → strong signal
EXP_RATING_CONCERN        = 3.0  # avg candidate experience <3.0 → concern signal
MIN_CLOSED_FOR_FEEDBACK   = 3    # closed apps before "collect more feedback" fires


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


def compute_company_insights(company_profile):
    """
    Returns (strengths, opportunities) — two lists of Insight objects.

    strengths    → things the company is doing well in its hiring process
    opportunities → things they can improve (process quality, profile, responsiveness)
    """
    from candidates.models import JobApplication

    strengths     = []
    opportunities = []

    all_apps = JobApplication.objects.filter(job__company=company_profile)
    total_apps = all_apps.count()

    # ── 1. Endorsed company qualities (strengths) ─────────────────────────────
    quality_counts = dict(
        company_profile.quality_endorsements
        .values('quality_name')
        .annotate(n=Count('id'))
        .values_list('quality_name', 'n')
    )
    # Show the top two endorsed qualities that exceed the threshold
    top_qualities = sorted(quality_counts.items(), key=lambda x: x[1], reverse=True)
    for quality, count in top_qualities[:2]:
        if count >= MIN_QUALITY_ENDORSEMENTS:
            strengths.append(Insight(
                type='strength',
                title=f'Reconhecido por: {quality}',
                body=(
                    f'{count} candidato{"s" if count > 1 else ""} '
                    f'endossaram essa qualidade do seu processo seletivo.'
                ),
                icon='bi-award',
            ))

    # ── 2. No feedback despite closed processes ───────────────────────────────
    closed_apps = all_apps.filter(status__in=['accepted', 'rejected']).count()
    total_endorsements = sum(quality_counts.values())
    if closed_apps >= MIN_CLOSED_FOR_FEEDBACK and total_endorsements == 0:
        opportunities.append(Insight(
            type='opportunity',
            title='Colete mais feedback dos candidatos',
            body=(
                'Você concluiu vários processos, mas nenhum candidato avaliou a experiência. '
                'Um processo seletivo bem avaliado atrai mais talentos qualificados.'
            ),
            icon='bi-chat-left-text',
        ))

    # ── 3. Pending application backlog ────────────────────────────────────────
    if total_apps >= MIN_APPS_FOR_PENDING_WARN:
        pending_count = all_apps.filter(status='pending').count()
        pending_rate  = pending_count / total_apps
        if pending_rate > PENDING_CONCERN_RATE:
            opportunities.append(Insight(
                type='opportunity',
                title='Candidatos aguardando retorno',
                body=(
                    f'{pending_count} candidatura{"s estão" if pending_count > 1 else " está"} '
                    f'sem resposta. Responder rapidamente melhora sua reputação na plataforma.'
                ),
                icon='bi-hourglass-split',
            ))

    # ── 4. Candidate experience rating ───────────────────────────────────────
    rated = all_apps.filter(experience_rating__isnull=False)
    rated_count = rated.count()
    if rated_count >= MIN_RATINGS_FOR_EXP:
        avg_exp = rated.aggregate(avg=Avg('experience_rating'))['avg']
        if avg_exp >= EXP_RATING_STRENGTH:
            strengths.append(Insight(
                type='strength',
                title='Candidatos adoram seu processo',
                body=(
                    f'Avaliação média de {avg_exp:.1f}/5 pelos candidatos. '
                    f'Isso atrai mais talentos de qualidade.'
                ),
                icon='bi-heart-fill',
            ))
        elif avg_exp < EXP_RATING_CONCERN:
            opportunities.append(Insight(
                type='opportunity',
                title='Melhore a experiência do candidato',
                body=(
                    f'A avaliação média do seu processo é {avg_exp:.1f}/5. '
                    f'Candidatos insatisfeitos raramente recomendam sua empresa.'
                ),
                icon='bi-emoji-frown',
            ))

    # ── 5. Company profile completeness ──────────────────────────────────────
    missing = []
    if not company_profile.bio:
        missing.append('tagline')
    if not company_profile.description:
        missing.append('descrição da empresa')
    if not company_profile.sector:
        missing.append('setor de atuação')
    if not company_profile.website and not company_profile.linkedin_url:
        missing.append('website ou LinkedIn')

    if missing:
        listed = ', '.join(missing[:3])
        suffix = '...' if len(missing) > 3 else '.'
        opportunities.append(Insight(
            type='tip',
            title='Complete o perfil da empresa',
            body=f'Adicione: {listed}{suffix} Perfis completos atraem candidatos mais qualificados.',
            icon='bi-building-fill-exclamation',
        ))

    return strengths, opportunities
