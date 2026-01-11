# 🔬 Comet ML Integration Guide

Complete guide to using Comet ML for tracking your model training.

## What is Comet ML?

Comet ML is an experiment tracking platform that helps you:
- Track training metrics in real-time (loss, mAP, precision, recall)
- Visualize validation predictions on images
- Compare different training runs
- Share results with your team
- Never lose track of what worked and what didn't

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `comet-ml` along with other dependencies.

### 2. Get Your API Key

1. Go to [comet.com](https://www.comet.com/) and sign in
2. Navigate to your account settings: https://www.comet.com/api/my/settings/
3. Copy your API key (looks like: `abc123def456...`)

### 3. Set Environment Variable

**Option A: Temporary (current terminal session only)**
```bash
export COMET_API_KEY='your-api-key-here'
```

**Option B: Permanent (add to your shell profile)**
```bash
# For zsh (default on macOS)
echo "export COMET_API_KEY='your-api-key-here'" >> ~/.zshrc
source ~/.zshrc

# For bash
echo "export COMET_API_KEY='your-api-key-here'" >> ~/.bashrc
source ~/.bashrc
```

**Option C: Using .env file**
```bash
# Create .env file in project root
echo "COMET_API_KEY=your-api-key-here" > .env
echo "COMET_PROJECT_NAME=miso-ozzy-detector" >> .env
echo "COMET_WORKSPACE=your-workspace-name" >> .env
```

### 4. Run Training with Comet ML

```bash
python scripts/train_with_comet.py
```

You'll see a message like:
```
🔬 Initializing Comet ML experiment...
✅ Comet ML enabled
📊 View live training at: https://www.comet.com/
```

### 5. View Results

1. Open https://www.comet.com/
2. Navigate to your project: `miso-ozzy-detector`
3. Click on your experiment to see:
   - **Charts**: Real-time training/validation loss, mAP, precision, recall
   - **Images**: Validation images with predicted bounding boxes
   - **System Metrics**: GPU/CPU usage, memory
   - **Hyperparameters**: All training settings
   - **Confusion Matrix**: How well the model distinguishes classes

## What Gets Logged

### Metrics (Every Epoch)
- **Training Loss**: Box loss, class loss, DFL loss
- **Validation Metrics**:
  - mAP50 (mean Average Precision at 50% IoU)
  - mAP50-95 (mAP across IoU thresholds)
  - Precision (how many detections were correct)
  - Recall (how many actual cats were found)
- **Per-Class Performance**: Metrics for background, miso, and ozzy

### Images
- **Validation Predictions**: Sample images with predicted bounding boxes
- **Training Batches**: Sample training images showing augmentations
- **Confusion Matrix**: Visual representation of classification accuracy
- **PR Curves**: Precision-Recall curves
- **F1 Score Curves**: F1 vs confidence threshold

### System Info
- Device (CPU/MPS/CUDA)
- Training time
- Model architecture
- Dataset statistics

## Configuration Options

Set these environment variables to customize:

```bash
# Required
export COMET_API_KEY='your-api-key'

# Optional
export COMET_PROJECT_NAME='miso-ozzy-detector'  # Default project name
export COMET_WORKSPACE='your-workspace'         # Your workspace (username or team)
export COMET_LOG_PREDICTIONS='true'             # Log validation images (default: true)
```

## Comparing Training Runs

After multiple training runs, you can:

1. Go to your Comet ML project
2. Select multiple experiments
3. Click "Compare"
4. View side-by-side comparisons of:
   - Training curves
   - Final metrics
   - Hyperparameters
   - Best epoch

## Troubleshooting

### "API key not found"
```bash
# Verify it's set
echo $COMET_API_KEY

# If empty, set it again
export COMET_API_KEY='your-api-key'
```

### "Cannot find project"
The project will be created automatically on first run. Make sure:
- Your API key is valid
- You have internet connection
- The project name doesn't have special characters

### Training works but nothing appears in Comet
- Check you're logged into the correct account
- Verify the workspace/project names match
- Look for error messages in the training output
- Check: https://www.comet.com/api/my/settings/ for API key status

### Want to disable Comet temporarily?
```bash
# Don't set COMET_API_KEY, or unset it
unset COMET_API_KEY

# Then run regular training
python scripts/train_cat_model.py
```

## Example: Viewing Your Results

After training completes, you'll see something like:

```
🎉 TRAINING COMPLETE!
✅ Model saved to: models/cat_detector.pt

📊 Final Metrics:
   mAP50: 0.966
   mAP50-95: 0.827
   Precision: 1.000
   Recall: 0.933

🔬 Comet ML Dashboard: https://www.comet.com/your-workspace/miso-ozzy-detector
```

Click that link to explore:
1. **Charts Tab**: See how loss decreased over time
2. **Images Tab**: View validation predictions to see where model succeeds/struggles
3. **Confusion Matrix**: See if model confuses Miso/Ozzy or mistakes background
4. **Hyperparameters**: Review all training settings

## Advanced: Custom Logging

If you want to log additional custom metrics or images:

```python
from comet_ml import Experiment

# Create experiment
experiment = Experiment(
    api_key=os.environ.get('COMET_API_KEY'),
    project_name='miso-ozzy-detector'
)

# Log custom metrics
experiment.log_metric('custom_metric', value, step=epoch)

# Log images
experiment.log_image('path/to/image.jpg', name='validation_sample')

# End experiment
experiment.end()
```

## Tips

1. **Name your experiments**: Use descriptive names in the training output
2. **Tag experiments**: Add tags like "baseline", "augmentation-test", etc.
3. **Add notes**: Document what you changed in each run
4. **Compare often**: Use the compare feature to see what works best
5. **Check images**: Don't just look at numbers - view prediction images to understand model behavior

## Resources

- [Comet ML Docs](https://www.comet.com/docs/)
- [Ultralytics + Comet Integration](https://docs.ultralytics.com/integrations/comet/)
- [Comet ML Examples](https://github.com/comet-ml/comet-examples)

---

**Next Steps**: Run `python scripts/train_with_comet.py` and watch your training come to life in the Comet dashboard! 🚀
