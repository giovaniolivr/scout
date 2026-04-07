from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from company.models import CompanyProfile, Job


SEED_DATA = [
    {
        'company_name': 'TechGlobal',
        'email': 'rh@techglobal.com',
        'cnpj': '11111111000101',
        'jobs': [
            {
                'title': 'Desenvolvedor Front-End Jr',
                'description': 'Desenvolvimento de interfaces modernas com React e TypeScript. Buscamos candidatos com boa comunicação e proatividade.',
                'location': 'São Paulo, SP',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
            },
            {
                'title': 'Analista de QA Jr',
                'description': 'Criação e execução de casos de teste, automação com Selenium e reporte de bugs. Perfil analítico e organizado.',
                'location': 'São Paulo, SP',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
            },
        ],
    },
    {
        'company_name': 'Digital Labs',
        'email': 'rh@digitallabs.com',
        'cnpj': '22222222000102',
        'jobs': [
            {
                'title': 'Estagiário em Desenvolvimento Web',
                'description': 'Apoio no desenvolvimento de sistemas internos com Django e Vue.js. Ideal para estudantes de TI.',
                'location': 'Rio de Janeiro, RJ',
                'job_type': Job.TYPE_INTERNSHIP,
                'status': Job.STATUS_OPEN,
            },
            {
                'title': 'Designer UI/UX',
                'description': 'Criação de wireframes, protótipos e design systems. Experiência com Figma e forte senso estético.',
                'location': 'Remoto',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
            },
        ],
    },
    {
        'company_name': 'QASolutions',
        'email': 'rh@qasolutions.com',
        'cnpj': '33333333000103',
        'jobs': [
            {
                'title': 'Analista de Dados Jr',
                'description': 'Análise de dados com Python e SQL, criação de dashboards e relatórios para tomada de decisão.',
                'location': 'Belo Horizonte, MG',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
            },
            {
                'title': 'Suporte de TI — Meio Período',
                'description': 'Atendimento a chamados de suporte, manutenção de equipamentos e configuração de redes.',
                'location': 'Belo Horizonte, MG',
                'job_type': Job.TYPE_PART_TIME,
                'status': Job.STATUS_OPEN,
            },
        ],
    },
    {
        'company_name': 'Inova Startup',
        'email': 'rh@inovastartup.com',
        'cnpj': '44444444000104',
        'jobs': [
            {
                'title': 'Desenvolvedor Back-End Jr',
                'description': 'Construção de APIs REST com Node.js e PostgreSQL. Ambiente ágil, dinâmico e com muito aprendizado.',
                'location': 'Remoto',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
            },
            {
                'title': 'Estagiário em Marketing Digital',
                'description': 'Gestão de redes sociais, criação de conteúdo e análise de métricas de campanhas.',
                'location': 'Curitiba, PR',
                'job_type': Job.TYPE_INTERNSHIP,
                'status': Job.STATUS_OPEN,
                'external_url': 'https://linkedin.com/jobs',
            },
        ],
    },
    {
        'company_name': 'Nexus Tech',
        'email': 'rh@nexustech.com',
        'cnpj': '55555555000105',
        'jobs': [
            {
                'title': 'Engenheiro de Software Pleno',
                'description': 'Desenvolvimento de sistemas distribuídos em escala. Buscamos profissionais com experiência em cloud e microsserviços.',
                'location': 'São Paulo, SP',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
                'external_url': 'https://linkedin.com/jobs',
            },
            {
                'title': 'Product Manager Jr',
                'description': 'Gestão de roadmap de produto, alinhamento com times de engenharia e design. Experiência com metodologias ágeis.',
                'location': 'Remoto',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
                'external_url': 'https://indeed.com/jobs',
            },
        ],
    },
    {
        'company_name': 'CloudBase',
        'email': 'rh@cloudbase.com',
        'cnpj': '66666666000106',
        'jobs': [
            {
                'title': 'Engenheiro DevOps Jr',
                'description': 'Configuração e manutenção de pipelines CI/CD, gerenciamento de infraestrutura com Terraform e AWS.',
                'location': 'Remoto',
                'job_type': Job.TYPE_FULL_TIME,
                'status': Job.STATUS_OPEN,
                'external_url': 'https://glassdoor.com/jobs',
            },
            {
                'title': 'Estagiário em Ciência de Dados',
                'description': 'Exploração e limpeza de dados, criação de modelos preditivos com Python e scikit-learn.',
                'location': 'Campinas, SP',
                'job_type': Job.TYPE_INTERNSHIP,
                'status': Job.STATUS_OPEN,
                'external_url': 'https://indeed.com/jobs',
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with sample job listings for development.'

    def handle(self, *args, **options):
        created_jobs = 0

        for entry in SEED_DATA:
            user, _ = User.objects.get_or_create(
                email=entry['email'],
                defaults={
                    'username': entry['email'],
                    'is_active': True,
                },
            )

            profile, _ = CompanyProfile.objects.get_or_create(
                cnpj=entry['cnpj'],
                defaults={
                    'user': user,
                    'company_name': entry['company_name'],
                    'responsible_name': 'Responsável Seed',
                    'cpf_responsible': '00000000000',
                    'phone': '',
                    'cep': '',
                    'city': '',
                    'district': '',
                    'street': '',
                },
            )

            for job_data in entry['jobs']:
                job, created = Job.objects.get_or_create(
                    company=profile,
                    title=job_data['title'],
                    defaults=job_data,
                )
                if created:
                    created_jobs += 1

        self.stdout.write(self.style.SUCCESS(f'{created_jobs} vagas criadas com sucesso.'))
