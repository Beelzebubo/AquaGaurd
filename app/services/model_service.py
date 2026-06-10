import numpy as np
import torch
import torch.nn as nn
from pathlib import Path
from sklearn.preprocessing import StandardScaler


class FloodModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear1 = nn.Linear(4, 64)
        self.hidden = nn.Linear(64, 64)
        self.relu = nn.ReLU()
        self.linear2 = nn.Linear(64, 1)

    def forward(self, x):
        x = self.relu(self.linear1(x))
        x = self.relu(self.hidden(x))
        x = self.linear2(x)
        return x


model = FloodModel()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "flood_prediction_weights.pth"

model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# Scaler statistics from the training data (Melamchi river):
#   Waterflow (river_flow):   mean=0.556,  std=2.524
#   Temperature:              mean=9.063,  std=5.265
#   Rainfall:                 mean=2.029,  std=4.732
#   Relative_Humidity:        mean=62.635, std=22.585
scaler = StandardScaler()
scaler.mean_ = np.array([0.556, 9.063, 2.029, 62.635])
scaler.scale_ = np.array([2.524, 5.265, 4.732, 22.585])
scaler.n_features_in_ = 4


def predict_risk(features):
    # Model was trained on [Waterflow, Temperature, Rainfall, Relative_Humidity]
    # Input dict keys:  temperature, rainfall, humidity, river_flow
    raw = [[
        features[0][3],  # river_flow  -> Waterflow
        features[0][0],  # temperature -> Temperature
        features[0][1],  # rainfall    -> Rainfall
        features[0][2],  # humidity    -> Relative_Humidity
    ]]
    scaled = scaler.transform(np.array(raw))
    tensor = torch.tensor(scaled, dtype=torch.float32)
    with torch.no_grad():
        logits = model(tensor)
        prob = torch.sigmoid(logits)
    return float(prob.item())