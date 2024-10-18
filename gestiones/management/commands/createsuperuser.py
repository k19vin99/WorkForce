from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperUserCommand
from django.core.management import CommandError
from gestiones.models import Empresa

class Command(CreateSuperUserCommand):
    def handle(self, *args, **options):
        empresa_id = input('Empresa ID: ')
        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            raise CommandError(f'Empresa con ID {empresa_id} no existe.')
        
        options['empresa'] = empresa
        super().handle(*args, **options)

    def get_input_data(self, data):
        empresa_id = input('Empresa ID: ')
        data['empresa'] = empresa_id
        return data
