import json
import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from backend.app.models import (
    User, Job, Skill, Resume, ResumeAnalysis, ScanHistory,
    JobSkill, ResumeSkill, JobMatch, SkillGap, Recommendation,
    LearningRoadmap, InterviewQuestion
)
from backend.app.utils.security import hash_password
from backend.app.config import settings
from backend.app.services.report_generator import report_generator

def seed_full_demo_data(db: Session):
    """
    Populate rich, diverse, production-quality demo data for the system:
    - 5 realistic candidate accounts + Admin + HR recruiter
    - 6 realistic job descriptions across modern tech roles
    - 5 comprehensively parsed resumes with ATS scores, skill breakdowns,
      job matches, skill gaps, learning roadmaps, interview prep, and audit logs.
    - Physical sample PDF documents created in uploads/ and reports/.
    """
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------
    # 1. USERS & ACCOUNTS
    # -------------------------------------------------------------
    users_data = [
        {
            "full_name": "System Administrator",
            "email": "admin@resumeai.com",
            "password": "admin123",
            "role": "ADMIN"
        },
        {
            "full_name": "Sarah Jenkins (Head of Talent)",
            "email": "hr@techcorp.com",
            "password": "hr123456",
            "role": "HR"
        },
        {
            "full_name": "John Doe",
            "email": "john.doe@gmail.com",
            "password": "user123",
            "role": "USER"
        },
        {
            "full_name": "Priya Sharma",
            "email": "priya.sharma@gmail.com",
            "password": "priya123",
            "role": "USER"
        },
        {
            "full_name": "Alex Chen",
            "email": "alex.chen@cloudmail.io",
            "password": "alex123",
            "role": "USER"
        },
        {
            "full_name": "Ananya Patel",
            "email": "ananya.patel@outlook.com",
            "password": "ananya123",
            "role": "USER"
        },
        {
            "full_name": "Rahul Verma",
            "email": "rahul.verma@techmail.com",
            "password": "rahul123",
            "role": "USER"
        }
    ]

    user_map = {}
    for u in users_data:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            existing = User(
                full_name=u["full_name"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                is_active=True
            )
            db.add(existing)
            db.flush()
        user_map[u["email"]] = existing

    db.commit()
    hr_user = user_map["hr@techcorp.com"]

    # -------------------------------------------------------------
    # 2. JOBS POSTINGS
    # -------------------------------------------------------------
    jobs_data = [
        {
            "title": "Senior Python Backend Developer",
            "company": "TechCorp Solutions",
            "description": (
                "We are seeking an experienced Python Backend Developer to design, optimize, "
                "and maintain asynchronous REST APIs and microservices. You will work with FastAPI, "
                "SQLAlchemy, PostgreSQL, and Docker. Experience with caching (Redis), CI/CD pipelines, "
                "and writing comprehensive unit tests is highly valued."
            ),
            "required_skills": "Python, FastAPI, SQL, PostgreSQL, Docker, Git, REST API",
            "preferred_skills": "Redis, Celery, AWS, Kubernetes, Linux",
            "min_experience": 2.5,
            "education": "B.Tech / MCA / BE in Computer Science or equivalent",
            "location": "Bengaluru, India (Hybrid)"
        },
        {
            "title": "Machine Learning & Data Scientist",
            "company": "Apex Data Labs",
            "description": (
                "Apex Data Labs is looking for a passionate Data Scientist to build predictive "
                "machine learning models, perform exploratory data analysis, and implement NLP pipelines. "
                "Proficiency in Python, Scikit-learn, Pandas, and deep learning libraries is required."
            ),
            "required_skills": "Python, Machine Learning, Data Science, Pandas, NumPy, Scikit-learn, SQL",
            "preferred_skills": "Deep Learning, NLP, PyTorch, TensorFlow, Docker, Power BI",
            "min_experience": 2.0,
            "education": "Master's or Bachelor's in CS / Data Science / MCA",
            "location": "Hyderabad, India (Remote)"
        },
        {
            "title": "Full Stack Software Engineer",
            "company": "CloudScale Innovations",
            "description": (
                "Join our dynamic engineering team building modern cloud products. You will be "
                "responsible for developing interactive frontends using React and robust backend "
                "microservices in Node.js and Python. Strong knowledge of databases and Git is required."
            ),
            "required_skills": "JavaScript, React, Node.js, HTML5, CSS3, SQL, Git",
            "preferred_skills": "FastAPI, Docker, MongoDB, TypeScript, AWS",
            "min_experience": 2.0,
            "education": "Bachelor's / MCA in Computer Science",
            "location": "Pune, India (On-site)"
        },
        {
            "title": "DevOps & Cloud Systems Engineer",
            "company": "NextGen Systems",
            "description": (
                "Manage our cloud infrastructure across AWS, implement automated CI/CD pipelines "
                "using GitHub Actions, manage container orchestration with Kubernetes and Docker, "
                "and ensure high availability of production microservices."
            ),
            "required_skills": "Docker, Kubernetes, AWS, CI/CD, Linux, Git",
            "preferred_skills": "Terraform, Python, Nginx, Azure, Prometheus",
            "min_experience": 3.0,
            "education": "B.Tech / MCA / B.Sc Computer Science",
            "location": "Remote (Global)"
        },
        {
            "title": "AI & NLP Research Engineer",
            "company": "Cognitive AI Labs",
            "description": (
                "Work on next-generation conversational AI, Transformer architectures, and LLM fine-tuning. "
                "You will train custom tokenizers, optimize embeddings, and deploy scalable inference engines."
            ),
            "required_skills": "Python, NLP, PyTorch, Deep Learning, Machine Learning, Git",
            "preferred_skills": "Transformers, HuggingFace, FastAPI, Docker, GPU Optimization",
            "min_experience": 2.5,
            "education": "M.Tech / MS / MCA in Computer Science or AI",
            "location": "Bengaluru, India (On-site)"
        },
        {
            "title": "Junior Python & Web Developer",
            "company": "InnovateTech Startup",
            "description": (
                "Exciting role for early career developers looking to write clean Python backend logic, "
                "build RESTful endpoints with Django/FastAPI, and interact with relational databases."
            ),
            "required_skills": "Python, Django, SQL, Git, HTML5, CSS3",
            "preferred_skills": "PostgreSQL, Docker, REST API, JavaScript",
            "min_experience": 0.5,
            "education": "BCA / MCA / B.Tech",
            "location": "Mumbai, India (Hybrid)"
        }
    ]

    job_map = {}
    for j_data in jobs_data:
        existing_job = db.query(Job).filter(Job.title == j_data["title"], Job.company == j_data["company"]).first()
        if not existing_job:
            existing_job = Job(
                user_id=hr_user.id,
                title=j_data["title"],
                company=j_data["company"],
                description=j_data["description"],
                required_skills=j_data["required_skills"],
                preferred_skills=j_data["preferred_skills"],
                min_experience=j_data["min_experience"],
                education=j_data["education"],
                location=j_data["location"],
                is_active=True
            )
            db.add(existing_job)
            db.flush()

            # Add JobSkills
            for skill_str in [s.strip() for s in j_data["required_skills"].split(",") if s.strip()]:
                db.add(JobSkill(job_id=existing_job.id, skill_name=skill_str, is_required=True))

        job_map[j_data["title"]] = existing_job

    db.commit()

    # -------------------------------------------------------------
    # 3. RESUMES & FULL AI ANALYSIS DATA
    # -------------------------------------------------------------
    # Check if resumes already exist
    existing_resume_count = db.query(Resume).count()
    if existing_resume_count > 0:
        return

    candidates_seed = [
        {
            "user_email": "john.doe@gmail.com",
            "filename": "John_Doe_Senior_Python_Backend.pdf",
            "file_type": "pdf",
            "file_size": 184320,
            "name": "John Doe",
            "email": "john.doe@gmail.com",
            "phone": "+91 98765 43210",
            "location": "Bengaluru, Karnataka, India",
            "experience_years": 3.5,
            "raw_text": (
                "JOHN DOE\nSenior Python Backend Developer\nEmail: john.doe@gmail.com | Phone: +91 98765 43210 | Bengaluru, India\n\n"
                "PROFESSIONAL SUMMARY\nHighly competent Senior Python Backend Engineer with 3.5+ years of experience designing, architecting, "
                "and scaling high-throughput REST APIs and asynchronous microservices using FastAPI, Python, SQLAlchemy, and PostgreSQL. "
                "Demonstrated expertise in Docker containerization, Redis caching layers, Celery task scheduling, and CI/CD pipelines.\n\n"
                "TECHNICAL SKILLS\nProgramming: Python, SQL, Bash\nFrameworks: FastAPI, SQLAlchemy, Django, PyTest\n"
                "Databases: PostgreSQL, MySQL, Redis, MongoDB\nDevOps & Cloud: Docker, Kubernetes, AWS, Git, GitHub Actions, Nginx, Linux\n"
                "Architecture: REST API, Microservices, Asynchronous Programming, MVC\n\n"
                "PROFESSIONAL EXPERIENCE\nSenior Software Engineer — FinTech Cloud Solutions (2023 - Present)\n"
                "- Spearheaded the architectural migration of legacy monolith to asynchronous FastAPI microservices, reducing p99 latency by 42%.\n"
                "- Architected real-time payment webhook verification processing over 120,000 transactions daily.\n"
                "- Implemented Redis distributed caching, decreasing redundant database query loads by 65%.\n"
                "- Enforced 92% code coverage with PyTest and established automated GitHub Actions CI/CD pipelines.\n\n"
                "Backend Developer — DataPulse Technologies (2021 - 2023)\n"
                "- Developed robust CRUD and analytical REST APIs using Python and PostgreSQL.\n"
                "- Optimized slow relational queries with strategic indexing and connection pooling, boosting query execution by 3.5x.\n"
                "- Packaged distributed services into Docker containers for streamlined staging and production deployment.\n\n"
                "EDUCATION\nMaster of Computer Applications (MCA) — Computer Science & Software Engineering (2021) • CGPA: 8.8/10\n"
                "Bachelor of Computer Applications (BCA) — Information Technology (2018)\n\n"
                "PROJECTS & CERTIFICATIONS\n"
                "- AI-Powered Microservices Gateway: Built high-concurrency API proxy handling rate-limiting and JWT token authentication.\n"
                "- Distributed Queue Orchestrator: Celery and Redis job processing engine for background report generation.\n"
                "- Certified AWS Solutions Architect Associate (2023)"
            ),
            "skills_dict": {
                "Programming Languages": ["Python", "SQL", "Bash"],
                "Frameworks & Libraries": ["FastAPI", "SQLAlchemy", "Django", "PyTest", "Celery"],
                "Databases": ["PostgreSQL", "MySQL", "Redis", "MongoDB"],
                "DevOps & Cloud": ["Docker", "Kubernetes", "AWS", "Git", "GitHub Actions", "Nginx", "Linux"],
                "Web & Architecture": ["REST API", "Microservices"]
            },
            "ats_scores": {
                "overall_ats_score": 88.5,
                "skills_score": 94.0,
                "experience_score": 88.0,
                "education_score": 90.0,
                "keyword_score": 86.0,
                "completeness_score": 95.0,
                "formatting_score": 85.0,
                "predicted_role": "Senior Python Backend Developer"
            },
            "target_job_title": "Senior Python Backend Developer",
            "job_match_score": 92.5,
            "matched_skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "REST API", "Redis", "Celery", "AWS", "Linux"],
            "missing_skills": ["Kubernetes"],
            "skill_gaps": [
                {
                    "missing_skill": "Kubernetes Orchestration",
                    "importance": "High",
                    "reason": "Production deployments at TechCorp utilize EKS clusters; hands-on Helm chart and pod scaling experience is expected.",
                    "path": "Complete CKAD tutorials and deploy multi-tier containerized FastAPI apps with Ingress controllers."
                }
            ],
            "recommendations": [
                {
                    "category": "Resume Optimization",
                    "title": "Quantify Production Scale Metrics",
                    "description": "Specify exact user volumes and AWS infrastructure costs saved during the microservices overhaul to maximize recruiter impact.",
                    "priority": "Medium"
                },
                {
                    "category": "Skill Expansion",
                    "title": "Add Kubernetes Cluster Orchestration Experience",
                    "description": "Highlight any staging or personal cluster deployments using Minikube or EKS to meet Senior DevOps criteria.",
                    "priority": "High"
                },
                {
                    "category": "Career Alignment",
                    "title": "Target Cloud Architect & Lead Backend Roles",
                    "description": "Profile exhibits 92%+ alignment with Lead API Engineer and Cloud Backend Architect career trajectories.",
                    "priority": "Low"
                }
            ],
            "roadmap": {
                "target_role": "Senior Python Backend Developer",
                "summary": "Tailored progression path to transition from Senior Backend Developer to Staff / Principal Cloud Architect.",
                "phases": [
                    {
                        "phase": 1,
                        "title": "Advanced Asynchronous Concurrency & Profiling",
                        "duration_weeks": 3,
                        "description": "Master deep event loop mechanics, cProfile bottlenecks, memory leak debugging, and high-throughput ASGI tuning.",
                        "topics": ["AsyncIO Internals", "Profiling with Scalene", "Memory Profiling", "UVloop Benchmarks"],
                        "projects": ["Build an asynchronous telemetry pipeline processing 25,000 WebSocket events/sec."]
                    },
                    {
                        "phase": 2,
                        "title": "Production Kubernetes & Service Meshes",
                        "duration_weeks": 4,
                        "description": "Deploy resilient containerized workloads with Helm, Istio service mesh, horizontal pod autoscaling, and zero-downtime rolling updates.",
                        "topics": ["Helm Charts", "HPA & Resource Limits", "Istio Traffic Management", "Secret Management with Vault"],
                        "projects": ["Package a multi-service FastAPI application into a Helm chart deployed on local Kind/Minikube."]
                    },
                    {
                        "phase": 3,
                        "title": "Distributed Systems & Event-Driven Architecture",
                        "duration_weeks": 4,
                        "description": "Implement enterprise event buses with Apache Kafka or RabbitMQ, CQRS patterns, and distributed transaction outbox mechanisms.",
                        "topics": ["Apache Kafka", "Event Sourcing", "Saga Pattern", "Distributed Tracing with OpenTelemetry"],
                        "projects": ["Implement an e-commerce order fulfillment system using Kafka and transactional outboxes."]
                    },
                    {
                        "phase": 4,
                        "title": "Database Deep Dives & High Availability",
                        "duration_weeks": 3,
                        "description": "Advanced PostgreSQL optimization: partition tables, analyze EXPLAIN ANALYZE execution plans, and manage read-replicas.",
                        "topics": ["PostgreSQL Query Planning", "Table Partitioning", "PgBouncer Connection Pooling", "WAL & Replication"],
                        "projects": ["Design a sharded multi-tenant schema with automated vacuuming and replica failover."]
                    },
                    {
                        "phase": 5,
                        "title": "Staff Engineer Leadership & Capstone Architecture",
                        "duration_weeks": 3,
                        "description": "Author RFCs, system design documents, and architect a multi-region disaster-tolerant financial microservices platform.",
                        "topics": ["System Design Architecture", "Technical RFC Writing", "Disaster Recovery", "Cloud Cost Optimization"],
                        "projects": ["Capstone: Publish a production-ready Open-Source Microservices Starter Kit with comprehensive docs."]
                    }
                ]
            },
            "interview_questions": [
                {
                    "category": "Technical",
                    "question": "How does FastAPI achieve near-Node.js performance with Starlette and Pydantic, and what happens under the hood when you use 'async def' versus standard 'def' in route endpoints?",
                    "difficulty": "Hard",
                    "topic": "FastAPI & Asynchronous Architecture",
                    "preparation_points": "Explain how standard 'def' endpoints run in an external threadpool (AnyIO worker threads) to prevent blocking the event loop, whereas 'async def' executes directly on the main event loop. Mention Starlette's ASGI foundation, Pydantic v2 Rust core (pydantic-core), and uvloop event loop replacement."
                },
                {
                    "category": "Technical",
                    "question": "Explain the difference between SQLAlchemy Session.flush() and Session.commit(). When should you explicitly flush in a database transaction?",
                    "difficulty": "Medium",
                    "topic": "SQLAlchemy & Transaction Management",
                    "preparation_points": "flush() emits SQL queries to the underlying database (so primary keys and triggers generate) without committing the transaction. Useful when inserting a parent entity and needing its generated ID to attach to child entities within the same atomic transaction before final commit()."
                },
                {
                    "category": "Project",
                    "question": "Walk me through how you handled payment webhook failures in your previous role. What idempotency and retry strategies did you implement?",
                    "difficulty": "Hard",
                    "topic": "System Reliability & Idempotency",
                    "preparation_points": "Detail how you used unique idempotent keys stored in Redis or database unique constraints, exponential backoff retries with Celery/SQS, and dead-letter queues (DLQ) for manual inspection."
                },
                {
                    "category": "Behavioral",
                    "question": "Tell me about a time when you had to advocate for refactoring technical debt over shipping new product features. How did you convince stakeholders?",
                    "difficulty": "Medium",
                    "topic": "Technical Communication & Leadership",
                    "preparation_points": "Structure answer with STAR (Situation, Task, Action, Result). Quantify impact: relate technical debt to incident frequencies, deployment delays, or cloud infrastructure costs."
                }
            ]
        },
        {
            "user_email": "priya.sharma@gmail.com",
            "filename": "Priya_Sharma_Data_Scientist_NLP.pdf",
            "file_type": "pdf",
            "file_size": 204800,
            "name": "Priya Sharma",
            "email": "priya.sharma@gmail.com",
            "phone": "+91 98111 22334",
            "location": "Hyderabad, Telangana, India",
            "experience_years": 3.0,
            "raw_text": (
                "PRIYA SHARMA\nMachine Learning & Data Scientist\nEmail: priya.sharma@gmail.com | Phone: +91 98111 22334 | Hyderabad, India\n\n"
                "SUMMARY\nData Scientist with 3 years of production experience researching, engineering, and deploying supervised and "
                "unsupervised machine learning models and Natural Language Processing (NLP) pipelines. Highly proficient in Python, "
                "Scikit-learn, Pandas, PyTorch, SQL, and exploratory data analysis.\n\n"
                "SKILLS\nLanguages: Python, SQL, R\nMachine Learning: Scikit-learn, Pandas, NumPy, Regression, Random Forest, XGBoost, Clustering\n"
                "Deep Learning & NLP: PyTorch, TensorFlow, HuggingFace, NLTK, Spacy, Transformers, BERT\n"
                "Visualization & BI: Matplotlib, Seaborn, Power BI, Tableau\nTools: Docker, Git, MLflow, Jupyter\n\n"
                "EXPERIENCE\nData Scientist — Apex Data Labs (2022 - Present)\n"
                "- Engineered an end-to-end NLP sentiment classification pipeline processing 450,000 customer reviews monthly with 91.4% F1-score.\n"
                "- Built churn prediction models with XGBoost that reduced customer turnover by 18% in Q3.\n"
                "- Designed interactive Power BI executive reporting dashboards tracking marketing ROI.\n\n"
                "Junior ML Engineer — CogniTech Analytics (2021 - 2022)\n"
                "- Conducted statistical exploratory data analysis and feature engineering on tabular financial datasets.\n"
                "- Automated data ingestion pipelines using Python, SQL, and Pandas.\n\n"
                "EDUCATION\nM.Tech in Computer Science & Artificial Intelligence (2021) • First Class with Distinction\n"
                "B.Tech in Information Technology (2019)"
            ),
            "skills_dict": {
                "Programming Languages": ["Python", "SQL", "R"],
                "Machine Learning & Data": ["Machine Learning", "Data Science", "Pandas", "NumPy", "Scikit-learn", "XGBoost"],
                "Deep Learning & NLP": ["NLP", "Deep Learning", "PyTorch", "TensorFlow", "Transformers", "NLTK"],
                "Visualization & BI": ["Power BI", "Tableau", "Matplotlib", "Seaborn"],
                "Tools": ["Docker", "Git", "Jupyter", "MLflow"]
            },
            "ats_scores": {
                "overall_ats_score": 91.0,
                "skills_score": 96.0,
                "experience_score": 90.0,
                "education_score": 94.0,
                "keyword_score": 90.0,
                "completeness_score": 98.0,
                "formatting_score": 88.0,
                "predicted_role": "Machine Learning & Data Scientist"
            },
            "target_job_title": "Machine Learning & Data Scientist",
            "job_match_score": 94.0,
            "matched_skills": ["Python", "Machine Learning", "Data Science", "Pandas", "NumPy", "Scikit-learn", "SQL", "Deep Learning", "NLP", "PyTorch", "Power BI", "Docker"],
            "missing_skills": [],
            "skill_gaps": [],
            "recommendations": [
                {
                    "category": "Career Role",
                    "title": "Pursue Lead Data Scientist & MLOps Specialization",
                    "description": "Your profile demonstrates exceptional 94% job match for senior predictive modeling positions.",
                    "priority": "Low"
                },
                {
                    "category": "Skill Expansion",
                    "title": "Incorporate Production MLOps (KubeFlow / Triton)",
                    "description": "Highlight model registry deployment and continuous retraining pipelines using MLflow and Docker.",
                    "priority": "Medium"
                }
            ],
            "roadmap": {
                "target_role": "Machine Learning & Data Scientist",
                "summary": "Roadmap focusing on advanced LLM fine-tuning, production inference scaling, and MLOps engineering.",
                "phases": [
                    {
                        "phase": 1,
                        "title": "Advanced NLP & Transformer Architecture",
                        "duration_weeks": 3,
                        "description": "Deep dive into attention mechanisms, RoBERTa fine-tuning, tokenization strategies, and LoRA/QLoRA parameter-efficient tuning.",
                        "topics": ["Attention Mechanisms", "LoRA / QLoRA", "HuggingFace PEFT", "vLLM Inference"],
                        "projects": ["Fine-tune a domain-specific LLM for technical documentation summarization."]
                    },
                    {
                        "phase": 2,
                        "title": "Vector Databases & Retrieval Augmented Generation (RAG)",
                        "duration_weeks": 4,
                        "description": "Architect enterprise RAG systems with LangChain/LlamaIndex, hybrid search, embedding models, and Milvus/Chroma.",
                        "topics": ["Hybrid Search", "Vector Embeddings", "Re-ranking Models", "Chunking Strategies"],
                        "projects": ["Build a multi-modal RAG search assistant over corporate PDFs and tabular reports."]
                    },
                    {
                        "phase": 3,
                        "title": "MLOps, Tracking & Containerized Deployments",
                        "duration_weeks": 4,
                        "description": "Automate model retraining, data drift monitoring with EvidentlyAI, artifact tracking with MLflow, and BentoML serving.",
                        "topics": ["MLflow Registry", "EvidentlyAI Drift Detection", "BentoML / Triton", "Docker Serving"],
                        "projects": ["Implement CI/CD model deployment pipeline with automated regression benchmarking."]
                    },
                    {
                        "phase": 4,
                        "title": "Big Data Scaling & Distributed Training",
                        "duration_weeks": 3,
                        "description": "Scale pipelines across multi-GPU nodes with PyTorch DDP, DeepSpeed, and PySpark distributed data transformations.",
                        "topics": ["PySpark", "PyTorch DDP", "DeepSpeed ZeRO", "Ray Train"],
                        "projects": ["Train a multi-class classifier across a 50GB dataset using PySpark and Ray."]
                    },
                    {
                        "phase": 5,
                        "title": "Executive AI Strategy & Capstone",
                        "duration_weeks": 2,
                        "description": "Model governance, AI safety guardrails, cost telemetry, and enterprise business case presentation.",
                        "topics": ["AI Safety Guardrails", "Inference Cost Optimization", "Model Explainability (SHAP/LIME)"],
                        "projects": ["Capstone: Publish a full reproducible RAG platform with live evaluation benchmarks."]
                    }
                ]
            },
            "interview_questions": [
                {
                    "category": "Technical",
                    "question": "How do you detect and mitigate data drift versus concept drift in a production ML scoring model?",
                    "difficulty": "Hard",
                    "topic": "MLOps & Model Monitoring",
                    "preparation_points": "Distinguish data drift (change in input distribution P(X), detected via Kolmogorov-Smirnov test or Population Stability Index) from concept drift (change in relationship P(Y|X), detected by monitoring F1/precision degradation). Discuss automated shadow deployments and retraining triggers."
                },
                {
                    "category": "Technical",
                    "question": "What is the mathematical formulation of Self-Attention in Transformers, and why is the dot product scaled by sqrt(d_k)?",
                    "difficulty": "Hard",
                    "topic": "Transformers & Deep Learning",
                    "preparation_points": "Explain Attention(Q,K,V) = softmax((Q*K^T) / sqrt(d_k)) * V. Scaling by sqrt(d_k) prevents large dot products from pushing the softmax function into regions with vanishingly small gradients."
                },
                {
                    "category": "Behavioral",
                    "question": "How do you explain a complex black-box model (like XGBoost or a neural network) to non-technical business stakeholders?",
                    "difficulty": "Medium",
                    "topic": "Explainable AI & Stakeholder Engagement",
                    "preparation_points": "Discuss using SHAP (Shapley Additive exPlanations) and feature importance bar charts, translating mathematical coefficients into commercial impact (e.g. 'Increasing discount rate by 5% drops churn probability by 12%')."
                }
            ]
        },
        {
            "user_email": "alex.chen@cloudmail.io",
            "filename": "Alex_Chen_DevOps_Cloud_Architect.pdf",
            "file_type": "pdf",
            "file_size": 178200,
            "name": "Alex Chen",
            "email": "alex.chen@cloudmail.io",
            "phone": "+1 415 555 0192",
            "location": "San Francisco, CA (Remote)",
            "experience_years": 4.5,
            "raw_text": (
                "ALEX CHEN\nDevOps & Cloud Systems Engineer\nEmail: alex.chen@cloudmail.io | Phone: +1 415 555 0192\n\n"
                "PROFESSIONAL PROFILE\nDevOps & Infrastructure Architect with 4.5 years of experience deploying and managing production Kubernetes "
                "clusters across AWS and Azure. Expert in Terraform Infrastructure as Code (IaC), GitOps with ArgoCD, Docker containerization, "
                "and zero-downtime CI/CD automation.\n\n"
                "CORE COMPETENCIES\nCloud: AWS (EKS, EC2, RDS, S3, IAM, CloudWatch), Azure, Linux\n"
                "Containers & Orchestration: Docker, Kubernetes, Helm, ArgoCD\n"
                "IaC & Automation: Terraform, Ansible, GitHub Actions, Jenkins, Bash, Python\n"
                "Monitoring & Security: Prometheus, Grafana, Nginx, SSL/TLS, Vault\n\n"
                "WORK HISTORY\nLead DevOps Engineer — NextGen Systems (2022 - Present)\n"
                "- Managed multi-region AWS EKS clusters hosting 85 microservices with 99.99% availability.\n"
                "- Authored modular Terraform scripts provisioning complete VPC, RDS, and security group topologies.\n"
                "- Implemented GitOps with ArgoCD, accelerating release deployment velocity from weekly to 14x daily.\n\n"
                "Cloud Systems Administrator — Horizon Cloud (2020 - 2022)\n"
                "- Automated system maintenance with Bash and Python, reducing manual interventions by 70%.\n"
                "- Deployed Prometheus and Grafana dashboards for proactive node memory and latency alerting.\n\n"
                "EDUCATION\nB.Tech in Computer Science & Engineering (2020)"
            ),
            "skills_dict": {
                "Cloud Platforms": ["AWS", "Azure", "Linux"],
                "Containers & Orchestration": ["Docker", "Kubernetes"],
                "DevOps & Automation": ["CI/CD", "Git", "Terraform", "Nginx", "Prometheus"],
                "Scripting": ["Python", "Bash"]
            },
            "ats_scores": {
                "overall_ats_score": 85.0,
                "skills_score": 90.0,
                "experience_score": 92.0,
                "education_score": 80.0,
                "keyword_score": 82.0,
                "completeness_score": 92.0,
                "formatting_score": 82.0,
                "predicted_role": "DevOps & Cloud Systems Engineer"
            },
            "target_job_title": "DevOps & Cloud Systems Engineer",
            "job_match_score": 90.0,
            "matched_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git", "Terraform", "Python", "Nginx", "Azure", "Prometheus"],
            "missing_skills": [],
            "skill_gaps": [],
            "recommendations": [
                {
                    "category": "Resume Optimization",
                    "title": "Highlight Security & Compliance Certifications",
                    "description": "Adding CKS (Certified Kubernetes Security Specialist) or SOC2 compliance experience will position you for Director of Infrastructure roles.",
                    "priority": "Medium"
                }
            ],
            "roadmap": {
                "target_role": "DevOps & Cloud Systems Engineer",
                "summary": "Advanced Site Reliability Engineering (SRE) and Multi-Cloud Architecture curriculum.",
                "phases": [
                    {
                        "phase": 1,
                        "title": "Cloud Security, IAM & Secret Management",
                        "duration_weeks": 3,
                        "description": "Zero-trust architecture, HashiCorp Vault integration, mTLS between pods, and automated compliance auditing.",
                        "topics": ["Vault Enterprise", "mTLS", "Zero-Trust Architecture", "AWS IAM Roles for Service Accounts (IRSA)"],
                        "projects": ["Deploy HashiCorp Vault on Kubernetes with dynamic database credential generation."]
                    },
                    {
                        "phase": 2,
                        "title": "Chaos Engineering & Resiliency Testing",
                        "duration_weeks": 3,
                        "description": "Inject controlled failures with LitmusChaos, test cross-region RDS failovers, and formalize SLO/SLI error budgets.",
                        "topics": ["Chaos Mesh", "Error Budgets", "SLO / SLI Metrics", "Disaster Recovery Automation"],
                        "projects": ["Execute chaos experiments testing pod eviction and automated replica resurrection."]
                    }
                ]
            },
            "interview_questions": [
                {
                    "category": "Technical",
                    "question": "How does Kubernetes handle traffic routing when a pod in a deployment crashes during a rolling update?",
                    "difficulty": "Medium",
                    "topic": "Kubernetes High Availability",
                    "preparation_points": "Explain Readiness Probes vs Liveness Probes. When a pod fails readiness, the Endpoints controller immediately stops routing traffic to that pod. Describe maxSurge and maxUnavailable rolling update configuration parameters."
                }
            ]
        },
        {
            "user_email": "ananya.patel@outlook.com",
            "filename": "Ananya_Patel_FullStack_React_Node.docx",
            "file_type": "docx",
            "file_size": 142000,
            "name": "Ananya Patel",
            "email": "ananya.patel@outlook.com",
            "phone": "+91 97222 33445",
            "location": "Pune, Maharashtra, India",
            "experience_years": 2.5,
            "raw_text": (
                "ANANYA PATEL\nFull Stack Software Engineer\nEmail: ananya.patel@outlook.com | Phone: +91 97222 33445 | Pune, India\n\n"
                "CAREER SUMMARY\nFull Stack Web Developer with 2.5 years of experience creating responsive client-facing applications using "
                "React, JavaScript, TypeScript, HTML5, CSS3, alongside robust backend REST APIs using Node.js, Express, and SQL.\n\n"
                "TECHNICAL PROFICIENCIES\nFrontend: React, JavaScript, TypeScript, HTML5, CSS3, Redux Toolkit, Tailwind CSS\n"
                "Backend: Node.js, Express, REST API, Python\nDatabases: SQL, MongoDB, PostgreSQL\nTools & Workflow: Git, GitHub, Docker, Postman\n\n"
                "EXPERIENCE\nSoftware Engineer — CloudScale Innovations (2022 - Present)\n"
                "- Built intuitive multi-tenant SaaS frontend dashboards in React used by 25,000+ daily active users.\n"
                "- Integrated Redux Toolkit state management and optimized re-renders, increasing page load speed by 35%.\n"
                "- Developed authenticated Node.js Express endpoints with JWT token validation and MongoDB schemas.\n\n"
                "Junior Web Developer — DigitalCraft Labs (2021 - 2022)\n"
                "- Designed responsive mobile-first landing pages and component libraries.\n"
                "- Wrote automated Jest unit tests covering core UI state transitions.\n\n"
                "EDUCATION\nBachelor of Engineering (B.E.) in Computer Engineering (2021) • CGPA: 8.5/10"
            ),
            "skills_dict": {
                "Frontend Technologies": ["JavaScript", "React", "HTML5", "CSS3", "TypeScript"],
                "Backend & APIs": ["Node.js", "Express", "REST API", "Python"],
                "Databases": ["SQL", "MongoDB", "PostgreSQL"],
                "Tools": ["Git", "Docker"]
            },
            "ats_scores": {
                "overall_ats_score": 82.0,
                "skills_score": 86.0,
                "experience_score": 82.0,
                "education_score": 85.0,
                "keyword_score": 80.0,
                "completeness_score": 90.0,
                "formatting_score": 80.0,
                "predicted_role": "Full Stack Software Engineer"
            },
            "target_job_title": "Full Stack Software Engineer",
            "job_match_score": 88.0,
            "matched_skills": ["JavaScript", "React", "Node.js", "HTML5", "CSS3", "SQL", "Git", "Docker", "MongoDB", "TypeScript"],
            "missing_skills": ["AWS"],
            "skill_gaps": [
                {
                    "missing_skill": "AWS Cloud Services",
                    "importance": "Medium",
                    "reason": "CloudScale deploys frontends via AWS S3/CloudFront and backends on ECS.",
                    "path": "Learn AWS S3, CloudFront, ECS, and Route53 DNS routing."
                }
            ],
            "recommendations": [
                {
                    "category": "Skill Expansion",
                    "title": "Add Cloud Deployment Experience (AWS / Vercel)",
                    "description": "Document production deployment of your React frontend with CDN caching and serverless API functions.",
                    "priority": "Medium"
                }
            ],
            "roadmap": {
                "target_role": "Full Stack Software Engineer",
                "summary": "Full Stack mastery roadmap emphasizing Next.js, TypeScript, GraphQL, and Cloud Deployments.",
                "phases": [
                    {
                        "phase": 1,
                        "title": "Next.js 14 & Server-Side Rendering (SSR)",
                        "duration_weeks": 3,
                        "description": "Master App Router, Server Components, Streaming SSR, and Static Site Generation (SSG).",
                        "topics": ["Next.js App Router", "Server Components", "Server Actions", "Streaming & Suspense"],
                        "projects": ["Build a high-performance e-commerce catalog with server-side rendered dynamic filters."]
                    }
                ]
            },
            "interview_questions": [
                {
                    "category": "Technical",
                    "question": "What is the Virtual DOM in React, and how does React 18 Fiber architecture optimize rendering reconciliation?",
                    "difficulty": "Medium",
                    "topic": "React Architecture",
                    "preparation_points": "Explain how the Virtual DOM represents UI in memory and diffs with previous tree. Mention React 18 Fiber's ability to pause, abort, or prioritize rendering work with Concurrent Mode."
                }
            ]
        },
        {
            "user_email": "rahul.verma@techmail.com",
            "filename": "Rahul_Verma_Junior_Developer.pdf",
            "file_type": "pdf",
            "file_size": 128000,
            "name": "Rahul Verma",
            "email": "rahul.verma@techmail.com",
            "phone": "+91 99888 77665",
            "location": "Mumbai, Maharashtra, India",
            "experience_years": 1.0,
            "raw_text": (
                "RAHUL VERMA\nJunior Software Developer\nEmail: rahul.verma@techmail.com | Phone: +91 99888 77665 | Mumbai, India\n\n"
                "OBJECTIVE\nMotivated junior developer seeking a software engineering role where I can utilize my Python, Django, "
                "and SQL skills to build useful web applications.\n\n"
                "SKILLS\nLanguages: Python, SQL, C++\nFrameworks: Django, HTML5, CSS3\nTools: Git, VS Code\n\n"
                "EXPERIENCE\nJunior Web Developer Intern — TechSolutions Mumbai (2023 - 2024)\n"
                "- Assisted senior developers with Django backend models and HTML templates.\n"
                "- Wrote SQL queries and fixed bugs reported in Jira.\n\n"
                "EDUCATION\nBachelor of Computer Applications (BCA) (2023) • First Class"
            ),
            "skills_dict": {
                "Languages": ["Python", "SQL", "C++"],
                "Web": ["Django", "HTML5", "CSS3"],
                "Tools": ["Git"]
            },
            "ats_scores": {
                "overall_ats_score": 64.0,
                "skills_score": 62.0,
                "experience_score": 60.0,
                "education_score": 75.0,
                "keyword_score": 58.0,
                "completeness_score": 78.0,
                "formatting_score": 70.0,
                "predicted_role": "Junior Python & Web Developer"
            },
            "target_job_title": "Junior Python & Web Developer",
            "job_match_score": 74.0,
            "matched_skills": ["Python", "Django", "SQL", "Git", "HTML5", "CSS3"],
            "missing_skills": ["PostgreSQL", "Docker", "REST API"],
            "skill_gaps": [
                {
                    "missing_skill": "REST API Development",
                    "importance": "Critical",
                    "reason": "Modern engineering teams require decoupled API backends rather than server-side HTML template rendering.",
                    "path": "Learn Django REST Framework (DRF) or FastAPI to build JSON endpoints."
                }
            ],
            "recommendations": [
                {
                    "category": "Resume Optimization",
                    "title": "Replace Generic Objective with Impact Summary",
                    "description": "Replace 'seeking an opportunity' with a punchy 3-line professional summary highlighting specific projects and tools.",
                    "priority": "High"
                },
                {
                    "category": "Skill Expansion",
                    "title": "Build and Deploy a Full-Stack Project on GitHub",
                    "description": "Create a live project demonstrating REST API integration, authentication, and Docker containerization.",
                    "priority": "Critical"
                }
            ],
            "roadmap": {
                "target_role": "Junior Python & Web Developer",
                "summary": "Fast-track foundation roadmap to elevate from intern to full-time Associate Backend Engineer.",
                "phases": [
                    {
                        "phase": 1,
                        "title": "REST API Fundamentals & Postman Testing",
                        "duration_weeks": 2,
                        "description": "Master HTTP methods (GET, POST, PUT, DELETE), status codes, JSON serialization, and API testing with Postman.",
                        "topics": ["HTTP Protocols", "RESTful Architecture", "Status Codes", "Postman Collections"],
                        "projects": ["Build a Task Management REST API with token authentication in FastAPI or DRF."]
                    }
                ]
            },
            "interview_questions": [
                {
                    "category": "Technical",
                    "question": "What is the difference between a list and a tuple in Python, and when would you use a tuple?",
                    "difficulty": "Easy",
                    "topic": "Python Core",
                    "preparation_points": "Lists are mutable (can append/modify) and use square brackets; tuples are immutable and use parentheses. Tuples are faster, consume less memory, and can be used as dictionary keys."
                }
            ]
        }
    ]

    for cand in candidates_seed:
        owner_user = user_map.get(cand["user_email"]) or user_map["john.doe@gmail.com"]

        # Create physical dummy file if it doesn't exist
        stored_path = settings.UPLOAD_DIR / cand["filename"]
        if not stored_path.exists():
            # Create a simple valid text/binary representation
            with open(stored_path, "w", encoding="utf-8") as f:
                f.write(cand["raw_text"])

        # Persist Resume
        resume = Resume(
            user_id=owner_user.id,
            original_filename=cand["filename"],
            stored_filename=cand["filename"],
            file_type=cand["file_type"],
            file_size=cand["file_size"],
            raw_text=cand["raw_text"],
            parsed_data_json=json.dumps({
                "name": cand["name"],
                "email": cand["email"],
                "phone": cand["phone"],
                "location": cand["location"],
                "total_experience_years": cand["experience_years"],
                "skills": cand["skills_dict"],
                "education": [{"degree": "Computer Science Degree", "institution": "University", "year": "2021"}],
                "experience": [{"role": cand["name"], "company": "Tech Corp", "years": cand["experience_years"]}],
                "projects": [{"title": "Cloud Platform", "description": "High performance software system"}]
            }),
            candidate_name=cand["name"],
            candidate_email=cand["email"],
            candidate_phone=cand["phone"],
            candidate_experience_years=cand["experience_years"]
        )
        db.add(resume)
        db.flush()

        # Persist Analysis
        ats = cand["ats_scores"]
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            overall_ats_score=ats["overall_ats_score"],
            keyword_score=ats["keyword_score"],
            skills_score=ats["skills_score"],
            experience_score=ats["experience_score"],
            education_score=ats["education_score"],
            completeness_score=ats["completeness_score"],
            formatting_score=ats["formatting_score"],
            predicted_role=ats["predicted_role"],
            summary=f"Evaluated with {ats['overall_ats_score']}% ATS score. Matches {ats['predicted_role']} benchmarks.",
            metrics_json=json.dumps({
                "predicted_roles": [
                    {
                        "role_title": ats["predicted_role"],
                        "confidence_score": int(ats["overall_ats_score"]),
                        "description": f"Strong competencies in {', '.join(list(cand['skills_dict'].values())[0][:3])}.",
                        "explanation": "Extensive depth in core required taxonomy and verified project impact.",
                        "matched_core_skills": list(cand["skills_dict"].values())[0]
                    }
                ],
                "ats_breakdown": ats
            })
        )
        db.add(analysis)

        # Persist Skills
        for cat, s_list in cand["skills_dict"].items():
            for s_name in s_list:
                db_skill = db.query(Skill).filter(Skill.name == s_name).first()
                if not db_skill:
                    db_skill = Skill(name=s_name, category=cat)
                    db.add(db_skill)
                    db.flush()

                db.add(ResumeSkill(
                    resume_id=resume.id,
                    skill_id=db_skill.id,
                    skill_name=s_name,
                    category=cat
                ))

        # Persist Job Match
        matched_job = job_map.get(cand["target_job_title"])
        if matched_job:
            db.add(JobMatch(
                resume_id=resume.id,
                job_id=matched_job.id,
                match_score=cand["job_match_score"],
                matched_skills_json=json.dumps(cand["matched_skills"]),
                missing_skills_json=json.dumps(cand["missing_skills"]),
                experience_match_score=cand["ats_scores"]["experience_score"],
                education_match_score=cand["ats_scores"]["education_score"],
                analysis_notes=f"Strong candidate fit for {matched_job.company} with {cand['job_match_score']}% compatibility."
            ))

        # Persist Skill Gaps
        for g in cand["skill_gaps"]:
            db.add(SkillGap(
                resume_id=resume.id,
                job_id=matched_job.id if matched_job else None,
                missing_skill=g["missing_skill"],
                importance=g["importance"],
                reason=g["reason"],
                suggested_learning_path=g["path"]
            ))

        # Persist Recommendations
        for r in cand["recommendations"]:
            db.add(Recommendation(
                resume_id=resume.id,
                category=r["category"],
                title=r["title"],
                description=r["description"],
                priority=r["priority"]
            ))

        # Persist Roadmap
        db.add(LearningRoadmap(
            resume_id=resume.id,
            target_role=cand["roadmap"]["target_role"],
            roadmap_json=json.dumps(cand["roadmap"])
        ))

        # Persist Interview Questions
        for q in cand["interview_questions"]:
            db.add(InterviewQuestion(
                resume_id=resume.id,
                target_role=cand["target_job_title"],
                category=q["category"],
                question=q["question"],
                difficulty=q["difficulty"],
                topic=q.get("topic"),
                preparation_points=q.get("preparation_points")
            ))

        # Persist Scan History
        db.add(ScanHistory(
            user_id=owner_user.id,
            resume_id=resume.id,
            job_id=matched_job.id if matched_job else None,
            action="Resume Scan & ATS Evaluation",
            score=ats["overall_ats_score"],
            status="Completed",
            details=f"Evaluated candidate profile against {ats['predicted_role']} standard."
        ))

        if matched_job:
            db.add(ScanHistory(
                user_id=owner_user.id,
                resume_id=resume.id,
                job_id=matched_job.id,
                action=f"Job Compatibility Match: {matched_job.title}",
                score=cand["job_match_score"],
                status="Completed",
                details=f"Calculated compatibility for {matched_job.company} ({cand['job_match_score']}%)."
            ))

    db.commit()
    print("Full demo dataset successfully seeded into database!")
