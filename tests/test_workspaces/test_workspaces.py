from __future__ import unicode_literals

import boto3
import sure  # noqa
import datetime

from datetime import datetime
from botocore.exceptions import ClientError
from nose.tools import assert_raises

from moto import mock_sts, mock_workspaces
from moto.core import ACCOUNT_ID

region = "us-east-1"
simple_definition = (
    '{"Comment": "An example of the Amazon States Language using a choice state.",'
    '"StartAt": "DefaultState",'
    '"States": '
    '{"DefaultState": {"Type": "Fail","Error": "DefaultStateError","Cause": "No Matches!"}}}'
)
account_id = None

@mock_workspaces
def test_state_machine_list_returns_empty_list_by_default():
    client = boto3.client("workspaces", region_name=region)
    #
    list = client.list_state_machines()
    list["stateMachines"].should.be.empty

#describe_workspaces()

@mock_workspaces
@mock_sts
def test_state_machine_list_returns_created_state_machines():
    client = boto3.client("workspaces", region_name=region)
    #
    machine2 = client.create_state_machine(
        name="name2", definition=str(simple_definition), roleArn=_get_default_role()
    )
    machine1 = client.create_state_machine(
        name="name1",
        definition=str(simple_definition),
        roleArn=_get_default_role(),
        tags=[{"key": "tag_key", "value": "tag_value"}],
    )
    list = client.list_state_machines()
    #
    list["ResponseMetadata"]["HTTPStatusCode"].should.equal(200)
    list["stateMachines"].should.have.length_of(2)
    list["stateMachines"][0]["creationDate"].should.be.a(datetime)
    list["stateMachines"][0]["creationDate"].should.equal(machine1["creationDate"])
    list["stateMachines"][0]["name"].should.equal("name1")
    list["stateMachines"][0]["stateMachineArn"].should.equal(
        machine1["stateMachineArn"]
    )
    list["stateMachines"][1]["creationDate"].should.be.a(datetime)
    list["stateMachines"][1]["creationDate"].should.equal(machine2["creationDate"])
    list["stateMachines"][1]["name"].should.equal("name2")
    list["stateMachines"][1]["stateMachineArn"].should.equal(
        machine2["stateMachineArn"]
    )

def _get_account_id():
    global account_id
    if account_id:
        return account_id
    sts = boto3.client("sts", region_name=region)
    identity = sts.get_caller_identity()
    account_id = identity["Account"]
    return account_id


def _get_default_role():
    return "arn:aws:iam::" + _get_account_id() + ":role/unknown_sf_role"
