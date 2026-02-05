
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add src to sys.path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock the qwen_tts dependency before importing the server
sys.modules["qwen_tts"] = MagicMock()
from chichi_speech import server

class TestServer(unittest.TestCase):
    def setUp(self):
        # Reset the global model and prompt for each test
        server.model = MagicMock()
        server.VOICE_PROMPT = MagicMock()
        self.client = TestClient(server.app)

    def test_synthesize_endpoint_success(self):
        """Test happy path for synthesis"""
        # Mock the generate_voice_clone return value
        # It returns (wavs, sr)
        # wavs is a list of tensors/arrays
        mock_audio = MagicMock()
        mock_audio.cpu.return_value.float.return_value.numpy.return_value = [0.1, 0.2, 0.3]
        server.model.generate_voice_clone.return_value = ([mock_audio], 24000)
        
        response = self.client.post("/synthesize", json={
            "text": "Hello world",
            "language": "English"
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "audio/wav")

    def test_synthesize_endpoint_not_initialized(self):
        """Test error when model is not initialized"""
        server.model = None
        server.VOICE_PROMPT = None
        
        response = self.client.post("/synthesize", json={
            "text": "Hello world"
        })
        
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "Service not initialized")

if __name__ == '__main__':
    unittest.main()
