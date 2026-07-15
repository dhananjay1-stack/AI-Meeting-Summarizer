"""
Transcript cleaning and post-processing.
"""

import re


class TranscriptCleaner:
    """Post-process raw transcription output for readability."""

    # Common filler words to optionally reduce
    FILLER_WORDS = {
        "um", "uh", "uhm", "umm", "erm", "er", "ah",
        "like", "you know", "basically", "actually",
        "sort of", "kind of", "i mean",
    }

    def clean(self, text: str, remove_fillers: bool = True) -> str:
        """
        Clean a transcript text:
        1. Normalize whitespace
        2. Fix sentence boundaries
        3. Optionally remove filler words
        4. Group into paragraphs
        """
        if not text:
            return text

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Remove fillers
        if remove_fillers:
            text = self._remove_fillers(text)

        # Fix sentence boundaries — capitalize after period
        text = self._fix_sentence_boundaries(text)

        # Group into paragraphs (roughly every 3-5 sentences)
        text = self._group_into_paragraphs(text)

        return text

    def _remove_fillers(self, text: str) -> str:
        """Remove common filler words while preserving sentence structure."""
        for filler in sorted(self.FILLER_WORDS, key=len, reverse=True):
            # Match filler words as whole words (case-insensitive)
            pattern = r"\b" + re.escape(filler) + r"\b[,]?\s*"
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

        # Clean up double spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _fix_sentence_boundaries(self, text: str) -> str:
        """Ensure proper capitalization after sentence-ending punctuation."""
        # Capitalize after . ! ?
        def capitalize_match(match):
            return match.group(1) + " " + match.group(2).upper()

        text = re.sub(r"([.!?])\s+([a-z])", capitalize_match, text)

        # Capitalize first letter
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        return text

    def _group_into_paragraphs(self, text: str, sentences_per_paragraph: int = 4) -> str:
        """Split text into paragraphs based on sentence count."""
        # Split on sentence-ending punctuation
        sentences = re.split(r"(?<=[.!?])\s+", text)

        if len(sentences) <= sentences_per_paragraph:
            return text

        paragraphs = []
        for i in range(0, len(sentences), sentences_per_paragraph):
            paragraph = " ".join(sentences[i : i + sentences_per_paragraph])
            paragraphs.append(paragraph)

        return "\n\n".join(paragraphs)


# Singleton
transcript_cleaner = TranscriptCleaner()
