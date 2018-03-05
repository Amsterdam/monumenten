import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dataset', '0003_geoview_monumenten'),
    ]

    operations = [
        migrations.CreateModel(
            name='PandRelatie',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('pand_id', models.CharField(max_length=16, null=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='monument',
            options={'ordering': ('external_id',)},
        ),
        migrations.AlterField(
            model_name='monument',
            name='complex',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='monumenten',
                to='dataset.Complex'),
        ),
        migrations.AlterField(
            model_name='situering',
            name='monument',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name='situeringen', to='dataset.Monument'),
        ),
        migrations.AddField(
            model_name='pandrelatie',
            name='monument',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='betreft_pand',
                to='dataset.Monument'),
        ),
        migrations.AlterUniqueTogether(
            name='pandrelatie',
            unique_together={('monument', 'pand_id')},
        ),
    ]
