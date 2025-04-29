import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs
from TTS.config.shared_configs import BaseDatasetConfig

torch.serialization.add_safe_globals([
    XttsConfig,
    XttsAudioConfig,
    BaseDatasetConfig,
    XttsArgs
])

def load_model():
    config = XttsConfig()
    config.load_json('tts_models--multilingual--multi-dataset--xtts_v2/config.json')
    model = Xtts.init_from_config(config)
    model.load_checkpoint(config, checkpoint_dir='tts_models--multilingual--multi-dataset--xtts_v2', use_deepspeed=False)
    #model.cuda()
    return model
