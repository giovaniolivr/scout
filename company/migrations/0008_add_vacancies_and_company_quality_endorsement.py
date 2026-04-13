import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0010_add_company_rating_and_scout_score'),
        ('company', '0007_add_skill_endorsement'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='vacancies',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.CreateModel(
            name='CompanyQualityEndorsement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quality_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_quality_endorsements', to='candidates.candidateprofile')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quality_endorsements', to='company.companyprofile')),
                ('job_application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_quality_endorsements', to='candidates.jobapplication')),
            ],
            options={
                'unique_together': {('job_application', 'quality_name')},
            },
        ),
    ]
