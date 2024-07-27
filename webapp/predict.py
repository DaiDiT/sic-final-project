import joblib

def predict_air_quality(temp, humid, co):
    model = joblib.load('D:/Projek/samsung-innovation-campus/sic-final-project/webapp/model_decision_tree.pkl')
    label_encoder = joblib.load('D:/Projek/samsung-innovation-campus/sic-final-project/webapp/label_encoder.pkl')
    
    prediction_encoded = model.predict([[temp, humid, co]])
    
    prediction = label_encoder.inverse_transform(prediction_encoded)

    return prediction[0]