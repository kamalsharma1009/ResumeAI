import re
from typing import Dict, List, Set, Tuple

# Comprehensive taxonomy of skills mapped to categories
SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "Programming Languages": {
        "Python": ["python", "python3", "py"],
        "Java": ["java", "core java", "j2ee"],
        "C++": ["c++", "cpp"],
        "C": [r"\bc\b"],
        "C#": ["c#", "csharp", ".net c#"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "TypeScript": ["typescript", "ts"],
        "PHP": ["php"],
        "Ruby": ["ruby", "ruby on rails"],
        "Go": ["golang", r"\bgo\b"],
        "Rust": ["rust"],
        "Kotlin": ["kotlin"],
        "Swift": ["swift"],
        "R": [r"\br\b", "r-programming"],
        "Scala": ["scala"],
        "SQL": ["sql", "t-sql", "pl/sql"],
        "Shell/Bash": ["bash", "shell scripting", "powershell", "sh"]
    },
    "Frameworks & Web": {
        "React": ["react", "react.js", "reactjs"],
        "Node.js": ["node.js", "nodejs", "node"],
        "FastAPI": ["fastapi"],
        "Django": ["django"],
        "Flask": ["flask"],
        "Spring Boot": ["spring boot", "springboot", "spring framework"],
        "Express": ["express.js", "expressjs", "express"],
        "Angular": ["angular", "angularjs"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Next.js": ["next.js", "nextjs"],
        "ASP.NET": ["asp.net", ".net core", "dotnet"],
        "HTML5": ["html", "html5"],
        "CSS3": ["css", "css3", "sass", "scss", "tailwind", "tailwindcss", "bootstrap"]
    },
    "Databases": {
        "MySQL": ["mysql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "MongoDB": ["mongodb", "mongo"],
        "SQLite": ["sqlite", "sqlite3"],
        "Redis": ["redis"],
        "Oracle": ["oracle", "oracle db"],
        "Cassandra": ["cassandra"],
        "Firebase": ["firebase", "firestore"],
        "Elasticsearch": ["elasticsearch"]
    },
    "Cloud & DevOps": {
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "Azure": ["azure", "microsoft azure"],
        "Google Cloud": ["gcp", "google cloud platform", "google cloud"],
        "Git": ["git"],
        "GitHub": ["github"],
        "GitLab": ["gitlab"],
        "CI/CD": ["ci/cd", "ci-cd", "continuous integration", "github actions"],
        "Jenkins": ["jenkins"],
        "Linux": ["linux", "ubuntu", "centos", "redhat"],
        "Terraform": ["terraform"],
        "Nginx": ["nginx"]
    },
    "Data Science & AI/ML": {
        "Machine Learning": ["machine learning", "ml", "supervised learning", "unsupervised learning"],
        "Deep Learning": ["deep learning", "dl", "neural networks", "cnn", "rnn", "lstm"],
        "NLP": ["nlp", "natural language processing", "spacy", "nltk", "transformers"],
        "Data Science": ["data science"],
        "Data Analytics": ["data analytics", "data analysis", "eda"],
        "Scikit-learn": ["scikit-learn", "sklearn"],
        "TensorFlow": ["tensorflow", "tf"],
        "PyTorch": ["pytorch"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Keras": ["keras"],
        "Computer Vision": ["computer vision", "opencv"],
        "Generative AI": ["genai", "generative ai", "llm", "large language models", "prompt engineering"]
    },
    "Business & Tools": {
        "Power BI": ["power bi", "powerbi"],
        "Tableau": ["tableau"],
        "Excel": ["excel", "ms excel", "advanced excel", "vlookup"],
        "Jira": ["jira"],
        "Postman": ["postman"],
        "Agile": ["agile", "scrum", "kanban"],
        "Figma": ["figma"]
    },
    "Soft Skills": {
        "Communication": ["communication", "verbal communication", "written communication"],
        "Leadership": ["leadership", "team leadership", "mentoring"],
        "Problem Solving": ["problem solving", "critical thinking", "troubleshooting", "analytical skills"],
        "Teamwork": ["teamwork", "collaboration", "cross-functional"],
        "Time Management": ["time management", "organization", "multitasking"],
        "Adaptability": ["adaptability", "flexibility", "fast learner"]
    }
}

class SkillExtractor:
    def __init__(self):
        # Precompile regex patterns for each canonical skill
        self.compiled_skills = []
        for category, skills_dict in SKILL_TAXONOMY.items():
            for canonical_name, patterns in skills_dict.items():
                regex_list = []
                for p in patterns:
                    if p.startswith(r"\b"):
                        regex_list.append(p)
                    else:
                        escaped = re.escape(p)
                        regex_list.append(rf"\b{escaped}\b")
                combined_pattern = re.compile("|".join(regex_list), re.IGNORECASE)
                self.compiled_skills.append((canonical_name, category, combined_pattern))

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all recognized skills from resume or job text and categorize them.
        Returns a dictionary mapping category -> list of detected skill names.
        """
        if not text:
            return {}

        extracted_by_cat: Dict[str, Set[str]] = {cat: set() for cat in SKILL_TAXONOMY.keys()}
        lowered_text = text.lower()

        for canonical_name, category, pattern in self.compiled_skills:
            if pattern.search(lowered_text):
                extracted_by_cat[category].add(canonical_name)

        # Convert sets to sorted lists, remove empty categories
        return {
            category: sorted(list(skills))
            for category, skills in extracted_by_cat.items()
            if skills
        }

    def extract_all_skills_flat(self, text: str) -> List[str]:
        """Extract a flattened unique list of all detected skills."""
        by_cat = self.extract_skills(text)
        all_skills = []
        for s_list in by_cat.values():
            all_skills.extend(s_list)
        return sorted(list(set(all_skills)))

skill_extractor = SkillExtractor()
