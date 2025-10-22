from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('temporadas', '0004_extend_models'),
        ('core', '0004_cpf_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='ajuda_custo_classe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='temporadas.ajudacustoclasse', verbose_name='Classe de Ajuda de Custo'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='categoria',
            field=models.CharField(blank=True, choices=[('conselheiro_senior', 'Conselheiro Senior'), ('conselheiro', 'Conselheiro'), ('monitor', 'Monitor'), ('monitor_junior', 'Monitor Junior'), ('estagiario', 'Estagiário'), ('enfermeira', 'Enfermeira'), ('enfermeira_estagiaria', 'Enfermeira Estagiária'), ('fotografo_1', 'Fotógrafo 1'), ('fotografo_2', 'Fotógrafo 2')], max_length=30, null=True, verbose_name='Categoria/Função'),
        ),
    ]

