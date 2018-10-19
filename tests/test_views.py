# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017, 2018 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test server views."""

import json

import pytest
from uuid import uuid4
from io import BytesIO
from flask import url_for
from jsonschema.exceptions import ValidationError
from mock import Mock, PropertyMock, patch
from pytest_reana.fixtures import default_user
from pytest_reana.test_utils import make_mock_api_client


def test_get_workflows(app, default_user):
    """Test get_workflows view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            res = client.get(
                url_for("workflows.get_workflows"),
                query_string={"user_id": default_user.id_},
            )
            assert res.status_code == 403

            res = client.get(
                url_for("workflows.get_workflows"),
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 200


def test_create_workflow(app, default_user):
    """Test create_workflow view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            # access token needs to be passed instead of user_id
            res = client.post(
                url_for("workflows.create_workflow"),
                query_string={"user_id": default_user.id_},
            )
            assert res.status_code == 403

            # remote repository given as spec, not implemented
            res = client.post(
                url_for("workflows.create_workflow"),
                query_string={"access_token": default_user.access_token,
                              "spec": "not_implemented"},
            )
            assert res.status_code == 501

            # no specification provided
            res = client.post(
                url_for("workflows.create_workflow"),
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 500

            # unknown workflow engine
            workflow_data = {
                "workflow": {"specification": {}, "type": "unknown"},
                "workflow_name": "test",
            }
            res = client.post(
                url_for("workflows.create_workflow"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token},
                data=json.dumps(workflow_data),
            )
            assert res.status_code == 500

            # name cannot be valid uuid4
            workflow_data['workflow']['type'] = 'serial'
            res = client.post(
                url_for("workflows.create_workflow"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token,
                              "workflow_name": str(uuid4())},
                data=json.dumps(workflow_data),
            )
            assert res.status_code == 400

            # wrong specification json
            workflow_data = {
                "nonsense": {"specification": {}, "type": "unknown"},
            }
            res = client.post(
                url_for("workflows.create_workflow"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token},
                data=json.dumps(workflow_data),
            )
            assert res.status_code == 400

            # correct case
            workflow_data = {
                "workflow": {"specification": {}, "type": "serial"},
                "workflow_name": "test",
            }
            res = client.post(
                url_for("workflows.create_workflow"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token},
                data=json.dumps(workflow_data),
            )
            assert res.status_code == 200


def test_get_workflow_logs(app, default_user):
    """Test get_workflow_logs view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            res = client.get(
                url_for("workflows.get_workflow_logs",
                        workflow_id_or_name="1"),
                query_string={"user_id": default_user.id_},
            )
            assert res.status_code == 403

            res = client.get(
                url_for("workflows.get_workflow_logs",
                        workflow_id_or_name="1"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 200


def test_get_workflow_status(app, default_user):
    """Test get_workflow_logs view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            res = client.get(
                url_for("workflows.get_workflow_status",
                        workflow_id_or_name="1"),
                query_string={"user_id": default_user.id_},
            )
            assert res.status_code == 403

            res = client.get(
                url_for("workflows.get_workflow_status",
                        workflow_id_or_name="1"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 200


def test_set_workflow_status(app, default_user):
    """Test get_workflow_logs view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            res = client.put(
                url_for("workflows.set_workflow_status",
                        workflow_id_or_name="1"),
                query_string={"user_id": default_user.id_},
            )
            assert res.status_code == 403

            res = client.put(
                url_for("workflows.set_workflow_status",
                        workflow_id_or_name="1"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 500

            res = client.put(
                url_for("workflows.set_workflow_status",
                        workflow_id_or_name="1"),
                headers={"Content-Type": "application/json"},
                query_string={"access_token": default_user.access_token,
                              "status": 0},
                data=json.dumps(dict(parameters=None))
            )
            assert res.status_code == 200


def test_upload_file(app, default_user):
    """Test upload_file view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            res = client.post(
                url_for("workflows.upload_file",
                        workflow_id_or_name="1"),
                query_string={"user_id": default_user.id_,
                              "file_name": "test_upload.txt"},
                data={
                    "file_content": "tests/test_files/test_upload.txt"
                }
            )
            assert res.status_code == 403

            res = client.post(
                url_for("workflows.upload_file",
                        workflow_id_or_name="1"),
                query_string={"access_token": default_user.access_token,
                              "file_name": "test_upload.txt"},
                headers={"content_type": "multipart/form-data"},
                data={
                    "file": (BytesIO(b"Upload this data."),
                             "tests/test_files/test_upload.txt")
                }
            )
            assert res.status_code == 400

            res = client.post(
                url_for("workflows.upload_file",
                        workflow_id_or_name="1"),
                query_string={"access_token": default_user.access_token,
                              "file_name": None},
                headers={"content_type": "multipart/form-data"},
                data={
                    "file_content": (BytesIO(b"Upload this data."),
                                     "tests/test_files/test_upload.txt")
                }
            )
            assert res.status_code == 400

            res = client.post(
                url_for("workflows.upload_file",
                        workflow_id_or_name="1"),
                query_string={"access_token": default_user.access_token,
                              "file_name": "test_upload.txt"},
                headers={"content_type": "multipart/form-data"},
                data={
                    "file_content": (BytesIO(b"Upload this data."),
                                     "tests/test_files/test_upload.txt")
                }
            )
            assert res.status_code == 200


def test_download_file(app, default_user):
    """Test download_file view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            res = client.get(
                url_for("workflows.download_file",
                        workflow_id_or_name="1",
                        file_name="test_download"),
                query_string={"user_id": default_user.id_,
                              "file_name": "test_upload.txt"},
            )
            assert res.status_code == 403

            res = client.get(
                url_for("workflows.download_file",
                        workflow_id_or_name="1",
                        file_name="test_download"),
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 200


def test_get_files(app, default_user):
    """Test get_files view."""
    with app.test_client() as client:
        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(),
        ):
            res = client.get(
                url_for("workflows.get_files",
                        workflow_id_or_name="1"),
                query_string={"user_id": default_user.id_},
            )
            assert res.status_code == 403

            res = client.get(
                url_for("workflows.get_files",
                        workflow_id_or_name="1"),
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 500

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = dict(key='value')

        with patch(
            "reana_server.rest.workflows.current_rwc_api_client",
            make_mock_api_client("reana-workflow-controller")(mock_response),
        ):
            res = client.get(
                url_for("workflows.get_files",
                        workflow_id_or_name="1"),
                query_string={"access_token": default_user.access_token},
            )
            assert res.status_code == 200
