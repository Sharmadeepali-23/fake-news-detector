# Dataset Instructions

This directory holds the raw dataset CSV files for model training:

1. `Fake.csv` - Fake news articles dataset.
2. `True.csv` - Real/True news articles dataset.

### Kaggle Dataset Download
You can download the full Kaggle Fake & Real News Dataset (ISOT Fake News Dataset) from Kaggle:
- **Kaggle Link**: [Fake and Real News Dataset](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset)

Place `Fake.csv` and `True.csv` into this directory (`dataset/`) before running:
```bash
python train_model.py
```

*Note: If `Fake.csv` and `True.csv` are missing, `train_model.py` will automatically generate a balanced sample dataset so the application can be built and evaluated out of the box.*
