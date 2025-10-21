from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Temporada, InteresseTemporada
from .forms import TemporadaForm
from django.core import mail


class TemporadaFormTests(TestCase):
    def test_numero_diarias_aceita_virgula(self):
        form = TemporadaForm(data={
            'data_inicio': '2025-01-01',
            'data_fim': '2025-01-03',
            'tipo': 'ferias',
            'numero_diarias': '2,5',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(str(form.cleaned_data['numero_diarias']), '2.5')

    def test_dayuse_forca_uma_diaria(self):
        form = TemporadaForm(data={
            'data_inicio': '2025-01-01',
            'data_fim': '2025-01-01',
            'tipo': 'dayuse',
            'numero_diarias': '0,5',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(str(form.cleaned_data['numero_diarias']), '1')


class MonitorDashboardCountsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.monitor = User.objects.create_user(username='m1', password='x', user_type='monitor', is_approved=True)
        self.gestor = User.objects.create_user(username='g1', password='x', user_type='gestor')

    def test_temporadas_disponiveis_contador_bate_listagem(self):
        hoje = timezone.now().date()
        t1 = Temporada.objects.create(nome='T1', data_inicio=hoje, data_fim=hoje, tipo='ferias')
        t2 = Temporada.objects.create(nome='T2', data_inicio=hoje, data_fim=hoje, tipo='dayuse')
        # monitor demonstrou interesse em t2, deve sair da lista
        InteresseTemporada.objects.create(monitor=self.monitor, temporada=t2, status='interessado')

        self.client.login(username='m1', password='x')
        resp_list = self.client.get(reverse('listar_temporadas_monitor'))
        temporadas_listadas = list(resp_list.context['temporadas'])

        resp_home = self.client.get(reverse('home'))
        self.assertEqual(resp_home.context['temporadas_disponiveis'], len(temporadas_listadas))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EnvioEmailsFeedbackTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.gestor = User.objects.create_user(username='g', password='x', user_type='gestor')
        self.monitor = User.objects.create_user(username='m', password='x', user_type='monitor', email='m@x.com', is_approved=True)

    def test_envio_emails_mostra_feedback(self):
        t = Temporada.objects.create(nome='T', data_inicio='2025-01-01', data_fim='2025-01-02', tipo='ferias', email_enviado=False)
        self.client.login(username='g', password='x')
        resp = self.client.post(reverse('enviar_emails_temporadas'), {'temporadas': [t.id]})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(mail.outbox)
