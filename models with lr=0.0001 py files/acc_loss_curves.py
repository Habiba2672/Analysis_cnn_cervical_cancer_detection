import imports
import matplotlib.pyplot as plt

# Plot training, validation, and test loss and accuracy curves
plt.figure(figsize=(8, 4))

# Plot training loss
plt.subplot(1, 2, 1)
plt.plot(train_losses, label='Training Loss')
plt.plot(validation_losses, label='Validation Loss')
plt.plot(len(train_losses) - 1, test_loss, marker='o', markersize=8, label='Test Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

# Plot training accuracy
plt.subplot(1, 2, 2)
plt.plot(train_accuracies, label='Training Accuracy')
plt.plot(validation_accuracies, label='Validation Accuracy')
plt.plot(len(train_accuracies) - 1, test_acc, marker='o', markersize=8, label='Test Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

plt.tight_layout()  # Adjust layout for better spacing
plt.show()
