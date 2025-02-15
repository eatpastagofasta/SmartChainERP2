# QR Detection Model Dataset

This repository contains datasets for training and evaluating a QR code detection model. The dataset is categorized into two main folders:

- **QR_Normal**: Contains standard QR code images.
- **QR_Anomaly**: Contains both normal and anomalous QR code images.

## Dataset Structure

### QR_Normal
```
QR_Normal/
├── train/
│   ├── images/       # Training images
│   ├── labels/       # Corresponding labels for training images
│
├── test/
│   ├── 2250 images   # Testing images for QR detection
│
├── validate/
    ├── images/       # Validation images
    ├── validate/     # Validation labels (if applicable)
```

### QR_Anomaly
```
QR_Anomaly/
├── train/
│   ├── normal/       # Normal QR images for training
│
├── test/
│   ├── anomaly/      # Anomalous QR images for testing
│   ├── normal/       # Normal QR images for testing
│
├── validate/
    ├── anomaly/      # Anomalous QR images for validation
    ├── normal/       # Normal QR images for validation
```

## Usage

1. **Training the Model**: Use images and labels from `QR_Normal/train` and `QR_Anomaly/train/normal`.
2. **Testing the Model**: Evaluate performance using `QR_Normal/test` and both `QR_Anomaly/test/normal` & `QR_Anomaly/test/anomaly`.
3. **Validation**: Use `QR_Normal/validate` and `QR_Anomaly/validate` for model tuning.

## Notes
- The dataset is structured to support both standard and anomaly detection models.
- Ensure labels are correctly mapped to their respective images in the training phase.
- Use the test and validation sets for assessing model performance and fine-tuning.

## License
This dataset is intended for research and educational purposes. Please cite the repository if used in any publication.

## Contact
For any issues or inquiries, please reach out via the repository's issue section.
