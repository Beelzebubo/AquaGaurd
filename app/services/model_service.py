import torch
import torch.nn as nn
from pathlib import Path

# neural network architecture for flood risk prediction define gainxa
#nn.Module is the base clss used for all neural network modules in PyTorch.
#kina use garne bhanda chai nn.Module lai inherit garea custom neural network banauna sakinxa
#hamle flood prediction ko lagi 3 layer ko neural network define gareko xam jasko lagi custom neural network chainxa ani tei karan nn.Module lai priority deko.
# also yesle garda Floodmodel le training capabilities, weight management, GPU support jasto features inherit garxa ani training is easierand more efficient.
class FloodModel(nn.Module):
# __init__ le chai neural network architecture lai initialize garxa and layers define ni garxa.
# super().__init__() le parent class nn.Modulelai initialize garxa.
    def __init__(self):
        super().__init__()

        ## hidden layer 1 with 4 types if input features and 64 neurons
        self.hidden1 = nn.Linear(4, 64)
        # hidden layer 2 with 64 input and 64 neurons
        self.hidden2 = nn.Linear(64, 64)
        # output layer with 64 neurons and 1 output (flood risk score) basically flood risk ko prediction garxa ani score dinxa 0 - low risk and 1 - high risk
        self.output = nn.Linear(64, 1)
# forward method le input data lai layers bata pass garxa and output generate garxa.
#basically the neural network ko definition ho ani forword method le data lai layers bata pass garxa and output generate garxa
    def forward(self, x):
        # data lai hidden layer 1 bata pass garxa ani ReLU activation function apply garxa
        x = torch.relu(self.hidden1(x))
        # data lai hidden layer 2 bata pass garxa ani ReLU activation function apply garxa
        x = torch.relu(self.hidden2(x))
        # data lai output layer bata pass garxa ani final flood risk score generate garxa
        x = self.output(x)

        return x
# FloodModel class ko object create garxa ani trained model ko weight load garera evaluation mode ma rakxa
# Evaluation mode ma rake inference yani prediction garna ready hunxa.

model = FloodModel()

BASE_DIR = Path(__file__).resolve().parent.parent
# Trained model ko file ka xa bhanera path define garxa. Models folder vitra flood_model.pth file xa jasma trained model ko weights stored xa.
# torch.load() le .pth file ma stored weights load garxa ani model.load_state_dict() le loaded weights lai model ma set garxa
MODEL_PATH = BASE_DIR / "models" / "flood_prediction_weights.pth"

model.load_state_dict(
    torch.load(MODEL_PATH)
)
# model lai evaluation mode ma rakxa.
model.eval()

# prediction Function garxa jasma input features lai tensor ma convert garera model bata prediction generate garexi float ma value return hunxa
# dtype=float32 only works with tensors.
def predict_risk(features):

    tensor = torch.tensor(
        features,
        dtype=torch.float32
    )
#torch.no_grad() improves perforamance by disabling gradient calculations and lowering memory usage
# also inference becomes faster cause of these reasons.
    with torch.no_grad():
        prediction = model(tensor)
# tensor to float conversion garxa ani prediction value return garxa
    return float(prediction.item())