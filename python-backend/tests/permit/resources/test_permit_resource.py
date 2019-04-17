import json
import uuid
import pytest

from app.api.mines.mine.models.mine import Mine
from app.api.permits.permit.models.permit import Permit
from app.api.permits.permit_amendment.models.permit_amendment import PermitAmendment

from tests.factories import MineFactory, PermitFactory, PermitAmendmentFactory


# GET
def test_get_permit_not_found(test_client, db_session, auth_headers):
    get_resp = test_client.get(f'/permits/{uuid.uuid4()}', headers=auth_headers['full_auth_header'])
    get_data = json.loads(get_resp.data.decode())
    assert 'not found' in get_data['message']
    assert get_resp.status_code == 404


def test_get_permit(test_client, db_session, auth_headers):
    permit_guid = PermitFactory().permit_guid

    get_resp = test_client.get(f'/permits/{permit_guid}', headers=auth_headers['full_auth_header'])
    get_data = json.loads(get_resp.data.decode())
    assert get_data['permit_guid'] == str(permit_guid)
    assert get_resp.status_code == 200


def test_get_with_permit_no(test_client, db_session, auth_headers):
    permit_no = PermitFactory().permit_no

    get_resp = test_client.get(
        f'/permits?permit_no={permit_no}', headers=auth_headers['full_auth_header'])
    get_data = json.loads(get_resp.data.decode())
    assert get_resp.status_code == 200
    assert get_data.get('permit_no') == permit_no


#Create
def test_post_permit(test_client, db_session, auth_headers):
    mine_guid = MineFactory().mine_guid

    PERMIT_NO = 'mx-test-999'
    data = {
        'mine_guid': str(mine_guid),
        'permit_no': PERMIT_NO,
        'permit_status_code': 'O',
        'received_date': '1999-12-12',
        'issue_date': '1999-12-21',
        'authorization_end_date': '2012-12-02'
    }
    post_resp = test_client.post('/permits', headers=auth_headers['full_auth_header'], json=data)
    post_data = json.loads(post_resp.data.decode())

    assert post_resp.status_code == 200
    assert post_data.get('mine_guid') == str(mine_guid)
    assert post_data.get('permit_no') == PERMIT_NO
    assert len(post_data.get('amendments')) == 1


def test_post_permit_bad_mine_guid(test_client, db_session, auth_headers):
    data = {'mine_guid': str(uuid.uuid4())}
    post_resp = test_client.post('/permits', headers=auth_headers['full_auth_header'], json=data)
    assert post_resp.status_code == 404


def test_post_permit_with_duplicate_permit_no(test_client, db_session, auth_headers):
    mine_guid = MineFactory().mine_guid
    permit_no = PermitFactory().permit_no

    data = {'mine_guid': str(mine_guid), 'permit_no': permit_no}
    post_resp = test_client.post('/permits', headers=auth_headers['full_auth_header'], json=data)
    assert post_resp.status_code == 400


def test_post_with_permit_guid(test_client, db_session, auth_headers):
    mine_guid = MineFactory().mine_guid
    permit_guid = PermitFactory().permit_guid

    data = {
        'mine_guid': str(mine_guid),
        'permit_no': 'mx-test-999',
        'permit_status_code': 'O',
        'received_date': '1999-12-12',
        'issue_date': '1999-12-21',
        'authorization_end_date': '2012-12-02'
    }
    post_resp = test_client.post(
        f'/permits/{permit_guid}', headers=auth_headers['full_auth_header'], data=data)
    assert post_resp.status_code == 400


#Put
def test_put_permit(test_client, db_session, auth_headers):
    permit_guid = PermitFactory(permit_status_code='O').permit_guid

    data = {'permit_status_code': 'C'}
    put_resp = test_client.put(
        f'/permits/{permit_guid}', headers=auth_headers['full_auth_header'], json=data)
    put_data = json.loads(put_resp.data.decode())
    assert put_resp.status_code == 200
    assert put_data.get('permit_status_code') == 'C'


def test_put_permit_bad_permit_guid(test_client, db_session, auth_headers):
    PermitFactory(permit_status_code='O')

    data = {'permit_status_code': 'C'}
    put_resp = test_client.put(
        f'/permits/{uuid.uuid4()}', headers=auth_headers['full_auth_header'], json=data)
    assert put_resp.status_code == 404
