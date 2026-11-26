"""
PyTorch Deep Learning Architectures Module (Phase 07)
Implements MLP, 1D-CNN, BiLSTM, and Unsupervised Autoencoder for HTTP payload inspection.
Optimized for low-latency inference and CPU/GPU compatibility.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class CharTokenizer:
    """
    Lightweight character-level tokenizer mapping ASCII characters to integer IDs.
    Restricted to standard ASCII vocabulary [0..127] for bounded memory footprint.
    """
    def __init__(self, max_length: int = 256):
        self.max_length = max_length
        self.vocab_size = 128  # ASCII characters

    def encode(self, text: str) -> List[int]:
        if not text or not isinstance(text, str):
            return [0] * self.max_length
        
        # Clamp to ASCII 0..127, replace unknown/high chars with 127
        tokens = [ord(c) if ord(c) < 127 else 127 for c in text[:self.max_length]]
        # Pad with zeros if shorter than max_length
        if len(tokens) < self.max_length:
            tokens = tokens + [0] * (self.max_length - len(tokens))
        return tokens

    def encode_batch(self, texts: List[str]) -> torch.Tensor:
        encoded = [self.encode(t) for t in texts]
        return torch.tensor(encoded, dtype=torch.long)


class MLPClassifier(nn.Module):
    """
    Multi-Layer Perceptron operating on handcrafted numerical domain features.
    """
    def __init__(self, input_dim: int = 79, hidden_dim1: int = 128, hidden_dim2: int = 64, dropout_rate: float = 0.2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.BatchNorm1d(hidden_dim1),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.ReLU(),
            nn.Linear(hidden_dim2, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.net(x)
        return torch.sigmoid(logits)


class Conv1DClassifier(nn.Module):
    """
    1D-Convolutional Neural Network learning local character n-gram attack patterns.
    """
    def __init__(self, vocab_size: int = 128, embedding_dim: int = 32, num_filters: int = 64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.conv1 = nn.Conv1d(embedding_dim, num_filters, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(num_filters, num_filters * 2, kernel_size=5, padding=2)
        self.pool = nn.AdaptiveMaxPool1d(1)
        self.classifier = nn.Sequential(
            nn.Linear(num_filters * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, seq_len)
        emb = self.embedding(x).transpose(1, 2)  # (batch_size, emb_dim, seq_len)
        c1 = F.relu(self.conv1(emb))
        c2 = F.relu(self.conv2(c1))
        pooled = self.pool(c2).squeeze(-1)       # (batch_size, num_filters * 2)
        logits = self.classifier(pooled)
        return torch.sigmoid(logits)


class BiLSTMClassifier(nn.Module):
    """
    Bidirectional LSTM learning long-range sequential token dependencies.
    """
    def __init__(self, vocab_size: int = 128, embedding_dim: int = 32, hidden_dim: int = 64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            batch_first=True,
            bidirectional=True
        )
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch_size, seq_len)
        emb = self.embedding(x)  # (batch_size, seq_len, emb_dim)
        lstm_out, _ = self.lstm(emb)  # (batch_size, seq_len, hidden_dim * 2)
        # Take representation from mean pooling across time steps
        pooled = torch.mean(lstm_out, dim=1)
        logits = self.classifier(pooled)
        return torch.sigmoid(logits)


class NumericalAutoencoder(nn.Module):
    """
    Unsupervised Reconstruction Autoencoder trained strictly on normal traffic.
    High reconstruction MSE indicates anomalous/malicious patterns.
    """
    def __init__(self, input_dim: int = 79, latent_dim: int = 24):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 48),
            nn.ReLU(),
            nn.Linear(48, latent_dim),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 48),
            nn.ReLU(),
            nn.Linear(48, input_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction

    def compute_reconstruction_error(self, x: torch.Tensor) -> torch.Tensor:
        """Computes MSE per sample."""
        recon = self.forward(x)
        mse = torch.mean((x - recon) ** 2, dim=1)
        return mse
