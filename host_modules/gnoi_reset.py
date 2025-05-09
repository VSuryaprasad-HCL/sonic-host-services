"""gNOI reset module which performs factory reset."""

import json
import logging
import threading
from host_modules import host_service

MOD_NAME = "gnoi_reset"
logger = logging.getLogger(__name__)

class GnoiReset(host_service.HostModule):
    """DBus endpoint that handles factory reset requests but returns unimplemented."""

    def __init__(self, mod_name):
        self.lock = threading.Lock()
        self.reset_request = {}
        self.reset_response = {}
        super(GnoiReset, self).__init__(mod_name)

    def populate_reset_response(
        self,
        reset_success=True,
        factory_os_unsupported=False,
        zero_fill_unsupported=False,
        detail="",
    ) -> tuple[int, str]:
        """Generate a reset response."""
        with self.lock:
            self.reset_response = {}
            if reset_success:
                self.reset_response["reset_success"] = {}
            else:
                self.reset_response["reset_error"] = {}
                if factory_os_unsupported:
                    self.reset_response["reset_error"]["factory_os_unsupported"] = True
                elif zero_fill_unsupported:
                    self.reset_response["reset_error"]["zero_fill_unsupported"] = True
                else:
                    self.reset_response["reset_error"]["other"] = True
                self.reset_response["reset_error"]["detail"] = detail

            response_data = json.dumps(self.reset_response)
            return 0, response_data

    def _parse_arguments(self, options) -> tuple[int, str]:
        """reject the factory reset as unimplemented."""
        try:
            self.reset_request = json.loads(options)
        except ValueError:
            return self.populate_reset_response(
                reset_success=False,
                detail="Invalid JSON format in request."
            )

        if "zeroFill" in self.reset_request and self.reset_request["zeroFill"]:
            return self.populate_reset_response(
                reset_success=False,
                zero_fill_unsupported=True,
                detail="zero_fill operation is currently unsupported."
            )

        if "retainCerts" in self.reset_request and self.reset_request["retainCerts"]:
            logger.warning("%s: retain_certs is currently ignored.", MOD_NAME)

        return self.populate_reset_response(
            reset_success=False,
            detail="Method FactoryReset.Start is unimplemented."
        )

    @host_service.method(
       host_service.bus_name(MOD_NAME), in_signature="as", out_signature="is")
    def issue_reset(self, options) -> tuple[int, str]:
        print("Issueing reset from Back end")
        return self._parse_arguments(options)


def register():
    """Return the class name for D-Bus registration."""
    return GnoiReset, MOD_NAME
