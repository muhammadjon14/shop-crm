from django.db import migrations, models
import django.db.models.deletion


def create_default_types(apps, schema_editor):
    """Create default product types from the old TextChoices"""
    MahsulotTuri = apps.get_model('mahsulotlar', 'MahsulotTuri')
    
    default_types = [
        ('Elektronika', '💻'),
        ('Kiyim', '👕'),
        ('Oziq-ovqat', '🍎'),
        ('Mebel', '🪑'),
        ('Sport', '⚽'),
        ('Kitob', '📚'),
        ('Boshqa', '📦'),
    ]
    
    for nomi, icon in default_types:
        MahsulotTuri.objects.get_or_create(nomi=nomi, defaults={'icon': icon})


def migrate_product_types(apps, schema_editor):
    """Migrate old string-based types to new ForeignKey types"""
    Mahsulot = apps.get_model('mahsulotlar', 'Mahsulot')
    MahsulotTuri = apps.get_model('mahsulotlar', 'MahsulotTuri')
    
    # Mapping from old string values to new names
    type_mapping = {
        'elektronika': 'Elektronika',
        'kiyim': 'Kiyim',
        'oziq_ovqat': 'Oziq-ovqat',
        'mebel': 'Mebel',
        'sport': 'Sport',
        'kitob': 'Kitob',
        'boshqa': 'Boshqa',
    }
    
    for mahsulot in Mahsulot.objects.all():
        if mahsulot.turi_old:
            new_type_name = type_mapping.get(mahsulot.turi_old, 'Boshqa')
            try:
                turi_obj = MahsulotTuri.objects.get(nomi=new_type_name)
                mahsulot.turi = turi_obj
                mahsulot.save()
            except MahsulotTuri.DoesNotExist:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('mahsulotlar', '0003_alter_mahsulot_id'),
    ]

    operations = [
        # Step 1: Create the new MahsulotTuri model
        migrations.CreateModel(
            name='MahsulotTuri',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomi', models.CharField(max_length=100, unique=True, verbose_name='Tur nomi')),
                ('tavsif', models.TextField(blank=True, verbose_name='Tavsif')),
                ('icon', models.CharField(blank=True, default='📦', max_length=10, verbose_name='Emoji/Icon')),
                ('yaratilgan_vaqt', models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan vaqt')),
            ],
            options={
                'verbose_name': 'Mahsulot turi',
                'verbose_name_plural': 'Mahsulot turlari',
                'ordering': ['nomi'],
            },
        ),
        
        # Step 2: Create default product types
        migrations.RunPython(create_default_types, migrations.RunPython.noop),
        
        # Step 3: Rename old turi field to turi_old
        migrations.RenameField(
            model_name='mahsulot',
            old_name='turi',
            new_name='turi_old',
        ),
        
        # Step 4: Add new turi ForeignKey field
        migrations.AddField(
            model_name='mahsulot',
            name='turi',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='mahsulotlar',
                to='mahsulotlar.mahsulotturi',
                verbose_name='Mahsulot turi'
            ),
        ),
        
        # Step 5: Migrate data from old field to new field
        migrations.RunPython(migrate_product_types, migrations.RunPython.noop),
        
        # Step 6: Remove old field
        migrations.RemoveField(
            model_name='mahsulot',
            name='turi_old',
        ),
    ]
