"""
RAA Earthquake — Multi-Disaster Platform Models
New database models for the expanded platform.
The existing User model remains in app.py untouched.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Dictionary / holder for model classes
class ModelHolder:
    pass

models_registry = ModelHolder()

def init_models(database):
    """Initialize all models with the app's database instance and return model registry."""
    global db
    db = database
    models_registry.DisasterType = create_disaster_type_model(db)
    models_registry.DataSource = create_data_source_model(db)
    models_registry.Event = create_event_model(db)
    models_registry.SafetyGuide = create_safety_guide_model(db)
    models_registry.IndianState = create_indian_state_model(db)
    models_registry.IndianDistrict = create_indian_district_model(db)
    models_registry.GlossaryTerm = create_glossary_term_model(db)
    models_registry.HistoricalEvent = create_historical_event_model(db)
    models_registry.EmergencyContact = create_emergency_contact_model(db)
    models_registry.UserPreference = create_user_preference_model(db)
    models_registry.AlertSubscription = create_alert_subscription_model(db)
    return models_registry



# ================= DISASTER TYPE =================
class DisasterType(object):
    """Registry of all hazard types supported by the platform."""
    pass

def create_disaster_type_model(db):
    class DisasterType(db.Model):
        __tablename__ = 'disaster_types'
        id = db.Column(db.Integer, primary_key=True)
        slug = db.Column(db.String(100), unique=True, nullable=False)
        name = db.Column(db.String(200), nullable=False)
        icon = db.Column(db.String(10), default='⚠️')
        category = db.Column(db.String(100))  # geological, meteorological, hydrological, etc.
        short_description = db.Column(db.Text)
        description = db.Column(db.Text)
        how_it_forms = db.Column(db.Text)
        causes = db.Column(db.Text)
        dangers = db.Column(db.Text)
        scientific_explanation = db.Column(db.Text)
        measurement_scales = db.Column(db.Text)
        terminology = db.Column(db.Text)
        india_relevance = db.Column(db.Text)
        common_regions = db.Column(db.Text)
        frequency_info = db.Column(db.Text)
        duration_info = db.Column(db.Text)
        color_code = db.Column(db.String(7), default='#4f46e5')
        is_active = db.Column(db.Boolean, default=True)
        display_order = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    return DisasterType


# ================= DATA SOURCE =================
def create_data_source_model(db):
    class DataSource(db.Model):
        __tablename__ = 'data_sources'
        id = db.Column(db.Integer, primary_key=True)
        source_id = db.Column(db.String(50), unique=True, nullable=False)
        name = db.Column(db.String(200), nullable=False)
        country = db.Column(db.String(100))
        agency = db.Column(db.String(200))
        api_url = db.Column(db.String(500))
        website = db.Column(db.String(500))
        data_types = db.Column(db.Text)  # JSON list of disaster types covered
        update_frequency = db.Column(db.String(100))
        license_info = db.Column(db.Text)
        limitations = db.Column(db.Text)
        status = db.Column(db.String(20), default='operational')  # operational, degraded, unavailable
        priority = db.Column(db.Integer, default=5)
        last_successful_fetch = db.Column(db.DateTime)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    return DataSource


# ================= EVENT =================
def create_event_model(db):
    class Event(db.Model):
        __tablename__ = 'events'
        id = db.Column(db.Integer, primary_key=True)
        event_type = db.Column(db.String(100), nullable=False)  # earthquake, cyclone, etc.
        source = db.Column(db.String(100))
        source_event_id = db.Column(db.String(200))
        title = db.Column(db.String(500))
        description = db.Column(db.Text)
        latitude = db.Column(db.Float)
        longitude = db.Column(db.Float)
        country = db.Column(db.String(100))
        state = db.Column(db.String(100))
        district = db.Column(db.String(100))
        city = db.Column(db.String(200))
        start_time = db.Column(db.DateTime)
        end_time = db.Column(db.DateTime)
        severity = db.Column(db.String(50))  # low, moderate, high, severe, extreme
        magnitude = db.Column(db.Float)
        depth_km = db.Column(db.Float)
        status = db.Column(db.String(50), default='confirmed')  # confirmed, preliminary, estimated, unverified
        warning_level = db.Column(db.String(50))  # information, advisory, watch, warning, emergency
        official_url = db.Column(db.String(500))
        additional_data = db.Column(db.Text)  # JSON for hazard-specific fields
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        __table_args__ = (
            db.Index('idx_event_type_time', 'event_type', 'start_time'),
            db.Index('idx_event_source', 'source', 'source_event_id'),
            db.Index('idx_event_location', 'country', 'state'),
        )
    return Event


# ================= SAFETY GUIDE =================
def create_safety_guide_model(db):
    class SafetyGuide(db.Model):
        __tablename__ = 'safety_guides'
        id = db.Column(db.Integer, primary_key=True)
        disaster_slug = db.Column(db.String(100), nullable=False)
        title = db.Column(db.String(300))
        before_steps = db.Column(db.Text)  # JSON list
        during_steps = db.Column(db.Text)  # JSON list
        after_steps = db.Column(db.Text)   # JSON list
        additional_tips = db.Column(db.Text)
        source = db.Column(db.String(200))
        source_url = db.Column(db.String(500))
        version = db.Column(db.Integer, default=1)
        author = db.Column(db.String(100))
        reviewer = db.Column(db.String(100))
        last_reviewed = db.Column(db.DateTime)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    return SafetyGuide


