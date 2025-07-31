import os
import threading
import time
import asyncio
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
    logger.warning("llama-cpp-python not installed. GGUF models will not be available.")

class ModelManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.model_base_path = "models"
        self.default_model_name = "default.gguf"
        self._model_lock = threading.Lock()
        self._current_model = None
        self._current_model_name = None
        self._current_model_type = None
        self._loading = False
        self._load_progress = 0
        self._load_start_time = 0
        self._initialized = True
        logger.info("ModelManager initialized")
        
        # Load default model on startup
        asyncio.create_task(self._load_default_model())

    async def _load_default_model(self):
        """Load default model when server starts"""
        try:
            if self.default_model_name:
                await self.load_model(self.default_model_name)
        except Exception as e:
            logger.error(f"Failed to load default model: {str(e)}")

    async def load_model(self, model_name: str):
        """Load a new model, automatically unloading current model if exists"""
        if self._loading:
            raise RuntimeError("Another model is currently being loaded")
            
        self._loading = True
        self._load_progress = 0
        self._load_start_time = time.time()
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                self._sync_load_model, 
                model_name
            )
        except Exception as e:
            self._loading = False
            logger.error(f"Model loading failed: {str(e)}")
            raise
        finally:
            self._loading = False
            logger.info(f"Model loading completed in {time.time() - self._load_start_time:.2f} seconds")

    def _sync_load_model(self, model_name: str):
        """Synchronous model loading with proper unloading"""
        with self._model_lock:
            try:
                # Skip if same model is already loaded
                if self._current_model_name == model_name:
                    logger.info("Same model already loaded")
                    return

                # Unload current model if exists
                if self._current_model is not None:
                    self._update_load_progress(5, "Unloading current model")
                    self._safe_unload()

                # Load new model
                self._load_gguf_model(model_name)

                # Update state
                self._current_model_name = model_name
                self._current_model_type = "gguf"
                self._update_load_progress(100, "Model switched successfully")
                
            except Exception as e:
                logger.error(f"Error during model switching: {str(e)}")
                self._safe_unload()  # Clean up if error occurs
                raise

    def _safe_unload(self):
        """Safely unload current model with proper cleanup"""
        try:
            if self._current_model is not None:
                logger.info(f"Unloading model: {self._current_model_name}")
                del self._current_model
                self._current_model = None
                self._current_model_name = None
                self._current_model_type = None
                logger.info("Model unloaded successfully")
            else:
                logger.info("No model to unload")
        except Exception as e:
            logger.error(f"Error during model unloading: {str(e)}")
            # Force clear references if error occurs
            self._current_model = None
            self._current_model_name = None
            self._current_model_type = None

    def _load_gguf_model(self, model_name: str):
        """Load GGUF model implementation"""
        self._update_load_progress(10, "Loading new GGUF model")
        if Llama is None:
            raise ImportError("llama-cpp-python not installed")

        model_path = os.path.join(self.model_base_path, 'gguf-models', model_name)
        logger.info(f"Loading model from: {model_path}")
        
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")

        self._update_load_progress(20, "Initializing model")
        try:
            self._current_model = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=4,
                verbose=False
            )
            self._update_load_progress(80, "Model initialized")
        except Exception as e:
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    def _update_load_progress(self, progress: int, message: str):
        """Update loading progress with logging"""
        self._load_progress = progress
        logger.info(f"{message} - Progress: {progress}%")

    def get_model_info(self) -> Dict[str, Any]:
        """Get current model state information"""
        return {
            "model_loaded": self._current_model is not None,
            "model_name": self._current_model_name,
            "model_type": self._current_model_type,
            "loading": self._loading,
            "load_progress": self._load_progress,
            "load_time": time.time() - self._load_start_time if self._loading else 0
        }

    def get_current_model(self):
        """Get currently loaded model instance"""
        with self._model_lock:
            return {
                "model": self._current_model,
                "name": self._current_model_name,
                "type": self._current_model_type
            }
    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 200,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stream: bool = False
    ) -> Dict[str, Any]:
    
        if not self._current_model:
            raise RuntimeError("No model is currently loaded")
            
        try:
            # Generate response
            response = self._current_model.create_chat_completion(
                messages=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=stream
            )

            # --- If streaming, collect tokens ---
            if stream:
                collected_text = ""
                for chunk in response:  # generator
                    if "choices" in chunk and chunk["choices"][0].get("delta", {}).get("content"):
                        collected_text += chunk["choices"][0]["delta"]["content"]

                return {
                    "response": collected_text,
                    "model": self._current_model_name
                }

            # --- Normal mode (non-stream) ---
            else:
                if isinstance(response, dict) and "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                elif isinstance(response, str):
                    content = response
                else:
                    raise RuntimeError(f"Unexpected response format: {type(response)}")

                return {
                    "response": content,
                    "model": self._current_model_name
                }

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")
