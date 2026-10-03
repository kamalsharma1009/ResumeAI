from typing import Dict, Any, List

ROLE_ROADMAP_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "Python Developer": [
        {
            "phase": 1,
            "title": "Python Core & Advanced Concepts",
            "duration_weeks": 3,
            "description": "Master clean code, OOP, generators, decorators, async/await, and typing.",
            "topics": ["Type hinting & Pydantic", "Asyncio & concurrency", "Decorators & Context Managers", "Pytest & Unit Testing"],
            "projects": ["Build an asynchronous web scraper with rate limiting and retry backoff"]
        },
        {
            "phase": 2,
            "title": "API Frameworks & Databases",
            "duration_weeks": 4,
            "description": "Construct high-performance RESTful APIs with FastAPI and relational database modeling.",
            "topics": ["FastAPI dependency injection & middleware", "SQLAlchemy 2.0 ORM & Alembic migrations", "PostgreSQL indexing & query tuning", "JWT Auth & Security best practices"],
            "projects": ["Production-ready E-commerce or Analytics REST API with OAuth2 and PostgreSQL"]
        },
        {
            "phase": 3,
            "title": "Caching, Background Jobs & Microservices",
            "duration_weeks": 3,
            "description": "Scale backend systems using Redis caching, message queues, and async worker tasks.",
            "topics": ["Redis caching patterns", "Celery / RQ task workers", "RabbitMQ / Kafka basics", "Docker containerization"],
            "projects": ["Distributed background report generator processing asynchronous queues with Redis & Celery"]
        },
        {
            "phase": 4,
            "title": "Cloud Deployment & CI/CD",
            "duration_weeks": 2,
            "description": "Containerize, deploy to cloud infrastructure, and set up continuous integration.",
            "topics": ["Docker multi-stage builds", "GitHub Actions CI/CD pipelines", "AWS ECS / EC2 deployment", "Monitoring with Prometheus & Grafana"],
            "projects": ["Automated deployment of containerized Python API to cloud with health checks"]
        },
        {
            "phase": 5,
            "title": "System Design & Interview Mastery",
            "duration_weeks": 2,
            "description": "Prepare for technical coding interviews and distributed system design discussions.",
            "topics": ["Data Structures & Algorithms in Python", "High-level System Design (Load balancing, Caching, Sharding)", "Mock Technical Coding Interviews"],
            "projects": ["Design a scalable URL shortener or Notification service"]
        }
    ],
    "Data Scientist": [
        {
            "phase": 1,
            "title": "Data Wrangling & Statistical Foundations",
            "duration_weeks": 3,
            "description": "Establish deep fluency in statistical analysis, hypothesis testing, and pandas data manipulation.",
            "topics": ["Pandas & NumPy data manipulation", "Exploratory Data Analysis (EDA)", "Descriptive & Inferential Statistics", "Data Visualization with Seaborn & Plotly"],
            "projects": ["Comprehensive EDA on a financial or healthcare dataset with actionable findings"]
        },
        {
            "phase": 2,
            "title": "Machine Learning Algorithms & Scikit-learn",
            "duration_weeks": 4,
            "description": "Implement classical supervised and unsupervised ML models with rigorous validation.",
            "topics": ["Linear/Logistic Regression, Decision Trees, Random Forests, XGBoost", "Feature Engineering & Dimensionality Reduction (PCA)", "Cross-Validation, Precision/Recall, ROC-AUC", "Handling Imbalanced Datasets"],
            "projects": ["Customer Churn Prediction model with feature importance and business impact analysis"]
        },
        {
            "phase": 3,
            "title": "Deep Learning & NLP / Computer Vision",
            "duration_weeks": 4,
            "description": "Train neural networks using PyTorch for unstructured text and image data.",
            "topics": ["PyTorch tensors and autograd", "Feedforward & Convolutional Neural Networks", "Transformers & Hugging Face tokenizers", "Transfer Learning"],
            "projects": ["Sentiment analysis classifier or document tagger using pre-trained BERT embeddings"]
        },
        {
            "phase": 4,
            "title": "MLOps & Model Deployment",
            "duration_weeks": 3,
            "description": "Package models into interactive APIs and deploy them for live inference.",
            "topics": ["FastAPI inference endpoints", "MLflow experiment tracking", "Docker for ML", "Streamlit dashboard prototyping"],
            "projects": ["Interactive ML Web App with live inference and interactive model parameter tuning"]
        }
    ],
    "Full Stack Developer": [
        {
            "phase": 1,
            "title": "Modern JavaScript/TypeScript & Frontend Core",
            "duration_weeks": 3,
            "description": "Master modern ES6+, TypeScript typings, DOM manipulation, and responsive CSS.",
            "topics": ["ES6+ syntax & TypeScript interfaces", "Modern CSS (Flexbox, Grid, CSS Variables)", "Fetch API & Asynchronous programming", "Component thinking"],
            "projects": ["Interactive portfolio with theme switcher and real-time API integrations"]
        },
        {
            "phase": 2,
            "title": "React & State Management",
            "duration_weeks": 4,
            "description": "Build single-page apps with React Hooks, component lifecycles, and client routing.",
            "topics": ["React Hooks (useState, useEffect, useMemo, useCallback)", "Client-side routing with React Router", "Context API / Zustand state management", "Form validation & UI component libraries"],
            "projects": ["Full-featured Kanban Board or Task Management Dashboard"]
        },
        {
            "phase": 3,
            "title": "Backend Engineering with Node.js & Databases",
            "duration_weeks": 4,
            "description": "Construct REST APIs using Node.js/Express, connect to PostgreSQL or MongoDB, and implement auth.",
            "topics": ["Express.js routing & middleware", "PostgreSQL with Prisma/TypeORM or MongoDB with Mongoose", "JWT Authentication & bcrypt", "File uploads & cloud storage"],
            "projects": ["Full-stack social or collaboration platform with authentication and real-time updates"]
        },
        {
            "phase": 4,
            "title": "Production Deployment, Testing & Optimization",
            "duration_weeks": 2,
            "description": "Deploy full-stack applications, configure CI/CD, and optimize performance.",
            "topics": ["Docker & Docker Compose", "Deployment to Vercel/Render/AWS", "Lighthouse web performance optimization", "End-to-end testing with Playwright"],
            "projects": ["Live production deployment of your capstone full-stack SaaS application"]
        }
    ]
}