# ================= INDIAN STATE =================
def create_indian_state_model(db):
    class IndianState(db.Model):
        __tablename__ = 'indian_states'
        id = db.Column(db.Integer, primary_key=True)
        slug = db.Column(db.String(100), unique=True, nullable=False)
        name = db.Column(db.String(200), nullable=False)
        state_type = db.Column(db.String(20), default='state')  # state or ut
        capital = db.Column(db.String(200))
        latitude = db.Column(db.Float)
        longitude = db.Column(db.Float)
        geography = db.Column(db.Text)
        climate = db.Column(db.Text)
        terrain = db.Column(db.Text)
        population_context = db.Column(db.Text)
        major_hazards = db.Column(db.Text)  # JSON list of hazard slugs
        disaster_history = db.Column(db.Text)
        seismic_zone = db.Column(db.String(50))
        is_coastal = db.Column(db.Boolean, default=False)
        is_himalayan = db.Column(db.Boolean, default=False)
        region = db.Column(db.String(100))  # North, South, East, West, Northeast, Central
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    return IndianState


# ================= INDIAN DISTRICT =================
def create_indian_district_model(db):
    class IndianDistrict(db.Model):
        __tablename__ = 'indian_districts'
        id = db.Column(db.Integer, primary_key=True)
        slug = db.Column(db.String(200), nullable=False)
        name = db.Column(db.String(200), nullable=False)
        state_slug = db.Column(db.String(100), nullable=False)
        latitude = db.Column(db.Float)
        longitude = db.Column(db.Float)
        common_hazards = db.Column(db.Text)  # JSON list
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    return IndianDistrict


# ================= GLOSSARY =================
def create_glossary_term_model(db):
    class GlossaryTerm(db.Model):
        __tablename__ = 'glossary_terms'
        id = db.Column(db.Integer, primary_key=True)
        slug = db.Column(db.String(200), unique=True, nullable=False)
        term = db.Column(db.String(200), nullable=False)
        simple_definition = db.Column(db.Text)
        scientific_definition = db.Column(db.Text)
        example = db.Column(db.Text)
        related_hazards = db.Column(db.Text)  # JSON list of disaster slugs
        category = db.Column(db.String(100))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    return GlossaryTerm


# ================= HISTORICAL EVENT =================
def create_historical_event_model(db):
    class HistoricalEvent(db.Model):
        __tablename__ = 'historical_events'
        id = db.Column(db.Integer, primary_key=True)
        disaster_type = db.Column(db.String(100), nullable=False)
        title = db.Column(db.String(500), nullable=False)
        description = db.Column(db.Text)
        date = db.Column(db.Date)
        year = db.Column(db.Integer)
        country = db.Column(db.String(100))
        state = db.Column(db.String(100))
        location = db.Column(db.String(300))
        latitude = db.Column(db.Float)
        longitude = db.Column(db.Float)
        magnitude = db.Column(db.Float)
        severity = db.Column(db.String(100))
        deaths = db.Column(db.Integer)
        affected_people = db.Column(db.Integer)
        economic_damage = db.Column(db.String(200))
        source = db.Column(db.String(200))
        source_url = db.Column(db.String(500))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    return HistoricalEvent


# ================= EMERGENCY CONTACT =================
def create_emergency_contact_model(db):
    class EmergencyContact(db.Model):
        __tablename__ = 'emergency_contacts'
        id = db.Column(db.Integer, primary_key=True)
        service = db.Column(db.String(200), nullable=False)
        number = db.Column(db.String(50), nullable=False)
        country = db.Column(db.String(100), default='India')
        state = db.Column(db.String(100))
        region = db.Column(db.String(100))
        source = db.Column(db.String(200))
        last_verified = db.Column(db.DateTime)
        notes = db.Column(db.Text)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    return EmergencyContact


# ================= USER PREFERENCE =================
def create_user_preference_model(db):
    class UserPreference(db.Model):
        __tablename__ = 'user_preferences'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        country = db.Column(db.String(100), default='India')
        state = db.Column(db.String(100))
        district = db.Column(db.String(100))
        city = db.Column(db.String(200))
        language = db.Column(db.String(20), default='en')
        hazard_preferences = db.Column(db.Text)  # JSON list
        checklist_progress = db.Column(db.Text)   # JSON
        saved_locations = db.Column(db.Text)       # JSON list
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    return UserPreference


# ================= ALERT SUBSCRIPTION =================
def create_alert_subscription_model(db):
    class AlertSubscription(db.Model):
        __tablename__ = 'alert_subscriptions'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        disaster_type = db.Column(db.String(100))
        country = db.Column(db.String(100))
        state = db.Column(db.String(100))
        latitude = db.Column(db.Float)
        longitude = db.Column(db.Float)
        radius_km = db.Column(db.Integer, default=100)
        min_severity = db.Column(db.String(50))
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    return AlertSubscription
