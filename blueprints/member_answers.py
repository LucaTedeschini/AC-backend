from flask import Blueprint
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger

# Create a ResourceBlueprint for member-answers
member_answers_resource = ResourceBlueprint('member-answers')

# Use the blueprint from the ResourceBlueprint without any overrides
member_answers_bp = member_answers_resource.blueprint