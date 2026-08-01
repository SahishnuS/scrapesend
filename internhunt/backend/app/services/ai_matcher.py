import re

import structlog
from sentence_transformers import SentenceTransformer, util

log = structlog.get_logger(__name__)

# List of common technical skills relevant to this platform
CORE_KEYWORDS = [
    "python", "c++", "c", "java", "javascript", "golang", "rust",
    "ros", "ros2", "slam", "gazebo", "opencv", "yolo", "pytorch",
    "tensorflow", "keras", "scikit-learn", "numpy", "pandas",
    "embedded", "rtos", "firmware", "microcontroller", "stm32",
    "esp32", "arduino", "raspberry pi", "fpga", "vhdl", "verilog",
    "machine learning", "deep learning", "computer vision", "nlp",
    "git", "docker", "kubernetes", "aws", "gcp", "azure", "linux",
    "sql", "nosql", "postgres", "mongodb"
]


class AIMatcher:
    """
    AI Matching Service.
    Uses SentenceTransformers for semantic similarity (Match Score)
    and heuristic keyword overlap (ATS Score).
    """

    def __init__(self):
        # We use a very lightweight, fast, and highly capable model for semantic matching.
        # It will be downloaded and cached automatically the first time this is initialized.
        log.info("Initializing SentenceTransformer model (all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        log.info("SentenceTransformer model loaded successfully.")

    def calculate_match_score(self, resume_text: str, job_text: str) -> float:
        """
        Calculate the semantic cosine similarity between a resume and a job description.
        Returns a float between 0.0 and 1.0.
        """
        if not resume_text or not job_text:
            return 0.0

        # Truncate to avoid memory issues on massive texts; the model handles ~256-512 tokens best.
        # But for all-MiniLM, it truncates internally. Still, good practice.
        resume_slice = resume_text[:3000]
        job_slice = job_text[:3000]

        # Compute embeddings
        resume_embedding = self.model.encode(resume_slice, convert_to_tensor=True)
        job_embedding = self.model.encode(job_slice, convert_to_tensor=True)

        # Compute cosine similarity
        cosine_scores = util.cos_sim(resume_embedding, job_embedding)

        # Convert tensor result to standard float
        score = float(cosine_scores[0][0])

        # Clamp between 0.0 and 1.0 (sometimes cosine sim can be slightly negative)
        return max(0.0, min(1.0, score))

    def calculate_ats_score(self, resume_text: str, job_text: str) -> tuple[float, dict]:
        """
        Simulate an ATS system by extracting required keywords from the job description
        and checking if they exist in the resume.

        Returns:
            - ats_score: Float between 0.0 and 1.0
            - matched_keywords: Dict of keyword -> boolean (found in resume)
        """
        if not resume_text or not job_text:
            return 0.0, {}

        resume_lower = resume_text.lower()
        job_lower = job_text.lower()

        required_keywords = []
        for kw in CORE_KEYWORDS:
            # Simple word boundary regex to avoid partial matches (e.g., "c" in "cat")
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, job_lower):
                required_keywords.append(kw)

        if not required_keywords:
            # If the job description has none of our core keywords, we can't reliably score it this way.
            return 1.0, {} # Default to perfect to not penalize

        matched_dict = {}
        matched_count = 0

        for kw in required_keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, resume_lower):
                matched_dict[kw] = True
                matched_count += 1
            else:
                matched_dict[kw] = False

        ats_score = matched_count / len(required_keywords)

        return ats_score, matched_dict
