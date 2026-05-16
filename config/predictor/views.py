from django.shortcuts import render
import pandas as pd
from django.apps import apps
from django.shortcuts import render
from .forms import HousePriceForm

def predict_price_view(request):
    prediction = None

    if request.method == 'POST':
        form = HousePriceForm(request.POST)
        if form.is_valid():
            input_data = form.cleaned_data

            df = pd.DataFrame([input_data])

            predictor_app = apps.get_app_config('predictor')
            model = predictor_app.ml_model

            if model:
                pred_value = model.predict(df)[0]
                prediction = round(pred_value, 2)
    else:
        form = HousePriceForm()

    return render(request, 'predictor/index.html', {'form': form, 'prediction' : prediction})