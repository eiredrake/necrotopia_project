# Generated by Django 4.2.1 on 2023-06-08 16:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import necrotopia.models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('necrotopia', '0003_rule_rulepicture_rule_pictures_rule_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleAssembly',
            fields=[
                ('line_id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('expiration_units', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('time_units', models.IntegerField(choices=[(0, 'No_Expiration'), (1, 'end_of_event'), (2, 'hours'), (3, 'days'), (4, 'months'), (5, 'years')], default=necrotopia.models.TimeUnits['No_Expiration'])),
                ('item_type', models.IntegerField(choices=[(0, 'Scrap'), (1, 'Herb'), (2, 'Weapon'), (3, 'Gizmo'), (4, 'Produce'), (5, 'Brew'), (6, 'Meal'), (7, 'Injectable'), (8, 'Armor'), (9, 'Vehicle'), (10, 'Room_Augment'), (11, 'Weapon_Augment'), (12, 'Armor_Augment'), (13, 'Vehicle_Augment'), (14, 'Trap'), (15, 'Shield_Augment'), (16, 'Ranged_Exotic'), (17, 'Melee_Exotic')], default=necrotopia.models.ComponentType['Gizmo'])),
                ('achievement_mechanics', models.CharField(blank=True, max_length=1000, null=True)),
                ('print_duplication', models.CharField(blank=True, max_length=1000, null=True)),
                ('details', models.CharField(blank=True, max_length=1000, null=True)),
                ('registration_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='registration_date')),
                ('last_update_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last_update_date')),
                ('crafting_tree', models.CharField(blank=True, default='Artisan', max_length=100, null=True)),
                ('crafting_area', models.CharField(blank=True, default='Mechanical Crafting Zone', max_length=100, null=True)),
                ('usage_tree', models.CharField(blank=True, default='n/a', max_length=100, null=True)),
                ('update_required', models.BooleanField(blank=True, default=False, null=True)),
                ('visual_description', models.CharField(blank=True, max_length=1000, null=True)),
                ('season', models.CharField(blank=True, max_length=50, null=True)),
                ('active', models.BooleanField(default=True)),
                ('checked', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
            },
        ),
        migrations.CreateModel(
            name='ModuleGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.IntegerField(choices=[(0, 'Ungraded'), (1, 'Basic'), (2, 'Proficient'), (3, 'Master')], default=necrotopia.models.Grade['Basic'])),
                ('name', models.CharField(max_length=255)),
                ('mind', models.IntegerField(blank=True, default=5, null=True)),
                ('time', models.IntegerField(blank=True, default=20, null=True)),
                ('mechanics', models.CharField(blank=True, max_length=1000, null=True)),
                ('module_assembly', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moduleAssembly_parent', to='necrotopia.moduleassembly')),
            ],
            options={
                'verbose_name': 'Item Grade',
                'verbose_name_plural': 'Item Grades',
            },
        ),
        migrations.CreateModel(
            name='ModuleGradeSubAssembly',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('grade', models.IntegerField(choices=[(0, 'Ungraded'), (1, 'Basic'), (2, 'Proficient'), (3, 'Master')], default=necrotopia.models.Grade['Ungraded'])),
                ('assembly', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_sub_assembly', to='necrotopia.moduleassembly')),
                ('parent_grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='necrotopia.modulegrade')),
            ],
            options={
                'verbose_name': 'Crafted Item',
                'verbose_name_plural': 'Crafted Items',
            },
        ),
        migrations.CreateModel(
            name='ModuleGradeResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1)),
                ('parent_grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='necrotopia.modulegrade')),
                ('resource', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_resource', to='necrotopia.resourceitem')),
            ],
            options={
                'verbose_name': 'Resource',
                'verbose_name_plural': 'Resources',
            },
        ),
        migrations.AddField(
            model_name='modulegrade',
            name='resources',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='necrotopia.modulegraderesource'),
        ),
        migrations.AddField(
            model_name='modulegrade',
            name='sub_assemblies',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='necrotopia.modulegradesubassembly'),
        ),
        migrations.AddField(
            model_name='moduleassembly',
            name='module_grades',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='moduleGrade_grades', to='necrotopia.modulegrade'),
        ),
        migrations.AddField(
            model_name='moduleassembly',
            name='registrar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='moduleassembly',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.CreateModel(
            name='ItemPicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(upload_to='static_images')),
                ('assembly_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picture_ModuleAssembly', to='necrotopia.moduleassembly')),
            ],
        ),
    ]
