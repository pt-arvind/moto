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
def test_describe_workspaces_returns_empty_list_by_default():
    client = boto3.client("workspaces", region_name=region)
    #
    list = client.describe_workspaces()
    list["Workspaces"].should.be.empty

#describe_workspaces()

@mock_workspaces
@mock_sts
def test_describe_workspaces_returns_created_workspaces():
    client = boto3.client("workspaces", region_name=region)
    #
    workspace2 = client.create_workspaces(
        Workspaces=[{
            'DirectoryId': "d-29381asfdw",
            'BundleId': "wsb-asd42hfg1",
            'UserName': "johndoe"
        }]
    )
    workspace1 = client.create_workspaces(
        Workspaces=[{
            'DirectoryId': "d-29381asfdw",
            'BundleId': "wsb-asd42hfg1",
            'UserName': "janedoe"
        }]
    )
    list = client.describe_workspaces()
    #
    list["ResponseMetadata"]["HTTPStatusCode"].should.equal(200)
    list["Workspaces"].should.have.length_of(2)
    list["Workspaces"][0]["UserName"].should.equal("janedoe")
    list["Workspaces"][1]["UserName"].should.equal("johndoe")


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
