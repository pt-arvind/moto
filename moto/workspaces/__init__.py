from __future__ import unicode_literals
from .models import workspace_backends
from ..core.models import base_decorator

workspace_backend = workspace_backends["us-east-1"]
mock_workspaces = base_decorator(workspace_backends)
