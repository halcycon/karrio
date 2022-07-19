# Generated by Django 3.2.13 on 2022-07-05 20:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import functools
import karrio.server.core.models.base
import karrio.server.core.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orgs', '0007_auto_20220628_0044'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchOperation',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(default=functools.partial(karrio.server.core.models.base.uuid, *(), **{'prefix': 'batch_'}), editable=False, max_length=50, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('queued', 'queued'), ('running', 'running'), ('completed', 'completed'), ('failed', 'failed')], default='queued', max_length=25)),
                ('resource_type', models.CharField(choices=[('order', 'order'), ('shipment', 'shipment'), ('tracking', 'tracking'), ('billing', 'billing')], default='order', max_length=25)),
                ('resources', models.JSONField(blank=True, default=functools.partial(karrio.server.core.utils.identity, *(), **{'value': []}), null=True)),
                ('test_mode', models.BooleanField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Batch Operation',
                'verbose_name_plural': 'Batch Operations',
                'db_table': 'batch-operation',
                'ordering': ['-created_at'],
            },
            bases=(karrio.server.core.models.base.ControlledAccessModel, models.Model),
        ),
        migrations.CreateModel(
            name='DataTemplate',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(default=functools.partial(karrio.server.core.models.base.uuid, *(), **{'prefix': 'data_'}), editable=False, max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=25, validators=[django.core.validators.RegexValidator('^[a-z0-9_]+$')])),
                ('description', models.CharField(blank=True, max_length=50, null=True)),
                ('resource_type', models.CharField(choices=[('order', 'order'), ('shipment', 'shipment'), ('tracking', 'tracking'), ('billing', 'billing')], max_length=25)),
                ('fields_mapping', models.JSONField(default=functools.partial(karrio.server.core.utils.identity, *(), **{'value': {}}), help_text="\n        The fields is a mapping of key value pairs linking the resource type's\n        data field (key) to header used for import/export.\n\n        e.g: resource: tracking | fields [{'id': 'ID', 'tracking_number': 'Tracking Number'}]\n        ")),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Data Template',
                'verbose_name_plural': 'Data Templates',
                'db_table': 'data-template',
                'ordering': ['-created_at'],
            },
            bases=(karrio.server.core.models.base.ControlledAccessModel, models.Model),
        ),
        migrations.CreateModel(
            name='DataTemplateLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='link', to='data.datatemplate')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_template_links', to='orgs.organization')),
            ],
        ),
        migrations.AddField(
            model_name='datatemplate',
            name='org',
            field=models.ManyToManyField(related_name='data_templates', through='data.DataTemplateLink', to='orgs.Organization'),
        ),
        migrations.CreateModel(
            name='BatchOperationLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='link', to='data.batchoperation')),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='batch_operation_links', to='orgs.organization')),
            ],
        ),
        migrations.AddField(
            model_name='batchoperation',
            name='org',
            field=models.ManyToManyField(related_name='batch_operations', through='data.BatchOperationLink', to='orgs.Organization'),
        ),
    ]
