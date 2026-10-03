import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import fitz  # PyMuPDF
import docx
from backend.app.services.skill_extractor import skill_extractor

class ResumeParser:
    def __init__(self):
        self.email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        self.phone_regex = re.compile(r'(?:(?:\+|0{0,2})91(\s*[\- ]*\s*)?|[0]?)?[6789]\d{9}|(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})')
        self.degree_patterns = [
            r"\b(Ph\.?D|Doctorate)\b",
            r"\b(M\.?C\.?A|MCA|Master of Computer Applications)\b",
            r"\b(B\.?C\.?A|BCA|Bachelor of Computer Applications)\b",
            r"\b(M\.?Tech|M\.?E\.?|Master of Technology|Master of Engineering)\b",
            r"\b(B\.?Tech|B\.?E\.?|Bachelor of Technology|Bachelor of Engineering)\b",
            r"\b(M\.?S\.?|M\.?Sc|Master of Science)\b",
            r"\b(B\.?S\.?|B\.?Sc|Bachelor of Science)\b",
            r"\b(M\.?B\.?A|MBA|Master of Business Administration)\b",
            r"\b(B\.?B\.?A|BBA|Bachelor of Business Administration)\b",
            r"\b(Bachelor(?:'s)?|Master(?:'s)?|Diploma)\b"
        ]

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF (fitz) with block sorting."""
        text_content = []
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text_content.append(page.get_text("text"))
            doc.close()
        except Exception as e:
            # Fallback to pypdf if PyMuPDF fails
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            except Exception as e2:
                raise RuntimeError(f"Error reading PDF file: {e} | Fallback error: {e2}")
        
        return "\n".join(text_content)

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX including paragraphs and tables."""
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    full_text.append(para.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_data:
                        full_text.append(" | ".join(row_data))
            return "\n".join(full_text)
        except Exception as e:
            raise RuntimeError(f"Error reading DOCX file: {e}")

    def extract_name(self, text: str) -> str:
        """Extract candidate name heuristically from header lines."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:8]:
            # Skip if contains email, digits, URLs, common resume headers
            if self.email_regex.search(line) or re.search(r'\d{5,}', line) or "http" in line.lower():
                continue
            if re.search(r'\b(resume|curriculum|vitae|cv|page|summary|contact|profile)\b', line, re.IGNORECASE):
                continue
            # Candidate names are typically 2 to 4 words, mostly alphabetic
            words = line.split()
            if 2 <= len(words) <= 4 and all(re.match(r'^[A-Za-z.\'-]+$', w) for w in words):
                # Clean and return title-cased name
                return line.title()
        
        return "Candidate"

    def extract_email(self, text: str) -> Optional[str]:
        """Extract primary email address."""
        match = self.email_regex.search(text)
        return match.group(0).lower() if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        """Extract primary phone number."""
        match = self.phone_regex.search(text)
        if match:
            # Clean non-digit characters except leading plus
            cleaned = re.sub(r'[^\d+]', '', match.group(0))
            return cleaned
        return None

    def extract_location(self, text: str) -> Optional[str]:
        """Detect cities/states/locations."""
        common_cities = [
            "Bengaluru", "Bangalore", "Hyderabad", "Pune", "Mumbai", "Delhi", "Noida", 
            "Gurugram", "Gurgaon", "Chennai", "Kolkata", "Ahmedabad", "Jaipur", "Kochi", 
            "Indore", "Chandigarh", "San Francisco", "New York", "London", "Remote"
        ]
        for city in common_cities:
            if re.search(rf"\b{city}\b", text, re.IGNORECASE):
                return city
        return "Not Specified"

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract degrees, graduation years, and institutions."""
        education_entries = []
        lines = text.split("\n")
        
        for i, line in enumerate(lines):
            for deg_pat in self.degree_patterns:
                match = re.search(deg_pat, line, re.IGNORECASE)
                if match:
                    degree_name = match.group(0).strip()
                    # Look nearby for year (4 digits between 1990 and 2030)
                    context_chunk = " ".join(lines[max(0, i-1):min(len(lines), i+3)])
                    year_match = re.search(r'\b(19\d{2}|20[0-2]\d|2030)\b', context_chunk)
                    grad_year = year_match.group(0) if year_match else None
                    
                    # University/College detection
                    inst_match = re.search(
                        r'([A-Za-z\s]+(?:University|Institute|College|Academy|School|Campus)[A-Za-z\s]*)',
                        context_chunk,
                        re.IGNORECASE
                    )
                    institution = inst_match.group(1).strip() if inst_match else "Recognized Institution"

                    entry = {
                        "degree": degree_name,
                        "institution": institution[:80],
                        "year": grad_year
                    }
                    if not any(e["degree"].lower() == degree_name.lower() for e in education_entries):
                        education_entries.append(entry)
                    break

        return education_entries

    def estimate_experience_years(self, text: str) -> float:
        """Estimate total professional experience in years."""
        # 1. Direct statements like "3.5 years of experience", "4+ years experience"
        direct_match = re.search(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s*of)?\s*(?:total)?\s*experience', text, re.IGNORECASE)
        if direct_match:
            try:
                return float(direct_match.group(1))
            except ValueError:
                pass

        # 2. Date ranges like 2020 - 2023, 2021 to Present
        ranges = re.findall(r'\b(20[0-2]\d)\s*(?:-|–|to)\s*(20[0-2]\d|present|current)\b', text, re.IGNORECASE)
        total_months = 0
        current_year = 2026
        
        for start_str, end_str in ranges:
            start_yr = int(start_str)
            end_yr = current_year if end_str.lower() in ["present", "current"] else int(end_str)
            if end_yr >= start_yr:
                total_months += (end_yr - start_yr) * 12

        if total_months > 0:
            return round(min(total_months / 12.0, 30.0), 1)

        return 0.0

    def extract_experience_sections(self, text: str) -> List[Dict[str, Any]]:
        """Identify experience, roles, and companies."""
        roles_list = []
        titles = [
            "Software Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer",
            "Data Scientist", "Data Analyst", "Machine Learning Engineer", "DevOps Engineer",
            "Python Developer", "Java Developer", "Database Administrator", "System Engineer",
            "Project Intern", "Software Engineering Intern", "Web Developer", "QA Engineer"
        ]
        
        lines = text.split("\n")
        for i, line in enumerate(lines):
            for t in titles:
                if re.search(rf"\b{re.escape(t)}\b", line, re.IGNORECASE):
                    chunk = " ".join(lines[max(0, i):min(len(lines), i+4)])
                    roles_list.append({
                        "title": t,
                        "snippet": chunk[:200]
                    })
                    break
        return roles_list[:5]

    def extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract identified projects from resume text."""
        projects = []
        lines = text.split("\n")
        in_project_section = False
        current_project = None

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
            if re.search(r'^(projects?|academic projects?|key projects?)\b', trimmed, re.IGNORECASE):
                in_project_section = True
                continue
            if in_project_section:
                # Section boundary check
                if re.search(r'^(education|skills|certifications|experience|achievements|languages)\b', trimmed, re.IGNORECASE):
                    break
                # Project title usually starts with bullet or capitalized title
                if len(trimmed) > 5 and len(trimmed) < 60 and not trimmed.startswith(('•', '-', '*')):
                    if current_project:
                        projects.append(current_project)
                    current_project = {"title": trimmed, "description": ""}
                elif current_project and len(trimmed) > 10:
                    current_project["description"] += " " + trimmed

        if current_project:
            projects.append(current_project)

        # Truncate and clean
        for p in projects:
            p["description"] = p["description"].strip()[:300]
        return projects[:6]

    def extract_certifications(self, text: str) -> List[str]:
        """Extract listed certifications."""
        certs = []
        keywords = ["AWS Certified", "Azure", "GCP", "Certified Kubernetes", "TensorFlow Developer",
                    "Oracle Certified", "Cisco", "CCNA", "PMP", "Scrum Master", "Coursera", "HackerRank"]
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE):
                certs.append(kw)
        return certs

    def extract_achievements(self, text: str) -> List[str]:
        """Extract achievement statements."""
        achievements = []
        patterns = [
            r'(?:won|awarded|ranked|achieved|secured|published)\s+[^\.\n]+',
            r'(?:1st|2nd|3rd|first|second|top\s*\d+%?)\s+(?:place|rank|position|prize)[^\.\n]*'
        ]
        for p in patterns:
            for match in re.finditer(p, text, re.IGNORECASE):
                statement = match.group(0).strip()
                if 10 < len(statement) < 150:
                    achievements.append(statement)
        return list(set(achievements))[:4]

    def parse(self, file_path: str) -> Dict[str, Any]:
        """Main parsing function returning structured resume information."""
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            raw_text = self.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            raw_text = self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        skills_by_cat = skill_extractor.extract_skills(raw_text)
        exp_years = self.estimate_experience_years(raw_text)

        parsed_data = {
            "name": self.extract_name(raw_text),
            "email": self.extract_email(raw_text),
            "phone": self.extract_phone(raw_text),
            "location": self.extract_location(raw_text),
            "total_experience_years": exp_years,
            "skills": skills_by_cat,
            "education": self.extract_education(raw_text),
            "experience": self.extract_experience_sections(raw_text),
            "projects": self.extract_projects(raw_text),
            "certifications": self.extract_certifications(raw_text),
            "achievements": self.extract_achievements(raw_text),
            "languages": ["English"] if "english" in raw_text.lower() else []
        }

        return {
            "raw_text": raw_text,
            "parsed_data": parsed_data
        }

resume_parser = ResumeParser()
