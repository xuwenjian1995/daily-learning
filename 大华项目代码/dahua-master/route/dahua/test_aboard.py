#!/usr/bin/env python
# coding=utf-8
# author:xuwenjian@datagrand.com
# datetime:2019/12/19 10:37
import unittest
from route.dahua.compareOut import CompareOut, CompareOutMail
from app import app
from io import BytesIO
import os


class TestAboardCase(unittest.TestCase):

    def setUp(self):
        self._obj = CompareOut()
        self._mail_obj = CompareOutMail()
        self.client = app.test_client()

    def tearDown(self):
        pass

    def _test_oem_login(self):
        res = self._obj._oem_login()
        print(res)

    def _test_check_sc_total(self):
        from tools.idps import idps_utils
        test_file_path = "../../test/scan_20.01.07"
        template_file = "../../files/HK01.xlsx"
        template_dict = self._obj._extract_from_excel("HK01", "DAHUA TECHNOLOGY(HK) LIMITED", template_file)
        post_data_list = self._obj._request_json_by_no("4437219120093")
        post_data = post_data_list[0] if post_data_list else dict()
        for filename in os.listdir(test_file_path):
            if "c_dahua" not in filename:
                continue
            file_path = os.path.join(test_file_path, filename)
            print(file_path)

            scan_rst = idps_utils.check_saomiao(33, [3], file_path,
                                     extra_conf=dict(
                                         template_dict=template_dict,
                                         post_data=post_data,
                                         file_uuid=filename
                                     ))
            _, task_id = scan_rst.get("extract_info"), scan_rst.get("task_id")
            check_result = idps_utils.check_info(task_id)["items"]
            print(check_result)

    def test_process(self):  # pass
        test_file_path = "../../test/scan_20.01.07"
        for filename in os.listdir(test_file_path):
            if "c12" not in filename:
                continue
            file_path = os.path.join(test_file_path, filename)
            with open(file_path, 'rb') as pdf:
                pdfBytesIO = BytesIO(pdf.read())

            data = {
                "no": "4437219120093",
                "userid": "1234",
                "file": (pdfBytesIO, filename)
            }
            response = self.client.post("/dahua/compareout", content_type='multipart/form-data', data=data)
            print(response)

    def _test_aboard_status_page(self):
        response = self.client.get("/dahua/compareout?num=10&username=hugaofeng")
        print(response)

    def _test_process_mail(self):  # pass
        test_file_path = "../../test/scan_20.01.07"
        for filename in os.listdir(test_file_path):
            if "c12" not in filename:
                continue
            file_path = os.path.join(test_file_path, filename)
            mail = "cai_li@dahuatech.com"
            with open(file_path, 'rb') as pdf:
                pdfBytesIO = BytesIO(pdf.read())
            data = {
                "mail": mail,
                "file": (pdfBytesIO, filename)
            }
            response = self.client.post("/dahua/compareoutmail", content_type='multipart/form-data', data=data)
            print (response)

    def _test_extract_from_excel(self):  # pass
        excel_file = "../../files/HK01.xlsx"
        res = self._obj._extract_from_excel("HK01", excel_file)
        print(res)

    def _test_request_json_by_no(self):  # pass
        no = "4437219120093"
        resp = self._obj._request_json_by_no(no)
        print(resp)

    def _test_extract_template_code(self):  # pass
        save_file_path = filename = "../../test/scan_20.01.07/c_dahua.pdf"
        # resp = self._obj._extract_template_code(save_file_path)
        # print(resp)

        resp = self._obj._extract_template_code(save_file_path, with_no_and_po=True)
        print(resp)

    def _test_request_dh_template_info(self):  # pass
        resp = self._obj._request_dh_template_info("HK01", "DAHUA TECHNOLOGY(HK) LIMITED")
        print(resp)

    def _test_dh_login(self):  # pass
        resp = self._obj._dh_login()
        print(resp)

    def _test_request_json_by_po(self):  # pass
        po = "DH-40150506"
        resp = self._mail_obj._request_json_by_po(po)
        print(resp)

    def _test_extract_review_file(self):  # pass
        no = "4437219120093"
        template_code = "HK01"
        template_file = "../../files/HK01.xlsx"
        save_file_path = "../../files/scan_01.pdf"
        template_dict = self._obj._extract_from_excel("HK01", "DAHUA TECHNOLOGY(HK) LIMITED", template_file)
        post_json_data = self._obj._request_json_by_no(no)
        extract_key_info, review_info = self._obj._extract_review_file(template_code, template_dict, post_json_data,
                                                                       save_file_path)
        return (extract_key_info, review_info)

    def _test_report_review_info(self):  # pass
        extract_key_info, review_info = self._test_extract_review_file()

        self._obj.init_request()
        check_contract_info_list = self._obj._report_review_info(review_info, uuid=self._obj._uuid, origin=0)
        print(check_contract_info_list)

    def _test_report_extract_info(self):  # pass
        extract_key_info, review_info = self._test_extract_review_file()

        template_code = "HK01"
        user_id = "test_user"
        no = "4437219120093"
        save_file_path = "../../files/scan_01.pdf"
        jsession_id = self._obj._dh_login()
        self._obj.init_request()

        post_json_data_list = self._obj._request_json_by_no(no)
        crm_id_list = [each["Id"] for each in post_json_data_list if "Id" in each and each["Id"]]
        check_contract_info_list = self._obj._report_review_info(review_info, uuid=self._obj._uuid, origin=0)
        with open(save_file_path, "rb") as fr:
            attach_file_data = fr.read()
        row_id = self._obj._report_extract_info(extract_key_info, template_code, userid=user_id,
                                                jsession_id=jsession_id, crm_id_list=crm_id_list,
                                                check_contract_info_list=check_contract_info_list,
                                                attach_file_data=attach_file_data)
        print(row_id)

    def _test_upload_contract_attach(self):  # pass
        jsession_id = self._obj._dh_login()
        row_id = "1-17MFIGR"
        with open("../../files/scan_01.pdf", "rb") as fr:
            post_file = fr.read()
        upload_status = self._mail_obj._upload_contract_attach(row_id, post_file, jsession_id=jsession_id)
        print(upload_status)

    def _test_idps_utils_check_info(self):
        from tools.idps import idps_utils
        task_id = "1629"
        resp = idps_utils.check_info(task_id)
        print(resp)


if __name__ == '__main__':
    unittest.main()
