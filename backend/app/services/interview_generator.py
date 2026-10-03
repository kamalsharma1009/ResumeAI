from typing import Dict, Any, List

class InterviewQuestionGenerator:
    def generate_questions(
        self,
        parsed_data: Dict[str, Any],
        target_role: str = "Software Engineer"
    ) -> List[Dict[str, Any]]:
        """
        Generate contextual interview questions across Technical, HR,
        Project, and Behavioral categories tailored to the candidate's profile.
        """
        questions = []
        
        # Flatten skills
        detected_skills = []
        for cat_skills in parsed_data.get("skills", {}).values():
            detected_skills.extend(cat_skills)
        skills_set = set(detected_skills)
        projects = parsed_data.get("projects", [])

        # 1. Technical Questions based on detected skills
        if "Python" in skills_set:
            questions.append({
                "category": "Technical",
                "topic": "Python Core & Internals",
                "difficulty": "Medium",
                "question": "How does memory management and garbage collection work in Python, and how does the GIL affect multithreading vs multiprocessing?",
                "preparation_points": "Explain reference counting, cyclical garbage collector (gc module), and how GIL restricts execution to one native thread at a time. Highlight when to use multiprocessing vs asyncio."
            })
            questions.append({
                "category": "Technical",
                "topic": "Python Optimization",
                "difficulty": "Easy",
                "question": "What is the difference between Python generators and lists, and when would you choose a generator for performance?",
                "preparation_points": "Focus on lazy evaluation, memory efficiency with the `yield` keyword, and handling large data streams without loading everything into RAM."
            })

        if "SQL" in skills_set or "MySQL" in skills_set or "PostgreSQL" in skills_set:
            questions.append({
                "category": "Technical",
                "topic": "Databases & SQL Optimization",
                "difficulty": "Medium",
                "question": "How do B-Tree indexes work in relational databases, and what strategies would you use to diagnose and optimize a slow query?",
                "preparation_points": "Mention EXPLAIN / EXPLAIN ANALYZE, composite indexes, avoiding SELECT *, identifying full table scans, and evaluating query execution plans."
            })

        if "FastAPI" in skills_set or "Django" in skills_set or "Flask" in skills_set:
            questions.append({
                "category": "Technical",
                "topic": "API Architecture",
                "difficulty": "Hard",
                "question": f"In {target_role}, how do you design secure, rate-limited RESTful APIs with token-based authentication and database connection pooling?",
                "preparation_points": "Discuss JWT validation middleware, SQLAlchemy connection pool tuning (pool_size, max_overflow, pool_pre_ping), and handling CORS and input validation with Pydantic."
            })

        if "Machine Learning" in skills_set or "Data Science" in skills_set:
            questions.append({
                "category": "Technical",
                "topic": "Machine Learning Evaluation",
                "difficulty": "Medium",
                "question": "When evaluating an imbalanced classification problem, why is accuracy misleading, and which metrics should you prioritize?",
                "preparation_points": "Discuss Precision, Recall, F1-score, PR-AUC vs ROC-AUC, confusion matrix analysis, and resampling strategies like SMOTE."
            })

        if "Docker" in skills_set or "Cloud" in str(skills_set):
            questions.append({
                "category": "Technical",
                "topic": "Containerization & Cloud",
                "difficulty": "Medium",
                "question": "Explain the concept of multi-stage Docker builds and how they contribute to minimal image size and enhanced security.",
                "preparation_points": "Discuss separating the compilation/build environment from runtime dependencies, reducing image attack surface, and caching layers."
            })

        # Fallback technical questions if few skills detected
        if len(questions) < 3:
            questions.append({
                "category": "Technical",
                "topic": "Data Structures & Algorithms",
                "difficulty": "Medium",
                "question": "How do hash tables achieve average O(1) time complexity, and how are hash collisions handled?",
                "preparation_points": "Explain hash functions, separate chaining (linked lists/trees), open addressing (linear/quadratic probing), and load factor resizing."
            })

        # 2. Project-based Questions
        if projects:
            top_project = projects[0]
            p_title = top_project.get("title", "your major project")
            questions.append({
                "category": "Project",
                "topic": f"Architecture: {p_title}",
                "difficulty": "Medium",
                "question": f"In your project '{p_title}', what was the most complex technical hurdle you encountered and how did you architect a solution?",
                "preparation_points": "Structure answer using the STAR method (Situation, Task, Action, Result). State the initial problem, trade-offs of alternative approaches, and measurable success metrics."
            })
            if len(projects) > 1:
                p2_title = projects[1].get("title", "secondary project")
                questions.append({
                    "category": "Project",
                    "topic": "Tech Stack Decisions",
                    "difficulty": "Easy",
                    "question": f"Why did you choose the specific libraries and frameworks for '{p2_title}' over competing technologies?",
                    "preparation_points": "Demonstrate technical maturity by discussing speed of development, ecosystem maturity, community support, and performance characteristics."
                })
        else:
            questions.append({
                "category": "Project",
                "topic": "Software Lifecycle",
                "difficulty": "Medium",
                "question": "Describe an end-to-end software application you designed from scratch. How did you structure testing and version control?",
                "preparation_points": "Discuss modular component design, branch protection rules in Git, test coverage with pytest, and deployment automation."
            })

        # 3. Behavioral Questions
        questions.append({
            "category": "Behavioral",
            "topic": "Conflict Resolution & Collaboration",
            "difficulty": "Medium",
            "question": "Tell me about a time you had a technical disagreement with a team member or peer. How did you arrive at a constructive consensus?",
            "preparation_points": "Show emotional intelligence, active listening, reliance on data/benchmarks rather than ego, and prioritizing team velocity and project health."
        })
        questions.append({
            "category": "Behavioral",
            "topic": "Handling Ambiguity & Tight Deadlines",
            "difficulty": "Medium",
            "question": "Can you describe a situation where project requirements changed abruptly close to a deadline? How did you prioritize and execute?",
            "preparation_points": "Focus on rapid triage of essential vs nice-to-have features, transparent stakeholder communication, and maintaining code quality under pressure."
        })

        # 4. HR & Culture Questions
        questions.append({
            "category": "HR",
            "topic": "Career Goals & Motivation",
            "difficulty": "Easy",
            "question": f"What specifically attracts you to the {target_role} path, and where do you envision your technical expertise evolving over the next 2-3 years?",
            "preparation_points": "Connect your passion for problem-solving with continuous learning, mastering modern cloud architectures, and delivering measurable enterprise value."
        })
        questions.append({
            "category": "HR",
            "topic": "Strengths & Growth Areas",
            "difficulty": "Easy",
            "question": "What is one area of technology where you actively felt challenged recently, and what proactive steps did you take to master it?",
            "preparation_points": "Choose a genuine technical skill, explain your systematic learning process (documentation, tutorials, coding experiments), and mention the tangible result."
        })

        return questions

interview_generator = InterviewQuestionGenerator()
