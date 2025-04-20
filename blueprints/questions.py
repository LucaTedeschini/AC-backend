from flask import Blueprint
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger

# Create a ResourceBlueprint for questions
questions_resource = ResourceBlueprint('questions')

# Use the blueprint from the ResourceBlueprint without any overrides
questions_bp = questions_resource.blueprint