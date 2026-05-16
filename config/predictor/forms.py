from django import forms

class HousePriceForm(forms.Form):
    district_name = forms.CharField(label='İlçe (Örn: Buca)', max_length=100)
    neighborhood_name = forms.CharField(label='Mahalle (Örn: Adatepe)', max_length=100)
    gross_sqm = forms.FloatField(label='Brüt Metrekare')
    net_sqm = forms.FloatField(label='Net Metrekare') 
    building_age_num = forms.IntegerField(label='Bina Yaşı (Sıfır ise 0)')
    total_rooms = forms.IntegerField(label='Toplam Oda Sayısı (Örn: 3+1 için 4)')
    floor_level_num = forms.IntegerField(label='Bulunduğu Kat (-1, 1, 4 vb.)')

    IS_FURNISHED_CHOICES = [
        ('Eşyalı', 'Eşyalı'),
        ('Eşyalı Değil', 'Eşyalı Değil')
    ]
    is_furnished = forms.ChoiceField(label="Eşya Durumu", choices=IS_FURNISHED_CHOICES)

    HEATING_CHOICES = [
        ('Kombi', 'Kombi'),
        ('Merkezi', 'Merkezi'),
        ('Diğer', 'Diğer')
    ]
    heating_type = forms.ChoiceField(label='Isıtma Tipi', choices=HEATING_CHOICES)