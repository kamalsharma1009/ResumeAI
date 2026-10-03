import re
from typing import Dict, Any, List

class ResumeRecommendationEngine:
    def generate_recommendations(self, parsed_data: Dict[str, Any], raw_text: str) -> List[Dict[str, Any]]:
        """Generate targeted, actionable improvement suggestions based on resume evaluation."""
        recommendations = []

        # 1. Measurable impact / Metrics check
        metrics_found = re.findall(r'\b(?:\d+%(?:\.\d+)?|\$\d+|\d+x|\d+\+?\s*(?:users|clients|requests|ms|seconds|hours))\b', raw_text, re.IGNORECASE)
        if len(metrics_found) < 2:
            recommendations.append({
                "category": "Measurable Achievements",
                "title": "Add Quantifiable Metrics and Results",
                "description": "Recruiters and ATS algorithms favor resumes that demonstrate concrete impact. Quantify outcomes with metrics such as 'improved query response times by 35%' or 'reduced manual processing from 4 hours to 15 minutes'.",
                "priority": "High"
            })

        # 2. Action verbs check
        lowered = raw_text.lower()
        weak_verbs = ["worked on", "responsible for", "helped in", "did", "assisted with"]
        has_weak_verbs = any(wv in lowered for wv in weak_verbs)
        if has_weak_verbs:
            recommendations.append({
                "category": "Impact Language",
                "title": "Replace Passive Phrases with Dynamic Action Verbs",
                "description": "Avoid passive phrasing like 'responsible for' or 'assisted with'. Instead, begin bullet points with strong power verbs such as 'Spearheaded', 'Architected', 'Automated', 'Engineered', or 'Optimized'.",
                "priority": "Medium"
            })

        # 3. Skills categorization
        skills_dict = parsed_data.get("skills", {})
        total_skills = sum(len(s) for s in skills_dict.values())
        if total_skills < 8:
            recommendations.append({
                "category": "Skills Section",
                "title": "Expand Core Technical Skills Inventory",
                "description": f"Only {total_skills} skills were detected. Add a distinct 'Technical Skills' section grouped into Languages, Frameworks, Databases, and Developer Tools to maximize keyword discoverability.",
                "priority": "High"
            })
        elif len(skills_dict.keys()) < 3:
            recommendations.append({
                "category": "Skills Section",
                "title": "Group Skills into Clear Subcategories",
                "description": "Organize your technical skills into distinct subcategories (e.g., Programming Languages, Frameworks & Libraries, Databases, Cloud & DevOps) to improve recruiter readability.",
                "priority": "Low"
            })

        # 4. Project descriptions check
        projects = parsed_data.get("projects", [])
        if len(projects) < 2:
            recommendations.append({
                "category": "Projects",
                "title": "Highlight at least 2 to 3 In-Depth Projects",
                "description": "Showcase real-world projects featuring modern tech stacks, live deployment links, GitHub repository URLs, and brief summaries of the architectural challenges solved.",
                "priority": "High"
            })
        else:
            short_descs = [p for p in projects if len(p.get("description", "")) < 40]
            if short_descs:
                recommendations.append({
                    "category": "Projects",
                    "title": "Adopt STAR / PAR Formula in Project Descriptions",
                    "description": "Provide context on the Problem, Action taken, and Result achieved for each project, and explicitly list the libraries, databases, and APIs utilized.",
                    "priority": "Medium"
                })

        # 5. Education completeness
        education = parsed_data.get("education", [])
        missing_years = [e for e in education if not e.get("year")]
        if missing_years:
            recommendations.append({
                "category": "Education",
                "title": "Specify Graduation Year and Degree Specialization",
                "description": "Ensure your degree entries include the graduation year or expected completion date alongside university name and academic CGPA/percentage if strong.",
                "priority": "Low"
            })

        # 6. Certifications check
        certs = parsed_data.get("certifications", [])
        if not certs:
            recommendations.append({
                "category": "Professional Credentials",
                "title": "Add Industry Certifications or Badges",
                "description": "Include credentials such as AWS Certified Cloud Practitioner, Azure Fundamentals, HackerRank Problem Solving, or accredited Coursera/DeepLearning.AI certificates.",
                "priority": "Medium"
            })

        # 7. Summary / LinkedIn presence
        if "linkedin.com" not in lowered and "github.com" not in lowered:
            recommendations.append({
                "category": "Contact & Links",
                "title": "Include Hyperlinks to GitHub and LinkedIn",
                "description": "Add clickable, professional links to your active GitHub profile and customized LinkedIn URL at the top of your resume contact header.",
                "priority": "Medium"
            })

        return recommendations

recommendation_engine = ResumeRecommendationEngine()
