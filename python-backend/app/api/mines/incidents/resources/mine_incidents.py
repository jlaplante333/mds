from flask_restplus import Resource, reqparse, fields, inputs
from flask import request, current_app
from datetime import datetime
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from app.extensions import api
from app.api.utils.resources_mixins import UserMixin
from app.api.utils.access_decorators import requires_role_mine_view, requires_role_mine_create

from app.api.mines.mine.models.mine import Mine
from app.api.parties.party.models.party import Party
from ..models.mine_incident import MineIncident
from app.api.mines.compliance.models.compliance_article import ComplianceArticle
from ...mine_api_models import MINE_INCIDENT_MODEL


def _compliance_article_is_do_subparagraph(ca):
    if ca is None:
        return False

    return ca.article_act_code == 'HSRCM' and ca.section == '1' and ca.sub_section == '7' and ca.paragraph == '3' and ca.sub_paragraph is not None


class MineIncidentListResource(Resource, UserMixin):
    parser = reqparse.RequestParser(trim=True)
    # required
    parser.add_argument('incident_timestamp',
                        type=lambda x: datetime.strptime(
                            x, '%Y-%m-%d %H:%M') if x else None,
                        location='json',
                        required=True)
    parser.add_argument('incident_description', type=str,
                        location='json', required=True)
    parser.add_argument('reported_timestamp',
                        type=lambda x: datetime.strptime(
                            x, '%Y-%m-%d %H:%M') if x else None,
                        required=True,
                        location='json')
    parser.add_argument('reported_by_name', type=str, location='json')
    parser.add_argument('reported_by_email', type=str, location='json')
    parser.add_argument('reported_by_phone_no', type=str, location='json')
    parser.add_argument('reported_by_phone_ext', type=str, location='json')
    parser.add_argument('emergency_services_called',
                        type=inputs.boolean, location='json')
    parser.add_argument('number_of_injuries', type=int, location='json')
    parser.add_argument('number_of_fatalities', type=int, location='json')
    parser.add_argument('reported_to_inspector_party_guid',
                        type=str, location='json')
    parser.add_argument('responsible_inspector_party_guid',
                        type=str, location='json')
    parser.add_argument('determination_inspector_party_guid',
                        type=str, location='json')
    parser.add_argument('determination_type_code', type=str, location='json')
    parser.add_argument('followup_investigation_type_code',
                        type=str, location='json')
    parser.add_argument('followup_inspection',
                        type=inputs.boolean, location='json')
    parser.add_argument('followup_inspection_date',
                        type=lambda x: datetime.strptime(
                            x, '%Y-%m-%d') if x else None,
                        store_missing=False,
                        location='json')
    parser.add_argument('status_code', type=str, location='json')
    parser.add_argument(
        'dangerous_occurrence_subparagraph_ids', type=list, location='json')

    @api.marshal_with(MINE_INCIDENT_MODEL, envelope='mine_incidents', code=200, as_list=True)
    @api.doc(description='returns the incidents for a given mine.')
    @requires_role_mine_view
    def get(self, mine_guid):
        mine = Mine.find_by_mine_guid(mine_guid)
        if not mine:
            raise NotFound("Mine not found")
        return mine.mine_incidents

    @api.expect(MINE_INCIDENT_MODEL)
    @api.doc(description='creates a new incident for the mine')
    @api.marshal_with(MINE_INCIDENT_MODEL, code=201)
    @requires_role_mine_create
    def post(self, mine_guid):
        mine = Mine.find_by_mine_guid(mine_guid)
        if not mine:
            raise NotFound('Mine not found')

        data = self.parser.parse_args()

        do_sub_codes = []
        if data['determination_type_code'] == 'DO':
            do_sub_codes = data['dangerous_occurrence_subparagraph_ids']
            if not do_sub_codes:
                raise BadRequest(
                    'Dangerous occurrences require one or more cited sections of HSRC code 1.7.3')

        incident = MineIncident.create(
            mine,
            data['incident_timestamp'],
            data['incident_description'],
            determination_type_code=data['determination_type_code'],
            followup_investigation_type_code=data['followup_investigation_type_code'],
            reported_timestamp=data['reported_timestamp'],
            reported_by_name=data['reported_by_name'],
        )

        incident.reported_by_email = data.get('reported_by_email')
        incident.reported_by_phone_no = data.get(
            'reported_by_phone_no')  # string
        incident.reported_by_phone_ext = data.get(
            'reported_by_phone_ext')  # string
        incident.number_of_fatalities = data.get('number_of_fatalities')  # int
        incident.number_of_injuries = data.get('number_of_injuries')  # int
        incident.emergency_services_called = data.get(
            'emergency_services_called')  # bool
        incident.followup_inspection = data.get('followup_inspection')  # bool
        incident.followup_inspection_date = data.get(
            'followup_inspection_date')

        # lookup and validated inspector party relationships
        tmp_party = Party.query.filter_by(
            party_guid=data.get('reported_to_inspector_party_guid')).first()
        if tmp_party and 'INS' in tmp_party.business_roles_codes:
            incident.reported_to_inspector_party_guid = tmp_party.party_guid
        tmp_party = Party.query.filter_by(
            party_guid=data.get('responsible_inspector_party_guid')).first()
        if tmp_party and 'INS' in tmp_party.business_roles_codes:
            incident.responsible_inspector_party_guid = tmp_party.party_guid
        tmp_party = Party.query.filter_by(
            party_guid=data.get('determination_inspector_party_guid')).first()
        if tmp_party and 'INS' in tmp_party.business_roles_codes:
            incident.determination_inspector_party_guid = tmp_party.party_guid

        incident.determination_type_code = data.get('determination_type_code')
        incident.followup_investigation_type_code = data.get(
            'followup_investigation_type_code')

        for id in do_sub_codes:
            sub = ComplianceArticle.find_by_compliance_article_id(id)
            if not _compliance_article_is_do_subparagraph(sub):
                raise BadRequest(
                    'One of the provided compliance articles is not a sub-paragraph of section 1.7.3 (dangerous occurrences)'
                )
            incident.dangerous_occurrence_subparagraphs.append(sub)
        try:
            incident.save()
        except Exception as e:
            raise InternalServerError(f'Error when saving: {e}')

        return incident, 201


