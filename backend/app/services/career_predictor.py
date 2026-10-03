import numpy as np
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Target occupational profiles and their key defining competencies
CAREER_PROFILES: Dict[str, Dict[str, Any]] = {
    "Python Developer": {
        "core_skills": ["Python", "FastAPI", "Django", "Flask", "SQL", "Git", "Docker", "REST API"],
        "description": "Designs, develops, and maintains scalable backend services and microservices using Python frameworks.",
        "growth": "High demand in cloud backends, API automation, and data pipelines.",
        "keywords": "python fastapi django flask backend sql rest orm pytest async celery"
    },
    "Data Scientist": {
        "core_skills": ["Python", "Machine Learning", "Data Science", "Pandas", "NumPy", "Scikit-learn", "SQL", "Deep Learning"],
        "description": "Applies statistical modeling, exploratory analysis, and ML algorithms to extract predictive business insights.",
        "growth": "Top tier priority across finance, healthcare, e-commerce, and SaaS enterprises.",
        "keywords": "data science machine learning pandas numpy scikit-learn statistics visualization predictive modeling python r"
    },
    "ML Engineer": {
        "core_skills": ["Machine Learning", "Deep Learning", "Python", "TensorFlow", "PyTorch", "Docker", "NLP", "Scikit-learn"],
        "description": "Bridges research and production by training, tuning, and deploying scalable machine learning models.",
        "growth": "Rapid growth with enterprise adoption of autonomous systems, LLMs, and real-time inference.",
        "keywords": "machine learning deep learning pytorch tensorflow docker mlops model deployment computer vision nlp"
    },
    "AI Engineer": {
        "core_skills": ["Python", "Deep Learning", "NLP", "Generative AI", "PyTorch", "TensorFlow", "Docker", "Machine Learning"],
        "description": "Develops production-ready Generative AI solutions, prompt systems, computer vision, and neural networks.",
        "growth": "Extremely high market momentum driven by foundational models and intelligent agents.",
        "keywords": "ai artificial intelligence llm generative ai transformers prompt engineering pytorch nlp computer vision"
    },
    "Data Analyst": {
        "core_skills": ["SQL", "Power BI", "Tableau", "Excel", "Data Analytics", "Python", "Pandas"],
        "description": "Transforms structured data into executive dashboards, business KPIs, and actionable commercial insights.",
        "growth": "Consistent high demand across every business vertical seeking data-driven decision making.",
        "keywords": "sql data analytics power bi tableau excel dashboards reporting metrics kpi business intelligence"
    },
    "Full Stack Developer": {
        "core_skills": ["JavaScript", "React", "Node.js", "HTML5", "CSS3", "SQL", "Git", "Express"],
        "description": "Architects end-to-end applications bridging interactive web user interfaces with robust backend APIs.",
        "growth": "Versatile and highly sought after by agile startups and tech scale-ups.",
        "keywords": "full stack react node.js javascript html5 css3 express rest api sql mongodb git frontend backend"
    },
    "Backend Developer": {
        "core_skills": ["Python", "Java", "SQL", "PostgreSQL", "Docker", "Node.js", "Git", "FastAPI"],
        "description": "Specializes in server-side architecture, relational database design, API security, and high-throughput systems.",
        "growth": "Critical cornerstone of every modern web, mobile, and cloud software infrastructure.",
        "keywords": "backend server database postgresql microservices api design authentication redis docker java python"
    },
    "Database Developer": {
        "core_skills": ["SQL", "MySQL", "PostgreSQL", "Oracle", "MongoDB", "Redis", "Database"],
        "description": "Optimizes relational schemas, indexing, stored procedures, replication, and data warehousing pipelines.",
        "growth": "Steady demand in finance, healthcare, and enterprise data storage administration.",
        "keywords": "database sql mysql postgresql oracle stored procedures indexing normalization query optimization dba"
    },
    "Business Analyst": {
        "core_skills": ["Excel", "Power BI", "SQL", "Agile", "Communication", "Problem Solving", "Tableau"],
        "description": "Liaises between technical engineering teams and business stakeholders to translate requirements into technical specs.",
        "growth": "Essential for digital transformation initiatives and project governance.",
        "keywords": "business analyst requirements gathering user stories agile scrum excel power bi communication workflow"
    },
    "Software Engineer": {
        "core_skills": ["Java", "Python", "C++", "SQL", "Git", "Data Structures", "Algorithms", "Linux"],
        "description": "Applies computer science fundamentals to develop maintainable, high-performance software applications.",
        "growth": "Evergreen foundational engineering role across all modern technology companies.",
        "keywords": "software engineer oop data structures algorithms java c++ problem solving system design linux git"
    },
    "DevOps / Cloud Engineer": {
        "core_skills": ["Docker", "Kubernetes", "AWS", "Azure", "CI/CD", "Linux", "Terraform", "Git"],
        "description": "Automates cloud infrastructure, build pipelines, monitoring, and high availability systems.",
        "growth": "Critical operational role with lucrative opportunities in modern cloud enterprises.",
        "keywords": "devops cloud aws azure docker kubernetes ci/cd terraform linux automation monitoring"
    }
}

