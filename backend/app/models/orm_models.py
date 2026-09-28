import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class SearchQuery(Base):
    """1. SEARCH QUERY Entity
    Represents a search query, target keyword, search intent, date, and location.
    """
    __tablename__ = "search_queries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    query = Column(String(500), nullable=False, index=True)
    target_keyword = Column(String(255), nullable=False, index=True)
    search_intent = Column(String(50), nullable=False, default="informational")  # informational, commercial, transactional, navigational
    date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    location = Column(String(100), nullable=True, default="Global")

    # Relationships
    ranking_records = relationship("RankingHistory", back_populates="search_query", cascade="all, delete-orphan")
    citations = relationship("ContentCitationInfo", back_populates="search_query")
    user_interactions = relationship("UserInteraction", back_populates="search_query")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "query": self.query,
            "target_keyword": self.target_keyword,
            "search_intent": self.search_intent,
            "date": self.date.isoformat() if self.date else None,
            "location": self.location,
            "results_count": len(self.ranking_records) if self.ranking_records else 0,
        }


class Website(Base):
    """2. WEBSITE Entity
    Represents an evaluated website or competitor.
    Stores domain, title, URL, content topic, and SEO observations.
    """
    __tablename__ = "websites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    content_topic = Column(String(255), nullable=False, default="General")
    
    # Flexible JSON storage for live/point-in-time SEO observations:
    # (word count, interactive widget flags, video previews, schema types, readability score, etc.)
    seo_observations = Column(JSON, nullable=False, default=dict)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    ranking_history = relationship("RankingHistory", back_populates="website", cascade="all, delete-orphan", order_by="RankingHistory.date")
    optimizations = relationship("SEOOptimization", back_populates="website", cascade="all, delete-orphan", order_by="SEOOptimization.date")
    competitor_events = relationship("CompetitorHistory", back_populates="competitor", cascade="all, delete-orphan", order_by="CompetitorHistory.date")
    outcomes = relationship("Outcome", back_populates="website", cascade="all, delete-orphan", order_by="Outcome.date")
    citations = relationship("ContentCitationInfo", back_populates="website")
    user_interactions = relationship("UserInteraction", back_populates="website")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "url": self.url,
            "content_topic": self.content_topic,
            "seo_observations": self.seo_observations or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RankingHistory(Base):
    """3. RANKING HISTORY Entity
    Stores historical ranking entries over time for a website on a keyword.
    """
    __tablename__ = "ranking_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    website_id = Column(String(36), ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    search_query_id = Column(String(36), ForeignKey("search_queries.id", ondelete="SET NULL"), nullable=True, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    position = Column(Integer, nullable=False)
    previous_position = Column(Integer, nullable=True)
    change_in_position = Column(Integer, nullable=False, default=0)  # Positive = improved (e.g. #8 to #3 is +5)

    # Relationships
    website = relationship("Website", back_populates="ranking_history")
    search_query = relationship("SearchQuery", back_populates="ranking_records")

    __table_args__ = (
        Index("idx_website_keyword_date", "website_id", "keyword", "date"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "website_id": self.website_id,
            "domain": self.website.domain if self.website else None,
            "search_query_id": self.search_query_id,
            "keyword": self.keyword,
            "date": self.date.isoformat() if self.date else None,
            "position": self.position,
            "previous_position": self.previous_position,
            "change_in_position": self.change_in_position,
        }


class SEOOptimization(Base):
    """4. SEO OPTIMIZATION Entity
    Records an intentional SEO action taken on a website:
    type, description, reason, expected effect, and observed effect.
    """
    __tablename__ = "seo_optimizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    website_id = Column(String(36), ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    optimization_type = Column(String(100), nullable=False, index=True)  # content_depth, interactive_ux, schema_markup, etc.
    description = Column(Text, nullable=False)
    reason_for_optimization = Column(Text, nullable=False)
    expected_effect = Column(Text, nullable=False)
    observed_effect = Column(Text, nullable=True)  # Updated after evaluation

    # Relationships
    website = relationship("Website", back_populates="optimizations")
    outcomes = relationship("Outcome", back_populates="optimization", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "website_id": self.website_id,
            "domain": self.website.domain if self.website else None,
            "date": self.date.isoformat() if self.date else None,
            "optimization_type": self.optimization_type,
            "description": self.description,
            "reason_for_optimization": self.reason_for_optimization,
            "expected_effect": self.expected_effect,
            "observed_effect": self.observed_effect,
        }


class CompetitorHistory(Base):
    """5. COMPETITOR HISTORY Entity
    Tracks competitor movements over time:
    content changes, feature changes, ranking changes, and notable SEO changes.
    """
    __tablename__ = "competitor_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    competitor_website_id = Column(String(36), ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Detailed change categories (JSON structures for rich, structured diffs)
    content_changes = Column(JSON, nullable=False, default=list)        # e.g., ["Added 5 new FAQ items", "Revised intro"]
    feature_changes = Column(JSON, nullable=False, default=list)        # e.g., ["Added interactive coding console", "Embedded video demo"]
    ranking_changes = Column(JSON, nullable=False, default=dict)        # e.g., {"before": 2, "after": 1, "delta": +1}
    notable_seo_changes = Column(JSON, nullable=False, default=list)    # e.g., ["Implemented Course schema", "Updated canonical"]

    # Relationships
    competitor = relationship("Website", back_populates="competitor_events")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "competitor_website_id": self.competitor_website_id,
            "competitor_domain": self.competitor.domain if self.competitor else None,
            "keyword": self.keyword,
            "date": self.date.isoformat() if self.date else None,
            "content_changes": self.content_changes or [],
            "feature_changes": self.feature_changes or [],
            "ranking_changes": self.ranking_changes or {},
            "notable_seo_changes": self.notable_seo_changes or [],
        }


