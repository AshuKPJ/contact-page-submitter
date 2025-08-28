# app/workers/__init__.py

# Import the run function instead of non-existent CampaignProcessor class
from .campaign_processor import run as run_campaign_processor
from .processor import process_campaign

__all__ = ["run_campaign_processor", "process_campaign"]
