# Model Overview
* Model Name: OceanCV YOLOv11 Plastic Object Detection Model
* Description:
  * Experiment with different augmentations and hyperparameters for object detection
  * Evaluate the model’s performance and visualize the results

The model was trained on 7 classes:
  * Bottle Cap:
  * Cone Cap:
  * Leaf:
  * Netting:
  * Plastic Bag:
  * Plastic Strand:
  * Sponge:

# Intended Use
* Primary Use Case: Object detection of plastic in water
* Specific Applications:
* Relevant Factors:

# Metrics 
* Overall mAP:
* Class-Specific mAP:
  * Bottle Cap:
  * Cone Cap:
  * Leaf:
  * Netting:
  * Plastic Bag:
  * Plastic Strand:
  * Sponge:

# Evaluation
* Dataset Details:
  * Number of Images:
  * Total annotations
* Training Configuration
  * Image Size:
  * Batch Size:
  * Optimizer: SGD (`lr=0.01`, `momentum=0.9`
  * Hardware: AMD 7700XT GPU using ROCm and WSL
* Augmentations:

# Recommendations
* Optimal Performance:
* Underrepresented Classes:
* Review Pipeline: Manual verification in workflows
* Downstream Tasks: (clustering, two-shot fine-tuning, in-depth analytics)
* Real-Time Inference: YOLO model

# Caveats and Limitations

# Bias, Risks, and Harms
* Potential Biases:
  * Imbalances class distribution may affect performance on underrepresented classes
* Mitigation Strategies:
  * Rebalance Train/Validation splits
  * Appropriate representative classes

# Environmental Impact
  * Compute Location:
  * Carbon Efficiency:
  * Hardware:
  * Compute Duration:
  * Total Emissions:

