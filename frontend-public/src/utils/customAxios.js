import axios from "axios";
import { notification } from "antd";
import * as Strings from "@/constants/strings";

const UNAUTHORIZED = 401;
const MAINTENANCE = 503;

const CustomAxios = (errorToastMessage) => {
  const instance = axios.create();
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      const status = error.response ? error.response.status : null;
      if (status === UNAUTHORIZED || status === MAINTENANCE) {
        window.location.reload(false);
      } else if (errorToastMessage === "default" || errorToastMessage === undefined) {
        notification.error({
          message: error.response ? error.response.data.message : Strings.ERROR,
          duration: 10,
        });
      } else if (errorToastMessage) {
        notification.error({
          message: errorToastMessage,
          duration: 10,
        });
      }

      return Promise.reject(error);
    }
  );

  return instance;
};

export default CustomAxios;