class RoadmapGenerator:
    def generate_roadmap(
        self,
        current_skills: List[str],
        target_role: str = "Python Developer",
        missing_skills: List[str] = None
    ) -> Dict[str, Any]:
        """Generate structured phase-by-phase learning roadmap for the candidate."""
        missing_skills = missing_skills or []
        
        # Match closest role template or construct intelligent hybrid
        template = ROLE_ROADMAP_TEMPLATES.get(target_role)
        if not template:
            # Default to Python Developer / Software Engineer structure
            template = ROLE_ROADMAP_TEMPLATES["Python Developer"]

        # Adapt phases to incorporate missing skills
        customized_phases = []
        for phase_info in template:
            p = {
                "phase": phase_info["phase"],
                "title": phase_info["title"],
                "duration_weeks": phase_info["duration_weeks"],
                "description": phase_info["description"],
                "topics": list(phase_info["topics"]),
                "projects": list(phase_info["projects"])
            }
            # Inject relevant missing skills into phase 2 or 3
            if p["phase"] in [2, 3] and missing_skills:
                relevant_missing = [s for s in missing_skills if s not in p["topics"]][:2]
                if relevant_missing:
                    p["topics"].extend(relevant_missing)
            customized_phases.append(p)

        summary = (
            f"Tailored {sum(p['duration_weeks'] for p in customized_phases)}-week mastery curriculum "
            f"designed to elevate candidate competencies towards the target {target_role} standard."
        )

        return {
            "target_role": target_role,
            "summary": summary,
            "phases": customized_phases
        }

roadmap_generator = RoadmapGenerator()
