import { PropTypes, shape, arrayOf } from "prop-types";
import { mineExpectedDocument } from "@/customPropTypes/documents";

export const mine = shape({
  mine_guid: PropTypes.string.isRequired,
  mine_no: PropTypes.string,
  mine_name: PropTypes.string,
  mine_expected_documents: arrayOf(mineExpectedDocument),
  ohsc_ind: PropTypes.bool,
  union_ind: PropTypes.bool,
});

export const mineTypes = shape({
  mine_tenure_type_code: PropTypes.string,
  mine_commodity_code: PropTypes.arrayOf(PropTypes.string),
  mine_disturbance_code: PropTypes.arrayOf(PropTypes.string),
});

export const minePageData = shape({
  current_page: PropTypes.numnber,
  items_per_page: PropTypes.numnber,
  mines: PropTypes.arrayOf(mine),
  total: PropTypes.numnber,
  total_pages: PropTypes.numnber,
});
