"""Tests for minimal gnoi_reset module."""

import imp
import os
import sys
import logging

if sys.version_info >= (3, 3):
    from unittest import mock
else:
    import mock

test_path = os.path.dirname(os.path.abspath(__file__))
sonic_host_service_path = os.path.dirname(test_path)
host_modules_path = os.path.join(sonic_host_service_path, "host_modules")
sys.path.insert(0, sonic_host_service_path)

VALID_RESET_REQUEST = '{"factoryOs": true}'
ZERO_FILL_REQUEST = '{"factoryOs": true, "zeroFill": true}'
RETAIN_CERTS_REQUEST = '{"factoryOs": true, "retainCerts": true}'
INVALID_RESET_REQUEST = '"factoryOs": true, "zeroFill": true'

# Dynamically load modules from host_modules/
imp.load_source("host_service", host_modules_path + "/host_service.py")
imp.load_source("gnoi_reset", host_modules_path + "/gnoi_reset.py")
from gnoi_reset import *


class TestGnoiReset:
    @classmethod
    def setup_class(cls):
        with mock.patch("gnoi_reset.super"):
            cls.gnoi_reset_module = GnoiReset(MOD_NAME)

    def test_zero_fill_unsupported(self):
        result = self.gnoi_reset_module.issue_reset(ZERO_FILL_REQUEST)
        assert result[0] == 0
        assert result[1] == (
            '{"reset_error": {"zero_fill_unsupported": true, '
            '"detail": "zero_fill operation is currently unsupported."}}'
        )

    def test_retain_certs_warning(self, caplog):
        with caplog.at_level(logging.WARNING):
            result = self.gnoi_reset_module.issue_reset(RETAIN_CERTS_REQUEST)
            assert (
                caplog.records[0].message
                == "gnoi_reset: retain_certs is currently ignored."
            )
            assert result[0] == 0
            assert result[1] == (
                '{"reset_error": {"other": true, '
                '"detail": "Method FactoryReset.Start is unimplemented."}}'
            )

    def test_invalid_json_format(self):
        result = self.gnoi_reset_module.issue_reset(INVALID_RESET_REQUEST)
        assert result[0] == 0
        assert result[1] == (
            '{"reset_error": {"other": true, '
            '"detail": "Invalid JSON format in request."}}'
        )

    def test_valid_request_unimplemented(self):
        result = self.gnoi_reset_module.issue_reset(VALID_RESET_REQUEST)
        assert result[0] == 0
        assert result[1] == (
            '{"reset_error": {"other": true, '
            '"detail": "Method FactoryReset.Start is unimplemented."}}'
        )

    def test_register(self):
        result = register()
        assert result[0] == GnoiReset
        assert result[1] == MOD_NAME

    @classmethod
    def teardown_class(cls):
        print("TEARDOWN")
