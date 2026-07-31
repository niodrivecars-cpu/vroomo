import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fleet', '0006_set_default_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.company', verbose_name='الشركة', editable=False),
        ),
        migrations.AlterField(
            model_name='driver',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.company', verbose_name='الشركة', editable=False),
        ),
        migrations.AlterField(
            model_name='maintenance',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.company', verbose_name='الشركة', editable=False),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.company', verbose_name='الشركة', editable=False),
        ),
        migrations.AlterField(
            model_name='vehicledocument',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.company', verbose_name='الشركة', editable=False),
        ),
        migrations.AlterField(
            model_name='violation',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fleet.company', verbose_name='الشركة', editable=False),
        ),
    ]
