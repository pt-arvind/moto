import re
from datetime import datetime

from boto3 import Session

from moto.core import BaseBackend
from moto.core.utils import iso_8601_datetime_without_milliseconds
from moto.sts.models import ACCOUNT_ID
from uuid import uuid4
from .exceptions import (
    InvalidArn,
    InvalidName,
    WorkspaceDoesNotExist,
)

import random
import string

class Workspace:
    def __init__(self, workspace_id, directory_id, user_name, ip_address, state, bundle_id, subnet_id, computer_name, modification_states):
        self.workspace_id = workspace_id
        self.directory_id = directory_id
        self.user_name = user_name
        self.ip_address = ip_address
        self.state = state
        self.bundle_id = bundle_id
        self.subnet_id = subnet_id
        self.computer_name = computer_name
        self.modification_states = modification_states
    
    def stop(self):
        self.state = "STOPPED"


class WorkspaceBackend(BaseBackend):
    accepted_role_arn_format = re.compile(
        "arn:aws:iam::(?P<account_id>[0-9]{12}):role/.+"
    )

    def __init__(self, region_name):
        self.workspaces = []
        self.region_name = region_name
        self._account_id = None

    # FIXME: add proper params
    def create_workspaces(self, directory_id, bundle_id, user_name, tags=None):
        # self._validate_name(name)
        # self._validate_role_arn(roleArn)
        # try:
        #     return self.describe_state_machine(arn)
        # except WorkspaceDoesNotExist:
        
        lettersAndDigits = string.ascii_letters + string.digits
        workspace_id = 'ws-'+''.join((random.choice(lettersAndDigits) for i in range(10)))
        ip_address = '0.0.0.0'
        state = 'STOPPED'
        subnet_id = 'subnet-000000000000000abc'
        computer_name = 'A-0000000000ABC'
        modification_states = []
        
        workspace = Workspace(workspace_id, directory_id, user_name, ip_address, state, bundle_id, subnet_id, computer_name, modification_states)
        self.workspaces.append(workspace)

        return workspace

    def describe_workspaces(self):
        return self.workspaces

    def stop_workspaces(self, workspace_id):
        workspace = next(
            (x for x in self.workspaces if x.workspace_id == workspace_id), None
        )
        if not workspace:
            raise WorkspaceDoesNotExist(
                "Workspace Does Not Exist: '" + workspace_id + "'"
            )
        workspace.stop()
        return workspace

    def reset(self):
        region_name = self.region_name
        self.__dict__ = {}
        self.__init__(region_name)


workspace_backends = {}
for region in Session().get_available_regions("workspaces"):
    workspace_backends[region] = WorkspaceBackend(region)
for region in Session().get_available_regions(
    "workspaces", partition_name="aws-us-gov"
):
    workspace_backends[region] = WorkspaceBackend(region)
for region in Session().get_available_regions("workspaces", partition_name="aws-cn"):
    workspace_backends[region] = WorkspaceBackend(region)