class Outcome(Base):
    """6. OUTCOME Entity
    Causal attribution linking a specific optimization on a website to ranking outcomes:
    previous ranking, new ranking, observed change, date, and confidence/uncertainty score.
    """
    __tablename__ = "outcomes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    website_id = Column(String(36), ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    optimization_id = Column(String(36), ForeignKey("seo_optimizations.id", ondelete="CASCADE"), nullable=False, index=True)
    previous_ranking = Column(Integer, nullable=False)
    new_ranking = Column(Integer, nullable=False)
    observed_change = Column(String(255), nullable=False)  # e.g., "+5 positions (#8 to #3)"
    date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    confidence = Column(Float, nullable=False, default=0.85)  # 0.0 to 1.0 (confidence score)
    uncertainty_factors = Column(JSON, nullable=False, default=list)  # Confounding factors, e.g. ["competitor counter-surge", "core update"]

    # Relationships
    website = relationship("Website", back_populates="outcomes")
    optimization = relationship("SEOOptimization", back_populates="outcomes")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "website_id": self.website_id,
            "domain": self.website.domain if self.website else None,
            "optimization_id": self.optimization_id,
            "optimization_type": self.optimization.optimization_type if self.optimization else None,
            "previous_ranking": self.previous_ranking,
            "new_ranking": self.new_ranking,
            "observed_change": self.observed_change,
            "date": self.date.isoformat() if self.date else None,
            "confidence": self.confidence,
            "uncertainty_factors": self.uncertainty_factors or [],
        }


class ContentCitationInfo(Base):
    """7. CONTENT/CITATION INFORMATION Entity
    Flexible citation/source reference storage.
    Only active/populated if used by the application, with arbitrary metadata_json.
    """
    __tablename__ = "content_citations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    website_id = Column(String(36), ForeignKey("websites.id", ondelete="SET NULL"), nullable=True, index=True)
    search_query_id = Column(String(36), ForeignKey("search_queries.id", ondelete="SET NULL"), nullable=True, index=True)
    source_title = Column(String(500), nullable=False)
    source_url = Column(String(1000), nullable=False)
    citation_snippet = Column(Text, nullable=True)
    citation_type = Column(String(100), nullable=False, default="authoritative_reference")  # external_reference, competitor_cite, etc.
    is_used_by_app = Column(Boolean, nullable=False, default=True)
    citation_metadata = Column(JSON, nullable=False, default=dict)  # Flexible store for custom future citation fields
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    website = relationship("Website", back_populates="citations")
    search_query = relationship("SearchQuery", back_populates="citations")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "website_id": self.website_id,
            "search_query_id": self.search_query_id,
            "source_title": self.source_title,
            "source_url": self.source_url,
            "citation_snippet": self.citation_snippet,
            "citation_type": self.citation_type,
            "is_used_by_app": self.is_used_by_app,
            "citation_metadata": self.citation_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserInteraction(Base):
    """8. USER INTERACTION Entity
    Records user queries, selected websites, questions asked, recommendations requested, and feedback.
    """
    __tablename__ = "user_interactions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    search_query_id = Column(String(36), ForeignKey("search_queries.id", ondelete="SET NULL"), nullable=True, index=True)
    query_text = Column(String(500), nullable=False)
    selected_website_id = Column(String(36), ForeignKey("websites.id", ondelete="SET NULL"), nullable=True, index=True)
    question_asked = Column(Text, nullable=True)
    recommendation_requested = Column(Text, nullable=True)
    recommendation_provided = Column(Text, nullable=True)
    feedback = Column(JSON, nullable=False, default=dict)  # e.g., {"rating": 5, "helpful": True, "comment": "Spot on"}
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    search_query = relationship("SearchQuery", back_populates="user_interactions")
    website = relationship("Website", back_populates="user_interactions")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "search_query_id": self.search_query_id,
            "query_text": self.query_text,
            "selected_website_id": self.selected_website_id,
            "selected_domain": self.website.domain if self.website else None,
            "question_asked": self.question_asked,
            "recommendation_requested": self.recommendation_requested,
            "recommendation_provided": self.recommendation_provided,
            "feedback": self.feedback or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
