import re
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

class SAGEDocsHelper:
    """Helper class for searching and answering questions from SAGE documentation"""
    
    def __init__(self, docs_file_path: str = "docs/llms.md"):
        self.docs_file_path = docs_file_path
        self.docs_content = ""
        self.sections = {}
        self.faqs = {}
        self._load_documentation()
        self._setup_faqs()
    
    def _load_documentation(self):
        try:
            docs_path = Path(self.docs_file_path)
            if docs_path.exists():
                with open(docs_path, 'r', encoding='utf-8') as f:
                    self.docs_content = f.read()
                self._parse_sections()
                logger.info(f"Loaded documentation from {self.docs_file_path}")
            else:
                logger.warning(f"Documentation file {self.docs_file_path} not found")
        except Exception as e:
            logger.error(f"Error loading documentation: {e}")
    
    def _parse_sections(self):
        if not self.docs_content:
            return
        sections = re.split(r'\n(#{1,2})\s+(.+)', self.docs_content)
        current_section = ""
        current_content = ""
        for i in range(0, len(sections), 3):
            if i + 2 < len(sections):
                header_level = sections[i + 1] if i + 1 < len(sections) else ""
                header_text = sections[i + 2] if i + 2 < len(sections) else ""
                content = sections[i] if i < len(sections) else ""
                if header_text:
                    if current_section:
                        self.sections[current_section] = current_content
                    current_section = header_text.strip()
                    current_content = content
                else:
                    current_content += content
        if current_section:
            self.sections[current_section] = current_content
    
    def _setup_faqs(self):
        self.faqs = {
            # ... (copy FAQ dict from sage_mcp.py) ...
        }
    
    def search_docs(self, query: str, max_results: int = 3) -> List[Tuple[str, str, float]]:
        if not self.docs_content:
            return []
        query_lower = query.lower()
        query_words = re.findall(r'\w+', query_lower)
        results = []
        for section_name, content in self.sections.items():
            content_lower = content.lower()
            score = 0
            if query_lower in content_lower:
                score += 100
            for word in query_words:
                if word in content_lower:
                    score += 10
                if word in section_name.lower():
                    score += 20
            if any(word in section_name.lower() for word in query_words):
                score += 50
            if score > 0:
                preview = content[:500] + "..." if len(content) > 500 else content
                results.append((section_name, preview, score))
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:max_results]
    
    def get_faq_answer(self, topic: str) -> str:
        if topic.lower() in self.faqs:
            faq = self.faqs[topic.lower()]
            return f"**{faq['question']}**\n\n{faq['answer']}"
        return ""
    
    def list_faq_topics(self) -> str:
        topics = list(self.faqs.keys())
        return "Available FAQ topics:\n" + "\n".join(f"- {topic}" for topic in topics)
    
    def search_and_answer(self, question: str) -> str:
        question_lower = question.lower()
        faq_matches = []
        for topic, faq in self.faqs.items():
            if any(word in question_lower for word in topic.split('_')):
                faq_matches.append(topic)
        response_parts = []
        if faq_matches:
            response_parts.append("## Quick Answer (FAQ):")
            for topic in faq_matches[:2]:
                response_parts.append(self.get_faq_answer(topic))
                response_parts.append("")
        search_results = self.search_docs(question)
        if search_results:
            response_parts.append("## Additional Documentation:")
            for i, (section, content, score) in enumerate(search_results, 1):
                response_parts.append(f"**{i}. {section}**")
                response_parts.append(content)
                response_parts.append("")
        if not response_parts:
            return f"I couldn't find specific information about '{question}' in the documentation. " + \
                   f"Try asking about: {', '.join(self.faqs.keys())} or contact us for help."
        return "\n".join(response_parts) 