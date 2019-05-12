import urllib3
import json
import os
from base64 import b64encode
import sys

class PcManager():

    def __init__(self, ip_addr, username, password):
        # Initialise the options.
        self.ip_addr = ip_addr
        self.username = username
        self.password = password
        self.rest_params_init()

    # Initialize REST API parameters
    def rest_params_init(self, sub_url="", method="",
                         body=None, content_type="application/json", response_file=None):
        self.sub_url = sub_url
        self.body = body
        self.method = method
        self.content_type = content_type
        self.response_file = response_file

    # Create a REST client session.
    def rest_call(self):
        base_url = 'https://%s:9440/api/nutanix/v3/%s' % (
            self.ip_addr, self.sub_url)
        if self.body and self.content_type == "application/json":
            self.body = json.dumps(self.body)

        creds = '%s:%s' % (self.username, self.password)
        base64string = b64encode(creds.encode()).strip().decode()
        
        header = {
            'Authorization': 'Basic %s' % base64string,
            'Content-Type': '%s; charset=utf-8' % self.content_type
        }

        http = urllib3.PoolManager(headers=header)
        response = http.request(method=self.method, url=base_url, body=self.body)

        if response:
            urllib3.disable_warnings()
            response = json.loads(response.data.decode('UTF-8'))
        return response

    def search_blueprint(self, blueprint_name):
        body = {
            "filter": "name==%s" % blueprint_name,
            "length": 250,
            "offset": 0
        }
        self.rest_params_init(sub_url="blueprints/list", method="POST", body=body)
        return self.rest_call()
    
    def get_blueprint(self, blueprint_uuid):
        sub_url = 'blueprints/%s' % blueprint_uuid
        self.rest_params_init(sub_url=sub_url, method="GET")
        return self.rest_call()

    def launch_blueprint(self, blueprint_uuid, blueprint_spec):
        sub_url = 'blueprints/%s/launch' % blueprint_uuid
        self.rest_params_init(sub_url=sub_url, method="POST", body=blueprint_spec)
        return self.rest_call()

    def get_blueprint_uuid(self, blueprint_name):
        bp = self.search_blueprint(blueprint_name)
        bp_uuid = bp['entities'][0]['metadata']['uuid']
        return bp_uuid  

class CalmAzureDevOps(object):

    ###########################################################################
    # Main execution path
    ###########################################################################

    def __init__(self):
        """Main execution path """

        # PrismCentralInventory data
        self.data = {}  # All PrismCentral data

        # Read settings, environment variables, and CLI arguments
        self.read_environment()

    def read_environment(self):
        """ Reads the settings from environment variables """
        # Setup PC IP
        if os.getenv("PC_IP"):
            self.ip_addr = os.getenv("PC_IP")
        # Setup credentials
        if os.getenv("PC_USERNAME"):
            self.username = os.getenv("PC_USERNAME")
        if os.getenv("PC_PASSWORD"):
            self.password = os.getenv("PC_PASSWORD")
        # Setup Calm
        if os.getenv("CALM_APPNAME"):
            self.calm_appname = os.getenv("CALM_APPNAME")
        if os.getenv("CALM_APPPROFILENAME"):
            self.calm_appprofilename = os.getenv("CALM_APPPROFILENAME")
        if os.getenv("CALM_BPNAME"):
            self.calm_bpname = os.getenv("CALM_BPNAME")
        if os.getenv("CALM_PRJNAME"):
            self.calm_prjname = os.getenv("CALM_PRJNAME")

        # Verify Prism Central IP was set
        if not hasattr(self, 'ip_addr'):
            msg = 'Could not find values for PrismCentral ip_addr. They must be specified via either ini file, ' \
                  'command line argument (--ip-addr, -i), or environment variables (PC_IP_ADDR)\n'
            sys.stderr.write(msg)
            sys.exit(-1)

        # Verify credentials were set
        if not hasattr(self, 'username'):
            msg = 'Could not find values for PrismCentral username. They must be specified via either ini file, ' \
                  'command line argument (--username, -u), or environment variables (PC_USERNAME)\n'
            sys.stderr.write(msg)
            sys.exit(-1)
        if not hasattr(self, 'password'):
            msg = 'Could not find values for PrismCentral password. They must be specified via either ini file, ' \
                  'command line argument (--password, -p), or environment variables (PC_PASSWORD)\n'
            sys.stderr.write(msg)
            sys.exit(-1)

        self.manager = PcManager(self.ip_addr, self.username, self.password)

        bp_uuid, bp_spec = self.build_blueprintSpec(self.calm_appname, self.calm_appprofilename, self.calm_bpname, self.calm_prjname)
        
        self.manager.launch_blueprint(bp_uuid, bp_spec)

    def build_blueprintSpec(self, calm_appname, calm_appprofilename, calm_bpname, calm_prjname):        
        bp_uuid = self.manager.get_blueprint_uuid(calm_bpname)
        bp_spec = self.manager.get_blueprint(bp_uuid)
        bp_spec.pop('status')
        bp_spec['spec'].pop('name')
        bp_spec['spec']['application_name'] = calm_appname

        app_profile_uuid = None
        app_profile_list = bp_spec['spec']['resources']['app_profile_list']
        i = 0
        while i < len(app_profile_list):
            app_profile = app_profile_list[i]
            if app_profile['name'] == calm_appprofilename:
                app_profile_uuid = app_profile['uuid']
                break  
            i += 1
        if app_profile_uuid == None:
            raise Exception("App profile with name " + calm_appprofilename + " not found in list")
        app_profile_reference = {}
        app_profile_reference['kind'] = 'app_profile'
        app_profile_reference['uuid'] = app_profile_uuid
        bp_spec['spec']['app_profile_reference'] = app_profile_reference
        return bp_uuid, bp_spec

CalmAzureDevOps()
