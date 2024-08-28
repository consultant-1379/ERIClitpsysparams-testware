#!/usr/bin/env python

'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Aug 2014
@author:    Priyanka/Maria
@summary:    Integration tests for the creation, update and removal of
             system parameters in the deployment model
            Agile: STORY LITPCDS-2327
'''

from litp_cli_utils import CLIUtils
from xml_utils import XMLUtils
from redhat_cmd_utils import RHCmdUtils
from litp_generic_test import GenericTest
import test_constants


class Story2327(GenericTest):

    '''
    As a LITP User, I want a model extension for system parameters,
    so that I can include them in my deployment description
    '''

    def setUp(self):
        """
        Description:
            Runs before every single test
        Actions:
            1. Call the super class setup method
            2. Set up variables used in the tests
        Results:
            The super class prints out diagnostics and variables
            common to all tests are available.
        """
        # 1. Call super class setup
        super(Story2327, self).setUp()
        self.test_ms = self.get_management_node_filename()
        self.test_nodes = self.get_managed_node_filenames()
        self.cli = CLIUtils()
        self.xml = XMLUtils()
        self.redhatutils = RHCmdUtils()

    def tearDown(self):
        """
        Description:
            Runs after every single test
        Actions:
            1. Perform Test Cleanup
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        super(Story2327, self).tearDown()

    def _create_sysparam_config(self, config_path, config_name):
        """
        Description:
            Creates sysparam node config
        Args:
            config_path(str): config_path
            config_name(str): config_name
        Actions:
            1. Create sysparam config
        Results:
            system-param config item-type is successfully created
        """
        config_type = "sysparam-node-config"
        # Create a sysparam-node-config
        config_url = config_path + "/{0}".format(config_name)
        self.execute_cli_create_cmd(
            self.test_ms, config_url, config_type)
        return config_url

    def _create_system_param(self, param_path, system_param_name, props):
        """
        Description:
            Create a system-param item-type
        Args:
            param_path (str): sysparam path
            system_param_name (str): system-param name
            props (str): properties to be created

        Actions:
            1. Create system-param item-type
        Results:
            system-param item-type is successfully created
        """

        sys_param_path = param_path + "/params/{0}".format(system_param_name)
        self.execute_cli_create_cmd(
            self.test_ms, sys_param_path, "sysparam", props)
        return sys_param_path

    def _update_system_param_props(self, param_path, system_param_name, props):
        """
        Description:
            Updates a system-param item-type
        Args:
            param_path (str): system-param path
            system_param_name (str): system-param name
            props (str): properties to be updated
        Actions:
            1. Update system-param item-type
        Results:
            system-param item-type is successfully updated
        """
        sys_param_path = param_path + "/params/{0}".format(system_param_name)
        self.execute_cli_update_cmd(
            self.test_ms, sys_param_path, props)

    def _remove_system_param(self, param_path, system_param_name):
        """
        Description:
            removes a system-param item-type
        Args:
            param_path (str): path to system-param
            system_param_name (str): system-param name
        Actions:
            1. Remove system-param item-type
        Results:
             system-param item-type is successfully removed
        """
        system_param = param_path + "/params/{0}".format(system_param_name)
        self.execute_cli_remove_cmd(
            self.test_ms, system_param)

    def _update_keyvalue_in_sysctl_conf(self, node, old_value, new_value):
        """
        Description:
            Function that replaces the key=old_value in sysctl.conf file with
            key=new_value and loads the /etc/sysctl.conf settings
        Args:
            node (str) : The node to find the file on.
           old_value (str): The old string that should be replaced.
           new_value (str): The new string.
       Actions:
            1. Replace the old value of system parameter with new value
        Results:
             Successfully replaced the value

        """

        # Replace the existing value with new value
        cmd = self.redhatutils.get_replace_str_in_file_cmd(
            old_value, new_value, test_constants.SYSCTL_CONFIG_FILE,
            sed_args='-i')
        std_out, std_err, rc = self.run_command(node, cmd, su_root=True)
        self.assertEquals([], std_err)
        self.assertEqual([], std_out)
        self.assertEquals(0, rc)

        # Load the sysctl.conf file
        cmd = self.redhatutils.get_sysctl_cmd(
            '-e -p {0}'.format(test_constants.SYSCTL_CONFIG_FILE))
        stdout, stderr, rc = self.run_command(node, cmd, su_root=True)
        self.assertEquals([], stderr)
        self.assertNotEqual([], stdout)
        self.assertEquals(0, rc)

    def _find_keyvalue_in_sysctl_conf(self, node, option):
        """
        Description:
            Function to find a specific key = value
            in the sysctl.conf file.
        Args:
            node (str) : The node to find the file on.
            option (str): parameter name
        Actions:
            1. finds the key in the file
        Results:
             Successfully checked the parameter and returns key=value

        """
        cmd = self.redhatutils.get_grep_file_cmd(
            test_constants.SYSCTL_CONFIG_FILE, option)
        std_out, std_err, rc = self.run_command(node, cmd, su_root=True)
        self.assertEquals([], std_err)
        self.assertNotEqual([], std_out)
        self.assertEquals(0, rc)
        return std_out[0]

    def obsolete_01_p_create_remove_system_param_positive(self):
        """
        Description:

        This test changed to obsolete because Test case01
        is duplicated in the story 5774

        Test that an preexisting key in the sysctl.conf file and
        a key not present in sysctl.conf file can be configured and
        removed through the deployment model
        and that a manually updated key will not be overwritten

        Actions:
        1. Backup sysctl.conf file to tmp_location
        2. Create a sysparam-node-config
        3. Define system-param with pre-existing key(a) in the file
        4. Update another pre-existing key(c) in the file manually
        5. Create plan
        6. Run plan
        7. Check properties in the model
        8. Check that puppet has not overridden the updated value for key(c)
           in the sysctl.conf file
        9. Remove the system-param item-types that have been created
        10.Check their states are, "ForRemoval"
        11.Create plan
        12.Check for CardinalityError
        13. remove sysparam-node-config
        14.Create_plan
        15.Run plan

        Result:
        Successfully added the preexisting key(a) in the model
        The manually updated key(c) in the sysctl.conf file was not
        overwritten by puppet
        Successfully removed the preexisting key(a) from the model
        Successfully returned key(c) in the sysctl.conf file to
        it's original value
        """
        pass

    def obsolete_02_n_check_system_parameter_validation_negative(self):
        """
        Description:

        This test changed to obsolete because Test case02
        is duplicated in the story 5774

             Test the system-param item-type validation

        Actions:
        1. Create a sysparam-node-config
        2. Attempt to create system-param key with an empty string
        3. Attempt to create system-param with key contains ,
        4. Attempt to create system-param with key contains =
        5. Attempt to create system-param value to empty string
        6. Attempt to create system-param with an additional property
        7. Attempt to create system-param with a missing value property
        8. Attempt to create system-param with missing key property
        9. Check the same key cannot be specified more than once for a node
           - fails with error at create_plan
        10. Attempt to remove the key
        11. Attempt to remove the value
        12. Attempt to remove non existing system-param
        13. Attempt to remove "system-param node config" from the model

        Result:
            Successfully checked the system-param item-type validation
        """
        pass

    def obsolete_03_p_update_system_parameter_positive(self):
        """
        Description:

        This test changed to obsolete because Test case03
        is duplicated in the story 5774

        Test that a value of a key and the key name can be
        updated through the deployment model

        Actions:
        1. Create a sysparam-node-config
        2. Define 2 system-param item-types
        3. Create plan
        4. Run plan
        5. Check their states are, "Applied"
        6. Update the value of the system-param
        7. Update the name of the key of the other system-param
        8. Check their states are, "Updated"
        9. Create plan
        10. Run plan
        11. Check their states are, "Applied"
        Result:
            Successfully updated the key value and key name in
            the deployment model
        """
        pass

    def obsolete_04_p_system_param_export_load_xml(self):
        """
        Description:

        This test changed to obsolete because Test case04
        is duplicated in the story 5774

        Verify system parameter can be exported and loaded

        Actions:
        1. Create a sysparam-node-config
        2. Define system-param
        3. export the sysparam-node-config
        4. load the system-param node config into model
           using --merge
        5. load the system-param node config into model
           using --replace
        6. export system-param
        7. remove system-param
        8. load the system-param into model
        9. Copy xml files onto the MS
           XML file contains
           ==> an updated key
           ==> removed key
           ==> Created key
        10. Load xml file using the --merge
        11. Load xml file using the --replace
        12. Create plan
        13. Run plan
        14. Check state of items in tree
        15. Remove all items that were loaded

        Result:
            Successful export and load of the xml snippets
        """
        pass
