import re
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.services.skill_extractor import skill_extractor

class JobMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )

    def match_resume_to_job(
        self,
        resume_raw_text: str,
        resume_parsed_data: Dict[str, Any],
        job_description: str,
        job_required_skills_str: str = "",
        min_experience_req: float = 0.0,
        education_req: str = ""
    ) -> Dict[str, Any]:
        """
        Calculate deep semantic and skill-based match between resume and job.
        Combines:
        1. Cosine similarity on TF-IDF vectors (35%)
        2. Exact skill overlap (40%)
        3. Experience compatibility (15%)
        4. Education compatibility (10%)
        """
        # 1. Extract skills from Job Description & Required Skills
        job_combined_text = f"{job_description} {job_required_skills_str}"
        job_skills = skill_extractor.extract_all_skills_flat(job_combined_text)
        
        # If explicit required skills string has commas, parse those too
        if job_required_skills_str:
            explicit_skills = [s.strip() for s in job_required_skills_str.replace(";", ",").split(",") if s.strip()]
            job_skills = sorted(list(set(job_skills + explicit_skills)))

        # Resume skills
        resume_skills_dict = resume_parsed_data.get("skills", {})
        resume_skills_list = []
        for cat_skills in resume_skills_dict.values():
            resume_skills_list.extend(cat_skills)
        resume_skills_list = list(set(resume_skills_list))

        # 2. Skill Overlap Calculation
        resume_skills_lower = {s.lower(): s for s in resume_skills_list}
        matched_skills = []
        missing_skills = []

        for j_skill in job_skills:
            if j_skill.lower() in resume_skills_lower or any(j_skill.lower() in s.lower() for s in resume_skills_list):
                matched_skills.append(j_skill)
            else:
                missing_skills.append(j_skill)

        skill_overlap_ratio = 0.0
        if job_skills:
            skill_overlap_ratio = len(matched_skills) / len(job_skills)
        else:
            skill_overlap_ratio = 0.75  # Default if job description had no explicit skills detected

        skill_score = skill_overlap_ratio * 100.0

        # 3. TF-IDF Cosine Similarity
        cosine_score = 0.0
        try:
            corpus = [resume_raw_text, job_combined_text]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Rescale cosine score (raw cosine on resume vs JD usually ranges 0.15 - 0.70)
            cosine_score = min(max(sim * 135.0, 10.0), 98.0)
        except Exception:
            cosine_score = 50.0

        # 4. Experience Match
        candidate_exp = resume_parsed_data.get("total_experience_years", 0.0)
        exp_match_score = 100.0
        if min_experience_req > 0:
            if candidate_exp >= min_experience_req:
                exp_match_score = 100.0
            else:
                ratio = candidate_exp / min_experience_req
                exp_match_score = max(ratio * 80.0, 30.0)
        else:
            exp_match_score = 90.0

        # 5. Education Match
        edu_match_score = 80.0
        if education_req:
            edu_lower = education_req.lower()
            candidate_edus = [e.get("degree", "").lower() for e in resume_parsed_data.get("education", [])]
            if any(edu_lower in deg or deg in edu_lower for deg in candidate_edus):
                edu_match_score = 100.0
            else:
                edu_match_score = 65.0

        # Composite Match Score
        final_match_score = (
            skill_score * 0.40 +
            cosine_score * 0.35 +
            exp_match_score * 0.15 +
            edu_match_score * 0.10
        )
        final_match_score = round(min(max(final_match_score, 12.0), 98.0), 1)

        # Generate human-readable analysis notes
        notes = []
        if len(missing_skills) == 0:
            notes.append("Outstanding match! Candidate possesses all identified core technical skills.")
        else:
            notes.append(f"Missing {len(missing_skills)} target skills: {', '.join(missing_skills[:5])}.")

        if min_experience_req > 0 and candidate_exp < min_experience_req:
            notes.append(f"Experience gap: Role requires {min_experience_req} yrs, candidate has ~{candidate_exp} yrs.")
        else:
            notes.append(f"Candidate meets or exceeds minimum required experience.")

        return {
            "match_score": final_match_score,
            "matched_skills": sorted(list(set(matched_skills))),
            "missing_skills": sorted(list(set(missing_skills))),
            "skill_score": round(skill_score, 1),
            "cosine_score": round(cosine_score, 1),
            "experience_match_score": round(exp_match_score, 1),
            "education_match_score": round(edu_match_score, 1),
            "analysis_notes": " ".join(notes)
        }

job_matcher = JobMatcher()
