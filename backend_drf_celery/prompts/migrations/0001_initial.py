# Generated by Django 4.2.7 on 2025-06-20 09:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('system', 'system'), ('template', 'template'), ('tool', 'tool'), ('user', 'user')], max_length=32)),
                ('name', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('parameters', models.JSONField(blank=True, default=dict)),
                ('version', models.PositiveIntegerField(default=1, help_text='Current active version number')),
                ('tags', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPrompt',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('text', models.TextField()),
                ('lang', models.CharField(default='en', max_length=8)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prompts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PromptVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version', models.PositiveIntegerField()),
                ('text', models.TextField()),
                ('parameters', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('prompt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='prompts.prompt')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='prompt',
            index=models.Index(fields=['type', 'name'], name='prompts_pro_type_c55aaf_idx'),
        ),
        migrations.AddIndex(
            model_name='prompt',
            index=models.Index(fields=['tags'], name='prompt_tags_gin'),
        ),
        migrations.AddIndex(
            model_name='userprompt',
            index=models.Index(fields=['lang'], name='prompts_use_lang_bb6cc8_idx'),
        ),
        migrations.AddIndex(
            model_name='userprompt',
            index=models.Index(fields=['created_at'], name='prompts_use_created_3f575d_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='promptversion',
            unique_together={('prompt', 'version')},
        ),
    ]
