# Generated by Django 3.0.6 on 2020-07-03 03:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('perfiles', '0001_initial'),
        ('libros', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportespoiler',
            name='reportador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='reporteofensivo',
            name='comentario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libros.Comentario'),
        ),
        migrations.AddField(
            model_name='reporteofensivo',
            name='reportador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='librosugerido',
            name='perfiles',
            field=models.ManyToManyField(to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='libroleido',
            name='cap',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='libros.Capitulo'),
        ),
        migrations.AddField(
            model_name='libroleido',
            name='libro',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='libros.Libro'),
        ),
        migrations.AddField(
            model_name='libroleido',
            name='perfil',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='perfiles.Perfil'),
        ),
        migrations.AddField(
            model_name='libro',
            name='autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='libros.Autor'),
        ),
        migrations.AddField(
            model_name='libro',
            name='editorial',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='libros.Editorial'),
        ),
    ]
