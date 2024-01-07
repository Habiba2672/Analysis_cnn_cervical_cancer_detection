# -*- coding: utf-8 -*-
"""mobilnet_sgd_aug_splitting .ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/112WHF1DvTbUhjxishSMGuxlXa8Hsrr1L
"""

!cp /content/drive/MyDrive/sipakmed/modular/libraries.py /content
import libraries

!pip install torchviz
!pip install torchsummary
!apt-get install graphviz -y
!pip install graphviz
!pip install Pillow
from torchviz import make_dot

# Define the data path
DATA_PATH = '/content/drive/MyDrive/sipakmed/sipakmed/'

# Import the module
!cp /content/drive/MyDrive/sipakmed/modular/dataset_management.py /content

import dataset_management

"""i used this to make sure there isn't duplicated data and data for training was succesful and splitting dataset

i used this to check now how many files i have knowing that my data for sipakmed originally were 4049 bmb files
"""

# Get a list of all image file paths
file_paths = []
categories = []

for root, dirs, files in libraries.os.walk(DATA_PATH):
    for file in files:
        if file.endswith('.bmp'):
            file_path = libraries.os.path.join(root, file)
            file_paths.append(file_path)
            if 'normal' in file_path:
                categories.append(0)
            else:
                categories.append(1)

import libraries
df = libraries.pd.DataFrame({'filename (X)': file_paths, 'category (Y)': categories})
df

import os
import shutil
import random
# Specify the path to your dataset on Google Drive
drive_path = '/content/drive/MyDrive/sipakmed/sipakmed/'

# Define the output directory for your divided dataset on Google Drive
output_dir = '/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training'

"""to check if my data are balanced regarding the training ones or not"""

import sys
sys.path.append('/content/drive/My Drive/sipakmed/modular')

import check_balanced_data
check_balanced_data.check_balanced_data()

"""data balance in normal and atypical"""

# Function to balance data by randomly undersampling the majority class
def balance_data(train_files):
    normal_files = [file for file in train_files if 'normal' in file]
    atypical_files = [file for file in train_files if 'atypical' in file]

    min_samples = min(len(normal_files), len(atypical_files))

    balanced_data = random.sample(normal_files, min_samples) + random.sample(atypical_files, min_samples)
    return balanced_data

def check_balance(data):
    normal_count = sum(1 for file in data if 'normal' in file)
    atypical_count = sum(1 for file in data if 'atypical' in file)

    return normal_count, atypical_count

# Call the balance_data function to get the balanced dataset
balanced_train_data = balance_data(train_files)

# Check the balance
normal_count, atypical_count = check_balance(balanced_train_data)
print(f"Normal samples: {normal_count}, Atypical samples: {atypical_count}")

if normal_count == atypical_count:
    print("The data is balanced.")
else:
    print("The data is not balanced.")

"""Data preprocessing and loading using torchvision

load images and their labels from the balanced_dataset:
"""

!cp /content/drive/MyDrive/sipakmed/modular/data_loading.py /content
import data_loading

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import torch.nn.functional as F
import os
from torchvision.models import mobilenet_v3_small
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import time

# Model
class MobileNetV3Small(nn.Module):
    def __init__(self, num_classes=2):
        super(MobileNetV3Small, self).__init__()
        self.model = mobilenet_v3_small(pretrained=True)
        in_features = self.model.classifier[3].in_features
        self.model.classifier[3] = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.model(x)

# Dataset
class PTImageDataset(Dataset):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.files = self.get_files(data_dir)
        self.num_classes = 2  # Assuming you have 2 classes
        self.class_names = ["normal", "abnormal"]

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        img_path = self.files[idx]
        img_tensor = torch.load(img_path)

        # Extract label from the file path or filename
        label = self.extract_label(img_path)

        return img_tensor, label

    def extract_label(self, file_path):
        # Modify this logic based on your actual file naming or directory structure
        parts = file_path.split(os.path.sep)
        class_name = parts[-2]
        return 0 if class_name == "normal" else 1  # Adjust based on your class names

    def get_files(self, data_dir):
        all_files = []
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                if file.endswith(".pt"):
                    all_files.append(os.path.join(root, file))
        return all_files

