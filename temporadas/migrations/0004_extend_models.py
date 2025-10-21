from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('temporadas', '0003_temporada_email_enviado'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoValores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('conselheiro_senior', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('conselheiro', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('monitor', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('monitor_junior', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('estagiario', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('day_camp', models.DecimalField(decimal_places=2, default=0, help_text='Valor usado para tipo Day Use', max_digits=8)),
                ('enfermeira', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('enfermeira_estagiaria', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('fotografo_1', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('fotografo_2', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
            ],
            options={
                'verbose_name': 'Configuração de Valores',
                'verbose_name_plural': 'Configurações de Valores',
            },
        ),
        migrations.CreateModel(
            name='AjudaCustoClasse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
            options={
                'verbose_name': 'Classe de Ajuda de Custo',
                'verbose_name_plural': 'Classes de Ajuda de Custo',
            },
        ),
        migrations.AlterField(
            model_name='temporada',
            name='tipo',
            field=models.CharField(choices=[('escola', 'Escola'), ('dayuse', 'Day Use'), ('familia', 'Família'), ('ferias', 'Férias'), ('evento', 'Evento Especial')], max_length=20),
        ),
        migrations.AddField(
            model_name='temporada',
            name='hora_chegada_equipe',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='temporada',
            name='hora_saida_equipe',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='temporada',
            name='numero_diarias',
            field=models.DecimalField(decimal_places=1, default=1, max_digits=4),
        ),
        migrations.CreateModel(
            name='TemporadaEquipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('confirmado', 'Confirmado'), ('concluido', 'Concluído')], default='pendente', max_length=20)),
                ('recebe_ajuda_custo', models.BooleanField(default=False)),
                ('recebe_embarque', models.BooleanField(default=False)),
                ('valor_embarque_especial', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('recebe_desembarque', models.BooleanField(default=False)),
                ('valor_desembarque_especial', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('ajuda_custo_classe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='temporadas.ajudacustoclasse')),
                ('monitor', models.ForeignKey(limit_choices_to={'user_type': 'monitor'}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('temporada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='temporadas.temporada')),
            ],
            options={
                'unique_together': {('temporada', 'monitor')},
            },
        ),
    ]

