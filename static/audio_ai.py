from transformers import pipeline
import librosa

# Load AI sound classification model
classifier = pipeline(
    "audio-classification",
    model="MIT/ast-finetuned-audioset-10-10-0.4593"
)


def analyze_audio(audio_path):

    try:
        # Load audio and convert to 16 kHz
        audio, sample_rate = librosa.load(
            audio_path,
            sr=16000,
            mono=True
        )

        # AI sound classification
        results = classifier(
            audio,
            top_k=5
        )

        detected_sounds = []

        for result in results:
            detected_sounds.append(
                result["label"]
            )

        return ", ".join(detected_sounds)

    except Exception as e:
        return "Unable to analyze audio"