# Training function
def train(model, train_loader, criterion, optimizer):
    model.train()
    epoch_loss = 0
    epoch_acc = 0

    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item() * inputs.size(0)
        _, predicted = torch.max(outputs.data, 1)
        total = labels.size(0)
        correct = (predicted == labels).sum().item()
        epoch_acc += correct / total

    epoch_loss /= len(train_loader.dataset)
    epoch_acc /= len(train_loader.dataset)

    return epoch_loss, epoch_acc

# Placeholder for the test function
def test(model, test_loader, criterion):
    model.eval()
    epoch_loss = 0
    epoch_acc = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)

            epoch_loss += criterion(outputs, labels).item() * inputs.size(0)
            _, predicted = torch.max(outputs.data, 1)
            total = labels.size(0)
            correct = (predicted == labels).sum().item()
            epoch_acc += correct

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    epoch_loss /= len(test_loader.dataset)
    epoch_acc /= len(test_loader.dataset)

    return epoch_loss, epoch_acc, all_preds, all_labels

# Dataset and dataloaders
PREPROCESSED_PATH = "/content/drive/MyDrive/sipakmed/sipakmed/sipakmed_training/preprocessed_classified/"
dataset = PTImageDataset(PREPROCESSED_PATH)
total_size = len(dataset)
train_size = int(0.6 * total_size)
val_size = int(0.2 * total_size)
test_size = total_size - train_size - val_size

train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import torch.nn.functional as F
import os
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
from sklearn.metrics import f1_score, precision_score, recall_score

from torchvision.models import mobilenet_v3_small

# Model, optimizer, loss
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MobileNetV3Small().to(device)
optimizer = optim.SGD(model.parameters(), lr=0.0001, momentum=0.9)
criterion = nn.CrossEntropyLoss()

# Check if a pre-trained model should be loaded
load_pretrained = input("Do you want to load a pre-trained model? (yes/no): ").lower()

if load_pretrained == "yes":
    # Check if a previously saved model exists
    saved_model_path = "mobilenetv3_small.pth"  # Adjust the filename as needed
    if os.path.exists(saved_model_path):
        model = MobileNetV3Small().to(device)
        model.load_state_dict(torch.load(saved_model_path))
        print("Pre-trained model loaded.")
    else:
        print(f"No pre-trained model found at {saved_model_path}. Training a new model.")
        load_pretrained = "no"

if load_pretrained != "yes":
    # Training loop
    train_losses = []
train_accuracies = []
validation_losses = []
validation_accuracies = []
patience = 5
best_val_loss = float('inf')
epochs_no_improve = 0
for epoch in range(50):
    train_loss, train_acc = train(model, train_loader, criterion, optimizer)
    val_loss, val_acc, _, _ = test(model, val_loader, criterion)
    print(f"Epoch {epoch + 1} - "
          f"Train Loss: {train_loss:.4f} Train Acc: {train_acc:.4f} "
          f"Validation Loss: {val_loss:.4f} Validation Acc: {val_acc:.4f}")
    train_losses.append(train_loss)
    train_accuracies.append(train_acc)
    validation_losses.append(val_loss)
    validation_accuracies.append(val_acc)
    # Early stopping
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        epochs_no_improve = 0
    else:
        epochs_no_improve += 1
    if epochs_no_improve == patience:
        print("Early stopping!")
        break
# Testing
test_loss, test_acc, test_preds, test_labels = test(model, test_loader, criterion)
print(f"Final Test Loss: {test_loss:.4f} Test Acc: {test_acc:.4f}")

!cp /content/drive/MyDrive/sipakmed/modular/acc_loss_curves.py /content
import acc_loss_curves

!cp /content/drive/MyDrive/sipakmed/modular/confusion_matrix.py /content
import confusion_matrix

!cp /content/drive/MyDrive/sipakmed/modular/evaluation_metrics.py /content
import evaluation_metrics

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

num_params = count_parameters(model)
print(f"Number of trainable parameters in the model: {num_params}")

!cp /content/drive/MyDrive/sipakmed/modular/sample_input_time.py /content
import sample_input_time

from torchsummary import summary

# Instantiate the model
model = mobilenet_v3_small()

# Define a function to print a concise summary
def concise_summary(model, input_size):
    summary(model, input_size, device="cuda" if torch.cuda.is_available() else "cpu")

# Print the concise summary
input_size = (3, 125, 125)
concise_summary(model, input_size)