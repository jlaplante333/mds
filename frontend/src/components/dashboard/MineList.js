import React from "react";
import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import { Table } from "antd";
import * as router from "@/constants/routes";
import * as String from "@/constants/strings";
import NullScreen from "@/components/common/NullScreen";

/**
 * @class MineList - paginated list of mines
 */

const propTypes = {
  mines: PropTypes.object.isRequired,
  mineIds: PropTypes.array.isRequired,
  mineRegionHash: PropTypes.object.isRequired,
  mineTenureHash: PropTypes.object.isRequired,
  mineCommodityOptionsHash: PropTypes.object.isRequired,
};

const columns = [
  {
    title: "Mine Name",
    width: 200,
    dataIndex: "mineName",
    render: (text, record) => <Link to={router.MINE_SUMMARY.dynamicRoute(record.key)}>{text}</Link>,
  },
  {
    title: "Mine No.",
    width: 100,
    dataIndex: "mineNo",
  },
  {
    title: "Operational Status",
    dataIndex: "operationalStatus",
    width: 150,
  },
  {
    title: "Permit No.",
    dataIndex: "permit",
    width: 150,
    render: (text, record) => (
      <div>
        {text && text.map(({ permit_no, permit_guid }) => <div key={permit_guid}>{permit_no}</div>)}
        {!text && <div>{record.emptyField}</div>}
      </div>
    ),
  },
  {
    title: "Region",
    dataIndex: "region",
    width: 150,
  },
  {
    title: "Tenure",
    dataIndex: "tenure",
    width: 150,
    render: (text, record) => (
      <div>
        {text &&
          text.map((tenure) => (
            <span className="mine_tenure" key={tenure.mine_type_guid}>
              {record.tenureHash[tenure.mine_tenure_type_code]}
            </span>
          ))}
        {!text && <div>{record.emptyField}</div>}
      </div>
    ),
  },
  {
    title: "Commodity",
    dataIndex: "commodity",
    width: 150,
    render: (text, record) => (
      <div>
        {text &&
          text.map(({ mine_type_detail, mine_type_guid }) => (
            <div key={mine_type_guid}>
              {mine_type_detail.map(({ mine_commodity_code, mine_type_detail_guid }) => (
                <span key={mine_type_detail_guid}>
                  {mine_commodity_code && record.commodityHash[mine_commodity_code] + ", "}
                </span>
              ))}
            </div>
          ))}
      </div>
    ),
  },
  {
    title: "TSF",
    dataIndex: "tsf",
    width: 150,
  },
];

const transformRowData = (mines, mineIds, mineRegionHash, mineTenureHash, mineCommodityHash) =>
  mineIds.map((id) => ({
    key: id,
    emptyField: String.EMPTY_FIELD,
    mineName: mines[id].mine_detail[0] ? mines[id].mine_detail[0].mine_name : String.EMPTY_FIELD,
    mineNo: mines[id].mine_detail[0] ? mines[id].mine_detail[0].mine_no : String.EMPTY_FIELD,
    operationalStatus: mines[id].mine_status[0]
      ? mines[id].mine_status[0].status_labels[0]
      : String.EMPTY_FIELD,
    permit: mines[id].mine_permit[0] ? mines[id].mine_permit : null,
    region: mines[id].mine_detail[0].region_code
      ? mineRegionHash[mines[id].mine_detail[0].region_code]
      : String.EMPTY_FIELD,
    commodity: mines[id].mine_type[0] ? mines[id].mine_type : null,
    commodityHash: mineCommodityHash,
    tenure: mines[id].mine_type[0] ? mines[id].mine_type : null,
    tenureHash: mineTenureHash,
    tsf: mines[id].mine_tailings_storage_facility
      ? mines[id].mine_tailings_storage_facility.length
      : String.EMPTY_FIELD,
  }));

export const MineList = (props) => (
  <Table
    align="center"
    pagination={false}
    columns={columns}
    dataSource={transformRowData(
      props.mines,
      props.mineIds,
      props.mineRegionHash,
      props.mineTenureHash,
      props.mineCommodityOptionsHash
    )}
    scroll={{ x: 1500 }}
    locale={{ emptyText: <NullScreen type="no-results" /> }}
  />
);

MineList.propTypes = propTypes;

export default MineList;
