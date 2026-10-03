import os
import datetime
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from backend.app.config import settings

class ReportGenerator:
    def generate_pdf_report(
        self,
        resume_id: int,
        candidate_info: Dict[str, Any],
        ats_scores: Dict[str, float],
        skills_by_category: Dict[str, List[str]],
        predicted_roles: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        job_match: Dict[str, Any] = None,
        skill_gaps: List[Dict[str, Any]] = None,
        target_role: str = ""
    ) -> str:
        """
        Generate a professional executive PDF report summarizing the resume scan,
        ATS analytics, skill gaps, role predictions, and recommendations.
        Returns the absolute filepath of the generated PDF.
        """
        report_filename = f"report_resume_{resume_id}_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = settings.REPORT_DIR / report_filename

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom palette: Deep Blue #0F172A, Primary Accent #3B82F6, Slate #64748B
        primary_color = colors.HexColor("#0F172A")
        accent_color = colors.HexColor("#2563EB")
        light_bg = colors.HexColor("#F8FAFC")
        text_dark = colors.HexColor("#1E293B")
        text_muted = colors.HexColor("#64748B")

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=primary_color,
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=text_muted
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=accent_color,
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=text_dark
        )
        badge_style = ParagraphStyle(
            'Badge',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1D4ED8")
        )
        score_val_style = ParagraphStyle(
            'ScoreVal',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=24,
            textColor=accent_color,
            alignment=1
        )
        score_lbl_style = ParagraphStyle(
            'ScoreLbl',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=text_muted,
            alignment=1
        )

        story = []

        # 1. Header Banner
        header_table_data = [
            [
                Paragraph("<b>AI RESUME INTELLIGENCE REPORT</b>", title_style),
                Paragraph(f"<b>Report ID:</b> RES-{resume_id:05d}<br/><b>Generated:</b> {datetime.datetime.utcnow().strftime('%b %d, %Y')}", subtitle_style)
            ]
        ]
        header_table = Table(header_table_data, colWidths=[380, 160])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=6, spaceAfter=12))

        # 2. Candidate Overview Card
        cand_name = candidate_info.get("name", "Candidate")
        cand_email = candidate_info.get("email", "Not provided")
        cand_phone = candidate_info.get("phone", "Not provided")
        cand_exp = f"{candidate_info.get('total_experience_years', 0.0)} Years"
        cand_loc = candidate_info.get("location", "Not Specified")

        cand_card_data = [
            [
                Paragraph(f"<b>Candidate:</b> {cand_name}", body_style),
                Paragraph(f"<b>Email:</b> {cand_email}", body_style),
            ],
            [
                Paragraph(f"<b>Phone:</b> {cand_phone}", body_style),
                Paragraph(f"<b>Est. Experience:</b> {cand_exp}", body_style),
            ],
            [
                Paragraph(f"<b>Location:</b> {cand_loc}", body_style),
                Paragraph(f"<b>Target/Suggested Role:</b> {target_role or predicted_roles[0]['role_title'] if predicted_roles else 'Software Engineer'}", body_style),
            ]
        ]
        cand_table = Table(cand_card_data, colWidths=[270, 270])
        cand_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_bg),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(cand_table)
        story.append(Spacer(1, 10))

        # 3. ATS Score Breakdown Section
        story.append(Paragraph("AI ATS-STYLE SCORE BREAKDOWN", section_heading))
        
        overall = ats_scores.get("overall_ats_score", 0.0)
        score_boxes_data = [
            [
                Paragraph(f"{overall}%", score_val_style),
                Paragraph(f"{ats_scores.get('skills_score', 0)}%", score_val_style),
                Paragraph(f"{ats_scores.get('experience_score', 0)}%", score_val_style),
                Paragraph(f"{ats_scores.get('education_score', 0)}%", score_val_style),
                Paragraph(f"{ats_scores.get('keyword_score', 0)}%", score_val_style),
                Paragraph(f"{ats_scores.get('completeness_score', 0)}%", score_val_style),
            ],
            [
                Paragraph("OVERALL ATS", score_lbl_style),
                Paragraph("SKILLS", score_lbl_style),
                Paragraph("EXPERIENCE", score_lbl_style),
                Paragraph("EDUCATION", score_lbl_style),
                Paragraph("KEYWORDS", score_lbl_style),
                Paragraph("COMPLETENESS", score_lbl_style),
            ]
        ]
        score_table = Table(score_boxes_data, colWidths=[90]*6)
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 10))

        # 4. Job Match (if present)
        if job_match:
            story.append(Paragraph("TARGET JOB DESCRIPTION MATCH ANALYSIS", section_heading))
            jm_score = job_match.get("match_score", 0)
            jm_job = job_match.get("job_title", "Custom Job Description")
            jm_comp = job_match.get("company", "Company")
            matched_s = ", ".join(job_match.get("matched_skills", [])) or "None detected"
            missing_s = ", ".join(job_match.get("missing_skills", [])) or "None"

            jm_data = [
                [Paragraph(f"<b>Job:</b> {jm_job} ({jm_comp})", body_style), Paragraph(f"<b>Match Score:</b> {jm_score}%", badge_style)],
                [Paragraph(f"<b>Matched Skills:</b> {matched_s}", body_style), Paragraph(f"<b>Missing Skills:</b> {missing_s}", body_style)],
            ]
            jm_table = Table(jm_data, colWidths=[360, 180])
            jm_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#DBEAFE")),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
            ]))
            story.append(jm_table)
            story.append(Spacer(1, 10))

        # 5. Detected Skills by Category
        story.append(Paragraph("EXTRACTED SKILLS & COMPETENCIES", section_heading))
        skill_rows = []
        for cat, s_list in skills_by_category.items():
            if s_list:
                skill_rows.append([
                    Paragraph(f"<b>{cat}</b>", body_style),
                    Paragraph(", ".join(s_list), body_style)
                ])
        
        if not skill_rows:
            skill_rows.append([Paragraph("Skills", body_style), Paragraph("No specific skills identified from dictionary.", body_style)])

        skills_table = Table(skill_rows, colWidths=[150, 390])
        skills_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(skills_table)
        story.append(Spacer(1, 10))

        # 6. Top AI Suggested Career Roles
        if predicted_roles:
            story.append(Paragraph("AI SUGGESTED CAREER ROLES", section_heading))
            role_rows = [["Role Title", "Compatibility", "Matching Analysis"]]
            for r in predicted_roles[:3]:
                role_rows.append([
                    Paragraph(f"<b>{r.get('role_title')}</b>", body_style),
                    Paragraph(f"<b>{r.get('confidence_score')}%</b>", badge_style),
                    Paragraph(r.get('explanation', ''), body_style)
                ])
            role_table = Table(role_rows, colWidths=[130, 80, 330])
            role_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(role_table)
            story.append(Spacer(1, 10))

        # 7. Actionable Recommendations
        if recommendations:
            story.append(Paragraph("TARGETED RESUME IMPROVEMENTS", section_heading))
            rec_rows = [["Priority", "Area", "Actionable Recommendation"]]
            for rec in recommendations[:4]:
                pri = rec.get("priority", "Medium")
                pri_color = colors.HexColor("#DC2626") if pri == "High" else colors.HexColor("#D97706")
                rec_rows.append([
                    Paragraph(f"<b>{pri}</b>", ParagraphStyle('p', parent=body_style, textColor=pri_color)),
                    Paragraph(f"<b>{rec.get('title')}</b>", body_style),
                    Paragraph(rec.get('description', ''), body_style)
                ])
            rec_table = Table(rec_rows, colWidths=[65, 145, 330])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(rec_table)

        # Build document
        doc.build(story)
        return str(output_path)

report_generator = ReportGenerator()
