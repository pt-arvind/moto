from __future__ import unicode_literals
from .responses import WorkspaceResponse

url_bases = ["https?://workspaces.(.+).amazonaws.com"]

url_paths = {"{0}/$": WorkspaceResponse.dispatch}
