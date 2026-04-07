"""
Canonical skill lists for Scout.

These are the single source of truth for both server-side validation
and the client-side autocomplete / toggle UI. Keep JS in sync with this file.
"""

HARD_SKILLS = sorted([
    # Languages
    'Python', 'JavaScript', 'TypeScript', 'Java', 'C', 'C++', 'C#',
    'Go', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'R', 'Scala', 'MATLAB',
    'Dart', 'Lua', 'Perl', 'Haskell', 'Elixir', 'Clojure',

    # Web — back-end
    'Django', 'Flask', 'FastAPI', 'Node.js', 'Express.js', 'Spring Boot',
    'Laravel', 'Ruby on Rails', 'ASP.NET', 'NestJS', 'Symfony',

    # Web — front-end
    'React', 'Vue.js', 'Angular', 'Next.js', 'Nuxt.js', 'Svelte',
    'HTML', 'CSS', 'Sass', 'Tailwind CSS', 'Bootstrap', 'jQuery',

    # Mobile
    'Android', 'iOS', 'React Native', 'Flutter',

    # Databases
    'SQL', 'MySQL', 'PostgreSQL', 'SQLite', 'SQL Server', 'Oracle',
    'MongoDB', 'Redis', 'Firebase', 'Elasticsearch', 'Cassandra', 'DynamoDB',

    # DevOps / infra
    'Git', 'GitHub', 'GitLab', 'Docker', 'Kubernetes', 'Linux', 'Bash',
    'Terraform', 'Ansible', 'CI/CD', 'Jenkins', 'GitHub Actions', 'AWS',
    'Azure', 'Google Cloud', 'Nginx', 'Apache',

    # Data / AI
    'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
    'scikit-learn', 'Pandas', 'NumPy', 'Matplotlib', 'Power BI',
    'Tableau', 'Excel Avançado', 'Spark', 'Hadoop', 'Airflow', 'dbt',

    # APIs / architecture
    'REST APIs', 'GraphQL', 'WebSockets', 'Microsserviços', 'gRPC',
    'Message Queues', 'RabbitMQ', 'Kafka',

    # Testing
    'Selenium', 'Cypress', 'Jest', 'JUnit', 'Pytest', 'Playwright',

    # Design / product
    'Figma', 'Adobe XD', 'Photoshop', 'Illustrator', 'InDesign',
    'Sketch', 'Prototyping',

    # Games
    'Unity', 'Unreal Engine',

    # Enterprise / business tools
    'SAP', 'Salesforce', 'Jira', 'Confluence', 'Trello', 'Notion',
    'Word', 'PowerPoint', 'Excel', 'Google Workspace',

    # Methodology
    'Scrum', 'Kanban', 'Agile',
])


# Soft skill categories, grouped by domain.
# Each category will later have associated sub-skills used in the rating system.
SOFT_SKILL_CATEGORIES = [
    # Comunicação
    'Comunicação',
    'Comunicação Técnica',
    'Comunicação Interpessoal',
    'Comunicação Escrita',
    'Apresentação e Oratória',
    'Escuta Ativa',
    'Feedback Construtivo',

    # Liderança
    'Liderança',
    'Gestão de Equipes',
    'Mentoria e Coaching',
    'Delegação',
    'Desenvolvimento de Pessoas',
    'Gestão de Conflitos',
    'Influência e Persuasão',
    'Tomada de Decisão',

    # Trabalho em equipe
    'Trabalho em Equipe',
    'Colaboração',
    'Empatia',
    'Escuta Empática',
    'Construção de Relacionamentos',
    'Networking',

    # Resolução de problemas
    'Resolução de Problemas',
    'Pensamento Analítico',
    'Pensamento Crítico',
    'Raciocínio Lógico',
    'Criatividade',
    'Inovação',
    'Pensamento Lateral',

    # Gestão e organização
    'Gestão do Tempo',
    'Organização',
    'Planejamento',
    'Priorização',
    'Gestão de Projetos',
    'Atenção aos Detalhes',
    'Multitarefa',

    # Adaptabilidade
    'Adaptabilidade',
    'Flexibilidade',
    'Resiliência',
    'Aprendizado Contínuo',
    'Gestão de Mudanças',
    'Tolerância à Ambiguidade',

    # Inteligência emocional
    'Inteligência Emocional',
    'Autoconhecimento',
    'Autocontrole',
    'Motivação',
    'Gestão do Estresse',
    'Consciência Social',

    # Profissionalismo
    'Proatividade',
    'Iniciativa',
    'Ética Profissional',
    'Comprometimento',
    'Responsabilidade',
    'Autonomia',
    'Foco em Resultados',
    'Orientação para o Cliente',
    'Pontualidade',

    # Negociação
    'Negociação',
    'Argumentação',
    'Gestão de Expectativas',
    'Resolução de Impasses',

    # Visão estratégica
    'Visão Estratégica',
    'Pensamento Sistêmico',
    'Visão de Negócio',
    'Orientação para Dados',
    'Gestão de Riscos',
]


def filter_hard_skills(raw: str) -> str:
    """
    Parse a comma-separated string of hard skills and return only those
    present in the canonical list. Preserves order, strips duplicates.
    """
    allowed = set(HARD_SKILLS)
    seen = set()
    result = []
    for s in raw.split(','):
        s = s.strip()
        if s in allowed and s not in seen:
            result.append(s)
            seen.add(s)
    return ', '.join(result)


def filter_soft_skills(raw: str) -> str:
    """
    Parse a comma-separated string of soft skill categories and return only
    those present in the canonical list.
    """
    allowed = set(SOFT_SKILL_CATEGORIES)
    seen = set()
    result = []
    for s in raw.split(','):
        s = s.strip()
        if s in allowed and s not in seen:
            result.append(s)
            seen.add(s)
    return ', '.join(result)
