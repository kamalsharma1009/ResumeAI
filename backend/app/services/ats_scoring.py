import re
from typing import Dict, Any, List

# Strong action verbs favored by ATS systems and recruiters
ATS_ACTION_VERBS = [
    "accelerated", "achieved", "analyzed", "architected", "automated", "built", "collaborated",
    "configured", "created", "decreased", "delivered", "deployed", "designed", "developed",
    "engineered", "established", "executed", "expanded", "generated", "implemented", "improved",
    "increased", "initiated", "innovated", "integrated", "launched", "led", "managed",
    "maximized", "mentored", "migrated", "minimized", "modeled", "monitored", "optimized",
    "orchestrated", "overhauled", "pioneered", "reduced", "refactored", "resolved", "scaled",
    "spearheaded", "standardized", "streamlined", "supervised", "trained", "transformed", "upgraded"
]

class ATSScoringEngine:
    def calculate_score(self, parsed_data: Dict[str, Any], raw_text: str) -> Dict[str, float]:
        """
        Calculate a multi-factor AI ATS-style score out of 100.
        Factors:
        - Completeness (20%)
        - Skills depth & breadth (25%)
        - Experience & impact (20%)
        - Education (15%)
        - Keyword & action verbs (10%)
        - Formatting & metrics (10%)
        """
        completeness_score = self._calc_completeness(parsed_data)
        skills_score = self._calc_skills(parsed_data)
        experience_score = self._calc_experience(parsed_data, raw_text)
        education_score = self._calc_education(parsed_data)
        keyword_score = self._calc_keywords(raw_text)
        formatting_score = self._calc_formatting(raw_text, parsed_data)

        # Weighted calculation
        overall = (
            completeness_score * 0.20 +
            skills_score * 0.25 +
            experience_score * 0.20 +
            education_score * 0.15 +
            keyword_score * 0.10 +
            formatting_score * 0.10
        )

        overall_ats_score = round(min(max(overall, 15.0), 98.0), 1)

        return {
            "overall_ats_score": overall_ats_score,
            "keyword_score": round(keyword_score, 1),
            "skills_score": round(skills_score, 1),
            "experience_score": round(experience_score, 1),
            "education_score": round(education_score, 1),
            "completeness_score": round(completeness_score, 1),
            "formatting_score": round(formatting_score, 1)
        }

    def _calc_completeness(self, data: Dict[str, Any]) -> float:
        points = 0.0
        # Contact info
        if data.get("name") and data.get("name") != "Candidate":
            points += 15
        if data.get("email"):
            points += 15
        if data.get("phone"):
            points += 15
        if data.get("location") and data.get("location") != "Not Specified":
            points += 5
        # Core sections
        if data.get("education") and len(data["education"]) > 0:
            points += 20
        if data.get("skills") and len(data["skills"]) > 0:
            points += 20
        if data.get("projects") and len(data["projects"]) > 0:
            points += 15
        return min(points, 100.0)

    def _calc_skills(self, data: Dict[str, Any]) -> float:
        skills_by_cat = data.get("skills", {})
        total_skills = sum(len(s_list) for s_list in skills_by_cat.values())
        categories_count = len(skills_by_cat.keys())

        # Count score: 10 skills -> 70 pts, 18+ skills -> 100 pts
        count_score = min(total_skills * 5.0, 75.0)
        # Category balance score: covers prog languages, db, frameworks, etc.
        cat_score = min(categories_count * 8.0, 25.0)
        return min(count_score + cat_score, 100.0)

    def _calc_experience(self, data: Dict[str, Any], raw_text: str) -> float:
        exp_years = data.get("total_experience_years", 0.0)
        exp_entries = data.get("experience", [])
        
        # Experience level points
        score = 40.0  # Base score for students/freshers with internships
        if exp_years >= 1.0:
            score += 20.0
        if exp_years >= 2.5:
            score += 20.0
        if exp_years >= 5.0:
            score += 15.0

        if len(exp_entries) >= 2:
            score += 10.0

        # Check for quantified achievements (percentages, revenue, latency, users)
        quantified_matches = len(re.findall(r'\b(?:\d+%(?:\.\d+)?|\$\d+|\d+x|\d+\+?\s*(?:users|clients|requests|ms|seconds|hours))\b', raw_text, re.IGNORECASE))
        score += min(quantified_matches * 3.0, 15.0)
        
        return min(score, 100.0)

    def _calc_education(self, data: Dict[str, Any]) -> float:
        edu_list = data.get("education", [])
        if not edu_list:
            return 35.0  # default partial score
        
        score = 60.0
        for item in edu_list:
            deg = item.get("degree", "").lower()
            if any(k in deg for k in ["ph.d", "doctorate", "mca", "m.tech", "master", "ms"]):
                score = max(score, 95.0)
            elif any(k in deg for k in ["b.tech", "be", "bca", "b.sc", "bachelor"]):
                score = max(score, 85.0)
        
        if any(item.get("institution") and "Recognized" not in item.get("institution") for item in edu_list):
            score += 5.0
        return min(score, 100.0)

    def _calc_keywords(self, raw_text: str) -> float:
        text_lower = raw_text.lower()
        matched_verbs = 0
        for verb in ATS_ACTION_VERBS:
            if re.search(rf"\b{verb}\b", text_lower):
                matched_verbs += 1
        
        # 8 action verbs -> 80 pts, 12+ verbs -> 100 pts
        verb_score = min(matched_verbs * 8.0, 100.0)
        return max(verb_score, 30.0)

    def _calc_formatting(self, raw_text: str, data: Dict[str, Any]) -> float:
        score = 80.0
        word_count = len(raw_text.split())
        
        # Ideal resume word count: 250 - 1000 words
        if word_count < 150:
            score -= 30.0  # Too sparse
        elif word_count > 1400:
            score -= 15.0  # Overly verbose
        else:
            score += 10.0

        # Bullet points presence
        if any(char in raw_text for char in ['•', '-', '▪', '*']):
            score += 10.0

        return min(max(score, 25.0), 100.0)

ats_engine = ATSScoringEngine()
