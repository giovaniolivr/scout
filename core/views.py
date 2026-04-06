from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from core.models import EmailVerificationToken
from candidates.models import CandidateProfile
from company.models import CompanyProfile


def _redirect_authenticated(request):
    """Returns a redirect response if the user is already logged in, else None."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'candidate_profile'):
            return redirect('home_candidate')
        if hasattr(request.user, 'company_profile'):
            return redirect('home_company')
    return None


def home(request):
    return render(request, 'home.html')


# ---------------------------------------------------------------------------
# CANDIDATE REGISTRATION
# ---------------------------------------------------------------------------

def register_candidate(request):
    redir = _redirect_authenticated(request)
    if redir:
        return redir

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
            return render(request, 'register_candidate.html', {'hide_nav_links': True})

        token = EmailVerificationToken.generate_candidate_code(email)
        request.session['registration_candidate_email'] = email

        send_mail(
            subject='Seu código de verificação Scout',
            message=f'Seu código de verificação é: {token.token}\n\nEle expira em 10 minutos.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return redirect('verify_email_candidate')

    return render(request, 'register_candidate.html', {'hide_nav_links': True})


def verify_email_candidate(request):
    email = request.session.get('registration_candidate_email')

    if not email:
        return redirect('register_candidate')

    if request.method == 'POST':
        code = (
            request.POST.get('code_1', '') +
            request.POST.get('code_2', '') +
            request.POST.get('code_3', '') +
            request.POST.get('code_4', '')
        )

        try:
            token = EmailVerificationToken.objects.get(
                email=email,
                token=code,
                user_type=EmailVerificationToken.USER_TYPE_CANDIDATE,
                is_used=False,
            )
        except EmailVerificationToken.DoesNotExist:
            messages.error(request, 'Código inválido. Tente novamente.')
            return render(request, 'verify_email_candidate.html', {'email': email, 'hide_nav_links': True})

        if token.is_expired():
            messages.error(request, 'Código expirado. Solicite um novo.')
            return render(request, 'verify_email_candidate.html', {'email': email, 'hide_nav_links': True})

        token.is_used = True
        token.save()
        request.session['candidate_email_verified'] = True

        return redirect('register_details_candidate')

    return render(request, 'verify_email_candidate.html', {'email': email, 'hide_nav_links': True})


def resend_candidate_code(request):
    """Regenerates the verification code and resends the email."""
    email = request.session.get('registration_candidate_email')

    if not email:
        return redirect('register_candidate')

    token = EmailVerificationToken.generate_candidate_code(email)

    send_mail(
        subject='Seu novo código de verificação Scout',
        message=f'Seu novo código de verificação é: {token.token}\n\nEle expira em 10 minutos.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )

    messages.success(request, 'Novo código enviado para o seu e-mail.')
    return redirect('verify_email_candidate')


def register_details_candidate(request):
    email = request.session.get('registration_candidate_email')
    verified = request.session.get('candidate_email_verified')

    if not email or not verified:
        return redirect('register_candidate')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        cpf = request.POST.get('cpf', '').replace('.', '').replace('-', '').strip()
        phone = request.POST.get('phone', '').strip()
        cep = request.POST.get('cep', '').replace('-', '').strip()
        city = request.POST.get('city', '').strip()
        district = request.POST.get('district', '').strip()
        street = request.POST.get('street', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        errors = {}

        if not first_name:
            errors['first_name'] = 'Nome é obrigatório.'
        if not last_name:
            errors['last_name'] = 'Sobrenome é obrigatório.'
        if len(cpf) != 11:
            errors['cpf'] = 'CPF deve conter 11 dígitos.'
        elif CandidateProfile.objects.filter(cpf=cpf).exists():
            errors['cpf'] = 'CPF já cadastrado.'
        if password != password_confirm:
            errors['password_confirm'] = 'As senhas não coincidem.'
        else:
            try:
                validate_password(password)
            except ValidationError as e:
                errors['password'] = ' '.join(e.messages)

        if errors:
            return render(request, 'register_details_candidate.html', {
                'hide_nav_links': True,
                'errors': errors,
                'form_data': request.POST,
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        CandidateProfile.objects.create(
            user=user,
            cpf=cpf,
            phone=phone,
            cep=cep,
            city=city,
            district=district,
            street=street,
        )

        del request.session['registration_candidate_email']
        del request.session['candidate_email_verified']

        login(request, user)
        return redirect('home_candidate')

    return render(request, 'register_details_candidate.html', {'hide_nav_links': True})


# ---------------------------------------------------------------------------
# COMPANY REGISTRATION
# ---------------------------------------------------------------------------

def register_company(request):
    redir = _redirect_authenticated(request)
    if redir:
        return redir

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        cnpj = request.POST.get('cnpj', '').replace('.', '').replace('/', '').replace('-', '').strip()

        errors = {}

        if not email:
            errors['email'] = 'E-mail é obrigatório.'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Este e-mail já está cadastrado.'

        if len(cnpj) != 14:
            errors['cnpj'] = 'CNPJ deve conter 14 dígitos.'
        elif CompanyProfile.objects.filter(cnpj=cnpj).exists():
            errors['cnpj'] = 'CNPJ já cadastrado.'

        if errors:
            return render(request, 'register_company.html', {
                'hide_nav_links': True,
                'errors': errors,
                'form_data': request.POST,
            })

        request.session['registration_company_email'] = email
        request.session['registration_company_cnpj'] = cnpj

        return redirect('register_details_company')

    return render(request, 'register_company.html', {'hide_nav_links': True})


def register_details_company(request):
    email = request.session.get('registration_company_email')
    cnpj = request.session.get('registration_company_cnpj')

    if not email or not cnpj:
        return redirect('register_company')

    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        responsible_name = request.POST.get('responsible_name', '').strip()
        cpf_responsible = request.POST.get('cpf_responsible', '').replace('.', '').replace('-', '').strip()
        phone = request.POST.get('phone', '').strip()
        cep = request.POST.get('cep', '').replace('-', '').strip()
        city = request.POST.get('city', '').strip()
        district = request.POST.get('district', '').strip()
        street = request.POST.get('street', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        errors = {}

        if not company_name:
            errors['company_name'] = 'Nome da empresa é obrigatório.'
        if not responsible_name:
            errors['responsible_name'] = 'Nome do responsável é obrigatório.'
        if len(cpf_responsible) != 11:
            errors['cpf_responsible'] = 'CPF deve conter 11 dígitos.'
        if password != password_confirm:
            errors['password_confirm'] = 'As senhas não coincidem.'
        else:
            try:
                validate_password(password)
            except ValidationError as e:
                errors['password'] = ' '.join(e.messages)

        if errors:
            return render(request, 'register_details_company.html', {
                'hide_nav_links': True,
                'errors': errors,
                'form_data': request.POST,
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False,
        )

        CompanyProfile.objects.create(
            user=user,
            company_name=company_name,
            cnpj=cnpj,
            responsible_name=responsible_name,
            cpf_responsible=cpf_responsible,
            phone=phone,
            cep=cep,
            city=city,
            district=district,
            street=street,
        )

        token = EmailVerificationToken.generate_company_token(email)
        verify_url = request.build_absolute_uri(f'/verify/company/?token={token.token}')

        send_mail(
            subject='Verifique o e-mail da sua empresa no Scout',
            message=f'Clique no link abaixo para verificar seu e-mail e ativar sua conta:\n\n{verify_url}\n\nO link expira em 10 minutos.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        del request.session['registration_company_email']
        del request.session['registration_company_cnpj']

        return redirect('verify_email_company')

    return render(request, 'register_details_company.html', {'hide_nav_links': True})


def verify_email_company(request):
    token_value = request.GET.get('token', '')

    if not token_value:
        return render(request, 'verify_email_company.html', {'hide_nav_links': True})

    try:
        token = EmailVerificationToken.objects.get(
            token=token_value,
            user_type=EmailVerificationToken.USER_TYPE_COMPANY,
            is_used=False,
        )
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Link de verificação inválido ou já utilizado.')
        return render(request, 'verify_email_company.html', {'hide_nav_links': True})

    if token.is_expired():
        messages.error(request, 'Link expirado. Faça o cadastro novamente.')
        return render(request, 'verify_email_company.html', {'hide_nav_links': True})

    token.is_used = True
    token.save()

    user = User.objects.get(email=token.email)
    user.is_active = True
    user.save()

    login(request, user)
    return redirect('home_company')


# ---------------------------------------------------------------------------
# LOGIN / LOGOUT
# ---------------------------------------------------------------------------

def login_view(request):
    redir = _redirect_authenticated(request)
    if redir:
        return redir

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'E-mail ou senha incorretos.')
            return render(request, 'login.html', {'hide_nav_links': True})

        user = authenticate(request, username=user_obj.username, password=password)

        if user is None:
            messages.error(request, 'E-mail ou senha incorretos.')
            return render(request, 'login.html', {'hide_nav_links': True})

        if not user.is_active:
            messages.error(request, 'Conta não verificada. Verifique seu e-mail antes de entrar.')
            return render(request, 'login.html', {'hide_nav_links': True})

        login(request, user)

        if hasattr(user, 'candidate_profile'):
            return redirect('home_candidate')
        if hasattr(user, 'company_profile'):
            return redirect('home_company')

        return redirect('home')

    return render(request, 'login.html', {'hide_nav_links': True})


def logout_view(request):
    logout(request)
    return redirect('home')
