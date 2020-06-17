from __future__ import unicode_literals

import json

from moto.core.responses import BaseResponse
from moto.core.utils import amzn_request_id
from .exceptions import AWSError
from .models import workspace_backends

class WorkspaceResponse(BaseResponse):
    @property
    def workspace_backend(self):
        return workspace_backends[self.region]

    @amzn_request_id
    def create_workspaces(self):
        # FIXME: handle multi create
        workspaces = self._get_param("Workspaces")
        directory_id = workspaces[0]["DirectoryId"]
        user_name = workspaces[0]["UserName"]
        bundle_id = workspaces[0]["BundleId"]
        # tags = workspaces[0]["tags"]
        try:
            state_machine = self.workspace_backend.create_workspaces(
                directory_id=directory_id, bundle_id=bundle_id, user_name=user_name
            )
            response = {
                "FailedRequests": []
            }
            return 200, {}, json.dumps(response)
        except AWSError as err:
            return err.response()

    @amzn_request_id
    def describe_workspaces(self):
        # FIXME: handle filtering
        list_all = self.workspace_backend.describe_workspaces()
        list_all = sorted(
            [
                {
                    "WorkspaceId": ws.workspace_id,
                    "DirectoryId": ws.directory_id,
                    "UserName": ws.user_name,
                    "IpAddress": ws.ip_address,
                    "State": ws.state,
                    "BundleId": ws.bundle_id,
                    "SubnetId": ws.subnet_id,
                    "ComputerName": ws.computer_name,
                    "WorkspaceProperties": {
                        "RunningMode": "AUTO_STOP",
                        "RunningModeAutoStopTimeoutInMinutes": 60,
                        "RootVolumeSizeGib": 80,
                        "UserVolumeSizeGib": 50,
                        "ComputeTypeName": "STANDARD"
                    },
                    "ModificationStates": []
                }
                for ws in list_all
            ],
            key=lambda x: x["UserName"],
        )
        response = {"Workspaces": list_all}
        return 200, {}, json.dumps(response)

    @amzn_request_id
    def stop_workspaces(self):
        # FIXME: handle multi stop
        reqs = self._get_param("StopWorkspaceRequests")
        workspace_id = reqs[0]["WorkspaceId"]

        self.workspace_backend.stop_workspaces(workspace_id)
        response = {"FailedRequests": []}
        return 200, {}, json.dumps(response)
