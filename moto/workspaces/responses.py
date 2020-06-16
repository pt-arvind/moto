from __future__ import unicode_literals

import json

from moto.core.responses import BaseResponse
from moto.core.utils import amzn_request_id
from .exceptions import AWSError
from .models import workspace_backends
# {
#     "Workspaces": [
#         {
#             "WorkspaceId": "ws-k715hzydy",
#             "DirectoryId": "d-90677bba6e",
#             "UserName": "test1",
#             "IpAddress": "172.16.1.128",
#             "State": "STOPPED",
#             "BundleId": "wsb-clj85qzj1",
#             "SubnetId": "subnet-058be0b52a4e4beab",
#             "ComputerName": "A-1MG57Y5QFK7KN",
#             "WorkspaceProperties": {
#                 "RunningMode": "AUTO_STOP",
#                 "RunningModeAutoStopTimeoutInMinutes": 60,
#                 "RootVolumeSizeGib": 80,
#                 "UserVolumeSizeGib": 10,
#                 "ComputeTypeName": "STANDARD"
#             },
#             "ModificationStates": []
#         },
#         {
#             "WorkspaceId": "ws-fps7wg4mc",
#             "DirectoryId": "d-90677bba6e",
#             "UserName": "testuser",
#             "IpAddress": "172.16.0.146",
#             "State": "STOPPED",
#             "BundleId": "wsb-clj85qzj1",
#             "SubnetId": "subnet-0f916918d759cdc7b",
#             "ComputerName": "A-3DBSJKTZ2YMII",
#             "WorkspaceProperties": {
#                 "RunningMode": "AUTO_STOP",
#                 "RunningModeAutoStopTimeoutInMinutes": 60,
#                 "RootVolumeSizeGib": 80,
#                 "UserVolumeSizeGib": 50,
#                 "ComputeTypeName": "STANDARD"
#             },
#             "ModificationStates": []
#         }
#     ]
# }

class WorkspaceResponse(BaseResponse):
    @property
    def workspace_backend(self):
        return workspace_backends[self.region]

    @amzn_request_id
    def create_state_machine(self):
        name = self._get_param("name")
        definition = self._get_param("definition")
        roleArn = self._get_param("roleArn")
        tags = self._get_param("tags")
        try:
            state_machine = self.workspace_backend.create_state_machine(
                name=name, definition=definition, roleArn=roleArn, tags=tags
            )
            response = {
                "creationDate": state_machine.creation_date,
                "stateMachineArn": state_machine.arn,
            }
            return 200, {}, json.dumps(response)
        except AWSError as err:
            return err.response()

    @amzn_request_id
    def list_state_machines(self):
        list_all = self.workspace_backend.list_state_machines()
        list_all = sorted(
            [
                {
                    "creationDate": sm.creation_date,
                    "name": sm.name,
                    "stateMachineArn": sm.arn,
                }
                for sm in list_all
            ],
            key=lambda x: x["name"],
        )
        response = {"stateMachines": list_all}
        return 200, {}, json.dumps(response)

    @amzn_request_id
    def describe_state_machine(self):
        arn = self._get_param("stateMachineArn")
        return self._describe_state_machine(arn)

    @amzn_request_id
    def _describe_state_machine(self, state_machine_arn):
        try:
            state_machine = self.workspace_backend.describe_state_machine(
                state_machine_arn
            )
            response = {
                "creationDate": state_machine.creation_date,
                "stateMachineArn": state_machine.arn,
                "definition": state_machine.definition,
                "name": state_machine.name,
                "roleArn": state_machine.roleArn,
                "status": "ACTIVE",
            }
            return 200, {}, json.dumps(response)
        except AWSError as err:
            return err.response()

    @amzn_request_id
    def delete_state_machine(self):
        arn = self._get_param("stateMachineArn")
        try:
            self.workspace_backend.delete_state_machine(arn)
            return 200, {}, json.dumps("{}")
        except AWSError as err:
            return err.response()

    @amzn_request_id
    def list_tags_for_resource(self):
        arn = self._get_param("resourceArn")
        try:
            state_machine = self.workspace_backend.describe_state_machine(arn)
            tags = state_machine.tags or []
        except AWSError:
            tags = []
        response = {"tags": tags}
        return 200, {}, json.dumps(response)

    @amzn_request_id
    def start_execution(self):
        arn = self._get_param("stateMachineArn")
        name = self._get_param("name")
        try:
            execution = self.workspace_backend.start_execution(arn, name)
        except AWSError as err:
            return err.response()
        response = {
            "executionArn": execution.execution_arn,
            "startDate": execution.start_date,
        }
        return 200, {}, json.dumps(response)

    @amzn_request_id
    def list_executions(self):
        arn = self._get_param("stateMachineArn")
        state_machine = self.workspace_backend.describe_state_machine(arn)
        executions = self.workspace_backend.list_executions(arn)
        executions = [
            {
                "executionArn": execution.execution_arn,
                "name": execution.name,
                "startDate": execution.start_date,
                "stateMachineArn": state_machine.arn,
                "status": execution.status,
            }
            for execution in executions
        ]
        return 200, {}, json.dumps({"executions": executions})

    @amzn_request_id
    def describe_execution(self):
        arn = self._get_param("executionArn")
        try:
            execution = self.workspace_backend.describe_execution(arn)
            response = {
                "executionArn": arn,
                "input": "{}",
                "name": execution.name,
                "startDate": execution.start_date,
                "stateMachineArn": execution.state_machine_arn,
                "status": execution.status,
                "stopDate": execution.stop_date,
            }
            return 200, {}, json.dumps(response)
        except AWSError as err:
            return err.response()

    @amzn_request_id
    def describe_state_machine_for_execution(self):
        arn = self._get_param("executionArn")
        try:
            execution = self.workspace_backend.describe_execution(arn)
            return self._describe_state_machine(execution.state_machine_arn)
        except AWSError as err:
            return err.response()

    @amzn_request_id
    def stop_execution(self):
        arn = self._get_param("executionArn")
        execution = self.workspace_backend.stop_execution(arn)
        response = {"stopDate": execution.stop_date}
        return 200, {}, json.dumps(response)
