"""
Canonical role taxonomy for Scout — single source of truth for job areas and
seniority levels. Keep in sync with any client-side usage.

These are the normalised dimensions used for candidate ↔ job matching.
The Job.title and CandidateProfile.desired_role fields remain free-text for
human display; matching runs on job_area + seniority + skills.
"""

JOB_AREAS = [
    ('backend',      'Desenvolvimento Backend'),
    ('frontend',     'Desenvolvimento Frontend'),
    ('fullstack',    'Desenvolvimento Full Stack'),
    ('mobile',       'Desenvolvimento Mobile'),
    ('data_science', 'Data Science / Machine Learning'),
    ('data_eng',     'Engenharia de Dados'),
    ('devops',       'DevOps / SRE / Cloud'),
    ('security',     'Segurança da Informação'),
    ('qa',           'QA / Testes'),
    ('ux',           'UX / Design de Produto'),
    ('product',      'Gerência de Produto (PM)'),
    ('bi',           'BI / Analytics'),
    ('infra',        'Suporte / Infraestrutura'),
    ('project_mgmt', 'Gestão de Projetos / Scrum Master'),
    ('other',        'Outro'),
]

SENIORITY_LEVELS = [
    ('estagio',      'Estágio'),
    ('junior',       'Júnior'),
    ('pleno',        'Pleno'),
    ('senior',       'Sênior'),
    ('especialista', 'Especialista / Staff'),
    ('gestao',       'Gerência / Tech Lead'),
]

# Numeric order used to compute proximity in match_score()
SENIORITY_ORDER = {
    'estagio':      0,
    'junior':       1,
    'pleno':        2,
    'senior':       3,
    'especialista': 4,
    'gestao':       5,
}

VALID_JOB_AREAS     = {v for v, _ in JOB_AREAS}
VALID_SENIORITIES   = {v for v, _ in SENIORITY_LEVELS}

LANGUAGES = [
    'Português',
    'Inglês',
    'Espanhol',
    'Francês',
    'Alemão',
    'Italiano',
    'Mandarim',
    'Japonês',
    'Árabe',
    'Russo',
]

# Soft skills for company endorsements — unified with the candidate skill list
# so that every skill a candidate can add to their profile can also be endorsed.
from core.skills import SOFT_SKILL_CATEGORIES as SOFT_SKILLS

# Qualities that candidates can endorse on companies after a hiring process.
COMPANY_QUALITIES = [
    'Retorno rápido',
    'Comunicação clara',
    'Processo seletivo organizado',
    'Feedback após o processo',
    'Respeitoso com o candidato',
    'Transparente sobre os requisitos',
    'Cumpriu os prazos prometidos',
    'Ambiente acolhedor',
    'Entrevistador bem preparado',
    'Descrição da vaga condizente',
]