class MineIncidentResource(Resource, UserMixin):
    parser = reqparse.RequestParser(trim=True)
    # required
    parser.add_argument('incident_timestamp',
                        type=lambda x: datetime.strptime(
                            x, '%Y-%m-%d %H:%M') if x else None,
                        location='json',
                        store_missing=False)
    parser.add_argument('incident_description', type=str, location='json',
                        store_missing=False)
    parser.add_argument('reported_timestamp',
                        type=lambda x: datetime.strptime(
                            x, '%Y-%m-%d %H:%M') if x else None,
                        store_missing=False,
                        location='json')
    parser.add_argument('reported_by_name', type=str, location='json',
                        store_missing=False)
    parser.add_argument('reported_by_email', type=str, location='json',
                        store_missing=False)
    parser.add_argument('reported_by_phone_no', type=str, location='json',
                        store_missing=False)
    parser.add_argument('reported_by_phone_ext', type=str, location='json',
                        store_missing=False)
    parser.add_argument('emergency_services_called', type=inputs.boolean, location='json',
                        store_missing=False)
    parser.add_argument('number_of_injuries', type=int, location='json',
                        store_missing=False)
    parser.add_argument('number_of_fatalities', type=int, location='json',
                        store_missing=False)
    parser.add_argument('reported_to_inspector_party_guid', type=str, location='json',
                        store_missing=False)
    parser.add_argument('responsible_inspector_party_guid', type=str, location='json',
                        store_missing=False)
    parser.add_argument('determination_inspector_party_guid', type=str, location='json',
                        store_missing=False)
    parser.add_argument('determination_type_code', type=str, location='json',
                        store_missing=False)
    parser.add_argument('followup_investigation_type_code', type=str, location='json',
                        store_missing=False)
    parser.add_argument('followup_inspection', type=inputs.boolean, location='json',
                        store_missing=False)
    parser.add_argument('followup_inspection_date',
                        type=lambda x: datetime.strptime(
                            x, '%Y-%m-%d') if x else None,
                        store_missing=False,
                        location='json')
    parser.add_argument('status_code', type=str, location='json',
                        store_missing=False)
    parser.add_argument('dangerous_occurrence_subparagraph_ids', type=list, location='json',
                        store_missing=False)

    @api.marshal_with(MINE_INCIDENT_MODEL, code=200)
    @requires_role_mine_view
    def get(self, mine_guid, mine_incident_guid):
        incident = MineIncident.find_by_mine_incident_guid(mine_incident_guid)
        if not incident:
            raise NotFound("Mine Incident not found")
        return incident

    @api.expect(parser)
    @api.marshal_with(MINE_INCIDENT_MODEL, code=200)
    @requires_role_mine_create
    def put(self, mine_guid, mine_incident_guid):
        incident = MineIncident.find_by_mine_incident_guid(mine_incident_guid)
        if not incident or str(incident.mine_guid) != mine_guid:
            raise NotFound("Mine Incident not found")

        data = self.parser.parse_args()
        do_sub_codes = []
        if data['determination_type_code'] == 'DO':
            do_sub_codes = data['dangerous_occurrence_subparagraph_ids']
            if not do_sub_codes:
                raise BadRequest(
                    'Dangerous occurrences require one or more cited sections of HSRC code 1.7.3')

        for key, value in data.items():
            if key == 'dangerous_occurrence_subparagraph_ids':
                continue
            if key in [
                    'reported_to_inspector_party_guid', 'responsible_inspector_party_guid',
                    'determination_inspector_party_guid'
            ]:
                tmp_party = Party.query.filter_by(party_guid=value).first()
                if tmp_party and 'INS' in tmp_party.business_roles_codes:
                    setattr(incident, key, value)
            else:
                setattr(incident, key, value)

        incident.dangerous_occurrence_subparagraphs = []
        for id in do_sub_codes:
            sub = ComplianceArticle.find_by_compliance_article_id(id)
            if not _compliance_article_is_do_subparagraph(sub):
                raise BadRequest(
                    'One of the provided compliance articles is not a sub-paragraph of section 1.7.3 (dangerous occurrences)'
                )
            incident.dangerous_occurrence_subparagraphs.append(sub)

        try:
            incident.save()
        except Exception as e:
            raise InternalServerError(f'Error when saving: {e}')
        return incident
