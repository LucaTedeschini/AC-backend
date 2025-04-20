from flask import Blueprint
from .resource_blueprint import ResourceBlueprint
from utilities.log import Logger

# Create a ResourceBlueprint for members
members_resource = ResourceBlueprint('members')

# Use the blueprint from the ResourceBlueprint without any overrides
members_bp = members_resource.blueprint