#!/usr/bin/env python3
"""
Setup script for Solomon-Sophia local models.
Downloads and configures Hugging Face models, TensorFlow models, and Ollama.
"""

import os
import sys
from pathlib import Path
import subprocess
import logging
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_command_exists(command: str) -> bool:
    """Check if a command exists in the system."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ollama():
    """Install Ollama if not present."""
    if check_command_exists("ollama"):
        logger.info("✅ Ollama is already installed")
        return True
    
    logger.info("📥 Installing Ollama...")
    try:
        # Install Ollama
        subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh"], 
                      stdout=subprocess.PIPE, check=True)
        subprocess.run(["sh"], input=subprocess.PIPE, check=True)
        logger.info("✅ Ollama installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install Ollama: {e}")
        return False

def download_ollama_models():
    """Download required Ollama models."""
    models = ["llama3.2", "codellama", "mistral"]
    
    for model in models:
        logger.info(f"📥 Downloading Ollama model: {model}")
        try:
            subprocess.run(["ollama", "pull", model], check=True)
            logger.info(f"✅ Downloaded {model}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Failed to download {model}: {e}")

def setup_huggingface_models():
    """Download and cache Hugging Face models."""
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from sentence_transformers import SentenceTransformer
    
    # LLM Models
    hf_models = [
        "microsoft/DialoGPT-large",
        "google/flan-t5-base",
        "microsoft/DialoGPT-medium",  # Fallback
    ]
    
    # Embedding Models
    embedding_models = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-mpnet-base-v2",
    ]
    
    logger.info("📥 Setting up Hugging Face models...")
    
    # Download LLM models
    for model_name in hf_models:
        try:
            logger.info(f"📥 Downloading LLM model: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            logger.info(f"✅ Downloaded and cached {model_name}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to download {model_name}: {e}")
    
    # Download embedding models
    for model_name in embedding_models:
        try:
            logger.info(f"📥 Downloading embedding model: {model_name}")
            model = SentenceTransformer(model_name)
            logger.info(f"✅ Downloaded and cached {model_name}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to download {model_name}: {e}")

def setup_tensorflow_models():
    """Setup TensorFlow models if requested."""
    try:
        import tensorflow as tf
        from transformers import TFAutoModelForSeq2SeqLM, AutoTokenizer
        
        logger.info("📥 Setting up TensorFlow models...")
        
        tf_models = [
            "google/flan-t5-base",
            "google/flan-t5-small",  # Fallback
        ]
        
        for model_name in tf_models:
            try:
                logger.info(f"📥 Downloading TF model: {model_name}")
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = TFAutoModelForSeq2SeqLM.from_pretrained(model_name)
                logger.info(f"✅ Downloaded and cached {model_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to download {model_name}: {e}")
                
    except ImportError:
        logger.info("⚠️ TensorFlow not installed, skipping TF models")

def create_model_config():
    """Create a local model configuration file."""
    config = {
        "local_models": {
            "llm": {
                "primary": "microsoft/DialoGPT-large",
                "fallback": "microsoft/DialoGPT-medium",
                "ollama": "llama3.2"
            },
            "embeddings": {
                "primary": "sentence-transformers/all-MiniLM-L6-v2",
                "fallback": "sentence-transformers/all-mpnet-base-v2"
            },
            "tensorflow": {
                "primary": "google/flan-t5-base",
                "fallback": "google/flan-t5-small"
            }
        },
        "settings": {
            "use_local_only": True,
            "use_ollama": True,
            "use_tensorflow": False,
            "cache_dir": "./cache/models"
        }
    }
    
    import json
    with open("local_models_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    logger.info("✅ Created local model configuration")

def main():
    """Main setup function."""
    logger.info("🚀 Setting up Solomon-Sophia local models...")
    
    # Create cache directories
    Path("cache/models").mkdir(parents=True, exist_ok=True)
    Path("cache/huggingface").mkdir(parents=True, exist_ok=True)
    
    # Setup Ollama
    if install_ollama():
        download_ollama_models()
    
    # Setup Hugging Face models
    try:
        setup_huggingface_models()
    except Exception as e:
        logger.error(f"❌ Failed to setup Hugging Face models: {e}")
    
    # Setup TensorFlow models (optional)
    setup_tensorflow_models()
    
    # Create configuration
    create_model_config()
    
    logger.info("🎉 Local model setup complete!")
    logger.info("📋 Summary:")
    logger.info("   - Ollama: Local LLM server")
    logger.info("   - Hugging Face: Transformer models")
    logger.info("   - Sentence Transformers: Embedding models")
    logger.info("   - TensorFlow: Optional advanced models")
    logger.info("   - No API keys required!")
    
    print("\n🚀 Next steps:")
    print("1. Start Ollama: ollama serve")
    print("2. Initialize database: solomon init-db")
    print("3. Start Solomon: solomon serve")

if __name__ == "__main__":
    main()
