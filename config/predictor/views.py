from django.shortcuts import render
import pandas as pd
import numpy as np
from django.apps import apps
from django.shortcuts import render
from .forms import HousePriceForm

def predict_price_view(request):
    prediction_formatted = None    
    ai_comment = None

    if request.method == 'POST':
        form = HousePriceForm(request.POST)
        if form.is_valid():
            input_data = form.cleaned_data

            df = pd.DataFrame([input_data])

            predictor_app = apps.get_app_config('predictor')
            model = predictor_app.ml_model

            if model:
                pred_log = model.predict(df)[0]
                pred_value = np.expm1(pred_log)

                prediction_formatted = "{:,.0f}".format(pred_value).replace(',', '.')

                district = input_data.get("district_name")
                m2 = input_data.get("net_sqm")
                room = input_data.get("room_count")

                ai_comment = (
                    f"Modelin analizine göre; evin {district} ilçesinde bulunması ve "
                    f"{m2} m² net kullanım alanına sahip olması bu değerlemenin "
                    f"belirlenmesindeki en büyük etkenler olmuştur."
                )

    else:
        form = HousePriceForm()

    context = {
        'form' : form,
        'prediction' : prediction_formatted,
        'ai_comment' : ai_comment
    }

    return render(request, 'predictor/index.html', context)