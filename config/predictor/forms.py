from django import forms

class HousePriceForm(forms.Form):
    district_name = forms.CharField(label="İlçe", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Kadıköy'}))
    neighborhood_name = forms.CharField(label="Mahalle", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Örn: Moda'}))
    net_sqm = forms.FloatField(label="Net Metrekare", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 120'}))
    gross_sqm = forms.FloatField(label="Brüt Metrekare", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 140'}))
    total_rooms = forms.IntegerField(label="Oda Sayısı", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 4'}))
    building_age_num = forms.IntegerField(label="Bina Yaşı", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 5'}))
    floor_level_num = forms.IntegerField(label="Bulunduğu Kat", widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Örn: 3'}))
    
    HEATING_CHOICES = [
        ('Kombi', 'Kombi'), 
        ('Merkezi', 'Merkezi'), 
        ('Yerden Isıtma', 'Yerden Isıtma'), 
        ('Diğer', 'Diğer')
    ]
    heating_type = forms.ChoiceField(choices=HEATING_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    FURNISHED_CHOICES = [
        ('Eşyalı', 'Eşyalı'), 
        ('Eşyalı Değil', 'Eşyalı Değil')
    ]
    is_furnished = forms.ChoiceField(choices=FURNISHED_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))