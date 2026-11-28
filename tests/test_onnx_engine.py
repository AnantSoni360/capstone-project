"""
tests/test_onnx_engine.py
Unit tests for ONNX Runtime Inference Acceleration Engine.
"""

import os
import numpy as np
import pytest
from src.onnx_engine import ONNX1DCNNEngine

@pytest.fixture
def engine():
    return ONNX1DCNNEngine()

def test_onnx_model_exists():
    assert os.path.exists("models/model_1d_cnn.onnx"), "models/model_1d_cnn.onnx should exist"

def test_onnx_engine_initialization(engine):
    assert engine.is_available, "ONNX Runtime session should initialize successfully"
    assert engine.input_name is not None
    assert engine.output_name is not None

def test_onnx_inference_output_shape(engine):
    batch_input = np.random.randint(0, 128, size=(4, 256), dtype=np.int64)
    probs = engine.predict_proba(batch_input)
    assert len(probs) == 4
    for p in probs:
        assert 0.0 <= p <= 1.0

def test_onnx_speed_benchmark(engine):
    bench = engine.benchmark_speed(num_iterations=100)
    assert bench["status"] == "ready"
    assert bench["avg_latency_ms"] < 2.0, "ONNX latency should be sub-2ms"
    assert bench["throughput_rps"] > 500.0, "Throughput should exceed 500 req/s"
