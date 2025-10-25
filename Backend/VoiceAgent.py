import io
import os
import tempfile

import numpy as np
import soundfile as sf      
import librosa              
import whisper              

class VoiceAgent:
    def __init__(self, model_name: str = "base", device: str | None = None, debug: bool = False):
        """
        model_name: tiny/base/small/medium/large
        device: "cuda" or "cpu" or None (auto)
        debug: prints audio shape/sr info
        """
        self.debug = debug
       
        if device:
            self.model = whisper.load_model(model_name, device=device)
        else:
            self.model = whisper.load_model(model_name)

    def _decode_audio_bytes(self, audio_bytes: bytes, target_sr: int = 16000) -> np.ndarray:
        """
        Returns a 1-D float32 numpy array at target_sr (mono).
        This tries soundfile on BytesIO first then falls back to writing a temp file.
        """
        buf = io.BytesIO(audio_bytes)
   
        try:
            buf.name = "file.wav"
        except Exception:
            pass

        try:
            data, sr = sf.read(buf, dtype="float32")
        except Exception:
     
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            try:
                data, sr = sf.read(tmp_path, dtype="float32")
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    
        if data.ndim > 1:
            data = np.mean(data, axis=1)

      
        if sr != target_sr:
            data = librosa.resample(data.astype(np.float32), orig_sr=sr, target_sr=target_sr)
            sr = target_sr

   
        data = data.astype(np.float32).flatten()

        if self.debug:
            print(f"[VoiceAgent] decoded audio -> shape={data.shape}, sr={sr}, min={data.min():.5f}, max={data.max():.5f}")

        return data

    def transcribe_bytes(self, audio_bytes: bytes, language: str = "en") -> str:
        """
        Main entry: feed raw audio bytes (what you get from websocket) and get transcription.
        Returns transcription text.
        """
        try:
            audio = self._decode_audio_bytes(audio_bytes, target_sr=16000)
           
            if audio.size == 0 or np.allclose(audio, 0.0):
                return ""

           
            result = self.model.transcribe(audio, language=language, fp16=False)
            return result.get("text", "").strip()
        except Exception as e:
       
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_bytes)
                    tmp_path = tmp.name
                if self.debug:
                    print("[VoiceAgent] fallback: using temp file for transcription:", tmp_path)
                result = self.model.transcribe(tmp_path, language=language, fp16=False)
                return result.get("text", "").strip()
            finally:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
