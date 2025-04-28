# iris_gradio.py

import gradio as gr
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

# ─── 1) Train a simple model ─────────────────────────────────────────────────
iris = load_iris(as_frame=True)
X = iris.data
y = iris.target

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# ─── 2) Prediction function ──────────────────────────────────────────────────
def predict_iris(sepal_length, sepal_width, petal_length, petal_width):
    features = pd.DataFrame([[sepal_length, sepal_width, petal_length, petal_width]],
                            columns=iris.feature_names)
    pred_idx = model.predict(features)[0]
    proba   = model.predict_proba(features)[0]
    return {
        iris.target_names[i]: float(f"{proba[i]:.3f}") 
        for i in range(len(iris.target_names))
    }

# ─── 3) Build the Gradio interface ────────────────────────────────────────────
iface = gr.Interface(
    fn=predict_iris,
    inputs=[
        gr.Number(label="Sepal length (cm)", value=5.1, precision=1),
        gr.Number(label="Sepal width  (cm)", value=3.5, precision=1),
        gr.Number(label="Petal length (cm)", value=1.4, precision=1),
        gr.Number(label="Petal width  (cm)", value=0.2, precision=1),
    ],
    outputs=gr.Label(num_top_classes=3),
    title="Iris Flower Species Classifier",
    description="Enter measurements of an Iris flower to get a predicted species and probabilities."
)

if __name__ == "__main__":
    iface.launch(share=True)