class CareerPredictor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        # Build profile texts
        self.role_names = list(CAREER_PROFILES.keys())
        self.profile_texts = [
            f"{role} {' '.join(CAREER_PROFILES[role]['core_skills'])} {CAREER_PROFILES[role]['keywords']}"
            for role in self.role_names
        ]

    def predict_roles(self, parsed_data: Dict[str, Any], raw_text: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Predict top suitable roles using a hybrid ML TF-IDF cosine similarity
        and skill overlap algorithm with explainable reasons.
        """
        # Resume skills
        detected_skills = []
        for cat_skills in parsed_data.get("skills", {}).values():
            detected_skills.extend(cat_skills)
        detected_skills_set = set(detected_skills)
        
        # Candidate combined text for NLP
        candidate_corpus_chunk = f"{raw_text} {' '.join(detected_skills)}"

        # Compute TF-IDF matrix between candidate text and role profiles
        all_texts = [candidate_corpus_chunk] + self.profile_texts
        try:
            tfidf_mat = self.vectorizer.fit_transform(all_texts)
            candidate_vec = tfidf_mat[0:1]
            profile_vecs = tfidf_mat[1:]
            similarities = cosine_similarity(candidate_vec, profile_vecs)[0]
        except Exception:
            similarities = np.zeros(len(self.role_names))

        scored_roles = []
        for idx, role_name in enumerate(self.role_names):
            profile = CAREER_PROFILES[role_name]
            core_skills = set(profile["core_skills"])
            
            # Skill overlap ratio
            matched = core_skills.intersection(detected_skills_set)
            skill_ratio = len(matched) / max(len(core_skills), 1)

            # Combined score: 55% skill overlap + 45% ML TF-IDF text similarity
            tfidf_score = similarities[idx] * 100.0 if idx < len(similarities) else 0.0
            composite_score = (skill_ratio * 100.0 * 0.55) + (tfidf_score * 0.45)
            
            # Bound and round
            final_score = round(min(max(composite_score, 10.0), 96.0), 1)

            # Generate explainability rationale
            explanation = (
                f"Candidate matched {len(matched)} of {len(core_skills)} core competencies "
                f"({', '.join(sorted(list(matched))) if matched else 'foundational skills'}). "
                f"{profile['growth']}"
            )

            scored_roles.append({
                "role_title": role_name,
                "confidence_score": final_score,
                "description": profile["description"],
                "matched_core_skills": sorted(list(matched)),
                "unmatched_core_skills": sorted(list(core_skills - matched)),
                "explanation": explanation
            })

        # Sort descending by confidence score
        scored_roles.sort(key=lambda x: x["confidence_score"], reverse=True)
        return scored_roles[:top_k]

career_predictor = CareerPredictor()
