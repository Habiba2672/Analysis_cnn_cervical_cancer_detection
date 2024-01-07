# Direct imports for additional metrics
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report
import imports


# Additional metrics
f1 = f1_score(test_labels, test_preds, average='weighted')
precision = precision_score(test_labels, test_preds, average='weighted')
recall = recall_score(test_labels, test_preds, average='weighted')

print(f"F1 Score: {f1:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")

# Classification report
class_report = classification_report(test_labels, test_preds, target_names=dataset.class_names)
print("Classification Report:\n", class_report)

# Save the model
save_model = input("Do you want to save the trained model? (yes/no): ").lower()
if save_model == "yes":
    model_save_path = "mobilenetv3_adam0.0001_small.pth"  # Adjust the filename as needed
    imports.torch.save(model.state_dict(), model_save_path)
    print("Model saved.")

# Save the model
save_model = input("Do you want to save the trained model? (yes/no): ").lower()
if save_model == "yes":
    model_save_path = "mobilenetv3_adam0.0001_small.pth"  # Adjust the filename as needed
    imports.torch.save(model.state_dict(), model_save_path)
    print("Model saved.")
