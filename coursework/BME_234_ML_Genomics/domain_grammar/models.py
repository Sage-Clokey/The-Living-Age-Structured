"""
Models A, B, and C for protein function prediction (GO term classification).

Model A: Sequence only (ESM-2 embedding -> MLP)
Model B: Domain grammar only (domain bag + context -> MLP)
Model C: Combined (ESM-2 + domain bag + context -> MLP)
"""

import torch
import torch.nn as nn


class ModelA_SequenceOnly(nn.Module):
    """
    Baseline: ESM-2 embedding (1280-dim) -> MLP -> GO term predictions.
    Tests: how far does sequence-level information get you?
    """

    def __init__(self, embedding_dim: int = 1280, hidden_dim: int = 512, n_labels: int = 100, dropout: float = 0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, n_labels),
        )

    def forward(self, esm_embedding, **kwargs):
        return self.net(esm_embedding)


class ModelB_DomainGrammar(nn.Module):
    """
    Domain grammar only: bag-of-domains + context features -> MLP -> GO term predictions.
    Tests: can domain-level compositionality predict function with zero sequence info?
    """

    def __init__(self, n_domains: int, context_dim: int = 5, hidden_dim: int = 256, n_labels: int = 100, dropout: float = 0.3):
        super().__init__()
        input_dim = n_domains + context_dim
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, n_labels),
        )

    def forward(self, domain_bag, context, **kwargs):
        x = torch.cat([domain_bag, context], dim=1)
        return self.net(x)


class ModelC_Combined(nn.Module):
    """
    Combined: ESM-2 embedding + domain bag + context -> MLP -> GO term predictions.
    Tests: does domain grammar add information beyond what sequence captures?
    """

    def __init__(self, embedding_dim: int = 1280, n_domains: int = 500, context_dim: int = 5, hidden_dim: int = 512, n_labels: int = 100, dropout: float = 0.3):
        super().__init__()
        input_dim = embedding_dim + n_domains + context_dim
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, n_labels),
        )

    def forward(self, esm_embedding, domain_bag, context, **kwargs):
        x = torch.cat([esm_embedding, domain_bag, context], dim=1)
        return self.net(x)


def get_model(model_type: str, **kwargs) -> nn.Module:
    """Factory function to create models by type."""
    models = {
        "A": ModelA_SequenceOnly,
        "B": ModelB_DomainGrammar,
        "C": ModelC_Combined,
    }
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}. Choose from {list(models.keys())}")
    return models[model_type](**kwargs)
