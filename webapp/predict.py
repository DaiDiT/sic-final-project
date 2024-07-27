import joblib
import os

def predict_air_quality(temp, humid, co):
    model = joblib.load(os.path.join(os.path.dirname(__file__),'model_decision_tree.pkl'))
    label_encoder = joblib.load(os.path.join(os.path.dirname(__file__),'label_encoder.pkl'))
    
    prediction_encoded = model.predict([[temp, humid, co]])
    
    prediction = label_encoder.inverse_transform(prediction_encoded)

    return prediction[0]