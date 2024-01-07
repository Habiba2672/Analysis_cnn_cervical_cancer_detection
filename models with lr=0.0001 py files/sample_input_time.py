import imports
import time

# Use a sample input for inference
sample_input = imports.torch.randn(1, 3, 125, 125).to(device)

# Measure inference time
model.eval()
with imports.torch.no_grad():
    start_time = time.time()
    _ = model(sample_input)
    inference_time = time.time() - start_time

print(f"Inference time for a sample input: {inference_time} seconds")
