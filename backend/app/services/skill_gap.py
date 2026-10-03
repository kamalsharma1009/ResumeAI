from typing import Dict, Any, List

SKILL_IMPORTANCE_MAP: Dict[str, Dict[str, str]] = {
    "Docker": {
        "importance": "Critical",
        "reason": "Standard industry containerization tool for reproducible deployments and microservices.",
        "path": "Learn Docker basics, Dockerfile syntax, multi-stage builds, and Docker Compose by containerizing a full-stack app."
    },
    "Kubernetes": {
        "importance": "High",
        "reason": "Essential for container orchestration, scaling, and modern cloud-native architectures.",
        "path": "Understand pods, deployments, services, ingress, and practice with minikube or k3s."
    },
    "AWS": {
        "importance": "Critical",
        "reason": "Leading cloud provider used in modern enterprise infrastructure (EC2, S3, RDS, Lambda).",
        "path": "Study AWS Certified Cloud Practitioner / Solutions Architect concepts; deploy a live app on EC2 with RDS."
    },
    "Azure": {
        "importance": "High",
        "reason": "Dominant enterprise cloud platform for hybrid infrastructure and active directory integrations.",
        "path": "Explore Azure App Services, Azure Blob Storage, Azure SQL, and AZ-900 certification material."
    },
    "CI/CD": {
        "importance": "High",
        "reason": "Crucial for automated testing, linting, and continuous delivery in production teams.",
        "path": "Configure GitHub Actions workflows to run unit tests and automatically deploy to cloud."
    },
    "FastAPI": {
        "importance": "High",
        "reason": "High-performance Python asynchronous web framework with automatic OpenAPI docs.",
        "path": "Build asynchronous REST APIs with Pydantic validation, dependency injection, and SQLAlchemy 2.0."
    },
    "React": {
        "importance": "Critical",
        "reason": "Most widely requested frontend library for interactive, single-page web applications.",
        "path": "Master functional components, React Hooks (useState, useEffect, useContext), and state management."
    },
    "Node.js": {
        "importance": "High",
        "reason": "Event-driven runtime powering backend microservices and modern build tools.",
        "path": "Build asynchronous RESTful APIs using Express or NestJS, integrate with MongoDB or PostgreSQL."
    },
    "Machine Learning": {
        "importance": "Critical",
        "reason": "Core foundation for predictive modeling, classification, and AI-driven automation.",
        "path": "Review Supervised vs Unsupervised learning algorithms, train Scikit-learn models, evaluate with precision/recall."
    },
    "Deep Learning": {
        "importance": "High",
        "reason": "Underpins modern computer vision, NLP, and neural network applications.",
        "path": "Learn PyTorch or TensorFlow, build CNNs for image classification and transformers for text analysis."
    },
    "NLP": {
        "importance": "High",
        "reason": "Key discipline for text processing, sentiment analysis, entity extraction, and LLM applications.",
        "path": "Master spaCy, NLTK, TF-IDF, embeddings, and Hugging Face transformer tokenizers."
    },
    "SQL": {
        "importance": "Critical",
        "reason": "Fundamental database querying and manipulation standard across all software & data roles.",
        "path": "Practice complex joins, subqueries, indexing, window functions, and query optimization."
    },
    "PostgreSQL": {
        "importance": "High",
        "reason": "Advanced open-source relational database favored for enterprise data integrity and JSON support.",
        "path": "Learn relational schema design, transactions, indexing, foreign keys, and EXPLAIN ANALYZE."
    },
    "MongoDB": {
        "importance": "Medium",
        "reason": "NoSQL document database widely used for agile prototyping and schema-less data.",
        "path": "Study MongoDB aggregation pipelines, indexing, and Mongoose/Motor asynchronous drivers."
    },
    "Git": {
        "importance": "Critical",
        "reason": "Essential version control tool required by 100% of software engineering teams.",
        "path": "Practice branching strategies, rebasing, pull requests, resolving merge conflicts, and commit hygiene."
    },
    "Power BI": {
        "importance": "High",
        "reason": "Top business intelligence dashboarding tool for executive decision-making and KPI reporting.",
        "path": "Learn DAX formulas, Power Query data transformation, and building interactive drill-down dashboards."
    },
    "Tableau": {
        "importance": "High",
        "reason": "Industry standard data visualization platform for interactive business reporting.",
        "path": "Learn calculated fields, parameters, storyboards, and interactive dashboard publishing."
    }
}

class SkillGapAnalyzer:
    def analyze_gaps(self, missing_skills: List[str], target_role: str = "") -> List[Dict[str, Any]]:
        """
        Generate detailed skill gap analysis for missing skills with importance,
        reasons, and step-by-step learning paths.
        """
        gaps = []
        for skill in missing_skills:
            info = SKILL_IMPORTANCE_MAP.get(skill)
            if info:
                gaps.append({
                    "missing_skill": skill,
                    "importance": info["importance"],
                    "reason": info["reason"],
                    "suggested_learning_path": info["path"]
                })
            else:
                # Default intelligent fallback for other skills
                gaps.append({
                    "missing_skill": skill,
                    "importance": "Medium",
                    "reason": f"Frequently required technical competency for modern {target_role or 'software & data'} workflows.",
                    "suggested_learning_path": f"Study official documentation for {skill}, complete guided exercises, and implement a mini-project showcasing its practical usage."
                })
        
        # Sort by importance: Critical first, then High, then Medium
        importance_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        gaps.sort(key=lambda x: importance_order.get(x["importance"], 4))
        return gaps

skill_gap_analyzer = SkillGapAnalyzer()
