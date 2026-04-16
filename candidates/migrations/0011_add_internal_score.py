from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0010_add_company_rating_and_scout_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='internal_score',
            field=models.IntegerField(default=0),
        ),
    ]
